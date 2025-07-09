#!/bin/bash

# separate-branches.sh
# 
# Automates the separation of custom commits from main into a new crpage branch,
# and resets main to match upstream/main. This script is designed to be idempotent
# and safe to run multiple times.
#
# USAGE:
#   ./separate-branches.sh [UPSTREAM_REPO_URL]
#
# ARGUMENTS:
#   UPSTREAM_REPO_URL: Optional. The URL of the upstream repository.
#                      If not provided, you'll be prompted to enter it.
#                      Example: https://github.com/i-dot-ai/parliament-mcp.git
#
# EXAMPLES:
#   ./separate-branches.sh https://github.com/i-dot-ai/parliament-mcp.git
#   ./separate-branches.sh  # Will prompt for upstream URL
#
# WHAT THIS SCRIPT DOES:
# 1. Fetches the upstream repository (adds remote if needed)
# 2. Creates a 'crpage' branch from current main to preserve custom commits
# 3. Fetches latest upstream changes and resets main to match upstream/main
# 4. Pushes both branches to origin (main with --force to update it)
# 5. Provides instructions for further usage
#
# SAFETY FEATURES:
# - Idempotent: Can be run multiple times safely
# - Never pushes to upstream repository
# - Creates backups before destructive operations
# - Validates git state before proceeding
# - Provides clear status messages throughout

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BOLD}=== $1 ===${NC}\n"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository! Please run this script from the repository root."
        exit 1
    fi
}

# Function to check if remote exists
remote_exists() {
    git remote | grep -q "^$1$"
}

# Function to get upstream URL
get_upstream_url() {
    local upstream_url="$1"
    
    if [ -z "$upstream_url" ]; then
        echo -e "${YELLOW}Please enter the upstream repository URL:${NC}"
        echo -e "${YELLOW}(Example: https://github.com/i-dot-ai/parliament-mcp.git)${NC}"
        read -p "Upstream URL: " upstream_url
        
        if [ -z "$upstream_url" ]; then
            print_error "Upstream URL is required. Exiting."
            exit 1
        fi
    fi
    
    echo "$upstream_url"
}

# Function to validate URL format
validate_upstream_url() {
    local url="$1"
    if [[ ! "$url" =~ ^https?://.*\.git$ ]] && [[ ! "$url" =~ ^git@.*:.*\.git$ ]] && [[ ! "$url" =~ ^https?://github\.com/.+/.+$ ]]; then
        print_warning "URL format seems unusual. Expected format: https://github.com/user/repo.git"
        echo -e "${YELLOW}Continue anyway? (y/N):${NC}"
        read -p "" confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            print_error "Aborted by user."
            exit 1
        fi
    fi
}

# Function to create backup of current state
create_backup() {
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local backup_branch="backup-before-separation-$(date +%Y%m%d-%H%M%S)"
    
    print_status "Creating backup branch: $backup_branch"
    git branch "$backup_branch" "$current_branch"
    print_success "Backup created: $backup_branch"
    echo "    You can restore with: git checkout $backup_branch"
}

# Function to show help
show_help() {
    echo "Parliament MCP Branch Separation Script"
    echo
    echo "USAGE:"
    echo "  $0 [UPSTREAM_REPO_URL]"
    echo
    echo "ARGUMENTS:"
    echo "  UPSTREAM_REPO_URL  Optional. The URL of the upstream repository."
    echo "                     If not provided, you'll be prompted to enter it."
    echo
    echo "EXAMPLES:"
    echo "  $0 https://github.com/i-dot-ai/parliament-mcp.git"
    echo "  $0  # Will prompt for upstream URL"
    echo
    echo "For detailed documentation, see BRANCH_SEPARATION_README.md"
    echo
}

# Main function
main() {
    # Handle help requests
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    print_header "Parliament MCP Branch Separation Script"
    
    # Check if we're in a git repository
    check_git_repo
    
    # Get the repository root
    REPO_ROOT=$(git rev-parse --show-toplevel)
    cd "$REPO_ROOT"
    
    # Get upstream URL
    UPSTREAM_URL=$(get_upstream_url "$1")
    validate_upstream_url "$UPSTREAM_URL"
    
    print_status "Repository root: $REPO_ROOT"
    print_status "Upstream URL: $UPSTREAM_URL"
    
    # Get current state
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_status "Current branch: $CURRENT_BRANCH"
    
    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        print_warning "You have uncommitted changes!"
        git status --porcelain
        echo -e "${YELLOW}Please commit or stash your changes before continuing.${NC}"
        echo -e "${YELLOW}Continue anyway? (y/N):${NC}"
        read -p "" confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            print_error "Aborted. Please commit or stash your changes first."
            exit 1
        fi
    fi
    
    # Create backup
    create_backup
    
    print_header "Step 1: Setting up upstream remote"
    
    # Add upstream remote if it doesn't exist
    if remote_exists "upstream"; then
        print_status "Upstream remote already exists"
        git remote set-url upstream "$UPSTREAM_URL"
        print_status "Updated upstream URL to: $UPSTREAM_URL"
    else
        print_status "Adding upstream remote: $UPSTREAM_URL"
        git remote add upstream "$UPSTREAM_URL"
        print_success "Upstream remote added"
    fi
    
    # Fetch upstream
    print_status "Fetching from upstream..."
    if git fetch upstream; then
        print_success "Successfully fetched from upstream"
    else
        print_error "Failed to fetch from upstream. Please check the URL and your network connection."
        exit 1
    fi
    
    print_header "Step 2: Ensuring we have main branch locally"
    
    # Check if main branch exists locally
    if git branch | grep -q "main"; then
        print_status "Main branch exists locally"
        git checkout main
    else
        # Check if main exists on origin
        if git branch -r | grep -q "origin/main"; then
            print_status "Creating local main branch from origin/main"
            git checkout -b main origin/main
        else
            print_error "No main branch found on origin. Cannot proceed."
            exit 1
        fi
    fi
    
    print_header "Step 3: Creating crpage branch from current main"
    
    # Create or update crpage branch
    if git branch | grep -q "crpage"; then
        print_warning "crpage branch already exists"
        echo -e "${YELLOW}Do you want to update it to current main? (y/N):${NC}"
        read -p "" confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            git branch -D crpage
            git checkout -b crpage main
            print_success "Updated crpage branch from current main"
        else
            print_status "Keeping existing crpage branch"
        fi
    else
        git checkout -b crpage main
        print_success "Created crpage branch from current main"
    fi
    
    print_header "Step 4: Resetting main to match upstream/main"
    
    # Switch to main and reset to upstream
    git checkout main
    
    # Check if upstream/main exists
    if ! git branch -r | grep -q "upstream/main"; then
        print_error "upstream/main branch not found. Available upstream branches:"
        git branch -r | grep upstream | sed 's/^/  /'
        exit 1
    fi
    
    print_warning "About to reset main to upstream/main. This will remove any custom commits from main."
    echo -e "${YELLOW}Your custom commits are safely stored in the 'crpage' branch.${NC}"
    echo -e "${YELLOW}Continue? (y/N):${NC}"
    read -p "" confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_error "Aborted by user."
        exit 1
    fi
    
    print_status "Resetting main to upstream/main..."
    git reset --hard upstream/main
    print_success "Main branch reset to upstream/main"
    
    print_header "Step 5: Pushing branches to origin"
    
    # Push crpage branch
    print_status "Pushing crpage branch to origin..."
    if git push origin crpage; then
        print_success "crpage branch pushed to origin"
    else
        print_warning "Failed to push crpage branch (may already exist with different commits)"
        echo -e "${YELLOW}Force push crpage? (y/N):${NC}"
        read -p "" confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            git push --force origin crpage
            print_success "crpage branch force-pushed to origin"
        fi
    fi
    
    # Push main branch with force
    print_status "Force-pushing main branch to origin..."
    if git push --force origin main; then
        print_success "Main branch force-pushed to origin"
    else
        print_error "Failed to force-push main branch"
        exit 1
    fi
    
    print_header "Operation Completed Successfully!"
    
    print_success "Branch separation completed successfully!"
    echo
    echo -e "${BOLD}Summary of changes:${NC}"
    echo -e "  • ${GREEN}crpage${NC} branch: Contains your custom commits"
    echo -e "  • ${GREEN}main${NC} branch: Reset to match upstream/main"
    echo -e "  • ${GREEN}backup${NC} branch: Created as safety backup"
    echo
    echo -e "${BOLD}Next steps:${NC}"
    echo -e "  1. Review the changes: ${YELLOW}git log --oneline --graph main crpage${NC}"
    echo -e "  2. Continue development on the ${YELLOW}crpage${NC} branch"
    echo -e "  3. Periodically sync main with upstream: ${YELLOW}git checkout main && git pull upstream main && git push origin main${NC}"
    echo -e "  4. Merge upstream changes into crpage when needed: ${YELLOW}git checkout crpage && git merge main${NC}"
    echo
    echo -e "${BOLD}Available branches:${NC}"
    git branch -v
    echo
    echo -e "${BOLD}Remote tracking:${NC}"
    git remote -v
    
    print_header "Important Notes"
    echo -e "${YELLOW}• This script is idempotent - you can run it again safely${NC}"
    echo -e "${YELLOW}• Your custom work is preserved in the 'crpage' branch${NC}"
    echo -e "${YELLOW}• Main branch now tracks upstream changes${NC}"
    echo -e "${YELLOW}• Use 'crpage' branch for your continued development${NC}"
    echo -e "${YELLOW}• Backup branch created in case you need to revert${NC}"
}

# Run main function with all arguments
main "$@"