# Production Deployment

**Production deployment concepts and best practices**

---

## 🎯 Overview

This document covers production deployment in the abstract. Each module includes its own specific `deploy/{environment}/DEPLOYMENT.md` with detailed instructions.

**Note:** Not all teams use the same production environment. This guide provides general concepts that apply to most deployments.

---

## 📋 Deployment Strategies

### Git Repository Checkout (Recommended)

**How it works:**
1. Module code lives in a git repository
2. Production server clones/pulls the repository
3. Docker rebuilds image with new code
4. Services restart to pick up changes

**Benefits:**
- ✅ Version controlled
- ✅ Easy rollbacks (git reset)
- ✅ Audit trail (git log)
- ✅ CI/CD integration

**Typical structure on production:**
```
/home/deploy/dagster/
├── modules/
│   ├── my-data-pipeline/    (git repo)
│   ├── customer-analytics/  (git repo)
│   └── crm-sync/            (git repo)
├── docker-compose.yml
├── Dockerfile
├── workspace.yaml
├── dagster.yaml
└── .env
```

---

### File Sync (Alternative)

**How it works:**
1. Copy files to production via scp/rsync
2. Docker rebuilds image
3. Services restart

**Benefits:**
- ✅ Simple
- ✅ No git required on production

**Drawbacks:**
- ❌ No version control on server
- ❌ Harder rollbacks
- ❌ No audit trail

---

## 🏗️ Production Architecture

### Typical Production Setup

```
Production Server
├── Dagster Services (Docker)
│   ├── dagster_webserver (UI)
│   ├── dagster_daemon (Schedules/Sensors)
│   └── dagster_metadata_postgres (Metadata DB)
│
├── Module Databases (Docker)
│   ├── module1_postgres
│   ├── module2_mysql
│   └── shared_customer_data_postgres
│
├── Network
│   └── Shared network (e.g., metabase_metanet1)
│       ├── Dagster services
│       ├── Module databases
│       └── Other services (Metabase, etc.)
│
└── Volumes
    ├── /data/postgres/... (database persistence)
    ├── /tmp/dagster_storage/ (IO manager storage)
    └── /auth/ (credentials, mounted read-only)
```

---

### Key Differences: Local vs Production

| Aspect | Local | Production |
|--------|-------|------------|
| **Paths** | `/workspace/projects/` | `/workspace/modules/` or `/opt/dagster/modules/` |
| **Ports** | Exposed (3000, 5437, etc.) | Internal only (within Docker network) |
| **Networks** | `workspace-net` (local) | `metabase_metanet1` (shared) or custom |
| **Secrets** | `.env` files | Environment variables or secret manager |
| **UI Access** | `localhost:3000` | Via reverse proxy or VPN |
| **Updates** | Manual rebuild | Git pull + rebuild or CI/CD |

---

## 🚀 Deployment Workflow

### Initial Module Deployment

**Steps:**

1. **Prepare Module for Deployment**
   ```bash
   cd ~/workspace/projects/your-module

   # Commit all changes
   git add .
   git commit -m "feat: initial production deployment"
   git push origin main
   ```

2. **On Production Server: Clone Repository**
   ```bash
   ssh deploy@production.server.com
   cd /home/deploy/dagster/modules
   git clone git@github.com:org/your-module.git
   ```

3. **Add Module to Production Configs**

   **workspace.yaml:**
   ```yaml
   - python_package:
       package_name: your_module_dagster
       working_directory: /workspace/modules/your-module/src
   ```

   **.env:**
   ```env
   YOUR_MODULE_DB_HOST=your_module_postgres
   YOUR_MODULE_DB_USER=your_module_user
   YOUR_MODULE_DB_PASSWORD=<secure_password>
   YOUR_MODULE_DB_NAME=your_module_db
   ```

   **docker-compose.yml:**
   ```yaml
   services:
     your_module_postgres:
       image: postgres:15
       # ... service config ...

     dagster_webserver:
       depends_on:
         your_module_postgres:
           condition: service_healthy
   ```

   **Dockerfile:**
   ```dockerfile
   RUN pip install --no-cache-dir \
       your-module-dependencies

   ENV PYTHONPATH="${PYTHONPATH}:/workspace/modules/your-module/src"
   ```

4. **Add Environment Variables to dagster.yaml**

   If using DockerRunLauncher or other run launchers:
   ```yaml
   run_launcher:
     module: dagster_docker
     class: DockerRunLauncher
     config:
       env_vars:
         - YOUR_MODULE_DB_HOST
         - YOUR_MODULE_DB_USER
         - YOUR_MODULE_DB_PASSWORD
         - YOUR_MODULE_DB_NAME
   ```

5. **Rebuild and Restart**
   ```bash
   cd /home/deploy/dagster
   docker compose build
   docker compose up -d
   ```

6. **Verify Deployment**
   ```bash
   # Check module loaded
   docker logs dagster_webserver 2>&1 | grep your_module

   # Should see:
   # Started Dagster code server for package your_module_dagster
   ```

---

### Regular Updates

**Quick deploy command:**
```bash
ssh deploy@production.server.com '\
  cd /home/deploy/dagster/modules/your-module && \
  git pull origin main && \
  cd /home/deploy/dagster && \
  docker compose up -d --no-deps dagster_webserver'
```

**What this does:**
1. SSH to production server
2. Navigate to module directory
3. Pull latest code from git
4. Rebuild only dagster_webserver (faster)
5. Restart webserver

**Note:** Full rebuild (`docker compose build`) only needed when dependencies change.

---

### Rollback Procedure

**If deployment fails:**

```bash
ssh deploy@production.server.com

# Navigate to module
cd /home/deploy/dagster/modules/your-module

# Check recent commits
git log --oneline -5

# Rollback to previous commit
git reset --hard HEAD~1

# Rebuild and restart
cd /home/deploy/dagster
docker compose up -d --no-deps dagster_webserver
```

---

## 🔐 Production Security

### Secrets Management

**❌ Bad:** Committing secrets to git
```env
# .env (committed to git - BAD!)
DB_PASSWORD=actual_password123
```

**✅ Good:** Using environment templates
```env
# .env.deploy.example (safe to commit)
DB_PASSWORD=CHANGE_THIS_IN_PRODUCTION
```

**✅ Better:** Using secret management tools
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Environment variables injected at runtime

### SSH Keys & Credentials

**Storage:**
- Store in `/workspace/auth/{module}/` on production
- Mount as read-only volume in containers
- Never commit to git
- Restrict file permissions (600)

**Example:**
```yaml
volumes:
  - /home/deploy/dagster/auth:/workspace/auth:ro
```

---

## 📊 Production Monitoring

### Health Checks

**Database health:**
```bash
# PostgreSQL
docker exec module_postgres pg_isready -U module_user

# MySQL
docker exec module_mysql mysqladmin ping -u module_user -p
```

**Service health:**
```bash
# Check containers running
docker ps | grep dagster

# Check logs for errors
docker logs dagster_webserver 2>&1 | grep -i error
docker logs dagster_daemon 2>&1 | grep -i error
```

### Logs

**Access logs:**
```bash
# Webserver logs
docker logs dagster_webserver --tail 100

# Daemon logs
docker logs dagster_daemon --tail 100

# Follow logs in real-time
docker logs -f dagster_daemon
```

### Dagster UI

**Access methods:**
- Reverse proxy (nginx/traefik)
- SSH tunnel: `ssh -L 3000:localhost:3000 deploy@production.server.com`
- VPN

---

## 🗄️ Database Management

### Backups

**PostgreSQL backup:**
```bash
# Backup single module database
docker exec module_postgres pg_dump -U module_user module_db > backup.sql

# Restore
docker exec -i module_postgres psql -U module_user module_db < backup.sql
```

**MySQL backup:**
```bash
# Backup
docker exec module_mysql mysqldump -u module_user -p module_db > backup.sql

# Restore
docker exec -i module_mysql mysql -u module_user -p module_db < backup.sql
```

### Database Migrations

**For schema changes:**
1. Test locally first
2. Backup production database
3. Apply migrations during maintenance window
4. Verify data integrity
5. Keep backup for rollback

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /home/deploy/dagster/modules/your-module
            git pull origin main
            cd /home/deploy/dagster
            docker compose up -d --no-deps dagster_webserver
```

---

## 📋 Pre-Deployment Checklist

Before deploying a module to production:

- [ ] Module tested thoroughly in local environment
- [ ] Custom IO manager tested (data persists across restarts)
- [ ] All dependencies listed in requirements.txt
- [ ] Environment variables documented in .env.deploy.example
- [ ] .gitignore comprehensive (no secrets committed)
- [ ] README.md complete with usage instructions
- [ ] DEPLOYMENT.md complete with deployment steps
- [ ] Database schema/migrations prepared (if applicable)
- [ ] Rollback procedure documented and tested
- [ ] Monitoring/alerts configured
- [ ] Team notified of deployment

---

## 🐛 Common Production Issues

### Module Not Loading

**Check:**
- PYTHONPATH includes module path
- workspace.yaml has correct entry
- Python dependencies installed
- No import errors in logs

### Database Connection Failed

**Check:**
- Database service running and healthy
- Environment variables correct
- Network connectivity
- Credentials valid

### IO Manager File Not Found

**Check:**
- `/tmp/dagster_storage` mounted in containers
- Directory permissions correct
- Volume persists across restarts

### Schedule Not Running

**Check:**
- dagster_daemon container running
- Schedules enabled in Dagster UI
- Timezone configuration correct
- No errors in daemon logs

---

## 📞 Production Support

### Useful Commands

```bash
# Check all services
docker ps

# Restart specific service
docker compose restart dagster_webserver

# View service logs
docker compose logs dagster_webserver

# Execute command in container
docker exec dagster_webserver dagster instance info

# Check disk usage
df -h

# Check memory usage
free -h
```

---

## 🎯 Best Practices

1. **Always test locally first** - Never deploy untested code
2. **Use git tags for releases** - Makes rollbacks easier
3. **Deploy during low-traffic periods** - Minimize impact
4. **Monitor after deployment** - Watch for errors
5. **Have rollback ready** - Know how to undo changes
6. **Document everything** - Future you will thank you
7. **Backup before major changes** - Databases and configs
8. **Use staging environment** - Test production-like setup

---

## 📚 Module-Specific Guides

Each module includes its own detailed deployment guide:
- `~/workspace/projects/{module}/deploy/production/DEPLOYMENT.md`

These guides include:
- Exact commands for that module
- Module-specific configuration
- Known issues and solutions
- Module owner contact info

---

**Last Updated**: 2025-12-10
