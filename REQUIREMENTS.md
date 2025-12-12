# Requirements

**Prerequisites for setting up and using the Dagster workspace**

---

## 🔧 Required Tools

### 1. Docker & Docker Compose
**Required for running Dagster and databases**

- Docker Engine (latest stable)
- Docker Compose v2+ (uses `docker compose` not `docker-compose`)

**Install:**
- **Ubuntu/Debian**: [Docker Install Guide](https://docs.docker.com/engine/install/ubuntu/)
- **macOS**: [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)

**Verify:**
```bash
docker --version
# Docker version 24.0.0 or later

docker compose version
# Docker Compose version v2.20.0 or later
```

---

### 2. Git
**Required for version control**

- Git 2.0+

**Install:**
```bash
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/
```

**Verify:**
```bash
git --version
# git version 2.x.x
```

---

### 3. SSH Client
**Required for modules that fetch remote data (e.g., shopware-logs)**

- OpenSSH client

**Install:**
```bash
# Ubuntu/Debian
sudo apt-get install openssh-client

# macOS (pre-installed)
# Windows 10+ (pre-installed)
```

**Verify:**
```bash
ssh -V
# OpenSSH_8.x or later
```

---

### 4. Python 3.10+
**Required for local development and testing**

- Python 3.10 or later
- pip (Python package manager)

**Install:**
```bash
# Ubuntu/Debian
sudo apt-get install python3.10 python3-pip

# macOS
brew install python@3.10

# Windows
# Download from https://www.python.org/
```

**Verify:**
```bash
python3 --version
# Python 3.10.x or later

pip3 --version
# pip 23.x or later
```

---

### 5. Claude Code (Optional but Recommended)
**Recommended for automated module creation using the skill**

Claude Code CLI tool by Anthropic

**Install:**
Follow instructions at: [Claude Code Setup](https://github.com/anthropics/claude-code)

**Verify:**
```bash
claude --version
# claude-code x.x.x
```

**Note:** After cloning this repository, install the Claude Code skill from the `skill/` directory. See [skill/INSTALL.md](skill/INSTALL.md) for installation instructions.

---

## 💾 System Requirements

### Minimum
- **RAM**: 8 GB (16 GB recommended)
- **Disk**: 20 GB free space
- **CPU**: 2 cores (4 cores recommended)

### Recommended
- **RAM**: 16 GB or more
- **Disk**: 50 GB free space (for database growth)
- **CPU**: 4 cores or more

---

## 🌐 Network Requirements

### Ports Used
The following ports must be available on your local machine:

**Dagster Services:**
- `3000` - Dagster webserver UI
- `3001` - Dagster daemon (internal)
- `5437` - Dagster metadata PostgreSQL

**Module Databases:**
- `5438` - seo-stats PostgreSQL
- `5439` - customer_data PostgreSQL (shared by beast-hubspot)
- `5440` - dag-hello-world PostgreSQL
- `3307` - shopware-logs MySQL

**Future Modules:**
- `5441+` - Additional PostgreSQL databases
- `3308+` - Additional MySQL databases

---

## 📦 Development Tools (Optional)

### Recommended for Module Development

**Text Editor / IDE:**
- VS Code (recommended)
- PyCharm
- Vim/Neovim

**Database Clients:**
- DBeaver (multi-database)
- pgAdmin (PostgreSQL)
- MySQL Workbench (MySQL)

**Terminal:**
- iTerm2 (macOS)
- Windows Terminal (Windows)
- Terminator (Linux)

---

## 🔐 Credentials & Access

### Required Access

Depending on which modules you're working with:

**For seo-stats:**
- Google Analytics 4 property access
- Google Cloud credentials for GA4 API

**For shopware-logs:**
- SSH access to Shopware remote server
- SSH key for authentication

**For beast-hubspot:**
- HubSpot Private App access token
- HubSpot account with appropriate permissions

---

## 📁 Directory Structure

You'll need a workspace directory structure:

```bash
~/workspace/
├── services/dagster/     # Will be set up during SETUP.md
├── projects/             # Your Dagster modules
├── patterns/dagster/     # Templates (copied from this repo's templates/ directory)
├── data/                 # Database volumes (created automatically)
└── auth/                 # Credentials (you provide)
```

**Note:** Most directories will be created during setup. You only need to ensure `~/workspace/` exists. This documentation repository can be cloned anywhere - it doesn't need to be in `~/workspace/`.

---

## ✅ Pre-Setup Checklist

Before proceeding to [SETUP.md](SETUP.md), verify you have:

- [ ] Docker & Docker Compose installed and running
- [ ] Git installed
- [ ] SSH client available (if needed)
- [ ] Python 3.10+ installed
- [ ] Claude Code installed (optional)
- [ ] Ports 3000, 5437-5440, 3307 available
- [ ] At least 20 GB free disk space
- [ ] `~/workspace/` directory exists or can be created

---

## 🚀 Next Steps

Once you have all requirements met:

**→ Continue to [SETUP.md](SETUP.md)** to set up your local Dagster workspace

---

**Last Updated**: 2025-12-10
