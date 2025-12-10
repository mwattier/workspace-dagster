# Dagster Workspace Setup

**Step-by-step guide to setting up your local Dagster workspace**

---

## 📋 Before You Start

✅ Verify you've completed **[REQUIREMENTS.md](REQUIREMENTS.md)** checklist

---

## 🏗️ Setup Overview

This guide will help you:
1. Create the workspace directory structure
2. Set up the main Dagster service (Docker)
3. Configure workspace files
4. Start the Dagster instance
5. Verify everything works

**Estimated Time:** 30-45 minutes (first time)

---

## Step 1: Create Workspace Structure

```bash
# Create main workspace directory
mkdir -p ~/workspace

# Create subdirectories
mkdir -p ~/workspace/services/dagster
mkdir -p ~/workspace/projects
mkdir -p ~/workspace/patterns/dagster
mkdir -p ~/workspace/data/postgres
mkdir -p ~/workspace/data/mysql
mkdir -p ~/workspace/auth
mkdir -p ~/workspace/docs

# Navigate to workspace
cd ~/workspace
```

**Result:** You should have this structure:
```
~/workspace/
├── services/dagster/  (empty - we'll populate this)
├── projects/          (empty - for your modules)
├── patterns/dagster/  (empty - optional templates)
├── data/             (empty - Docker will populate)
├── auth/             (empty - you'll add credentials)
└── docs/             (contains this documentation)
```

---

## Step 2: Create Dagster Configuration Files

### 2.1 Create `workspace.yaml`

```bash
cat > ~/workspace/services/dagster/workspace.yaml << 'EOF'
# Dagster Workspace Configuration
# Modules are loaded from ~/workspace/projects/

load_from:
  # Add your modules here as you create them
  # Example format:
  # - python_package:
  #     package_name: your_module_dagster
  #     working_directory: /workspace/projects/your-module/src
EOF
```

### 2.2 Create `dagster.yaml`

```bash
cat > ~/workspace/services/dagster/dagster.yaml << 'EOF'
# Dagster Instance Configuration

# PostgreSQL storage for run history, event logs, schedules
storage:
  postgres:
    postgres_url:
      env: DAGSTER_PG_URL

# Default run launcher (local process)
run_launcher:
  module: dagster.core.launcher
  class: DefaultRunLauncher

# Scheduler configuration
scheduler:
  module: dagster.core.scheduler
  class: DagsterDaemonScheduler

# Compute log storage
compute_logs:
  module: dagster.core.storage.local_compute_log_manager
  class: LocalComputeLogManager
  config:
    base_dir: /opt/dagster/dagster_home/compute_logs

# Local artifact storage
local_artifact_storage:
  module: dagster.core.storage.root
  class: LocalArtifactStorage
  config:
    base_dir: /opt/dagster/dagster_home/storage

# Telemetry (optional - disable if needed)
telemetry:
  enabled: false
EOF
```

### 2.3 Create `.env`

```bash
cat > ~/workspace/services/dagster/.env << 'EOF'
# Dagster Workspace Environment Variables

# Network Configuration
NETWORK_NAME=workspace-net

# Dagster Metadata Database
DAGSTER_PG_HOST=dagster_metadata_postgres
DAGSTER_PG_PORT=5432
DAGSTER_PG_USER=dagster_user
DAGSTER_PG_PASSWORD=dagster_password
DAGSTER_PG_DB=dagster_metadata
DAGSTER_PG_URL=postgresql://dagster_user:dagster_password@dagster_metadata_postgres:5432/dagster_metadata

# Data Paths (relative to services/dagster/)
DATA_PATH=../../data

# Module-specific environment variables will be added here
# as you integrate new modules
EOF
```

### 2.4 Create `docker-compose.yml`

```bash
cat > ~/workspace/services/dagster/docker-compose.yml << 'EOF'
version: "3.8"

networks:
  workspace-net:
    driver: bridge

services:
  # Dagster Metadata PostgreSQL Database
  dagster_metadata_postgres:
    image: postgres:15
    container_name: dagster_metadata_postgres
    environment:
      POSTGRES_USER: ${DAGSTER_PG_USER:-dagster_user}
      POSTGRES_PASSWORD: ${DAGSTER_PG_PASSWORD:-dagster_password}
      POSTGRES_DB: ${DAGSTER_PG_DB:-dagster_metadata}
    volumes:
      - ${DATA_PATH:-../../data}/postgres/dagster-metadata:/var/lib/postgresql/data
    ports:
      - "${DAGSTER_PG_PORT:-5437}:5432"
    networks:
      - ${NETWORK_NAME:-workspace-net}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${DAGSTER_PG_USER:-dagster_user}"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  # Dagster Webserver (UI)
  dagster_webserver:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: workspace_dagster_webserver
    image: workspace-dagster:latest
    entrypoint:
      - dagster-webserver
      - -h
      - "0.0.0.0"
      - -p
      - "3000"
      - -w
      - /opt/dagster/dagster_home/workspace.yaml
    environment:
      DAGSTER_PG_URL: ${DAGSTER_PG_URL}
      PYTHONUNBUFFERED: "1"
    volumes:
      - ./workspace.yaml:/opt/dagster/dagster_home/workspace.yaml:ro
      - ./dagster.yaml:/opt/dagster/dagster_home/dagster.yaml:ro
      - ../../projects:/workspace/projects:ro
      - ../../auth:/workspace/auth:ro
      - /tmp/dagster_storage:/tmp/dagster_storage
    ports:
      - "3000:3000"
    networks:
      - ${NETWORK_NAME:-workspace-net}
    depends_on:
      dagster_metadata_postgres:
        condition: service_healthy
    restart: unless-stopped

  # Dagster Daemon (Schedules, Sensors, Run Queue)
  dagster_daemon:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: workspace_dagster_daemon
    image: workspace-dagster:latest
    entrypoint:
      - dagster-daemon
      - run
    environment:
      DAGSTER_PG_URL: ${DAGSTER_PG_URL}
      PYTHONUNBUFFERED: "1"
    volumes:
      - ./workspace.yaml:/opt/dagster/dagster_home/workspace.yaml:ro
      - ./dagster.yaml:/opt/dagster/dagster_home/dagster.yaml:ro
      - ../../projects:/workspace/projects:ro
      - ../../auth:/workspace/auth:ro
      - /tmp/dagster_storage:/tmp/dagster_storage
    networks:
      - ${NETWORK_NAME:-workspace-net}
    depends_on:
      dagster_metadata_postgres:
        condition: service_healthy
    restart: unless-stopped
EOF
```

### 2.5 Create `Dockerfile`

```bash
cat > ~/workspace/services/dagster/Dockerfile << 'EOF'
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create dagster user and directories
RUN useradd -m -u 1000 dagster && \
    mkdir -p /opt/dagster/dagster_home && \
    chown -R dagster:dagster /opt/dagster

# Set working directory
WORKDIR /opt/dagster/dagster_home

# Install Dagster
RUN pip install --no-cache-dir \
    dagster>=1.9.0 \
    dagster-webserver>=1.9.0 \
    dagster-postgres>=0.21.0

# Set environment variables
ENV DAGSTER_HOME=/opt/dagster/dagster_home
ENV PYTHONPATH="${PYTHONPATH}"

# Switch to dagster user
USER dagster

# Expose ports
EXPOSE 3000

# Default command (overridden by docker-compose)
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
EOF
```

---

## Step 3: Build and Start Dagster

### 3.1 Build the Docker Image

```bash
cd ~/workspace/services/dagster
docker compose build
```

**Expected output:**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition
 => => transferring dockerfile: 891B
 => [internal] load .dockerignore
 ...
 => exporting to image
 => => naming to docker.io/library/workspace-dagster:latest
```

**This may take 2-5 minutes the first time.**

### 3.2 Start the Services

```bash
docker compose up -d
```

**Expected output:**
```
[+] Running 3/3
 ✔ Network workspace-net                  Created
 ✔ Container dagster_metadata_postgres    Started
 ✔ Container workspace_dagster_webserver  Started
 ✔ Container workspace_dagster_daemon     Started
```

### 3.3 Verify Services Are Running

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected output:**
```
NAMES                          STATUS              PORTS
workspace_dagster_webserver    Up 30 seconds       0.0.0.0:3000->3000/tcp
workspace_dagster_daemon       Up 30 seconds
dagster_metadata_postgres      Up 30 seconds       0.0.0.0:5437->5432/tcp
```

---

## Step 4: Verify Dagster UI

### 4.1 Access the UI

Open your browser to: **http://localhost:3000**

You should see:
- ✅ Dagster UI loads successfully
- ✅ "No code locations found" message (expected - no modules yet)

### 4.2 Check Logs

```bash
# Check webserver logs
docker logs workspace_dagster_webserver --tail 50

# Check daemon logs
docker logs workspace_dagster_daemon --tail 50
```

**Look for:**
- ✅ "Serving dagster-webserver on http://0.0.0.0:3000"
- ✅ No ERROR messages

---

## Step 5: Initial Configuration Complete

🎉 **Congratulations!** Your Dagster workspace is now running!

### What You Have Now

- ✅ Dagster webserver at http://localhost:3000
- ✅ Dagster daemon running (for schedules/sensors)
- ✅ PostgreSQL metadata database
- ✅ Docker network for services
- ✅ Mounted volumes for persistence

### What's Next

Your workspace is ready but has no modules yet. You can now:

**→ Continue to [MODULE-PATTERN.md](MODULE-PATTERN.md)** to understand how modules work

**→ Or jump to [CREATING-MODULES.md](CREATING-MODULES.md)** to create your first module

---

## 🛠️ Common Commands

### Start Services
```bash
cd ~/workspace/services/dagster
docker compose up -d
```

### Stop Services
```bash
cd ~/workspace/services/dagster
docker compose down
```

### Restart Services
```bash
cd ~/workspace/services/dagster
docker compose restart
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker logs workspace_dagster_webserver -f
```

### Rebuild After Changes
```bash
cd ~/workspace/services/dagster
docker compose build
docker compose up -d
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using port 3000
lsof -i :3000

# Or use a different port in .env
echo "DAGSTER_WEBSERVER_PORT=3001" >> .env
```

### Database Connection Failed
```bash
# Check database is healthy
docker exec dagster_metadata_postgres pg_isready -U dagster_user

# Recreate database
docker compose down -v
docker compose up -d
```

### Can't Access UI
```bash
# Check firewall allows port 3000
sudo ufw allow 3000/tcp

# Check container is running
docker ps | grep dagster_webserver
```

**For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

---

**Last Updated**: 2025-12-10
