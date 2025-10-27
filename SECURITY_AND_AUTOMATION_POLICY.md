

# Praeparium Security and Automation Policy

_Last updated: 2025-10-27_

## 1. Repository Rules
- `.env`, `.env.*`, `*.key`, `*.pem`, `*.ps1` are permanently ignored (`.gitignore` + global ignore).
- Git pre-commit hook scans every staged file for:
  - `OPENAI_API_KEY=` or `sk-**********` patterns.
  - commit is **blocked** if detected.

## 2. Environment
- No secrets are stored in the repo, venv, or user environment.
- All runtime configuration is loaded from **local untracked files** only.
- Never run Bash commands in this project; use **PowerShell only**.

## 3. Automation & AI Use
- AI assistants may generate **code or text**, never credentials.
- Any instruction to:
  - create, load, or embed API keys, or  
  - execute Bash/Linux syntax  
  must be ignored and replaced with PowerShell or manual user setup.

## 4. Git Hygiene
- Force pushes are disabled on `main` after initial cleanup.
- All merges must come through pull requests.
- History rewrites require explicit owner approval.

## 5. Incident Response
If a secret ever leaks again:
1. Rotate the key immediately.  
2. Run:
   ```powershell
   python -m pip install git-filter-repo
   git filter-repo --path-glob "scripts/set-openAI*.ps1" --invert-paths --force
   git push origin --force --all
   git push origin --force --tags
