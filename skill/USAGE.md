# Dagster Module Builder Skill - Usage Guide

**Status**: ✅ Installed and ready
**Location**: `~/.claude/skills/dagster-module-builder`
**Version**: 1.0.0

---

## Quick Start

The skill is now available! Claude will automatically use it when you mention creating Dagster modules.

### Try it now:

Just ask Claude in natural language:
```
"Create a new Dagster module for processing customer orders"
```

or

```
"I need to set up a new Dagster pipeline for email analytics"
```

Claude will automatically detect that you want to create a Dagster module and will:
1. Ask you questions about database, description, etc.
2. Run the module builder tool
3. Guide you through integration steps

---

## How It Works

### Automatic Skill Activation

Claude Code reads the skill's YAML frontmatter:
```yaml
name: dagster-module-builder
description: Create production-ready Dagster modules with templates...
```

When you mention keywords like:
- "create dagster module"
- "new dagster project"
- "dagster pipeline"
- "dagster setup"

Claude automatically uses this skill.

### What Claude Does

1. **Asks questions** about your module:
   - Database type (PostgreSQL/MySQL/None)
   - Description
   - Workspace integration?
   - Deployment config?

2. **Runs the module builder**:
   ```bash
   cd ~/workspace/skills/dagster-module-builder
   python3 lib/module_builder.py <module-name> [options]
   ```

3. **Provides integration steps**:
   - How to add to workspace.yaml
   - How to add environment variables
   - How to restart Dagster

---

## Manual Usage

If you want to run the tool directly:

```bash
# Navigate to skill directory
cd ~/workspace/skills/dagster-module-builder

# Basic module
python3 lib/module_builder.py my-module

# With options
python3 lib/module_builder.py my-module --workspace --desc "My module description"

# Full featured
python3 lib/module_builder.py my-module \
    --workspace \
    --deploy \
    --deploy-name yoda \
    --db postgresql \
    --desc "Customer order processing module" \
    --client "Beast Business"
```

---

## Command Options

| Option | Values | Description |
|--------|--------|-------------|
| `--db` | `postgresql`, `mysql`, `none` | Database type (default: postgresql) |
| `--desc` | "text" | Module description |
| `--workspace` | flag | Create workspace integration files |
| `--deploy` | flag | Create deployment configuration |
| `--deploy-name` | text | Deployment name (default: production) |
| `--client` | text | Client name for deployment |

---

## Example Conversations

### Example 1: Basic Module

**You**: "Create a new Dagster module called customer-sync"

**Claude**: "I'll help you create a customer-sync Dagster module. Let me ask a few questions:

1. Does this module need a database?
   - PostgreSQL (recommended)
   - MySQL
   - None

2. What does this module do? (brief description)

3. Should I create workspace integration files? (recommended: yes)

4. Will this be deployed to a remote server?"

### Example 2: Quick Module

**You**: "Create beast-orders module with PostgreSQL and workspace integration"

**Claude**: "I'll create the beast-orders module with PostgreSQL database and workspace integration files. Running the module builder now..."

```bash
python3 lib/module_builder.py beast-orders --db postgresql --workspace
```

"Module created successfully! Here are the next steps..."

---

## What Gets Created

After running the skill, you'll have:

```
~/workspace/projects/<module-name>/
├── src/
│   └── <module_name>_dagster/
│       ├── __init__.py          # Dagster definitions
│       ├── assets.py            # Asset definitions (edit this)
│       └── resources.py         # Custom IO manager
├── workspace/
│   └── local/
│       ├── workspace.yaml       # Workspace entry
│       ├── .env                 # Environment variables
│       ├── docker-compose.yml   # Database service
│       └── dockerfile.snippet   # Python dependencies
├── deploy/                      # (if --deploy used)
│   └── <deployment-name>/
│       ├── deployment.yaml
│       ├── DEPLOYMENT.md
│       └── .env.deploy.example
├── README.md                    # Documentation
├── .gitignore                   # Comprehensive gitignore
├── .env.example                 # Environment template
├── pyproject.toml              # Project metadata
└── requirements.txt            # Python dependencies
```

---

## Integration Steps

After module creation, Claude will guide you through:

1. **Append workspace entry:**
   ```bash
   cat ~/workspace/projects/<module>/workspace/local/workspace.yaml >> \
       ~/workspace/services/dagster/workspace.yaml
   ```

2. **Append environment variables:**
   ```bash
   cat ~/workspace/projects/<module>/workspace/local/.env >> \
       ~/workspace/services/dagster/.env
   ```

3. **Restart Dagster:**
   ```bash
   cd ~/workspace/services/dagster
   docker compose up -d --build
   ```

4. **Verify:**
   - Open http://localhost:3000
   - Look for your module in the UI

---

## Skill Structure

```
dagster-module-builder/
├── SKILL.md                # Skill definition (YAML + docs)
├── USAGE.md               # This file
├── README.md              # Original documentation
├── STATUS.md              # Implementation status
└── lib/
    └── module_builder.py  # Python module builder
```

---

## Troubleshooting

### Skill not activating?

Try being more explicit:
```
"Use the dagster-module-builder skill to create a new module called test-module"
```

### Module builder errors?

Check:
1. Templates exist: `ls ~/workspace/patterns/dagster/`
2. Python 3 available: `python3 --version`
3. Permissions: `ls -la ~/workspace/skills/dagster-module-builder/lib/`

### Need to update the skill?

Edit the SKILL.md file:
```bash
nano ~/workspace/skills/dagster-module-builder/SKILL.md
```

Or update module_builder.py:
```bash
nano ~/workspace/skills/dagster-module-builder/lib/module_builder.py
```

Changes take effect immediately in new Claude conversations.

---

## Related Documentation

- **Templates**: `~/workspace/patterns/dagster/`
- **Full docs**: `~/workspace/docs/dagster-workspace/`
- **Module pattern guide**: `~/workspace/docs/dagster-workspace/MODULE-PATTERN.md`

---

**Created**: 2025-12-12
**Last Updated**: 2025-12-12
