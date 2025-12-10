# Dagster Module Builder Skill

**Purpose:** Generate production-ready Dagster modules with workspace integration and multi-strategy deployment support.

**Version:** 1.0.0
**Status:** Active
**Templates:** `~/workspace/patterns/dagster/`

---

## Overview

This skill creates self-contained Dagster modules with:
- **Base module** - Source code with custom IO manager
- **Workspace integration** - Self-describing configs for local workspace
- **Deployment configs** - Client-specific deployment strategies (git, rsync, docker, ci-cd)
- **Database addons** - PostgreSQL or MySQL configuration
- **Scheduled jobs** - Optional job and schedule definitions

**Key Benefits:**
- ✅ Prevents 3-day debugging cycles (storage, config, env vars)
- ✅ Separates local workspace from client deployments
- ✅ Supports multiple deployment strategies
- ✅ All best practices baked in from proven patterns

---

## Tool Access

This skill has access to:
- **Read** - Read templates and existing modules
- **Write** - Create new files
- **Edit** - Modify existing files
- **Bash** - Execute commands (mkdir, cp, mv, chmod)
- **Glob** - Find files by pattern
- **Grep** - Search file contents

---

## Modes

### Mode 1: `new` - Create New Module
```
@dagster-module-builder new <module-name>
```

**Interactive Questions:**
1. Module name (from command or prompt)
2. Database type (postgresql / mysql / none)
3. System requirements (pre-flight checklist)
4. Governance level (quick / standard / enterprise)
5. Integrate with workspace? (yes / no / later)
6. Configure deployment? (yes / no / later)

**Generates:**
- Complete module structure
- Source code with custom IO manager
- Workspace integration configs (if requested)
- Deployment configs (if requested)
- Documentation

### Mode 2: `workspace` - Workspace Integration
```
@dagster-module-builder workspace add <module-name>
@dagster-module-builder workspace remove <module-name>
@dagster-module-builder workspace list
@dagster-module-builder workspace validate
@dagster-module-builder workspace sync
```

**Commands:**
- **add** - Integrate module with workspace
- **remove** - Remove module from workspace
- **list** - List integrated modules
- **validate** - Check workspace consistency
- **sync** - Sync all projects/*/workspace/local/ to workspace

### Mode 3: `configure-deployment` - Add Deployment Config
```
@dagster-module-builder configure-deployment <module-name>
```

**Questions:**
1. Deployment name (e.g., "yoda")
2. Client name (e.g., "Beast Business")
3. Remote connection details
4. Deployment strategy (git / rsync / docker / ci-cd)
5. Strategy-specific questions

**Generates:**
- `deploy/<deployment-name>/deployment.yaml`
- `deploy/<deployment-name>/.env.deploy`
- `deploy/<deployment-name>/DEPLOYMENT.md`

### Mode 4: `audit` - Check Existing Module
```
@dagster-module-builder audit <module-name>
```

**Checks:**
- Has custom IO manager
- IO manager uses `/tmp/dagster_storage/`
- Has workspace integration configs
- Has deployment configs
- All env vars documented

**Output:**
- Checklist of what exists
- Recommendations for missing pieces
- Option to run `upgrade` command

### Mode 5: `upgrade` - Add Missing Pieces
```
@dagster-module-builder upgrade <module-name>
```

**Adds:**
- Create resources.py if missing
- Update __init__.py to register IO manager
- Generate workspace/local/ configs
- Generate deploy/template/ configs
- Create deployment checklist

---

## Implementation: Mode 1 - Create New Module

### Process Flow

```
1. Gather Requirements
   ├─ Module name
   ├─ Database type
   ├─ System requirements (pre-flight)
   ├─ Governance level
   ├─ Workspace integration? (yes/no/later)
   └─ Deployment config? (yes/no/later)

2. Generate Base Module
   ├─ Copy base/ templates
   ├─ Substitute placeholders
   ├─ Add database addon (if selected)
   ├─ Add scheduled jobs (if governance ≥ Standard)
   └─ Generate documentation

3. Generate Workspace Integration (if requested)
   ├─ Copy workspace-integration/ templates
   ├─ Auto-detect next available port
   ├─ Substitute placeholders
   └─ Add system dependencies based on pre-flight

4. Generate Deployment Config (if requested)
   ├─ Ask deployment questions
   ├─ Copy deploy-strategies/{strategy}/ templates
   ├─ Substitute placeholders
   └─ Generate client-specific docs

5. Report Created Files
   └─ List all generated files and next steps
```

### Variables & Substitution

**Core Variables:**
- `__MODULE_NAME__` - Snake case (e.g., `my_data_pipeline`)
- `__MODULE_NAME_UPPER__` - Upper snake case (e.g., `MY_DATA_PIPELINE`)
- `__MODULE_TITLE__` - Title case (e.g., `My Data Pipeline`)
- `__MODULE_DESCRIPTION__` - Short description

**Database Variables:**
- `__DB_TYPE__` - postgresql / mysql / none
- `__DB_PORT__` - Auto-assigned (scan workspace .env for next available)
- `__DB_NAME__` - Defaults to module name
- `__DB_USER__` - Defaults to `{module}_user`
- `__DB_PASSWORD__` - Generate secure random or prompt

**Deployment Variables:**
- `__DEPLOY_NAME__` - Deployment name (e.g., "yoda")
- `__CLIENT_NAME__` - Client name
- `__REMOTE_HOST__` - Remote hostname
- `__REMOTE_USER__` - SSH user
- `__REMOTE_BASE_PATH__` - Base path on remote
- `__GIT_REPOSITORY__` - Git repo URL (if git strategy)
- `__NETWORK_NAME__` - Docker network (default: workspace-net)

### Template Processing

```python
# Pseudocode for template processing

def substitute_placeholders(content: str, variables: dict) -> str:
    """Replace all placeholders in content."""
    for key, value in variables.items():
        content = content.replace(key, value)
    return content

def process_template_file(template_path: str, output_path: str, variables: dict):
    """Process a single template file."""
    # Read template
    content = read(template_path)

    # Substitute placeholders
    processed = substitute_placeholders(content, variables)

    # Write output
    write(output_path, processed)

def copy_template_dir(template_dir: str, output_dir: str, variables: dict):
    """Recursively copy and process template directory."""
    for file in glob(f"{template_dir}/**/*"):
        if file.endswith('.template'):
            # Process template file
            output_file = file.replace('.template', '').replace(template_dir, output_dir)
            output_file = substitute_placeholders(output_file, variables)
            process_template_file(file, output_file, variables)
        else:
            # Copy as-is (e.g., resources.py)
            output_file = file.replace(template_dir, output_dir)
            output_file = substitute_placeholders(output_file, variables)
            copy(file, output_file)
```

### Auto-Detect Next Available Port

```python
# Pseudocode for port detection

def get_next_available_port(base_port: int = 5440) -> int:
    """Scan workspace .env for used ports and return next available."""
    workspace_env = read("~/workspace/services/dagster/.env")

    # Extract all PORT= lines
    used_ports = grep(workspace_env, pattern=r"PORT=(\d+)")

    # Find highest port
    max_port = max(used_ports) if used_ports else base_port - 1

    # Return next available
    return max_port + 1
```

---

## Implementation: Mode 2 - Workspace Commands

### `workspace add` Logic

```
1. Validate
   ├─ Module exists at ~/workspace/projects/<module>?
   ├─ Has workspace/local/ directory?
   └─ Not already integrated? (check .registry)

2. Backup Workspace Files
   ├─ Create ~/workspace/services/dagster/modules/backups/
   └─ Copy workspace.yaml, .env, docker-compose.yml, Dockerfile

3. Read Module Integration Configs
   ├─ Read projects/<module>/workspace/local/workspace.yaml
   ├─ Read projects/<module>/workspace/local/.env
   ├─ Read projects/<module>/workspace/local/docker-compose.yml
   └─ Read projects/<module>/workspace/local/dockerfile.snippet

4. Merge into Workspace
   ├─ Append to workspace.yaml with markers:
   │  # BEGIN: <module>
   │  ... module entry ...
   │  # END: <module>
   ├─ Append to .env
   ├─ Merge docker-compose.yml (services section)
   ├─ Append to Dockerfile
   └─ Update PYTHONPATH

5. Add Database Dependencies
   ├─ Find database service name (e.g., my_module_postgres)
   ├─ Add to dagster_webserver depends_on
   └─ Add to dagster_daemon depends_on

6. Update Registry
   └─ Add entry to .registry with metadata

7. Report Changes
   └─ List all modified files and what was added
```

### `workspace remove` Logic

```
1. Validate
   ├─ Module integrated? (check .registry)
   └─ Confirm removal (ask user)

2. Backup Workspace Files
   └─ Same as add

3. Remove Markers
   ├─ Remove lines between # BEGIN: <module> and # END: <module>
   ├─ From workspace.yaml
   ├─ From .env (look for <MODULE>_ prefix)
   ├─ From docker-compose.yml (find service, remove service + dependencies)
   └─ From Dockerfile (find lines, remove)

4. Update Registry
   └─ Remove entry from .registry

5. Optional: Remove Data
   ├─ Ask: Remove database data directory? (yes/no)
   └─ If yes: rm -rf ~/workspace/data/postgres/<module>/

6. Report Changes
   └─ List all modified files and what was removed
```

### Registry File Structure

```json
{
  "version": "1.0.0",
  "integrated_modules": [
    {
      "name": "seo-stats",
      "path": "~/workspace/projects/seo-stats",
      "integrated_at": "2025-12-10T12:00:00Z",
      "database": {
        "type": "postgresql",
        "service": "seo_stats_postgres",
        "port": 5438
      },
      "marker": "seo_stats"
    }
  ]
}
```

---

## Implementation: Mode 3 - Configure Deployment

### Process Flow

```
1. Validate
   └─ Module exists at ~/workspace/projects/<module>?

2. Ask Deployment Questions
   ├─ Deployment name (e.g., "yoda")
   ├─ Client name (e.g., "Beast Business")
   ├─ Remote host
   ├─ Remote user
   ├─ Remote base path
   └─ Deployment strategy (git / rsync / docker / ci-cd)

3. Strategy-Specific Questions
   ├─ If git:
   │  ├─ Repository URL
   │  ├─ Branch
   │  └─ Monorepo? (yes/no)
   ├─ If rsync:
   │  └─ Additional exclusions?
   ├─ If docker:
   │  ├─ Registry
   │  ├─ Image name
   │  └─ Build context
   └─ If ci-cd:
      ├─ Platform (github/gitlab/jenkins)
      └─ Trigger (push/tag/manual)

4. Auto-Detect Settings
   ├─ Database type from module
   ├─ Database port from module
   └─ Network name from workspace

5. Generate Deployment Config
   ├─ Create deploy/<deployment-name>/
   ├─ Copy deploy-strategies/<strategy>/deployment.yaml.template
   ├─ Copy deploy-strategies/<strategy>/DEPLOYMENT.md.template
   ├─ Copy workspace-integration/.env.template → .env.deploy
   └─ Substitute all placeholders

6. Report Created Files
   └─ List generated files and next steps
```

---

## Implementation: Mode 4 - Audit

### Checklist

```python
def audit_module(module_name: str) -> dict:
    """Audit module and return checklist."""
    module_path = f"~/workspace/projects/{module_name}"

    checks = {
        "has_resources_py": exists(f"{module_path}/src/{module_name}_dagster/resources.py"),
        "has_custom_io_manager": grep(f"{module_path}/src/{module_name}_dagster/resources.py", "class.*IOManager"),
        "uses_tmp_storage": grep(f"{module_path}/src/{module_name}_dagster/resources.py", "/tmp/dagster_storage"),
        "has_workspace_integration": exists(f"{module_path}/workspace/local/"),
        "has_workspace_yaml": exists(f"{module_path}/workspace/local/workspace.yaml"),
        "has_workspace_compose": exists(f"{module_path}/workspace/local/docker-compose.yml"),
        "has_workspace_env": exists(f"{module_path}/workspace/local/.env"),
        "has_workspace_dockerfile": exists(f"{module_path}/workspace/local/dockerfile.snippet"),
        "has_deployment_config": exists(f"{module_path}/deploy/"),
        "has_at_least_one_deploy": len(glob(f"{module_path}/deploy/*/")) > 0,
        "all_env_vars_documented": check_env_vars_documented(module_path),
    }

    return checks

def generate_recommendations(checks: dict) -> list:
    """Generate recommendations based on checks."""
    recommendations = []

    if not checks["has_resources_py"]:
        recommendations.append("Create resources.py with custom IO manager")
    if not checks["has_custom_io_manager"]:
        recommendations.append("Add custom IO manager to resources.py")
    if not checks["uses_tmp_storage"]:
        recommendations.append("Update IO manager to use /tmp/dagster_storage/")
    if not checks["has_workspace_integration"]:
        recommendations.append("Generate workspace integration configs")
    if not checks["has_deployment_config"]:
        recommendations.append("Configure at least one deployment")

    return recommendations
```

### Output Format

```
Audit Results for: my-data-pipeline
=====================================

✅ PASS: Has resources.py
✅ PASS: Has custom IO manager
✅ PASS: Uses /tmp/dagster_storage/
✅ PASS: Has workspace integration configs
✅ PASS: Has deployment configs
⚠️  WARN: Only 1 deployment configured (consider staging)

Recommendations:
- Add deployment config for staging environment
- Consider adding scheduled jobs for Standard governance

Overall Status: GOOD (5/6 checks passed)

To fix issues, run: @dagster-module-builder upgrade my-data-pipeline
```

---

## System Requirements Pre-Flight Checklist

When creating a new module, ask about system requirements:

### Remote Systems
- **SSH/SCP** → Requires: `openssh-client`
- **SFTP** → Requires: `openssh-client`
- **FTP** → Requires: `ftp`
- **HTTP/HTTPS** → Usually built-in
- **Cloud Storage (S3/GCS)** → Requires: SDK packages

### Binary Tools
- **git** → Requires: `git`
- **curl/wget** → Usually pre-installed
- **imagemagick** → Requires: `imagemagick` (+40MB)
- **ffmpeg** → Requires: `ffmpeg` (+80MB)
- **pandoc** → Requires: `pandoc`

### File Formats
- **PDF** → Requires: `poppler-utils` (+15MB)
- **Images** → Requires: `pillow` (Python) or `imagemagick`
- **Video** → Requires: `ffmpeg` (+80MB)
- **Office docs** → Requires: `libreoffice-core` (+400MB ⚠️)

### Warnings

For large dependencies (>100MB), warn user:
```
⚠️  WARNING: libreoffice-core adds ~400MB to image size
    Consider alternatives:
    - Use Python docx/openpyxl libraries instead
    - Process documents outside container
    - Use cloud-based conversion APIs
```

---

## Error Handling

### Validation Errors

```python
# Check module doesn't already exist
if exists(f"~/workspace/projects/{module_name}"):
    raise Error(f"Module {module_name} already exists at ~/workspace/projects/{module_name}")

# Check workspace integration not already done
if module_in_registry(module_name):
    raise Error(f"Module {module_name} is already integrated. Use 'workspace remove' first.")

# Check templates exist
if not exists("~/workspace/patterns/dagster/base/"):
    raise Error("Templates not found. Run Phase 1 setup first.")
```

### Rollback on Failure

```python
def workspace_add_with_rollback(module_name: str):
    """Add module with automatic rollback on failure."""
    # Create backup
    backup_dir = f"~/workspace/services/dagster/modules/backups/{timestamp}/"
    backup_workspace_files(backup_dir)

    try:
        # Perform integration
        integrate_module(module_name)
    except Exception as e:
        # Rollback on failure
        restore_workspace_files(backup_dir)
        raise Error(f"Integration failed: {e}. Workspace restored from backup.")
    finally:
        # Keep backup for 7 days
        schedule_backup_cleanup(backup_dir, days=7)
```

---

## Next Steps After Module Creation

### After `new` Command

```
✓ Module created at: ~/workspace/projects/my-data-pipeline

Next steps:
1. Review generated files
2. Customize assets in src/my_data_pipeline_dagster/assets.py
3. Integrate with workspace:
   @dagster-module-builder workspace add my-data-pipeline

4. Start workspace:
   cd ~/workspace/services/dagster && docker-compose up -d

5. Test in Dagster UI:
   http://localhost:3000
```

### After `workspace add`

```
✓ Module integrated with workspace

Modified files:
- ~/workspace/services/dagster/workspace.yaml (+3 lines)
- ~/workspace/services/dagster/.env (+5 lines)
- ~/workspace/services/dagster/docker-compose.yml (+20 lines)
- ~/workspace/services/dagster/Dockerfile (+5 lines)

Next steps:
1. Restart workspace:
   cd ~/workspace/services/dagster
   docker-compose up -d --build

2. Verify in Dagster UI:
   http://localhost:3000
   Navigate to Assets → Should see my_data_pipeline/* assets

3. Test materialization:
   Click on asset → Materialize
```

### After `configure-deployment`

```
✓ Deployment config created: deploy/yoda/

Generated files:
- deploy/yoda/deployment.yaml (deployment metadata)
- deploy/yoda/.env.deploy (production env vars)
- deploy/yoda/DEPLOYMENT.md (complete deployment guide)

Next steps:
1. Review deployment.yaml and update values
2. Update .env.deploy with production credentials
3. Follow deployment guide:
   cat deploy/yoda/DEPLOYMENT.md

4. For git strategy:
   - Commit module to repository
   - Follow initial setup steps
   - Deploy with git pull

5. For rsync strategy:
   - Follow initial setup steps
   - Use provided rsync commands
```

---

## Usage Examples

### Example 1: New Module with Everything

```
User: @dagster-module-builder new customer-analytics

Skill asks:
- Database type? → postgresql
- System requirements:
  - SSH connections? → yes
  - PDF processing? → yes
- Governance level? → standard
- Integrate with workspace? → yes
- Configure deployment? → yes
  - Deployment name? → production
  - Strategy? → git
  - Repository? → git@github.com:company/dagster-modules.git

Skill generates:
- projects/customer-analytics/
  ├── src/ (with custom IO manager)
  ├── workspace/local/ (integration configs)
  ├── deploy/production/ (git deployment)
  ├── pyproject.toml
  └── README.md

Skill integrates with workspace automatically.

User can immediately:
1. docker-compose up -d
2. Test in localhost:3000
3. Deploy to production with git push
```

### Example 2: Quick Module, Deploy Later

```
User: @dagster-module-builder new data-pipeline-x

Skill asks:
- Database? → none
- Governance? → quick
- Workspace integration? → later
- Deployment? → later

Skill generates:
- projects/data-pipeline-x/
  ├── src/
  ├── workspace/local/ (for later)
  ├── deploy/ (empty, for later)
  └── README.md

User develops locally, then later:
- @dagster-module-builder workspace add data-pipeline-x
- @dagster-module-builder configure-deployment data-pipeline-x
```

---

## Files & Directories

**Skill Location:**
```
~/workspace/skills/dagster-module-builder/
├── SKILL.md (this file)
├── README.md (usage docs)
├── templates/ (symlink to ../../patterns/dagster/)
├── examples/ (example modules)
└── lib/ (helper functions, future)
```

**Templates Location:**
```
~/workspace/patterns/dagster/
├── base/
├── workspace-integration/
├── deploy-strategies/
├── addons/
└── examples/
```

---

## Maintenance

### Updating Templates

When patterns change:
1. Update templates in `~/workspace/patterns/dagster/`
2. Document changes in patterns/dagster/CHANGELOG.md
3. Test with new module creation
4. Update this SKILL.md if logic changes

### Adding New Deployment Strategy

To add docker strategy:
1. Create `patterns/dagster/deploy-strategies/docker/`
2. Add deployment.yaml.template
3. Add DEPLOYMENT.md.template
4. Add Dockerfile.template
5. Update this SKILL.md Mode 3 questions
6. Test end-to-end

---

## Success Metrics

**Time Savings:**
- Module creation: 3 days → 10 minutes
- Workspace integration: 2 hours → 2 minutes
- Deployment config: 1 day → 5 minutes

**Quality:**
- Deployment issues: 3-4 per module → 0
- Documentation: 60% complete → 100%
- First deploy success: 30% → 100%

**Measurables:**
- Time to first materialization: < 1 hour
- Modules using skill: Target 6+ modules
- Client deployments: Support 3+ clients per module

---

**Version:** 1.0.0
**Last Updated:** 2025-12-10
**Status:** Ready for Implementation
