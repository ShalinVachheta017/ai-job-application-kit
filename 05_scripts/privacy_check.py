"""Scan the public template for common private-data leaks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCLUDES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
}
TEXT_SUFFIXES = {
    ".csv",
    ".env",
    ".example",
    ".gitignore",
    ".md",
    ".py",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}


PATTERNS = [
    ("possible_email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("possible_phone", re.compile(r"(\+\d{1,3}[\s.-]?)?(\(?\d{2,5}\)?[\s.-]?){2,}\d{3,}")),
    (
        "possible_secret",
        re.compile(
            r"(?i)(api[_-]?key|secret|token|password)[^\S\r\n]*[:=][^\S\r\n]*['\"]?[A-Za-z0-9_./+=-]{8,}"
        ),
    ),
]

ALLOWED_EXAMPLE_TERMS = {
    "alex.example@example.com",
    "+49 000 000000",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
}


def load_denylist(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def should_scan(path: Path) -> bool:
    if any(part in DEFAULT_EXCLUDES for part in path.parts):
        return False
    if path.name.startswith("privacy_denylist"):
        return False
    return path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", "README.md"}


def iter_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and should_scan(path)]


def is_allowed(match: str) -> bool:
    return match in ALLOWED_EXAMPLE_TERMS or "example.com" in match or "alex-example" in match


def scan(root: Path, denylist: list[str]) -> list[str]:
    findings: list[str] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(root)

        for term in denylist:
            if term and term in text:
                findings.append(f"{relative}: denylist term found: {term!r}")

        for name, pattern in PATTERNS:
            for match in pattern.finditer(text):
                value = match.group(0)
                if not is_allowed(value):
                    findings.append(f"{relative}: {name}: {value!r}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT), help="Repository root to scan")
    parser.add_argument(
        "--denylist",
        default=str(ROOT / "privacy_denylist.txt"),
        help="Optional file containing private terms that must not appear",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    denylist = load_denylist(Path(args.denylist))
    findings = scan(root, denylist)

    if findings:
        print("Privacy check failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Privacy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
