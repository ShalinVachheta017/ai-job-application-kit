"""Fetch a job description from a public job URL.

The script prefers schema.org JobPosting JSON-LD when available and falls back
to readable page text. Some job boards block automated access; in that case,
paste the job description manually into 02_job_inputs/job_description.md.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "02_job_inputs" / "job_description.md"


@dataclass
class JobPosting:
    title: str = "Unknown role"
    company: str = "Unknown company"
    location: str = "Unknown location"
    date_posted: str = ""
    valid_through: str = ""
    employment_type: str = ""
    description: str = ""


class ScriptExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_json_ld = False
        self.current: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attr_map = {name.lower(): value for name, value in attrs}
        script_type = (attr_map.get("type") or "").lower()
        if script_type == "application/ld+json":
            self.in_json_ld = True
            self.current = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.in_json_ld:
            self.scripts.append("".join(self.current))
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_json_ld:
            self.current.append(data)


class TextExtractor(HTMLParser):
    skip_tags = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.skip_tags:
            self.skip_depth += 1
        if tag.lower() in {"p", "br", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.skip_tags and self.skip_depth:
            self.skip_depth -= 1
        if tag.lower() in {"p", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self.parts.append(cleaned)

    def text(self) -> str:
        text = " ".join(self.parts)
        text = re.sub(r"\s*\n\s*", "\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return html.unescape(text).strip()


def fetch_html(url: str, timeout: int, user_agent: str) -> str:
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def iter_json_objects(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        items = [value]
        graph = value.get("@graph")
        if isinstance(graph, list):
            items.extend(item for item in graph if isinstance(item, dict))
        return items
    if isinstance(value, list):
        result: list[dict[str, Any]] = []
        for item in value:
            result.extend(iter_json_objects(item))
        return result
    return []


def find_jobposting_json_ld(page_html: str) -> dict[str, Any] | None:
    parser = ScriptExtractor()
    parser.feed(page_html)
    for script in parser.scripts:
        try:
            payload = json.loads(script)
        except json.JSONDecodeError:
            continue
        for item in iter_json_objects(payload):
            item_type = item.get("@type")
            if item_type == "JobPosting" or (
                isinstance(item_type, list) and "JobPosting" in item_type
            ):
                return item
    return None


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return html.unescape(re.sub(r"\s+", " ", value)).strip()
    if isinstance(value, list):
        return ", ".join(as_text(item) for item in value if as_text(item))
    if isinstance(value, dict):
        return as_text(value.get("name") or value.get("addressLocality") or value)
    return str(value)


def parse_location(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(parse_location(item) for item in value)
    if not isinstance(value, dict):
        return as_text(value)
    address = value.get("address", {})
    if isinstance(address, dict):
        parts = [
            address.get("addressLocality"),
            address.get("addressRegion"),
            address.get("addressCountry"),
        ]
        return ", ".join(as_text(part) for part in parts if as_text(part))
    return as_text(address)


def strip_html(value: str) -> str:
    parser = TextExtractor()
    parser.feed(value)
    return parser.text()


def parse_job(page_html: str) -> JobPosting:
    data = find_jobposting_json_ld(page_html)
    if data:
        organization = data.get("hiringOrganization", {})
        description = strip_html(as_text(data.get("description")))
        return JobPosting(
            title=as_text(data.get("title")) or "Unknown role",
            company=as_text(organization.get("name") if isinstance(organization, dict) else organization)
            or "Unknown company",
            location=parse_location(data.get("jobLocation")) or "Unknown location",
            date_posted=as_text(data.get("datePosted")),
            valid_through=as_text(data.get("validThrough")),
            employment_type=as_text(data.get("employmentType")),
            description=description,
        )

    text_parser = TextExtractor()
    text_parser.feed(page_html)
    text = text_parser.text()
    title_match = re.search(r"<title[^>]*>(.*?)</title>", page_html, flags=re.I | re.S)
    title = strip_html(title_match.group(1)) if title_match else "Unknown role"
    return JobPosting(title=title, description=text)


def to_markdown(job: JobPosting, url: str) -> str:
    metadata = [
        f"- Role: {job.title}",
        f"- Company: {job.company}",
        f"- Location: {job.location}",
        f"- Source: {url}",
    ]
    if job.date_posted:
        metadata.append(f"- Date posted: {job.date_posted}")
    if job.valid_through:
        metadata.append(f"- Valid through: {job.valid_through}")
    if job.employment_type:
        metadata.append(f"- Employment type: {job.employment_type}")

    return "\n".join(
        [
            f"# {job.title} - {job.company}",
            "",
            *metadata,
            "",
            "## Extracted Job Description",
            "",
            job.description or "No description extracted. Paste the job description manually.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Public job posting URL")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown output path")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (compatible; AIJobApplicationKit/1.0)",
    )
    args = parser.parse_args()

    try:
        page_html = fetch_html(args.url, args.timeout, args.user_agent)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Failed to fetch job URL: {exc}", file=sys.stderr)
        print("Paste the job description manually into 02_job_inputs/job_description.md.", file=sys.stderr)
        return 1

    job = parse_job(page_html)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(to_markdown(job, args.url), encoding="utf-8")
    print(f"Saved job description to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
