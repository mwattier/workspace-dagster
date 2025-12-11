# Dagster Workspace Documentation

**Complete guide to setting up and using the Dagster workspace with standardized module pattern**


---

## 📚 Documentation Index

### Getting Started
1. **[REQUIREMENTS.md](REQUIREMENTS.md)** - Prerequisites and tools needed
2. **[SETUP.md](SETUP.md)** - Step-by-step local Dagster workspace setup

### Understanding the System
3. **[MODULE-PATTERN.md](MODULE-PATTERN.md)** - Architecture and concepts of the module pattern
4. **[CREATING-MODULES.md](CREATING-MODULES.md)** - How to create new Dagster modules

### Advanced Topics
5. **[PRODUCTION-DEPLOYMENT.md](PRODUCTION-DEPLOYMENT.md)** - Production deployment concepts
6. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

### Tools
7. **[skill/](skill/)** - Claude Code skill for automated module creation

---

## 🎯 Quick Start

**New to this workspace?** Follow this path:

```bash
# 1. Check you have the prerequisites
→ Read REQUIREMENTS.md

# 2. Set up your local Dagster workspace
→ Follow SETUP.md

# 3. Understand how modules work
→ Read MODULE-PATTERN.md

# 4. Create your first module
→ Follow CREATING-MODULES.md
```

---

## 🏗️ What is This?

This Dagster workspace uses a **standardized module pattern** that provides:

- ✅ **Isolated modules** - Each project is independent with its own database
- ✅ **Custom IO managers** - Proper data persistence across container restarts
- ✅ **Consistent structure** - All modules follow the same pattern
- ✅ **Easy integration** - Self-describing configs for workspace integration
- ✅ **Deployment ready** - Production deployment guides included
- ✅ **Security first** - Comprehensive .gitignore protecting secrets

---

## 📂 Workspace Structure

```
~/workspace/
├── services/dagster/           # Main Dagster workspace (Docker)
│   ├── workspace.yaml          # Loads all modules
│   ├── dagster.yaml            # Instance configuration
│   ├── docker-compose.yml      # All services (Dagster + databases)
│   ├── Dockerfile              # Dagster image with module dependencies
│   └── .env                    # Environment variables
│
├── projects/                   # Individual Dagster modules
│   ├── seo-stats/              # Example: SEO statistics module
│   ├── shopware-logs/          # Example: Shopware log processing
│   └── dag-hello-world/        # Example: Test module
│
├── patterns/dagster/           # Templates for creating new modules
│   ├── base/                   # Core module files
│   ├── addons/                 # Database & feature addons
│   └── workspace-integration/  # Integration configs
│
├── data/                       # Database data volumes
│   ├── postgres/               # PostgreSQL databases
│   └── mysql/                  # MySQL databases
│
└── auth/                       # Authentication credentials
    └── {module-name}/          # Per-module credentials
```

---

## 🚀 Key Concepts

### Module Independence
Each Dagster module is a separate Python package with:
- Its own source code (`src/{module}_dagster/`)
- Its own database (PostgreSQL or MySQL)
- Its own custom IO manager
- Its own deployment configuration

### Workspace Integration
Modules integrate with the main workspace via:
- `workspace/local/workspace.yaml` - Module entry
- `workspace/local/.env` - Environment variables
- `workspace/local/docker-compose.yml` - Database service
- `workspace/local/dockerfile.snippet` - Python dependencies

### Custom IO Managers
Every module uses a custom IO manager that:
- Stores outputs to `/tmp/dagster_storage/` (mounted volume)
- Ensures data persists across container restarts
- Prevents "file not found" errors in production

---

## 🛠️ Common Tasks

### Create a New Module
```bash
# Option 1: Use Claude Code skill (recommended)
# See CREATING-MODULES.md for details

# Option 2: Manual with templates
# See CREATING-MODULES.md for step-by-step guide
```

### Start Dagster Workspace
```bash
cd ~/workspace/services/dagster
docker compose up -d
```

### View Dagster UI
```
http://localhost:3000
```

### Check Module Status
```bash
docker logs workspace_dagster_webserver --tail 50
```

### Restart Services
```bash
cd ~/workspace/services/dagster
docker compose restart dagster_webserver dagster_daemon
```

---

## 📊 Current Modules

| Module | Description | Database | Status |
|--------|-------------|----------|--------|
| seo-stats | SEO statistics and analytics | PostgreSQL (5438) | ✅ Production |
| shopware-logs | Shopware log processing via SSH | MySQL (3307) | ✅ Production |
| dag-hello-world | Test/example module | PostgreSQL (5440) | ✅ Test only |

---

## 🤝 Contributing

When creating new modules:
1. Follow the standardized pattern (see MODULE-PATTERN.md)
2. Use the provided templates or Claude skill
3. Add comprehensive .gitignore (security!)
4. Create deployment guides
5. Test locally before deploying

---

## 📝 Notes

- **Docker Compose syntax**: Use `docker compose` (space) not `docker-compose` (hyphen)
- **Port allocation**: PostgreSQL uses 5438-5440+, MySQL uses 3306-3307+
- **Module paths**: All modules in `/workspace/projects/` not `/workspace/modules/`
- **Secrets**: Never commit `.env`, `.env.deploy`, or auth files to git

---

## 📞 Need Help?

1. Check **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for common issues
2. Review logs: `docker logs workspace_dagster_webserver`
3. Verify module loaded: Look for "Started Dagster code server for package..."

---

**Last Updated**: 2025-12-10
**Maintained By**: Mike Wattier <https://selltinfoil.com>
