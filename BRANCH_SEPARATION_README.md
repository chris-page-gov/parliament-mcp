# Branch Separation Script Documentation

## Overview

The `separate-branches.sh` script automates the process of separating custom commits from the main branch into a new `crpage` branch, while resetting the main branch to match the upstream repository. This is particularly useful when working with a fork that has accumulated custom changes that need to be preserved while keeping the main branch in sync with upstream.

## Purpose

This script solves the common problem of managing a fork where:
- Custom development has been done directly on the main branch
- You need to keep main in sync with the upstream repository
- You want to preserve your custom work in a separate branch

## Quick Start

```bash
# Make the script executable (if not already)
chmod +x separate-branches.sh

# Run with upstream URL
./separate-branches.sh https://github.com/i-dot-ai/parliament-mcp.git

# Or run and provide URL when prompted
./separate-branches.sh
```

## What the Script Does

### Step-by-Step Process

1. **Validates Environment**
   - Checks if you're in a git repository
   - Verifies git state and warns about uncommitted changes
   - Creates a backup branch as a safety measure

2. **Sets Up Upstream Remote**
   - Adds upstream remote if it doesn't exist
   - Updates upstream URL if remote already exists
   - Fetches latest changes from upstream

3. **Ensures Main Branch Exists**
   - Creates local main branch if it doesn't exist
   - Uses origin/main as source if available

4. **Creates/Updates crpage Branch**
   - Creates `crpage` branch from current main (preserving custom commits)
   - Asks for confirmation if crpage already exists

5. **Resets Main to Upstream**
   - Switches to main branch
   - Performs hard reset to upstream/main
   - Asks for explicit confirmation before destructive operation

6. **Pushes Changes**
   - Pushes crpage branch to origin
   - Force-pushes main branch to origin (to update it with upstream changes)

## Command Line Usage

```bash
./separate-branches.sh [UPSTREAM_REPO_URL]
```

### Arguments

- `UPSTREAM_REPO_URL` (optional): The URL of the upstream repository
  - If not provided, you'll be prompted to enter it
  - Example: `https://github.com/i-dot-ai/parliament-mcp.git`

### Examples

```bash
# Provide upstream URL directly
./separate-branches.sh https://github.com/i-dot-ai/parliament-mcp.git

# Interactive mode - script will prompt for URL
./separate-branches.sh

# With SSH URL
./separate-branches.sh git@github.com:i-dot-ai/parliament-mcp.git
```

## Safety Features

### Idempotent Operation
- Can be run multiple times safely
- Checks existing state before making changes
- Won't duplicate work if already completed

### Backup Creation
- Creates timestamped backup branch before any destructive operations
- Format: `backup-before-separation-YYYYMMDD-HHMMSS`
- Allows easy recovery if needed

### Confirmation Prompts
- Warns about uncommitted changes
- Asks for confirmation before destructive operations
- Provides clear information about what will happen

### No Upstream Interference
- Only fetches from upstream, never pushes
- Respects upstream repository integrity
- Only modifies your local and origin remotes

## Post-Script Workflow

After running the script successfully:

### Development Workflow

1. **Continue development on crpage branch:**
   ```bash
   git checkout crpage
   # Make your changes here
   git add .
   git commit -m "Your changes"
   git push origin crpage
   ```

2. **Keep main in sync with upstream:**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

3. **Merge upstream changes into your development branch:**
   ```bash
   git checkout crpage
   git merge main  # Brings in upstream changes
   # Resolve any conflicts if they occur
   git push origin crpage
   ```

### Branch Management

- **main**: Always tracks upstream/main
- **crpage**: Your custom development branch
- **backup-***: Safety backup (can be deleted after verification)

## Troubleshooting

### Common Issues

#### "Not in a git repository"
```bash
# Ensure you're in the repository root
cd /path/to/parliament-mcp
./separate-branches.sh
```

#### "Failed to fetch from upstream"
- Check the upstream URL is correct
- Verify network connectivity
- Ensure you have access to the upstream repository

#### "upstream/main branch not found"
- The upstream repository might use a different default branch (e.g., 'master')
- Check available branches: `git branch -r | grep upstream`
- Contact repository maintainer for correct branch name

#### Force Push Failed
- Check that you have write access to origin
- Verify you're authenticated with GitHub/GitLab

### Recovery Options

#### Restore from Backup
```bash
# List backup branches
git branch | grep backup

# Restore from backup
git checkout backup-before-separation-YYYYMMDD-HHMMSS
git checkout -b recovered-state
```

#### Manual Cleanup
```bash
# If you need to start over
git checkout main
git branch -D crpage  # Delete crpage if needed
git reset --hard origin/main  # Reset main to origin state
./separate-branches.sh  # Run script again
```

## Advanced Usage

### Custom Branch Names

If you need different branch names, you can modify the script variables:
- Edit `separate-branches.sh`
- Change the branch name in the "crpage" sections
- Update documentation accordingly

### Multiple Upstream Remotes

If you work with multiple upstream repositories:
```bash
# Run script for first upstream
./separate-branches.sh https://github.com/upstream1/repo.git

# Manually add second upstream
git remote add upstream2 https://github.com/upstream2/repo.git
git fetch upstream2
```

## Integration with Existing Workflows

### Pre-commit Hooks
Add branch validation to your pre-commit hooks:
```bash
# In .pre-commit-config.yaml or git hooks
- repo: local
  hooks:
    - id: check-branch
      name: Check if on correct branch
      entry: bash -c 'if [[ $(git rev-parse --abbrev-ref HEAD) == "main" ]]; then echo "Direct commits to main not allowed. Use crpage branch."; exit 1; fi'
      language: system
      pass_filenames: false
```

### CI/CD Considerations
Update your CI/CD pipelines to:
- Build and test both main and crpage branches
- Deploy from crpage branch for your custom version
- Monitor main branch for upstream changes

## Best Practices

### Before Running the Script
1. Commit all your work
2. Review what changes you have on main
3. Document any important custom modifications
4. Backup important local changes externally if critical

### After Running the Script
1. Verify the branch separation worked correctly
2. Test your application on the crpage branch
3. Update documentation about the new branch structure
4. Inform team members about the new workflow

### Ongoing Maintenance
1. Regularly sync main with upstream
2. Periodically merge main into crpage
3. Clean up old backup branches
4. Monitor upstream for breaking changes

## Script Validation

To verify the script worked correctly:

```bash
# Check branch structure
git branch -v

# Verify main matches upstream
git diff upstream/main main  # Should show no differences

# Verify crpage has your custom commits
git log --oneline main..crpage  # Shows commits only in crpage

# Check remote tracking
git remote -v
```

## Support

If you encounter issues:
1. Check this documentation first
2. Review the script's output messages
3. Examine your git state with `git status` and `git log`
4. Use the backup branch to recover if needed
5. Consult your team's git workflow documentation