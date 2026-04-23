#!/bin/bash
# Git Branch Management Script for Car Management Project
# Usage: ./git-workflow.sh [command] [branch-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# List of all feature branches
BRANCHES=(
    "feature/0-foundation-auth"
    "feature/1-car-management"
    "feature/2-customer-management"
    "feature/3-contract-management"
    "feature/4-inventory-management"
    "feature/5-reporting-system"
    "feature/6-warranty-management"
    "feature/7-promotion-management"
    "feature/8-accessory-management"
    "feature/9-supplier-management"
    "feature/10-installment-management"
    "feature/11-after-sales-services"
    "feature/12-marketing-management"
    "feature/13-complaint-management"
    "feature/14-security-system"
)

show_help() {
    echo -e "${BLUE}Git Workflow Management for Car Management Project${NC}"
    echo ""
    echo "Usage: ./git-workflow.sh [command]"
    echo ""
    echo "Commands:"
    echo "  list              List all feature branches"
    echo "  create-all        Create all feature branches (if not exist)"
    echo "  switch [branch]   Switch to a feature branch"
    echo "  merge [branch]    Merge a feature branch to main"
    echo "  delete [branch]   Delete a feature branch"
    echo "  status            Show status of all branches"
    echo "  clean             Delete all feature branches"
    echo "  help              Show this help message"
    echo ""
    echo "Feature Branch Naming Convention:"
    echo "  feature/[number]-[module-name]"
    echo ""
    echo "Example:"
    echo "  ./git-workflow.sh switch feature/1-car-management"
}

list_branches() {
    echo -e "${BLUE}All Feature Branches:${NC}"
    echo "====================="
    git branch | grep "feature/" || echo "No feature branches found"
}

create_all_branches() {
    echo -e "${YELLOW}Creating all feature branches...${NC}"

    for branch in "${BRANCHES[@]}"; do
        if git branch --list "$branch" >/dev/null 2>&1; then
            echo -e "  ${YELLOW}SKIP${NC} $branch (already exists)"
        else
            git branch "$branch"
            echo -e "  ${GREEN}CREATE${NC} $branch"
        fi
    done

    echo -e "${GREEN}Done!${NC}"
}

switch_branch() {
    local branch=$1
    if [ -z "$branch" ]; then
        echo -e "${RED}Error: Please specify a branch name${NC}"
        echo "Usage: ./git-workflow.sh switch feature/1-car-management"
        exit 1
    fi

    if git branch --list "$branch" >/dev/null 2>&1; then
        git checkout "$branch"
        echo -e "${GREEN}Switched to $branch${NC}"
    else
        echo -e "${RED}Error: Branch $branch does not exist${NC}"
        echo "Use './git-workflow.sh list' to see available branches"
        exit 1
    fi
}

merge_branch() {
    local branch=$1
    if [ -z "$branch" ]; then
        echo -e "${RED}Error: Please specify a branch name${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Merging $branch into main...${NC}"
    git checkout main
    git merge --no-ff "$branch" -m "Merge $branch into main"
    echo -e "${GREEN}Merged successfully!${NC}"
}

delete_branch() {
    local branch=$1
    if [ -z "$branch" ]; then
        echo -e "${RED}Error: Please specify a branch name${NC}"
        exit 1
    fi

    read -p "Are you sure you want to delete $branch? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -d "$branch"
        echo -e "${GREEN}Deleted $branch${NC}"
    else
        echo "Cancelled"
    fi
}

show_status() {
    echo -e "${BLUE}Branch Status:${NC}"
    echo "==============="

    for branch in "${BRANCHES[@]}"; do
        if git branch --list "$branch" >/dev/null 2>&1; then
            # Check if branch has unmerged commits
            ahead=$(git rev-list --count main..$branch 2>/dev/null || echo "0")
            behind=$(git rev-list --count $branch..main 2>/dev/null || echo "0")

            if [ "$ahead" -gt 0 ]; then
                echo -e "  ${GREEN}✓${NC} $branch (ahead: $ahead)"
            else
                echo -e "  ${YELLOW}○${NC} $branch (no commits)"
            fi
        else
            echo -e "  ${RED}✗${NC} $branch (not created)"
        fi
    done
}

clean_branches() {
    echo -e "${RED}WARNING: This will delete all feature branches!${NC}"
    read -p "Are you sure? (type 'yes' to confirm) " confirm

    if [ "$confirm" = "yes" ]; then
        for branch in "${BRANCHES[@]}"; do
            if git branch --list "$branch" >/dev/null 2>&1; then
                git branch -D "$branch"
                echo -e "  ${RED}DELETED${NC} $branch"
            fi
        done
        echo -e "${GREEN}All feature branches deleted${NC}"
    else
        echo "Cancelled"
    fi
}

# Main command handler
case ${1:-help} in
    list)
        list_branches
        ;;
    create-all)
        create_all_branches
        ;;
    switch)
        switch_branch "$2"
        ;;
    merge)
        merge_branch "$2"
        ;;
    delete)
        delete_branch "$2"
        ;;
    status)
        show_status
        ;;
    clean)
        clean_branches
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
