# Troubleshooting Guide

**Solutions to common Dagster workspace issues**

---

## 🔍 Quick Diagnostics

### Check System Status

```bash
# All services running?
docker ps --format "table {{.Names}}\t{{.Status}}"

# Recent logs
docker logs workspace_dagster_webserver --tail 50

# Check for errors
docker logs workspace_dagster_webserver 2>&1 | grep -i error
```

### Verify Configuration

```bash
# Check workspace.yaml
cat ~/workspace/services/dagster/workspace.yaml

# Check environment variables
docker exec workspace_dagster_webserver printenv | grep -E "(DB|DAGSTER)"

# Check PYTHONPATH
docker exec workspace_dagster_webserver printenv PYTHONPATH
```

---

## 🚨 Common Issues

### Issue: "Cannot connect to Docker daemon"

**Symptoms:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solutions:**

1. **Start Docker service:**
   ```bash
   # Linux
   sudo systemctl start docker

   # macOS
   open -a Docker

   # Verify
   docker ps
   ```

2. **Check Docker is installed:**
   ```bash
   docker --version
   ```

3. **Check user has Docker permissions:**
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER

   # Log out and back in for changes to take effect
   ```

---

### Issue: Port Already in Use

**Symptoms:**
```
Error: Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Solutions:**

1. **Find what's using the port:**
   ```bash
   # Linux/macOS
   lsof -i :3000

   # Or
   netstat -tulpn | grep 3000
   ```

2. **Kill the process:**
   ```bash
   # Replace PID with actual process ID
   kill -9 PID
   ```

3. **Or use a different port:**
   ```bash
   # Edit ~/workspace/services/dagster/.env
   echo "DAGSTER_WEBSERVER_PORT=3001" >> .env

   # Update docker-compose.yml ports section
   # ports:
   #   - "3001:3000"
   ```

---

### Issue: Module Not Appearing in UI

**Symptoms:**
- Dagster UI loads but module doesn't appear
- "No code locations found" message

**Diagnosis:**
```bash
# Check if module loaded
docker logs workspace_dagster_webserver 2>&1 | grep "your_module"

# Should see: "Started Dagster code server for package your_module_dagster"
```

**Solutions:**

1. **Check workspace.yaml has module entry:**
   ```bash
   docker exec workspace_dagster_webserver cat /opt/dagster/dagster_home/workspace.yaml
   ```

   Should contain:
   ```yaml
   - python_package:
       package_name: your_module_dagster
       working_directory: /workspace/projects/your-module/src
   ```

2. **Check PYTHONPATH includes module:**
   ```bash
   docker exec workspace_dagster_webserver printenv PYTHONPATH
   ```

   Should contain: `/workspace/projects/your-module/src`

3. **Check module directory exists:**
   ```bash
   docker exec workspace_dagster_webserver ls -la /workspace/projects/your-module/src
   ```

4. **Check for import errors:**
   ```bash
   docker logs workspace_dagster_webserver 2>&1 | grep -i "import\|error"
   ```

5. **Rebuild and restart:**
   ```bash
   cd ~/workspace/services/dagster
   docker compose build
   docker compose up -d
   ```

---

### Issue: Database Connection Failed

**Symptoms:**
```
OperationalError: could not connect to server: Connection refused
```

**Solutions:**

1. **Check database container is running:**
   ```bash
   docker ps | grep postgres
   ```

2. **Check database health:**
   ```bash
   docker exec your_module_postgres pg_isready -U your_module_user
   ```

3. **Check environment variables:**
   ```bash
   docker exec workspace_dagster_webserver printenv | grep "YOUR_MODULE_DB"
   ```

4. **Check database service in depends_on:**
   ```bash
   grep -A 5 "depends_on:" ~/workspace/services/dagster/docker-compose.yml
   ```

   Should include:
   ```yaml
   depends_on:
     your_module_postgres:
       condition: service_healthy
   ```

5. **Recreate database:**
   ```bash
   cd ~/workspace/services/dagster
   docker compose down
   docker volume rm workspace_your_module_postgres_data
   docker compose up -d
   ```

---

### Issue: IO Manager "File Not Found"

**Symptoms:**
```
FileNotFoundError: No stored data found at /tmp/dagster_storage/asset_name.pickle
```

**Solutions:**

1. **Check /tmp/dagster_storage is mounted:**
   ```bash
   docker inspect workspace_dagster_webserver | grep /tmp/dagster_storage
   ```

   Should show:
   ```json
   "/tmp/dagster_storage:/tmp/dagster_storage"
   ```

2. **Check directory exists and has data:**
   ```bash
   ls -la /tmp/dagster_storage/
   ```

3. **Materialize the upstream asset first:**
   - Go to Dagster UI
   - Find the upstream asset
   - Click "Materialize"
   - Then materialize the downstream asset

4. **Check IO manager configuration:**
   ```python
   # In resources.py
   @io_manager
   def your_module_io_manager():
       storage_path = os.environ.get('DAGSTER_STORAGE_PATH', '/tmp/dagster_storage')
       return YourModuleIOManager(base_path=storage_path)
   ```

---

### Issue: "docker compose: command not found"

**Symptoms:**
```
bash: docker compose: command not found
```

**Solution:**

You're using the old `docker-compose` (hyphen) command. This workspace requires Docker Compose v2+ which uses `docker compose` (space).

**Update Docker Compose:**
```bash
# Check current version
docker compose version

# If not installed or old version:
# Linux
sudo apt-get update
sudo apt-get install docker-compose-plugin

# macOS
# Update Docker Desktop to latest version

# Verify
docker compose version
# Should show v2.x.x or later
```

---

### Issue: Assets Not Materializing

**Symptoms:**
- Click "Materialize" but nothing happens
- Run stays in "STARTED" state forever

**Solutions:**

1. **Check dagster_daemon is running:**
   ```bash
   docker ps | grep daemon
   ```

2. **Check daemon logs:**
   ```bash
   docker logs workspace_dagster_daemon --tail 50
   ```

3. **Restart daemon:**
   ```bash
   docker compose restart dagster_daemon
   ```

4. **Check run launcher config in dagster.yaml:**
   ```bash
   cat ~/workspace/services/dagster/dagster.yaml | grep -A 5 "run_launcher"
   ```

5. **Check available resources:**
   ```bash
   # Memory
   free -h

   # Disk space
   df -h
   ```

---

### Issue: Builds Are Slow

**Symptoms:**
- `docker compose build` takes 5+ minutes
- Frequent rebuilds needed

**Solutions:**

1. **Use Docker BuildKit:**
   ```bash
   export DOCKER_BUILDKIT=1
   docker compose build
   ```

2. **Check for unnecessary files in build context:**
   ```bash
   # Create .dockerignore
   cat > ~/workspace/services/dagster/.dockerignore << 'EOF'
   **/__pycache__
   **/*.pyc
   **/.git
   **/data
   **/.vscode
   EOF
   ```

3. **Use layer caching:**
   - Don't change Dockerfile frequently
   - Put pip installs before code copies
   - Use multi-stage builds if needed

---

### Issue: Changes Not Reflecting in UI

**Symptoms:**
- Made code changes but UI shows old code
- Assets not updated

**Solutions:**

1. **Code changes require rebuild:**
   ```bash
   cd ~/workspace/services/dagster
   docker compose build
   docker compose up -d
   ```

2. **For asset definition changes (no rebuild needed):**
   ```bash
   # Just restart
   docker compose restart dagster_webserver dagster_daemon
   ```

3. **Force full reload:**
   ```bash
   docker compose down
   docker compose up -d
   ```

4. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (macOS)

---

### Issue: Logs Are Too Verbose

**Symptoms:**
- Too many log messages
- Hard to find relevant information

**Solutions:**

1. **Filter logs by keyword:**
   ```bash
   docker logs workspace_dagster_webserver 2>&1 | grep "your_module"
   ```

2. **Show only errors:**
   ```bash
   docker logs workspace_dagster_webserver 2>&1 | grep -i error
   ```

3. **Tail recent logs:**
   ```bash
   docker logs workspace_dagster_webserver --tail 50
   ```

4. **Set log level in code:**
   ```python
   # In your assets
   context.log.set_level(logging.WARNING)
   ```

---

### Issue: Permission Denied Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/tmp/dagster_storage/asset.pickle'
```

**Solutions:**

1. **Check directory permissions:**
   ```bash
   ls -ld /tmp/dagster_storage
   chmod 777 /tmp/dagster_storage
   ```

2. **Check file ownership:**
   ```bash
   ls -la /tmp/dagster_storage/
   chown -R 1000:1000 /tmp/dagster_storage/
   ```

3. **In Dockerfile, ensure dagster user has access:**
   ```dockerfile
   RUN mkdir -p /tmp/dagster_storage && \
       chown -R dagster:dagster /tmp/dagster_storage
   ```

---

### Issue: Schedules Not Running

**Symptoms:**
- Schedule defined but not executing
- No scheduled runs appearing

**Solutions:**

1. **Check dagster_daemon is running:**
   ```bash
   docker ps | grep daemon
   ```

2. **Check schedule is turned ON in UI:**
   - Go to Dagster UI → Overview
   - Find your schedule
   - Toggle switch to ON

3. **Check daemon logs:**
   ```bash
   docker logs workspace_dagster_daemon | grep schedule
   ```

4. **Verify schedule definition:**
   ```python
   from dagster import schedule, RunRequest

   @schedule(
       cron_schedule="0 9 * * *",  # 9 AM daily
       job=your_job,
   )
   def daily_schedule():
       return RunRequest()
   ```

5. **Check timezone:**
   ```bash
   # In Dockerfile
   ENV TZ=America/New_York
   ```

---

## 🔧 Advanced Troubleshooting

### Enable Debug Mode

**In dagster.yaml:**
```yaml
python_logs:
  python_log_level: DEBUG
  dagster_handler_log_level: DEBUG
```

Rebuild and restart to see more detailed logs.

---

### Interactive Debugging

**Enter container:**
```bash
docker exec -it workspace_dagster_webserver bash
```

**Test Python imports:**
```bash
python3 -c "from your_module_dagster import defs; print(defs)"
```

**Check installed packages:**
```bash
pip list | grep your-package
```

---

### Database Inspection

**PostgreSQL:**
```bash
# Enter database
docker exec -it module_postgres psql -U module_user -d module_db

# List tables
\dt

# Query data
SELECT * FROM your_table LIMIT 10;

# Exit
\q
```

**MySQL:**
```bash
# Enter database
docker exec -it module_mysql mysql -u module_user -p module_db

# Show tables
SHOW TABLES;

# Query data
SELECT * FROM your_table LIMIT 10;

# Exit
exit
```

---

### Complete Reset

**If all else fails:**

```bash
cd ~/workspace/services/dagster

# Stop everything
docker compose down

# Remove volumes (WARNING: Deletes data!)
docker compose down -v

# Remove images
docker rmi workspace-dagster:latest

# Clean up
docker system prune -a

# Start fresh
docker compose build
docker compose up -d
```

**Note:** This deletes all data. Backup first if needed!

---

## 📚 Useful Resources

### Docker Commands Reference

```bash
# List containers
docker ps

# List all containers (including stopped)
docker ps -a

# View logs
docker logs <container_name>

# Follow logs in real-time
docker logs -f <container_name>

# Execute command in container
docker exec -it <container_name> bash

# Inspect container
docker inspect <container_name>

# Container resource usage
docker stats

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune
```

### Docker Compose Commands Reference

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Rebuild services
docker compose build

# Restart specific service
docker compose restart <service_name>

# View logs
docker compose logs

# Follow logs
docker compose logs -f

# Scale services
docker compose up -d --scale dagster_webserver=2

# Remove volumes
docker compose down -v
```

---

## 🐛 Still Having Issues?

### Collect Information

Before asking for help, collect this information:

1. **Error message** (full text)
2. **Logs:**
   ```bash
   docker logs workspace_dagster_webserver > webserver.log
   docker logs workspace_dagster_daemon > daemon.log
   ```
3. **Configuration:**
   ```bash
   cat ~/workspace/services/dagster/workspace.yaml
   docker compose config
   ```
4. **System info:**
   ```bash
   docker version
   docker compose version
   uname -a
   ```

### Check Existing Modules

Look at working examples:
- `~/workspace/projects/seo-stats/`
- `~/workspace/projects/shopware-logs/`
- `~/workspace/projects/beast-hubspot/`
- `~/workspace/projects/dag-hello-world/`

Compare your module structure to these.

---

## 📞 Getting Help

1. **Review documentation:**
   - [MODULE-PATTERN.md](MODULE-PATTERN.md)
   - [CREATING-MODULES.md](CREATING-MODULES.md)
   - [PRODUCTION-DEPLOYMENT.md](PRODUCTION-DEPLOYMENT.md)

2. **Check module-specific docs:**
   - `{module}/README.md`
   - `{module}/deploy/production/DEPLOYMENT.md`

3. **Search Dagster documentation:**
   - https://docs.dagster.io/

4. **Ask your team:**
   - Share error logs
   - Describe what you tried
   - Provide system information

---

**Last Updated**: 2025-12-10
