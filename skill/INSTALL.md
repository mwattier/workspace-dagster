# Installing the Dagster Module Builder Skill

This guide explains how to install the dagster-module-builder skill for Claude Code CLI.

---

## Prerequisites

1. **Claude Code CLI installed** and configured
2. **Access to this repository** (pull from git)
3. **Templates available** at `~/workspace/patterns/dagster/` (separate repository/setup required)

---

## Installation Steps

### Step 1: Clone or Pull the Repository

If you haven't already, clone the dagster-workspace repo:

```bash
cd ~/workspace/docs
git clone <repository-url> dagster-workspace
```

Or if you already have it, pull the latest changes:

```bash
cd ~/workspace/docs/dagster-workspace
git pull
```

### Step 2: Create Skills Directory

Create your personal Claude Code skills directory if it doesn't exist:

```bash
mkdir -p ~/.claude/skills
```

### Step 3: Symlink the Skill

Create a symlink from your Claude skills directory to the skill in the repo:

```bash
ln -sf ~/workspace/docs/dagster-workspace/skill ~/.claude/skills/dagster-module-builder
```

### Step 4: Verify Installation

Check that the symlink was created:

```bash
ls -la ~/.claude/skills/ | grep dagster
```

You should see:
```
dagster-module-builder -> /home/your-username/workspace/docs/dagster-workspace/skill
```

### Step 5: Verify Skill File

Check that the SKILL.md file is readable:

```bash
cat ~/.claude/skills/dagster-module-builder/SKILL.md | head -10
```

You should see YAML frontmatter at the top:
```yaml
---
name: dagster-module-builder
description: Create production-ready Dagster modules...
---
```

### Step 6: Test the Skill

Start a new Claude Code session and try:

```
Create a test Dagster module
```

Claude should automatically activate the skill and ask you questions about database type, description, etc.

---

## Alternative: Copy Instead of Symlink

If you prefer to copy the skill instead of symlinking (useful if you want to modify it):

```bash
# Copy the skill directory
cp -r ~/workspace/docs/dagster-workspace/skill ~/.claude/skills/dagster-module-builder

# Note: Updates from git won't automatically apply
# You'll need to manually copy again when the skill is updated
```

---

## Troubleshooting

### Skill Not Activating

1. **Check the symlink exists:**
   ```bash
   ls -la ~/.claude/skills/dagster-module-builder
   ```

2. **Verify SKILL.md has YAML frontmatter:**
   ```bash
   head -5 ~/.claude/skills/dagster-module-builder/SKILL.md
   ```
   Should start with `---` on line 1

3. **Try being more explicit:**
   ```
   Use the dagster-module-builder skill to create a new module
   ```

4. **Start a fresh Claude session:**
   Skills are loaded when Claude starts, so restart if you just installed it

### Module Builder Fails

1. **Check templates exist:**
   ```bash
   ls ~/workspace/patterns/dagster/base/
   ```

2. **Verify Python 3 is available:**
   ```bash
   python3 --version
   ```

3. **Check permissions:**
   ```bash
   ls -la ~/.claude/skills/dagster-module-builder/lib/module_builder.py
   ```

### Symlink Broken

If the symlink points to the wrong location:

```bash
# Remove old symlink
rm ~/.claude/skills/dagster-module-builder

# Create new symlink with correct path
ln -sf ~/workspace/docs/dagster-workspace/skill ~/.claude/skills/dagster-module-builder
```

---

## Updating the Skill

When the skill is updated in the repository:

### If Using Symlink (Recommended)

```bash
cd ~/workspace/docs/dagster-workspace
git pull
# Changes are immediately available (restart Claude session)
```

### If Using Copy

```bash
cd ~/workspace/docs/dagster-workspace
git pull

# Re-copy the skill
rm -rf ~/.claude/skills/dagster-module-builder
cp -r ~/workspace/docs/dagster-workspace/skill ~/.claude/skills/dagster-module-builder
```

---

## Uninstalling

To remove the skill:

```bash
# Remove symlink or directory
rm -rf ~/.claude/skills/dagster-module-builder

# Skill will no longer be available in new Claude sessions
```

---

## Directory Structure

After installation, your structure should look like:

```
~/.claude/skills/
└── dagster-module-builder -> ~/workspace/docs/dagster-workspace/skill/

~/workspace/docs/dagster-workspace/skill/
├── SKILL.md                   # Skill definition (YAML + docs)
├── USAGE.md                   # How to use the skill
├── INSTALL.md                 # This file
├── STATUS.md                  # Implementation status
├── README.md                  # Original documentation
└── lib/
    └── module_builder.py      # Python module builder

~/workspace/patterns/dagster/  # Templates (required)
├── base/
├── workspace-integration/
├── deploy-strategies/
└── shared-resources/
```

---

## Team Setup

For consistent team setup, everyone should:

1. Clone the dagster-workspace repo
2. Symlink the skill (so updates propagate automatically)
3. Ensure templates exist at `~/workspace/patterns/dagster/`
4. Use the same directory structure

**Recommended team workflow:**

```bash
# One-time setup
cd ~/workspace/docs
git clone <repo-url> dagster-workspace
mkdir -p ~/.claude/skills
ln -sf ~/workspace/docs/dagster-workspace/skill ~/.claude/skills/dagster-module-builder

# Regular updates
cd ~/workspace/docs/dagster-workspace
git pull
# Restart Claude session to pick up changes
```

---

## Related Documentation

- **Usage Guide**: [USAGE.md](USAGE.md)
- **Implementation Status**: [STATUS.md](STATUS.md)
- **Main Documentation**: [README.md](../README.md)
- **Templates**: `~/workspace/patterns/dagster/`

---

**Questions or Issues?**

If you encounter problems:
1. Check this troubleshooting section
2. Verify your directory structure matches the expected layout
3. Consult [USAGE.md](USAGE.md) for usage examples
4. Check [STATUS.md](STATUS.md) for known limitations

---

**Last Updated**: 2025-12-12
