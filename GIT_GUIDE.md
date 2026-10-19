# Git & GitHub Cheatsheet: Mental Model, Commands & Arch CLI Workflow

A practical reference guide designed for developers on Arch Linux using Git and the official GitHub CLI (`gh`).

---

## 1. The Core Mental Model: Git Architecture

### Why Git is Not Like Google Drive or Dropbox
Dropbox and Google Drive continuously sync files byte-by-byte in the background. If you make a typo or accidentally delete half a function, that bad state syncs instantly.

Git is an **offline-first, distributed content-addressable version control system**. It does **not** track continuous file streams; it records **explicit, immutable snapshots** of your project over time.

### The 4 Zones of Git

```
┌─────────────────┐       git add       ┌─────────────────┐
│ Working Tree    │ ──────────────────> │  Staging Area   │ (The Index)
│ (Your files on  │                     │ (Preparation    │
│  disk / editor) │ <────────────────── │  room for next  │
└─────────────────┘     git restore     │  snapshot)      │
                                        └─────────────────┘
                                                 │
                                                 │ git commit
                                                 ▼
┌─────────────────┐       git push      ┌─────────────────┐
│ Remote Repo     │ <────────────────── │ Local Repo      │ (.git directory)
│ (GitHub /       │                     │ (Committed      │
│  origin /       │ ──────────────────> │  history /      │
│  upstream)      │  git fetch / pull   │  HEAD)          │
└─────────────────┘                     └─────────────────┘
```

| Zone | What it is | Where it lives |
|---|---|---|
| **1. Working Directory** | The actual files you see, edit, run, and break. | Your project folder |
| **2. Staging Area (Index)** | The curated list of changes queued for the next commit. | Inside `.git/index` |
| **3. Local Repository** | Your sealed, permanent commit history on your local machine. | Inside `.git/objects/` |
| **4. Remote Repository** | The cloud copy on GitHub (`origin`, `upstream`) shared with others. | GitHub servers |

---

## 2. Why Does the "Staging Area" (Commit Stage) Exist?

Why can't we just have `git upload`?

### The Bento Box Analogy
- **Working Tree**: Your kitchen counter. You chop vegetables, spill flour, open sauce jars, try weird spices.
- **Staging Area**: The bento box. You deliberately place only the items you want to serve.
- **Commit**: Sealing the box and stamping it with a date, author, and description.
- **Push**: Loading the boxes onto the delivery truck (GitHub).

### 4 Reasons Staging Exists

1. **Atomic Commits (Separation of Concerns)**
   Suppose you worked for 3 hours and touched 6 files:
   - 2 files fix a nasty bug in `data_loader.py`.
   - 3 files implement a new model architecture.
   - 1 file has random test code or debug prints.
   Without staging, an upload would lump everything into one messy commit. With staging (`git add`), you can commit the bug fix alone (`git commit -m "fix: resolve memory leak in data loader"`), then commit the new feature separately, and discard your debug prints.

2. **Accidental Leak Prevention (Sanity Checking)**
   Before sealing a commit, `git diff --staged` lets you inspect exactly what is about to enter history. This prevents committing `.env` files with secret API keys, multi-gigabyte temporary model weights, or unintended edits.

3. **Offline Speed & Distributed Resilience**
   Creating a commit takes under 5 milliseconds because it writes to your local SSD. You do not need Wi-Fi or GitHub uptime to commit. You can commit 20 times while on a train or offline, and push all 20 commits in one go when you reconnect.

4. **Clean Git History for `git bisect` and Rollbacks**
   If a regression happens 2 months later, clean commits allow Git's binary search (`git bisect`) to pinpoint the exact commit that broke the build. If every edit was an automatic cloud save, history would be millions of unusable noise entries.

---

## 3. How to Check "Am I In Sync?"

A common beginner trap is thinking `git status` checks GitHub. **It does not.** `git status` only compares your **Working Tree** with your **Local `.git` repository** and the last cached state of remotes.

### Step 1: The Three Questions to Ask

1. **Do I have uncommitted local edits?**
   ```bash
   git status
   ```
2. **Has the remote changed since my last fetch?**
   ```bash
   git fetch origin
   git fetch upstream
   ```
3. **Is my local branch ahead or behind?**
   ```bash
   # Commits you made that are not yet on GitHub:
   git log origin/main..HEAD --oneline

   # Commits on upstream (instructor repo) that you don't have:
   git log HEAD..upstream/main --oneline
   ```

### Step 2: Interpreting `git status` Output

- **`nothing to commit, working tree clean`**: Everything in your directory matches your latest local commit.
- **`Untracked files`**: Files created that Git has never seen before.
- **`Changes not staged for commit`**: Tracked files that were modified, but not yet added to the next commit.
- **`Changes to be committed`**: Files staged in the Index, ready for `git commit`.
- **`Your branch is ahead of 'origin/main' by X commits`**: You made commits locally, but haven't run `git push`.
- **`Your branch is behind 'origin/main' by X commits`**: Someone (or you from another machine) pushed to GitHub; run `git pull`.
- **`Your branch and 'origin/main' have diverged`**: Both you and the remote have different commits. Needs a merge or rebase.

---

## 4. Essential Git Commands Cheatsheet

### Inspecting State & History
```bash
# High-level repo status
git status

# Compact one-line status
git status -s

# See unstaged edits line-by-line
git diff

# See staged edits line-by-line (what WILL be in the next commit)
git diff --staged

# Clean, readable commit history graph
git log --oneline --graph --decorate -n 10

# Inspect the contents of a specific commit
git show <commit_hash>
```

### Staging & Committing
```bash
# Stage a specific file
git add path/to/file.py

# Stage all modified and new files
git add -A

# Interactive staging: review and stage file changes chunk-by-chunk (very powerful!)
git add -p

# Commit staged changes with a message
git commit -m "feat: implement training pipeline"

# Amend the most recent commit (add forgotten files or fix commit message)
# (Only do this BEFORE pushing!)
git commit --amend --no-edit
```

### Syncing Remotes (`origin` & `upstream`)
```bash
# Download latest info from remotes without merging
git fetch origin
git fetch upstream

# Push your local commits to your GitHub fork
git push origin main

# Pull remote commits and merge into your local branch
git pull origin main

# Pull updates cleanly with rebase (keeps history linear)
git pull --rebase upstream main
```

### Undoing & Fixing Mistakes Safely
```bash
# Unstage a file without losing its edits (move from Staged -> Working Tree)
git restore --staged <file>

# Discard all uncommitted changes in a specific file (DANGEROUS: cannot undo)
git restore <file>

# Undo the last commit, but keep all file changes staged
git reset --soft HEAD~1

# Undo the last commit and unstage changes, but keep files in working directory
git reset HEAD~1

# Temporarily shelve uncommitted work to clean directory
git stash

# Restore shelved work
git stash pop
```

---

## 5. GitHub CLI (`gh`) on Arch Linux

On Arch Linux, `gh` is installed via `pacman -S github-cli`. It interacts with GitHub's REST/GraphQL APIs directly from your terminal.

### Authentication & Account
```bash
# Check logged-in account, protocol, and token scopes
gh auth status

# Re-authenticate or switch accounts
gh auth login

# Open GitHub web settings for SSH keys or tokens
gh auth setup-git
```

### Repository Operations
```bash
# View repo details, description, and README directly in your pager/terminal
gh repo view

# Open current repository directly in your default Linux browser (Firefox/Chromium)
gh repo view --web

# View the upstream parent repo in browser
gh repo view upstream --web

# Clone any repo directly via GitHub handle
gh repo clone owner/repository
```

### The Ultimate Fork Sync Command (`gh repo sync`)
Instead of manually doing `git fetch upstream` + `git merge upstream/main` + `git push origin main`, `gh` can do it in one command:
```bash
# Sync your GitHub fork directly with the upstream parent repository
gh repo sync

# Sync a specific local branch with upstream
gh repo sync --branch main
```

### Pull Requests & Issues
```bash
# View open PRs in terminal
gh pr list

# Create a Pull Request with an interactive terminal wizard
gh pr create

# Create PR and open the browser editor immediately
gh pr create --web

# Check out a colleague's or student's PR locally to test it
gh pr checkout <pr_number>

# List open issues
gh issue list
```

### GitHub Actions & CI/CD
```bash
# See recent workflow runs for this repo
gh run list

# Watch a running GitHub Action in real-time in terminal
gh run watch
```

---

## 6. Daily Lab Workflows: Quick Recipes

### Recipe A: Daily Edit & Sync Workflow
When completing a lab practical (e.g. `P06`, `P07`):

```bash
# 1. Check what you changed
git status

# 2. Check the exact diff
git diff

# 3. Stage the files
git add P06-mlflow/S24CSEU2194_P06.ipynb P06-mlflow/SCSE3040_P06_S24CSEU2194.pdf

# 4. Review staged changes
git diff --staged

# 5. Commit with an intentional message
git commit -m "Add P06 solution and report (S24CSEU2194)"

# 6. Push to your GitHub fork
git push origin main

# 7. Verify state
git status
```

### Recipe B: Syncing New Labs from Course Upstream
When the lab instructor publishes a new practical (e.g., `P08`, `P09`):

```bash
# Option 1 (Using GitHub CLI - fastest):
gh repo sync parth-sarthi-code/SCSE3040-Lab --source Bennett-MLOps-Lab/SCSE3040-Lab
git pull origin main

# Option 2 (Standard Git):
git fetch upstream
git merge upstream/main
git push origin main
```

### Recipe C: End of Day "Is Everything Saved?" Checklist
Run this before shutting down your PC:

```bash
git fetch origin
git status
```
If you see:
```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```
...you are 100% safely backed up to GitHub.

---

## 7. Recommended Bash/Zsh Aliases (Arch Linux)

Add these to your `~/.bashrc` or `~/.zshrc` for faster navigation:

```bash
alias gs="git status -sb"
alias gl="git log --oneline --graph --decorate -n 15"
alias gd="git diff"
alias gds="git diff --staged"
alias gsync="gh repo sync && git pull origin main"
alias gclean="git fetch origin && git status"
```
