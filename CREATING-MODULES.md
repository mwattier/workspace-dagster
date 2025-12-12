# Creating Dagster Modules

**Complete guide to creating new Dagster modules**

---

## 🎯 Overview

You have two options for creating modules:
1. **Claude Code Skill** (Recommended) - Automated, fast, consistent
2. **Manual Process** - Full control, educational

Both produce the same standardized result.

---

## Option 1: Claude Code Skill (Recommended)

### Prerequisites

- Claude Code installed ([setup guide](https://github.com/anthropics/claude-code))
- This repository cloned locally
- Templates installed (see [templates/README.md](templates/README.md))

### Installation

See [skill/INSTALL.md](skill/INSTALL.md) for complete installation instructions.

**Quick install:**
```bash
# From this repository's root directory
ln -sf $(pwd)/skill ~/.claude/skills/dagster-module-builder

# Verify installation
claude skills list | grep dagster-module-builder
```

### Usage

```bash
# Navigate to workspace
cd ~/workspace

# Start Claude Code session
claude

# In Claude session, use the skill
@dagster-module-builder new
```

### Interactive Prompts

The skill will ask you:

1. **Module name** (e.g., "my-module")
2. **Database type** (postgres/mysql/none)
3. **Governance tier** (quick/standard/enterprise)
4. **Client name** (for deployment metadata)
5. **Workspace integration** (yes/no)
6. **Deployment environment** (production/staging/none)

### What Gets Created

The skill automatically creates:
- ✅ Complete module structure (17+ files)
- ✅ Custom IO manager
- ✅ Workspace integration configs
- ✅ Deployment guides
- ✅ Comprehensive .gitignore
- ✅ Environment templates

**Time: ~2 minutes** (vs 20-30 minutes manual)

### After Creation

```bash
# Navigate to your new module
cd ~/workspace/projects/your-module

# Review the generated files
ls -la

# Read the README
cat README.md

# Test locally (if workspace integrated)
cd ~/workspace/services/dagster
docker compose build
docker compose up -d
```

---

## Option 2: Manual Process

### Prerequisites

- Templates in `~/workspace/patterns/dagster/` (optional but helpful)
- Understanding of module pattern ([MODULE-PATTERN.md](MODULE-PATTERN.md))

---

### Step 1: Create Module Directory Structure

```bash
# Set your module name (snake_case)
MODULE_NAME="my_module"
MODULE_DIR="my-module"

# Create directories
mkdir -p ~/workspace/projects/${MODULE_DIR}/{src/${MODULE_NAME}_dagster,workspace/local,deploy/production}

cd ~/workspace/projects/${MODULE_DIR}
```

---

### Step 2: Create Dagster Code Files

#### 2.1 Create `src/{module}_dagster/__init__.py`

```python
from dagster import Definitions
from .assets import sample_asset
from .resources import ${MODULE_NAME}_io_manager

defs = Definitions(
    assets=[sample_asset],
    resources={
        "io_manager": ${MODULE_NAME}_io_manager
    }
)
```

#### 2.2 Create `src/{module}_dagster/assets.py`

```python
from dagster import asset
from datetime import datetime

@asset(
    key_prefix=["${MODULE_NAME}"],
    description="Sample asset for ${MODULE_NAME}"
)
def sample_asset(context):
    """
    Sample asset - replace with your actual logic
    """
    context.log.info("Running sample_asset")

    # Your data transformation logic here
    data = {
        "status": "success",
        "message": f"Sample data from ${MODULE_NAME}",
        "timestamp": datetime.now().isoformat()
    }

    return data
```

#### 2.3 Create `src/{module}_dagster/resources.py`

```python
import os
import pickle
from pathlib import Path
from typing import Any
from dagster import ConfigurableIOManager, InputContext, OutputContext, io_manager


class ${MODULE_NAME.title().replace('_', '')}IOManager(ConfigurableIOManager):
    """
    Custom IO Manager for ${MODULE_NAME} assets.

    Stores asset outputs as pickle files in /tmp/dagster_storage/ which is
    mounted to the host for persistence across container executions.
    """

    base_path: str = "/tmp/dagster_storage"

    def _get_path(self, context) -> str:
        """Generate file path for an asset."""
        asset_key_path = context.asset_key.path
        asset_name = asset_key_path[-1]

        Path(self.base_path).mkdir(parents=True, exist_ok=True)

        # Check if this asset is partitioned
        partition_key = None
        try:
            if hasattr(context, 'partition_key') and context.partition_key:
                partition_key = context.partition_key
        except Exception:
            partition_key = None

        if partition_key:
            return os.path.join(self.base_path, f"{asset_name}_{partition_key}.pickle")
        else:
            return os.path.join(self.base_path, f"{asset_name}.pickle")

    def handle_output(self, context: OutputContext, obj: Any) -> None:
        """Store the asset output."""
        file_path = self._get_path(context)
        storage_obj = {
            'data': obj,
            'type': type(obj).__name__,
        }
        with open(file_path, 'wb') as f:
            pickle.dump(storage_obj, f)
        context.log.info(f"Stored {type(obj).__name__} to {file_path}")

    def load_input(self, context: InputContext) -> Any:
        """Load the asset input."""
        file_path = self._get_path(context)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No stored data found at {file_path}")

        with open(file_path, 'rb') as f:
            storage_obj = pickle.load(f)

        # Handle legacy format
        if not isinstance(storage_obj, dict) or 'data' not in storage_obj:
            return storage_obj

        data = storage_obj['data']
        context.log.info(f"Loaded {type(data).__name__} from {file_path}")
        return data


@io_manager
def ${MODULE_NAME}_io_manager() -> ${MODULE_NAME.title().replace('_', '')}IOManager:
    """IO Manager factory for ${MODULE_NAME} assets."""
    storage_path = os.environ.get('DAGSTER_STORAGE_PATH', '/tmp/dagster_storage')
    return ${MODULE_NAME.title().replace('_', '')}IOManager(base_path=storage_path)
```

---

### Step 3: Create Project Configuration Files

#### 3.1 Create `pyproject.toml`

```toml
[project]
name = "${MODULE_NAME.replace('_', '-')}"
version = "0.1.0"
description = "${MODULE_NAME} Dagster module"

dependencies = [
    "dagster>=1.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

#### 3.2 Create `requirements.txt`

```txt
# Core Dagster dependencies
dagster>=1.9.0

# Add your module-specific dependencies here
# pandas>=2.0.0
# requests>=2.31.0
```

#### 3.3 Create `.env.example`

```env
# Local Development Environment Variables
# Copy this to .env and fill in actual values

# Database Configuration
${MODULE_NAME.upper()}_DB_HOST=localhost
${MODULE_NAME.upper()}_DB_PORT=5438
${MODULE_NAME.upper()}_DB_USER=${MODULE_NAME}_user
${MODULE_NAME.upper()}_DB_PASSWORD=CHANGE_THIS_PASSWORD
${MODULE_NAME.upper()}_DB_NAME=${MODULE_NAME}_db
```

#### 3.4 Create `.gitignore`

```bash
# Copy from the templates directory in this repository
cp path/to/this-repo/templates/base/.gitignore.template .gitignore
```

Or create manually with at minimum:
```
.env
__pycache__/
*.pyc
```

---

### Step 4: Create Workspace Integration Configs

#### 4.1 Create `workspace/local/workspace.yaml`

```yaml
# Workspace entry for ${MODULE_NAME}
# This gets appended to ~/workspace/services/dagster/workspace.yaml

- python_package:
    package_name: ${MODULE_NAME}_dagster
    working_directory: /workspace/projects/${MODULE_DIR}/src
```

#### 4.2 Create `workspace/local/.env`

```env
# Environment variables for ${MODULE_NAME}
# This gets appended to ~/workspace/services/dagster/.env

# ${MODULE_NAME.upper()} Database
${MODULE_NAME.upper()}_DB_HOST=${MODULE_NAME}_postgres
${MODULE_NAME.upper()}_DB_PORT=5438
${MODULE_NAME.upper()}_DB_USER=${MODULE_NAME}_user
${MODULE_NAME.upper()}_DB_PASSWORD=${MODULE_NAME}_password
${MODULE_NAME.upper()}_DB_NAME=${MODULE_NAME}_db
```

#### 4.3 Create `workspace/local/docker-compose.yml`

```yaml
# Database service for ${MODULE_NAME}
# This gets merged into ~/workspace/services/dagster/docker-compose.yml

services:
  ${MODULE_NAME}_postgres:
    image: postgres:15
    container_name: ${MODULE_NAME}_postgres
    environment:
      POSTGRES_USER: \${${MODULE_NAME.upper()}_DB_USER}
      POSTGRES_PASSWORD: \${${MODULE_NAME.upper()}_DB_PASSWORD}
      POSTGRES_DB: \${${MODULE_NAME.upper()}_DB_NAME}
    volumes:
      - \${DATA_PATH}/postgres/${MODULE_DIR}:/var/lib/postgresql/data
    ports:
      - "\${${MODULE_NAME.upper()}_DB_PORT}:5432"
    networks:
      - \${NETWORK_NAME}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "\${${MODULE_NAME.upper()}_DB_USER}"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
```

#### 4.4 Create `workspace/local/dockerfile.snippet`

```dockerfile
# Python dependencies for ${MODULE_NAME}
RUN pip install --no-cache-dir \
    pandas>=2.0.0

# Update PYTHONPATH to include ${MODULE_NAME}
ENV PYTHONPATH="\${PYTHONPATH}:/workspace/projects/${MODULE_DIR}/src"
```

---

### Step 5: Create Deployment Configs

#### 5.1 Create `deploy/production/deployment.yaml`

```yaml
deployment:
  name: production
  client: Your Client Name
  environment: production

  strategy: git

  remote:
    host: production.server.com
    user: deploy_user
    base_path: /home/deploy/dagster
    module_path: /home/deploy/dagster/modules/${MODULE_DIR}

  git:
    repository: <GIT_REPOSITORY_URL>
    branch: main
    post_checkout: |
      cd /home/deploy/dagster
      docker compose build
      docker compose up -d --no-deps dagster_webserver

  module:
    package_name: ${MODULE_NAME}_dagster
    working_directory: /workspace/modules/${MODULE_DIR}/src

  database:
    type: postgresql
    host: ${MODULE_NAME}_postgres
    port: 5432
    name: ${MODULE_NAME}_db
    user: ${MODULE_NAME}_user
```

#### 5.2 Create `deploy/production/.env.deploy.example`

```env
# Production Environment Variables for ${MODULE_NAME}
# Copy this to .env.deploy and fill in actual production values
# NEVER commit .env.deploy to git (contains secrets)

${MODULE_NAME.upper()}_DB_HOST=${MODULE_NAME}_postgres
${MODULE_NAME.upper()}_DB_USER=${MODULE_NAME}_user
${MODULE_NAME.upper()}_DB_PASSWORD=CHANGE_THIS_IN_PRODUCTION
${MODULE_NAME.upper()}_DB_NAME=${MODULE_NAME}_db
```

#### 5.3 Create `deploy/production/DEPLOYMENT.md`

Create a comprehensive deployment guide. See examples in existing modules.

---

### Step 6: Create README.md

```markdown
# ${MODULE_NAME}

${MODULE_NAME} Dagster module

## Setup

1. Copy .env.example to .env and fill in values
2. Install dependencies: \`pip install -r requirements.txt\`

## Integration

See \`workspace/local/\` for workspace integration configs.

## Deployment

See \`deploy/production/DEPLOYMENT.md\` for deployment guide.
```

---

### Step 7: Integrate with Workspace

Now follow the workspace integration steps:

#### 7.1 Backup Workspace Files

```bash
cd ~/workspace/services/dagster
BACKUP_DIR="modules/backups/$(date +%Y%m%d_%H%M%S)_${MODULE_DIR}"
mkdir -p "$BACKUP_DIR"
cp workspace.yaml .env docker-compose.yml Dockerfile "$BACKUP_DIR/"
```

#### 7.2 Append to workspace.yaml

```bash
cat ~/workspace/projects/${MODULE_DIR}/workspace/local/workspace.yaml >> workspace.yaml
```

#### 7.3 Append to .env

```bash
echo "" >> .env
cat ~/workspace/projects/${MODULE_DIR}/workspace/local/.env >> .env
```

#### 7.4 Add Database Service to docker-compose.yml

Manually merge the service from `workspace/local/docker-compose.yml` into the main `docker-compose.yml`.

Also add to `depends_on` for both `dagster_webserver` and `dagster_daemon`.

#### 7.5 Update Dockerfile

Add the contents of `workspace/local/dockerfile.snippet` to the Dockerfile.

#### 7.6 Rebuild and Restart

```bash
docker compose build
docker compose up -d
```

---

### Step 8: Verify Module Loaded

```bash
# Check logs for your module
docker logs workspace_dagster_webserver 2>&1 | grep "${MODULE_NAME}"

# Should see:
# Started Dagster code server for package ${MODULE_NAME}_dagster
```

Access UI at http://localhost:3000 and verify your module appears!

---

## 🎯 Next Steps After Creation

### Test Your Module

1. **Access Dagster UI**: http://localhost:3000
2. **Find your module** in the left sidebar
3. **Materialize sample_asset** to test

### Customize Your Module

1. **Replace sample_asset** with real data logic
2. **Add dependencies** to requirements.txt
3. **Add schedules/sensors** if needed
4. **Write tests** in tests/ directory

### Deploy to Production

When ready:
1. Follow `deploy/production/DEPLOYMENT.md`
2. Update production configs
3. Test in staging first
4. Deploy to production

---

## 📚 Examples

See existing modules for reference:
- `~/workspace/projects/seo-stats/` - PostgreSQL, GA4 API
- `~/workspace/projects/shopware-logs/` - MySQL, SSH fetching
- `~/workspace/projects/beast-hubspot/` - Shared DB, dlt framework
- `~/workspace/projects/dag-hello-world/` - Simple test module

---

## 🐛 Troubleshooting

### Module Not Loading

```bash
# Check PYTHONPATH includes your module
docker exec workspace_dagster_webserver printenv PYTHONPATH

# Check workspace.yaml has your module
docker exec workspace_dagster_webserver cat /opt/dagster/dagster_home/workspace.yaml

# Check for import errors
docker logs workspace_dagster_webserver 2>&1 | grep -i error
```

### Database Connection Failed

```bash
# Check database service is running
docker ps | grep ${MODULE_NAME}

# Check database health
docker exec ${MODULE_NAME}_postgres pg_isready -U ${MODULE_NAME}_user
```

### IO Manager Errors

Ensure `/tmp/dagster_storage` is mounted in docker-compose.yml:
```yaml
volumes:
  - /tmp/dagster_storage:/tmp/dagster_storage
```

**For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

---

**Last Updated**: 2025-12-10
