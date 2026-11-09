# AI Job Application Kit

## Project Summary

### What is this project?
This is a public template for organizing tailored job applications without sharing real personal data.

### Why is it interesting?
It can be repetitive to read a vacancy, prepare a CV, write a letter and track the result.

### How does it work?
You give it a job description and your own experience information. It helps produce drafts and checks them before you apply.

### Real-life example
You find an opening and use the template to prepare documents to review and submit yourself. Public sample data is fake.

### What did I learn?
I learned how to organize document generation, job matching, and privacy-conscious workflows.

---

## Technical Documentation


A privacy-first template for creating tailored job applications from a job link and a structured personal profile.

The kit is designed for applicants who want a repeatable workflow for:

- fetching a job description from a URL
- checking fit against a user-owned experience bank
- generating a tailored CV and cover letter
- running honesty and quality checks before applying
- tracking every application to avoid duplicates

This repository is a template. It intentionally contains only fake profile data and fake examples.

## How It Works

```text
User provides a job URL
-> script fetches and saves the job description
-> agent reads profile + truth rules + tracker
-> agent scores fit and identifies risks
-> agent generates CV, cover letter, fit score and QA check
-> tracker is updated as draft
```

Automatic job extraction works best on pages with public HTML or schema.org `JobPosting` metadata. Some job boards block automated access. When extraction fails, save the job text manually in `02_job_inputs/job_description.md` and continue with the same workflow.

## Quick Start

1. Copy the example profile files:

```bash
cp 00_user_profile/personal_info.example.yaml 00_user_profile/personal_info.yaml
cp 00_user_profile/experience_bank.example.yaml 00_user_profile/experience_bank.yaml
cp 00_user_profile/truth_rules.example.md 00_user_profile/truth_rules.md
cp 06_tracker/applied_jobs_master.example.csv 06_tracker/applied_jobs_master.csv
cp config.example.yaml config.yaml
```

2. Edit your private files:

```text
00_user_profile/personal_info.yaml
00_user_profile/experience_bank.yaml
00_user_profile/truth_rules.md
config.yaml
```

3. Fetch a job description from a link:

```bash
python 05_scripts/fetch_job_description.py "https://example.com/job-posting"
```

4. Use the workflow prompt:

```text
04_prompts/master_agent_prompt.md
```

5. Before publishing or sharing, run:

```bash
python 05_scripts/privacy_check.py
```

## Folder Structure

```text
00_user_profile/              Private user data lives here
01_templates/                 Generic CV and cover letter templates
02_job_inputs/                Fetched or manually saved job descriptions
03_generated_applications/    Generated application packages
04_prompts/                   Agent workflow prompt
05_scripts/                   Fetching and privacy-check helper scripts
06_tracker/                   Application tracker template
examples/                     Fake example application
```

## What Users Must Customize

- name and contact details
- language levels
- relocation preferences
- education
- approved work and project bullets
- truth rules
- preferred CV layout
- tracker columns if needed

Keep all real personal files out of Git. The `.gitignore` already excludes the private versions.

## Privacy Rules

Do not commit:

- real CV PDFs
- real cover letters
- real application folders
- real tracker rows
- phone numbers, emails, addresses
- profile photos
- `.env` files or API keys
- LaTeX build outputs

If you accidentally commit private data, `.gitignore` is not enough. Create a fresh clean repository or rewrite Git history before publishing.

## Example

See `examples/example_ai_company/` for a fully fake application package.

## Requirements

- Python 3.10+
- Optional: LaTeX distribution such as TeX Live or MiKTeX if compiling PDF templates

No API key is required for the included fetch and privacy scripts. If you connect this workflow to an LLM provider, store keys in `.env`, never in source files.

## License

MIT. See `LICENSE`.
