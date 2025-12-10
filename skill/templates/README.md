# Dagster Module Templates

Production-ready Dagster module templates with workspace integration and multi-strategy deployment support.

## Directory Structure

```
dagster/
├── base/                        # Core module template (always used)
│   ├── src/
│   │   └── __MODULE_NAME___dagster/
│   │       ├── __init__.py.template
│   │       ├── assets.py.template
│   │       └── resources.py           # Custom IO manager (proven)
│   ├── pyproject.toml.template
│   ├── requirements.txt.template
│   └── README.md.template
│
├── workspace-integration/       # Local workspace integration
│   ├── workspace.yaml.template
│   ├── docker-compose.yml.template
│   ├── .env.template
│   └── dockerfile.snippet.template
│
├── deploy-strategies/          # Remote deployment strategies
│   ├── rsync/
│   │   ├── deployment.yaml.template
│   │   └── DEPLOYMENT.md.template
│   ├── git/
│   │   ├── deployment.yaml.template
│   │   └── DEPLOYMENT.md.template
│   ├── docker/
│   │   ├── deployment.yaml.template
│   │   ├── Dockerfile.template
│   │   └── DEPLOYMENT.md.template
│   └── cicd/
│       ├── deployment.yaml.template
│       ├── github-actions.yml.template
│       └── DEPLOYMENT.md.template
│
├── addons/                     # Optional components
│   ├── database-postgres/
│   │   ├── docker-compose.yml.template
│   │   ├── .env.template
│   │   └── schema.sql.template
│   ├── database-mysql/
│   │   ├── docker-compose.yml.template
│   │   ├── .env.template
│   │   └── schema.sql.template
│   └── scheduled-jobs/
│       ├── jobs.py.template
│       └── schedules.py.template
│
└── examples/                   # Real working examples
    ├── beast-hubspot/
    └── seo-stats/
```

## Template Variables

### Standard Placeholders

All templates use these placeholders:

| Placeholder | Example | Description |
|-------------|---------|-------------|
| `__MODULE_NAME__` | `my_data_pipeline` | Snake case module name |
| `__MODULE_TITLE__` | `My Data Pipeline` | Title case for display |
| `__MODULE_DESCRIPTION__` | `ETL pipeline for customer data` | Short description |
| `__DB_TYPE__` | `postgresql` | Database type (postgresql/mysql/none) |
| `__DB_PORT__` | `5440` | Database port (auto-assigned) |
| `__DB_NAME__` | `my_data_pipeline` | Database name |
| `__DB_USER__` | `my_pipeline_user` | Database user |
| `__DB_PASSWORD__` | `my_pipeline_password` | Database password |

### Environment-Specific

**Workspace Integration:**
- `__WORKSPACE_PATH__` - Path to workspace root
- `__DATA_PATH__` - Path to data directory
- `__AUTH_PATH__` - Path to auth directory

**Deployment:**
- `__DEPLOY_NAME__` - Deployment name (e.g., "yoda")
- `__CLIENT_NAME__` - Client name (e.g., "Beast Business")
- `__REMOTE_HOST__` - Remote server hostname
- `__REMOTE_USER__` - Remote SSH user
- `__REMOTE_BASE_PATH__` - Base path on remote (e.g., /home/mwattier/tools/dagster)

## Usage

These templates are used by the `dagster-module-builder` skill at:
`~/workspace/skills/dagster-module-builder/`

**Create new module:**
```bash
@dagster-module-builder new my-data-pipeline
```

**Integrate with workspace:**
```bash
@dagster-module-builder workspace add my-data-pipeline
```

**Configure deployment:**
```bash
@dagster-module-builder configure-deployment my-data-pipeline
```

## Template Sources

Templates extracted from proven working modules:
- **beast-hubspot** - Most recent, git deployment, postgres
- **seo-stats** - Postgres, Google Analytics integration
- **shopware-logs** - MySQL, ETL from e-commerce logs

## Development Status

- [x] Directory structure created
- [ ] Base templates extracted
- [ ] Workspace integration templates created
- [ ] Deployment strategy templates created
- [ ] Database addons created
- [ ] Examples added
- [ ] Skill agent implemented
- [ ] Testing completed

**Last Updated:** 2025-12-10
**Status:** In Progress - Phase 1
