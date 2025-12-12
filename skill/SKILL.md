---
name: dagster-module-builder
description: Create production-ready Dagster modules with templates, workspace integration, and deployment configs. Use when user wants to create a new Dagster module, set up Dagster infrastructure, add a new data pipeline, or asks about Dagster module structure and patterns.
---

# Dagster Module Builder

Generate production-ready Dagster modules with workspace integration and multi-strategy deployment support using proven templates.

## When Claude Uses This Skill

Claude will automatically use this Skill when you:
- Want to create a new Dagster module
- Mention "create dagster module", "new dagster project", or "dagster setup"
- Need to add a new data pipeline to the Dagster workspace
- Ask about Dagster module structure or best practices
- Want to standardize Dagster module patterns

## What This Skill Provides

Creates complete Dagster modules with:
- ✅ Base module structure with custom IO manager (prevents file not found errors)
- ✅ PostgreSQL or MySQL database configuration
- ✅ Workspace integration configs (self-describing)
- ✅ Deployment configurations for multiple strategies
- ✅ All best practices baked in from proven production patterns

**Key Benefits:**
- Prevents 3-day debugging cycles (storage issues, config problems, env var mistakes)
- Separates local workspace from client deployments
- Auto-detects next available database port
- Consistent, tested structure across all modules

## Creating a Module

To create a new Dagster module, use the Python module builder tool:

```bash
cd ~/workspace/skills/dagster-module-builder
python3 lib/module_builder.py <module-name> [options]
```

### Command Options

```
--db postgresql|mysql|none
    Database type (default: postgresql)

--desc "description"
    Module description for documentation

--workspace
    Create workspace integration files (recommended)

--deploy
    Create deployment configuration

--deploy-name <name>
    Deployment name like "yoda" or "production" (default: production)

--client <name>
    Client name for deployment documentation
```

### Interactive Flow with User

When a user requests a new module, Claude should:

1. **Ask about database type:**
   - "Does this module need a database?"
   - Options: PostgreSQL (recommended), MySQL, or None
   - Default to PostgreSQL if unclear

2. **Ask for description:**
   - "Brief description of what this module does?"
   - Use for README and documentation
   - Can be brief, will be used as `__MODULE_DESCRIPTION__`

3. **Ask about workspace integration:**
   - "Create workspace integration files?"
   - Recommended: Yes (makes integration easier)
   - Creates `workspace/local/` configs

4. **Ask about deployment:**
   - "Will this be deployed to a remote server?"
   - If yes, ask for deployment name (e.g., "yoda", "production")
   - Creates `deploy/<name>/` configs

### Example Commands

**Basic module with PostgreSQL:**
```bash
python3 lib/module_builder.py my-new-module
```

**Module with workspace integration:**
```bash
python3 lib/module_builder.py my-module --workspace --desc "My module description"
```

**Full featured module:**
```bash
python3 lib/module_builder.py my-module \
    --workspace \
    --deploy \
    --deploy-name yoda \
    --db postgresql \
    --desc "My module description" \
    --client "Beast Business"
```

**Module without database:**
```bash
python3 lib/module_builder.py simple-module --db none --workspace
```

## After Module Creation

The tool creates a module at: `~/workspace/projects/<module-name>/`

### If workspace integration was created (--workspace flag)

Provide these next steps to the user:

1. **Add to workspace.yaml:**
   ```bash
   # The module created workspace/local/workspace.yaml
   # Append its contents to the main workspace file:
   cat ~/workspace/projects/<module-name>/workspace/local/workspace.yaml >> ~/workspace/services/dagster/workspace.yaml
   ```

2. **Add environment variables:**
   ```bash
   # Append the module's .env to the main .env:
   cat ~/workspace/projects/<module-name>/workspace/local/.env >> ~/workspace/services/dagster/.env
   ```

3. **Rebuild and restart Dagster:**
   ```bash
   cd ~/workspace/services/dagster
   docker compose up -d --build
   ```

4. **Verify module loaded:**
   - Open http://localhost:3000
   - Look for the new module in the Dagster UI
   - Check for any loading errors in logs

### If workspace integration was NOT created

User can integrate manually later, or run the tool again with --workspace flag.

## Quick Reference

**Create basic module:**
```bash
python3 lib/module_builder.py my-module
```

**Create with workspace integration:**
```bash
python3 lib/module_builder.py my-module --workspace
```

**Full featured:**
```bash
python3 lib/module_builder.py my-module --workspace --deploy --deploy-name yoda
```

**Module location after creation:**
```
~/workspace/projects/<module-name>/
```
