#!/usr/bin/env bash
#
# Dagster Module Builder - Automated Module Creation
#
# Usage: ./create-module.sh <module-name>
#
# This script automates the entire module creation process:
# - Asks interactive questions
# - Generates all files from templates
# - Integrates with workspace (optional)
# - Creates deployment configs (optional)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
WORKSPACE_DIR="$HOME/workspace"
TEMPLATES_DIR="$WORKSPACE_DIR/patterns/dagster"
PROJECTS_DIR="$WORKSPACE_DIR/projects"
SERVICES_DIR="$WORKSPACE_DIR/services/dagster"

# Check if module name provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Module name required${NC}"
    echo "Usage: $0 <module-name>"
    exit 1
fi

MODULE_NAME="$1"

# Convert to snake_case
MODULE_SNAKE=$(echo "$MODULE_NAME" | tr '-' '_' | tr '[:upper:]' '[:lower:]')
MODULE_UPPER=$(echo "$MODULE_SNAKE" | tr '[:lower:]' '[:upper:]')
MODULE_TITLE=$(echo "$MODULE_NAME" | sed 's/-/ /g' | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Dagster Module Builder${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}Module:${NC} $MODULE_NAME"
echo -e "${GREEN}Snake case:${NC} $MODULE_SNAKE"
echo -e "${GREEN}Upper case:${NC} $MODULE_UPPER"
echo -e "${GREEN}Title case:${NC} $MODULE_TITLE"
echo ""

# Check if module already exists
if [ -d "$PROJECTS_DIR/$MODULE_NAME" ]; then
    echo -e "${RED}Error: Module $MODULE_NAME already exists at $PROJECTS_DIR/$MODULE_NAME${NC}"
    exit 1
fi

# Helper function to substitute placeholders in a file
substitute_file() {
    local input_file="$1"
    local output_file="$2"

    # Read file and substitute all placeholders
    sed -e "s/__MODULE_NAME__/$MODULE_SNAKE/g" \
        -e "s/__MODULE_NAME_UPPER__/$MODULE_UPPER/g" \
        -e "s/__MODULE_TITLE__/$MODULE_TITLE/g" \
        -e "s/__MODULE_DESCRIPTION__/$MODULE_DESCRIPTION/g" \
        -e "s/__DB_TYPE__/$DB_TYPE/g" \
        -e "s/__DB_PORT__/$DB_PORT/g" \
        -e "s/__DEPLOY_NAME__/$DEPLOY_NAME/g" \
        -e "s/__CLIENT_NAME__/$CLIENT_NAME/g" \
        -e "s/__GIT_REPOSITORY__/$GIT_REPO/g" \
        "$input_file" > "$output_file"
}

# Function to auto-detect next available PostgreSQL port
get_next_port() {
    local env_file="$SERVICES_DIR/.env"

    if [ ! -f "$env_file" ]; then
        echo "5440"
        return
    fi

    # Extract all port numbers from PostgreSQL configs (5400-5500 range)
    local max_port=$(grep -oE 'PORT=[0-9]+' "$env_file" | \
                     grep -oE '[0-9]+' | \
                     awk '$1 >= 5400 && $1 <= 5500' | \
                     sort -n | \
                     tail -1)

    if [ -z "$max_port" ]; then
        echo "5440"
    else
        echo $((max_port + 1))
    fi
}

echo -e "${YELLOW}This script will guide you through creating a new Dagster module.${NC}"
echo ""

# Ask questions interactively
# Note: In the actual skill implementation, these would use AskUserQuestion
# For now, using bash read for testing

# Question 1: Database type
echo -e "${BLUE}Question 1: Database Type${NC}"
echo "1) PostgreSQL"
echo "2) MySQL"
echo "3) None"
read -p "Choice [1]: " db_choice
db_choice=${db_choice:-1}

case $db_choice in
    1) DB_TYPE="postgresql" ;;
    2) DB_TYPE="mysql" ;;
    3) DB_TYPE="none" ;;
    *) DB_TYPE="postgresql" ;;
esac

# Auto-detect port
if [ "$DB_TYPE" = "postgresql" ]; then
    DB_PORT=$(get_next_port)
elif [ "$DB_TYPE" = "mysql" ]; then
    DB_PORT="3307"  # Default MySQL port
else
    DB_PORT=""
fi

echo -e "${GREEN}✓ Database: $DB_TYPE${NC}"
if [ -n "$DB_PORT" ]; then
    echo -e "${GREEN}✓ Port: $DB_PORT (auto-detected)${NC}"
fi
echo ""

# Question 2: Module description
echo -e "${BLUE}Question 2: Module Description${NC}"
read -p "Description [$MODULE_TITLE Dagster module]: " MODULE_DESCRIPTION
MODULE_DESCRIPTION=${MODULE_DESCRIPTION:-"$MODULE_TITLE Dagster module"}
echo ""

# Question 3: Workspace integration
echo -e "${BLUE}Question 3: Integrate with workspace?${NC}"
echo "1) Yes (recommended)"
echo "2) No"
read -p "Choice [1]: " workspace_choice
workspace_choice=${workspace_choice:-1}

INTEGRATE_WORKSPACE=$([[ "$workspace_choice" = "1" ]] && echo "yes" || echo "no")
echo -e "${GREEN}✓ Workspace integration: $INTEGRATE_WORKSPACE${NC}"
echo ""

# Question 4: Deployment configuration
echo -e "${BLUE}Question 4: Configure deployment?${NC}"
echo "1) Yes"
echo "2) No"
read -p "Choice [2]: " deploy_choice
deploy_choice=${deploy_choice:-2}

CREATE_DEPLOYMENT=$([[ "$deploy_choice" = "1" ]] && echo "yes" || echo "no")

if [ "$CREATE_DEPLOYMENT" = "yes" ]; then
    echo -e "${BLUE}Deployment Configuration:${NC}"
    read -p "Deployment name [production]: " DEPLOY_NAME
    DEPLOY_NAME=${DEPLOY_NAME:-production}

    read -p "Client name [Test Client]: " CLIENT_NAME
    CLIENT_NAME=${CLIENT_NAME:-Test Client}

    read -p "Git repository [git@github.com:myorg/$MODULE_NAME.git]: " GIT_REPO
    GIT_REPO=${GIT_REPO:-"git@github.com:myorg/$MODULE_NAME.git"}
else
    DEPLOY_NAME="production"
    CLIENT_NAME="Test Client"
    GIT_REPO="git@github.com:myorg/$MODULE_NAME.git"
fi

echo -e "${GREEN}✓ Deployment config: $CREATE_DEPLOYMENT${NC}"
echo ""

# Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Module:${NC} $MODULE_NAME"
echo -e "${GREEN}Database:${NC} $DB_TYPE"
if [ -n "$DB_PORT" ]; then
    echo -e "${GREEN}Port:${NC} $DB_PORT"
fi
echo -e "${GREEN}Description:${NC} $MODULE_DESCRIPTION"
echo -e "${GREEN}Workspace:${NC} $INTEGRATE_WORKSPACE"
echo -e "${GREEN}Deployment:${NC} $CREATE_DEPLOYMENT"
echo ""
read -p "Proceed with creation? [Y/n]: " proceed
proceed=${proceed:-Y}

if [[ ! "$proceed" =~ ^[Yy] ]]; then
    echo -e "${YELLOW}Aborted${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Creating module...${NC}"

# Create base directory structure
MODULE_DIR="$PROJECTS_DIR/$MODULE_NAME"
mkdir -p "$MODULE_DIR/src/${MODULE_SNAKE}_dagster"
mkdir -p "$MODULE_DIR/workspace/local"
mkdir -p "$MODULE_DIR/deploy/$DEPLOY_NAME"

echo -e "${GREEN}✓ Created directory structure${NC}"

# TODO: Implement file generation from templates
# This is where we would:
# 1. Copy and process each template file
# 2. Generate all module files
# 3. Generate workspace integration files
# 4. Generate deployment files

echo -e "${YELLOW}Note: Full template processing not yet implemented in bash script${NC}"
echo -e "${YELLOW}Use Python implementation or manual process for now${NC}"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Module creation complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Review generated files in $MODULE_DIR"
if [ "$INTEGRATE_WORKSPACE" = "yes" ]; then
    echo "2. Rebuild workspace: cd $SERVICES_DIR && docker compose build"
    echo "3. Restart services: docker compose up -d"
fi
echo ""
