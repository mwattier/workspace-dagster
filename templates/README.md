# Dagster Module Templates

**Version**: 1.0.0
**Last Updated**: 2025-12-12
**Status**: Production Ready

This directory contains the complete set of templates used by the dagster-module-builder skill to create new Dagster modules.

---

## Installation for Team Members

These templates must be installed on your local system for the skill to work properly.

### Step 1: Create Patterns Directory

```bash
mkdir -p ~/workspace/patterns
```

### Step 2: Copy Templates

From the repository root:

```bash
cp -r templates ~/workspace/patterns/dagster
```

### Step 3: Verify Installation

Check that the templates are in place:

```bash
ls ~/workspace/patterns/dagster/
```

You should see:
```
addons/
base/
deploy-strategies/
shared-resources/
workspace-integration/
README.md
```

---

## Template Structure

```
~/workspace/patterns/dagster/
├── base/                        # Core module structure
│   ├── pyproject.toml.template
│   ├── README.md.template
│   ├── requirements.txt.template
│   └── src/
│       └── __MODULE_NAME___dagster/
│           ├── __init__.py.template
│           ├── assets.py.template
│           └── resources.py.template
│
├── addons/                      # Optional components
│   ├── database-postgres/
│   │   ├── docker-compose.yml.template
│   │   └── schema.sql.template
│   ├── database-mysql/
│   │   └── [similar structure]
│   └── scheduled-jobs/
│       ├── jobs.py.template
│       └── schedules.py.template
│
├── workspace-integration/       # Local workspace files
│   ├── docker-compose.yml.template
│   ├── dockerfile.snippet.template
│   └── workspace.yaml.template
│
├── deploy-strategies/           # Deployment configs
│   ├── git/
│   │   ├── DEPLOYMENT.md.template
│   │   └── deployment.yaml.template
│   └── rsync/
│       └── [similar structure]
│
└── shared-resources/            # Reusable components
    ├── metabase_resource.py
    └── README.md
```

---

## Template Placeholders

Templates use these placeholders that get replaced during module creation:

### Module Identification
- `__MODULE_NAME__` - Snake case name (e.g., `customer_analytics`)
- `__MODULE_TITLE__` - Human readable title (e.g., `Customer Analytics`)
- `__DESCRIPTION__` - Module purpose description

### Database Configuration
- `__DB_TYPE__` - Database type (`postgresql`, `mysql`, or empty)
- `__DB_PORT__` - Auto-assigned port (e.g., `5440`, `3307`)
- `__DB_NAME__` - Database name (e.g., `customer_analytics`)
- `__DB_USER__` - Database username
- `__DB_PASSWORD__` - Database password

### Deployment Configuration
- `__DEPLOY_NAME__` - Deployment name (e.g., `production`, `staging`)
- `__CLIENT_NAME__` - Client identifier
- `__GIT_REPO__` - Git repository URL

### Paths
- `__PROJECT_PATH__` - Full path to module directory
- `__WORKSPACE_PATH__` - Path to workspace directory

---

## Template Features

### Custom IO Manager
All modules include a custom IO manager (`resources.py`) that:
- Uses `/tmp/dagster_storage/` instead of default storage
- Prevents "file not found" errors in Docker containers
- Persists asset outputs across container restarts
- Handles serialization automatically

### Database Integration
When database is selected:
- Docker Compose service for database
- Health checks for proper startup
- Auto-detected ports to avoid conflicts
- Schema initialization scripts

### Workspace Integration
Generated files for easy workspace integration:
- `workspace.yaml` snippet for module registration
- Docker Compose configuration for database
- Environment variables template
- Dockerfile snippet for system dependencies

### Deployment Configurations
Multiple deployment strategies supported:
- **Git**: Version control on server, easy rollback
- **rsync**: Direct file sync, quick iterations
- **Docker**: Containerized deployment (coming soon)
- **CI/CD**: Automated pipelines (coming soon)

---

## Shared Resources

The `shared-resources/` directory contains reusable components:

### metabase_resource.py
Dagster resource for Metabase integration:
- Query execution
- Dashboard embedding
- Result caching
- Error handling

**Usage in modules:**
```python
from metabase_resource import metabase_resource

defs = Definitions(
    assets=[...],
    resources={
        "metabase": metabase_resource
    }
)
```

**Required environment variables:**
```bash
YODA_METABASE_URL=https://meta.example.com
YODA_METABASE_API_KEY=mb_...
```

---

## Updating Templates

### For Template Maintainers

When updating templates:

1. **Test thoroughly** - Create test module with updated templates
2. **Document changes** - Update this README with new features
3. **Version bump** - Update version at top of this file
4. **Commit to repo** - Push to shared repository
5. **Notify team** - Let team know to pull updates

### For Team Members

To get template updates:

```bash
cd ~/workspace/docs/dagster-workspace
git pull

# Re-copy templates
rm -rf ~/workspace/patterns/dagster
cp -r templates ~/workspace/patterns/dagster
```

**Note**: Always backup any custom modifications before updating.

---

## Adding Custom Templates

You can add custom templates or modify existing ones:

### Local Customization
```bash
# Edit templates in your patterns directory
vim ~/workspace/patterns/dagster/base/README.md.template

# Custom additions are local to your system
# Won't affect team unless committed
```

### Sharing with Team
```bash
# Copy your custom templates back to repo
cp ~/workspace/patterns/dagster/base/README.md.template \
   ~/workspace/docs/dagster-workspace/templates/base/

# Commit and push
cd ~/workspace/docs/dagster-workspace
git add templates/
git commit -m "Add custom README template"
git push
```

---

## Template Best Practices

### Module Structure
- Keep modules focused on single responsibility
- Use descriptive, specific module names
- Include comprehensive README with examples

### Database Configuration
- Always use custom IO manager (included in templates)
- Document database schema in schema.sql
- Include migration strategy for schema changes

### Environment Variables
- Never commit real values (.env in .gitignore)
- Always provide .env.example with placeholders
- Document required vs optional variables

### Documentation
- README.md: What the module does, how to use it
- DEPLOYMENT.md: How to deploy (generated per deployment)
- Inline comments: Complex logic only, not obvious code

### Testing
- Include test examples in assets.py
- Document how to test locally
- Provide sample data if needed

---

## Troubleshooting

### Templates Not Found

**Symptom**: Skill says templates directory doesn't exist

**Fix**:
```bash
# Verify path
ls ~/workspace/patterns/dagster/

# If missing, reinstall
cd ~/workspace/docs/dagster-workspace
cp -r templates ~/workspace/patterns/dagster
```

### Placeholder Not Replaced

**Symptom**: Generated file still has `__MODULE_NAME__`

**Fix**: Report to maintainer - bug in module_builder.py

### Custom Template Not Used

**Symptom**: Skill uses old template despite updates

**Fix**:
```bash
# Clear and reinstall templates
rm -rf ~/workspace/patterns/dagster
cp -r templates ~/workspace/patterns/dagster
```

---

## Usage

These templates are used by the `dagster-module-builder` skill.

**Create new module with Claude:**
```
Create a new Dagster module for customer analytics
```

**Or use CLI directly:**
```bash
cd ~/workspace/docs/dagster-workspace/skill
python3 lib/module_builder.py my-module --workspace
```

---

## Version History

### 1.0.0 - 2025-12-12
- Initial production release
- Base module structure
- PostgreSQL and MySQL database addons
- Git and rsync deployment strategies
- Workspace integration files
- Shared Metabase resource
- Custom IO manager

---

## Support

**Template Issues**: Report in this repository

**Skill Issues**: See `../skill/README.md`

**Usage Questions**: See `../skill/USAGE.md`

---

## Related Documentation

- [Skill Installation](../skill/INSTALL.md)
- [Skill Usage Guide](../skill/USAGE.md)
- [Module Builder README](../skill/README.md)

---

**Location**: This directory should be copied to `~/workspace/patterns/dagster/` on each team member's system.

**Maintenance**: Update when patterns change, notify team to pull and reinstall.
