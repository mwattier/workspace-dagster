# Module Pattern Documentation

**Understanding the standardized Dagster module pattern**

---

## 🎯 Overview

This workspace uses a **standardized module pattern** that ensures:
- **Independence**: Each module is self-contained
- **Consistency**: All modules follow the same structure
- **Security**: Comprehensive secret protection
- **Deployability**: Production-ready from day one

---

## 🏗️ Module Structure

Every module follows this structure:

```
module-name/
├── src/
│   └── module_name_dagster/
│       ├── __init__.py              # Dagster Definitions
│       ├── assets.py                # Data assets
│       ├── resources.py             # Custom IO manager
│       └── schedules.py             # (Optional) Schedules/sensors
│
├── workspace/
│   └── local/
│       ├── workspace.yaml           # Module entry for workspace
│       ├── .env                     # Environment variables
│       ├── docker-compose.yml       # Database service
│       └── dockerfile.snippet       # Python dependencies
│
├── deploy/
│   └── {environment}/
│       ├── deployment.yaml          # Deployment metadata
│       ├── .env.deploy.example      # Production env template
│       └── DEPLOYMENT.md            # Deployment guide
│
├── .gitignore                       # Comprehensive ignore rules
├── .env.example                     # Local env template
├── pyproject.toml                   # Python project config
├── requirements.txt                 # Python dependencies
└── README.md                        # Module documentation
```

---

## 🧩 Core Components

### 1. Dagster Code (`src/module_name_dagster/`)

#### `__init__.py` - The Definitions

```python
from dagster import Definitions
from .assets import my_asset
from .resources import module_name_io_manager

defs = Definitions(
    assets=[my_asset],
    resources={
        "io_manager": module_name_io_manager
    }
)
```

**Purpose:** Exposes your module's assets and resources to Dagster

---

#### `assets.py` - Your Data Pipelines

```python
from dagster import asset

@asset(
    key_prefix=["module_name"]  # Namespace isolation!
)
def my_asset(context):
    """
    Your data transformation logic here
    """
    # Fetch data
    data = fetch_data()

    # Transform data
    result = transform(data)

    # Return (IO manager handles storage)
    return result
```

**Key Concepts:**
- `key_prefix` creates namespace isolation
- Assets can depend on other assets
- Return value is stored by IO manager

---

#### `resources.py` - Custom IO Manager

```python
import os
import pickle
from pathlib import Path
from dagster import ConfigurableIOManager, InputContext, OutputContext, io_manager

class ModuleNameIOManager(ConfigurableIOManager):
    """
    Custom IO Manager for persistent storage
    """
    base_path: str = "/tmp/dagster_storage"

    def _get_path(self, context) -> str:
        """Generate file path for an asset"""
        asset_key_path = context.asset_key.path
        asset_name = asset_key_path[-1]

        Path(self.base_path).mkdir(parents=True, exist_ok=True)

        # Handle partitioned assets
        partition_key = getattr(context, 'partition_key', None)
        if partition_key:
            return os.path.join(self.base_path, f"{asset_name}_{partition_key}.pickle")
        else:
            return os.path.join(self.base_path, f"{asset_name}.pickle")

    def handle_output(self, context: OutputContext, obj) -> None:
        """Store the asset output"""
        file_path = self._get_path(context)
        storage_obj = {
            'data': obj,
            'type': type(obj).__name__,
        }
        with open(file_path, 'wb') as f:
            pickle.dump(storage_obj, f)
        context.log.info(f"Stored to {file_path}")

    def load_input(self, context: InputContext):
        """Load the asset input"""
        file_path = self._get_path(context)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No data found at {file_path}")

        with open(file_path, 'rb') as f:
            storage_obj = pickle.load(f)

        return storage_obj.get('data', storage_obj)

@io_manager
def module_name_io_manager() -> ModuleNameIOManager:
    """IO Manager factory"""
    storage_path = os.environ.get('DAGSTER_STORAGE_PATH', '/tmp/dagster_storage')
    return ModuleNameIOManager(base_path=storage_path)
```

**Why Custom IO Manager?**
- ✅ Data persists across container restarts
- ✅ Prevents "file not found" errors
- ✅ Works in both local and production
- ✅ Supports partitioned assets

---

### 2. Workspace Integration (`workspace/local/`)

#### `workspace.yaml` - Module Entry

```yaml
# This gets appended to ~/workspace/services/dagster/workspace.yaml

- python_package:
    package_name: module_name_dagster
    working_directory: /workspace/projects/module-name/src
```

**Purpose:** Tells Dagster where to find your module

---

#### `.env` - Environment Variables

```env
# This gets appended to ~/workspace/services/dagster/.env

# Module Database
MODULE_DB_HOST=module_name_postgres
MODULE_DB_PORT=5438
MODULE_DB_USER=module_user
MODULE_DB_PASSWORD=module_password
MODULE_DB_NAME=module_db

# Module-specific Configuration
MODULE_API_KEY=<from_auth>
MODULE_CONFIG_PATH=/workspace/projects/module-name/config.yaml
```

**Purpose:** Configuration and secrets for your module

---

#### `docker-compose.yml` - Database Service

```yaml
# This gets merged into ~/workspace/services/dagster/docker-compose.yml

services:
  module_name_postgres:
    image: postgres:15
    container_name: module_name_postgres
    environment:
      POSTGRES_USER: ${MODULE_DB_USER}
      POSTGRES_PASSWORD: ${MODULE_DB_PASSWORD}
      POSTGRES_DB: ${MODULE_DB_NAME}
    volumes:
      - ${DATA_PATH}/postgres/module-name:/var/lib/postgresql/data
    ports:
      - "${MODULE_DB_PORT}:5432"
    networks:
      - ${NETWORK_NAME}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${MODULE_DB_USER}"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
```

**Purpose:** Your module's dedicated database

---

#### `dockerfile.snippet` - Python Dependencies

```dockerfile
# This gets added to ~/workspace/services/dagster/Dockerfile

# Module-specific system packages
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*

# Module-specific Python packages
RUN pip install --no-cache-dir \
    pandas>=2.0.0 \
    requests>=2.31.0

# Add module to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/workspace/projects/module-name/src"
```

**Purpose:** Dependencies needed by your module

---

### 3. Deployment Configuration (`deploy/{environment}/`)

#### `deployment.yaml` - Metadata

```yaml
deployment:
  name: production
  client: Client Name
  environment: production

  strategy: git

  remote:
    host: production.server.com
    user: deploy_user
    base_path: /home/deploy/dagster
    module_path: /home/deploy/dagster/modules/module-name

  git:
    repository: git@github.com:org/module-name.git
    branch: main
    post_checkout: |
      cd /home/deploy/dagster
      docker compose build
      docker compose up -d --no-deps dagster_webserver

  module:
    package_name: module_name_dagster
    working_directory: /workspace/modules/module-name/src

  database:
    type: postgresql
    host: module_name_postgres
    port: 5432
    name: module_db
    user: module_user
```

**Purpose:** Deployment strategy and configuration

---

#### `.env.deploy.example` - Production Env Template

```env
# Production Environment Variables
# Copy this to .env.deploy and fill in actual values
# NEVER commit .env.deploy to git (contains secrets)

MODULE_DB_HOST=module_name_postgres
MODULE_DB_USER=module_user
MODULE_DB_PASSWORD=CHANGE_THIS_IN_PRODUCTION
MODULE_DB_NAME=module_db

MODULE_API_KEY=<GET_FROM_SECURE_STORAGE>
```

**Purpose:** Template for production secrets (safe to commit)

---

#### `DEPLOYMENT.md` - Deployment Guide

Complete step-by-step guide including:
- Quick deploy commands
- Configuration file examples
- Troubleshooting steps
- Rollback procedures

**Purpose:** Documentation for deploying to production

---

### 4. Security Files

#### `.gitignore` - Comprehensive Protection

```gitignore
# Environment Files (CRITICAL - Has Secrets)
.env
.env.local
.env.*.local

# Allow example files (safe to commit)
!.env.example
!.env.*.example

# Deployment environment files (has production passwords)
deploy/*/.env.deploy
deploy/**/.env.deploy

# Allow deployment examples (safe to commit)
!deploy/*/.env.deploy.example
!deploy/**/.env.deploy.example

# Session notes and handoff files
SESSION-*.md
*session-notes*.md
HANDOFF*.md

# Archived documentation
docs/archive/

# [... more comprehensive patterns ...]
```

**Purpose:** Prevent committing secrets to git

---

#### `.env.example` - Local Environment Template

```env
# Local Development Environment Variables
# Copy this to .env and fill in actual values

MODULE_DB_HOST=module_name_postgres
MODULE_DB_PORT=5438
MODULE_DB_USER=module_user
MODULE_DB_PASSWORD=CHANGE_THIS_PASSWORD
MODULE_DB_NAME=module_db
```

**Purpose:** Template for local secrets (safe to commit)

---

## 🔄 Integration Workflow

### How Modules Get Loaded

1. **Docker Compose** starts your module's database
2. **Dockerfile** includes your module in PYTHONPATH
3. **workspace.yaml** tells Dagster where to find your package
4. **Dagster** imports `{module}_dagster` and loads `defs`
5. **Assets** appear in Dagster UI under `module_name` namespace

### Namespace Isolation

Each module uses `key_prefix` to create isolated namespaces:

```python
@asset(key_prefix=["seo_stats"])
def my_asset(): ...
# Asset key: seo_stats/my_asset

@asset(key_prefix=["shopware_logs"])
def my_asset(): ...
# Asset key: shopware_logs/my_asset
```

**No conflicts!** Same asset name, different namespaces.

---

## 💾 Data Persistence

### The IO Manager Pattern

**Problem:** Default IO manager stores data in container filesystem
- ❌ Data lost on container restart
- ❌ "File not found" errors in production

**Solution:** Custom IO manager with mounted volume
- ✅ Data stored in `/tmp/dagster_storage/` (mounted to host)
- ✅ Data persists across container restarts
- ✅ Works in both local and production

### Storage Structure

```
/tmp/dagster_storage/
├── asset_name.pickle           # Non-partitioned asset
├── asset_name_2024-01-01.pickle  # Partitioned asset
└── asset_name_2024-01-02.pickle  # Another partition
```

---

## 🗄️ Database Strategy

### Each Module Gets Its Own Database

**Why?**
- ✅ **Isolation**: Module failures don't affect others
- ✅ **Security**: Separate credentials per module
- ✅ **Scaling**: Can move databases independently
- ✅ **Backup**: Module-specific backup strategies

### Port Allocation

**PostgreSQL:** 5438, 5439, 5440, 5441, ...
**MySQL:** 3307, 3308, 3309, ...

**Auto-detection:** New modules automatically get the next available port

---

## 📦 Dependency Management

### System Packages

Added to `dockerfile.snippet`:
```dockerfile
RUN apt-get update && apt-get install -y \
    openssh-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

### Python Packages

Added to `dockerfile.snippet`:
```dockerfile
RUN pip install --no-cache-dir \
    pandas>=2.0.0 \
    requests>=2.31.0 \
    your-package>=1.0.0
```

Also listed in `requirements.txt` for local development.

---

## 🔐 Security Principles

### Never Commit Secrets

**Protected by .gitignore:**
- `.env` (local secrets)
- `deploy/*/.env.deploy` (production secrets)
- `auth/` (credentials)

**Safe to commit:**
- `.env.example` (templates with placeholders)
- `.env.deploy.example` (production templates)
- All other configuration files

### Secret Management

**Local:** Store in `.env` (gitignored)
**Production:** Use secure secret management (env vars, vault)
**Auth Files:** Store in `~/workspace/auth/{module}/` (gitignored)

---

## 🚀 Production Ready

Every module includes:
- ✅ Custom IO manager (data persistence)
- ✅ Comprehensive .gitignore (security)
- ✅ Deployment guide (operations)
- ✅ Environment templates (configuration)
- ✅ Health checks (reliability)
- ✅ Rollback procedures (safety)

---

## 📊 Example Modules

### seo-stats (PostgreSQL)
- Fetches Google Analytics 4 data
- Stores in PostgreSQL database
- Scheduled daily updates

### shopware-logs (MySQL)
- Fetches logs via SSH from remote server
- Stores in MySQL database
- On-demand processing

### beast-hubspot (Shared PostgreSQL)
- Syncs HubSpot data via dlt framework
- Uses shared customer_data database
- Scheduled hourly updates

---

## 🎯 Key Takeaways

1. **Every module is independent** - Has its own database, IO manager, config
2. **Workspace integration is self-describing** - `workspace/local/` configs tell you exactly what to add
3. **Security is built-in** - Comprehensive .gitignore protects secrets
4. **Production-ready from day one** - Deployment guides included
5. **Custom IO managers are essential** - Ensure data persists

---

## 🔜 Next Steps

**→ Continue to [CREATING-MODULES.md](CREATING-MODULES.md)** to create your first module

---

**Last Updated**: 2025-12-10
