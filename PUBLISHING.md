# Publishing This Template To GitHub

Use a fresh repository for the public version. Do not publish a private application workspace with real generated applications in its history.

## Recommended Safe Path

1. Create a new empty GitHub repository, for example:

```text
ai-job-application-kit
```

2. Copy only the contents of `public_template/` into a new local folder.

3. Run the privacy check:

```bash
python 05_scripts/privacy_check.py
```

4. Initialize Git in the clean folder:

```bash
git init
git add .
git commit -m "Initial public template"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-job-application-kit.git
git push -u origin main
```

## Do Not Publish

- the original private workspace
- real `00_user_profile/*.yaml` files
- real `03_generated_applications/` contents
- real `06_tracker/applied_jobs_master.csv`
- real PDFs, DOCX files, profile photos, logs, or screenshots

## Before Every Public Push

Run:

```bash
python 05_scripts/privacy_check.py
git status --short
```

Make sure only template/example files are staged.

## If Private Data Was Already Committed

Do not rely on `.gitignore`. The data is already in Git history.

Safer options:

- create a fresh repository and copy only clean files
- or rewrite history with a tool such as `git filter-repo`

For most users, a fresh repository is simpler and safer.
