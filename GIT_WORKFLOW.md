# Git Workflow Guide for Hydroponics Project

## Initial Setup (One-time)

1. **Copy the `.gitignore` file to your project root**
2. **Run the setup script** (or follow manual steps below)

### Manual Setup:
```bash
cd /path/to/your/hydroponics/project
git init
git add .
git commit -m "Initial commit: Hydroponics monitoring system"
```

## Connecting to GitHub/GitLab

### Create a new repository on your Git hosting platform, then:

```bash
# Add remote repository
git remote add origin https://github.com/yourusername/hydroponics-system.git

# Push to remote (first time)
git branch -M main  # Rename branch to main if needed
git push -u origin main
```

## Daily Workflow

### Making Changes:
```bash
# Check what files changed
git status

# Stage specific files
git add src/hydroponics/core/main.py

# Or stage all changes
git add .

# Commit with a descriptive message
git commit -m "Add temperature alert threshold feature"

# Push to remote
git push
```

### Getting Updates:
```bash
# Pull latest changes from remote
git pull

# Or if you have local changes, stash them first
git stash
git pull
git stash pop
```

## Branching Strategy

### Feature Development:
```bash
# Create a new feature branch
git checkout -b feature/temperature-alerts

# Work on your feature, commit changes
git add .
git commit -m "Implement temperature alert logic"

# Push feature branch
git push -u origin feature/temperature-alerts

# When ready, merge back to main
git checkout main
git pull
git merge feature/temperature-alerts
git push
```

### Bug Fixes:
```bash
# Create a bugfix branch
git checkout -b bugfix/sensor-reading-error

# Fix the bug, commit
git add .
git commit -m "Fix sensor reading timeout issue"

# Push and merge
git push -u origin bugfix/sensor-reading-error
```

## Viewing History

```bash
# View commit history
git log

# View compact history
git log --oneline

# View changes in last commit
git show

# View changes in a specific file
git log -p src/hydroponics/core/main.py
```

## Undoing Changes

### Unstage files:
```bash
git reset HEAD <file>
```

### Discard local changes:
```bash
# Discard changes in specific file
git checkout -- <file>

# Discard all local changes (careful!)
git reset --hard
```

### Undo last commit (keep changes):
```bash
git reset --soft HEAD~1
```

## Important Notes for This Project

- **Never commit:**
  - `.db` files (databases are in .gitignore)
  - `.log` files (logs are ignored)
  - The `venv/` directory (virtual environment)
  - Config files with API keys or secrets

- **Always commit:**
  - Source code in `src/`
  - Documentation in `docs/`
  - Requirements files (`requirements.txt`, `requirements-raspi.txt`)
  - Tests in `tests/`
  - Templates and static files

## Collaboration Tips

### Before starting work:
```bash
git pull  # Get latest changes
```

### Before committing:
```bash
git status  # Review what you're committing
```

### Commit messages:
- Use present tense: "Add feature" not "Added feature"
- Be descriptive: "Add temperature alert threshold feature"
- Reference issues if applicable: "Fix #42: Sensor timeout error"

## Useful Aliases (Optional)

Add these to your `~/.gitconfig`:
```
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    last = log -1 HEAD
    unstage = reset HEAD --
```

Then use: `git st` instead of `git status`, etc.
