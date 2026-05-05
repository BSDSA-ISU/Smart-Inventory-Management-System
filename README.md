# Athlete Nutritional & Training Recovery Dashboard

> Group 6, now supports both mariadb and mysql

official System logo:

![alt text](./Kaguya.gif)

[ngrok mirror](https://modern-blowfish-virtually.ngrok-free.app)

## Members

- Bazar, Cyrus Troy C. [(AlieeLinux)](https://github.com/alieelinux)
- Serrano Joshua
- Imperial Jl
- Salamatin

## 💯 Progressions

- title: ✅
- Project Description: Okayish ✅❓
- Objective of the system: Okayish ✅❓
- Business Rule: Planning ❌
- Entity relationship diagram: Semi done ❌
- Normalization summary: Undone ❌
- System Features: Planning ❌

---

**table of contents:**

- [Athlete Nutritional \& Training Recovery Dashboard](#athlete-nutritional--training-recovery-dashboard)
  - [Members](#members)
  - [💯 Progressions](#-progressions)
  - [📌 Introduction](#-introduction)
  - [📖 Project Description](#-project-description)
  - [🎯 Objective of the System](#-objective-of-the-system)
  - [⬇️ Installation](#️-installation)
    - [📦 Install MariaDB or Mysql](#-install-mariadb-or-mysql)
  - [🚀 Start the Database Server](#-start-the-database-server)
    - [🪟 Windows](#-windows)
      - [🧩 Option 1: Services (Recommended)](#-option-1-services-recommended)
      - [💻 Option 2: Command Line](#-option-2-command-line)
      - [🧰 Option 3: XAMPP](#-option-3-xampp)
    - [🐧 Linux (systemd)](#-linux-systemd)
  - [👤 Setup Database User](#-setup-database-user)
    - [🐬 MariaDB](#-mariadb)
    - [🐬 MySQL](#-mysql)
  - [🔧 Configure Environment Variables](#-configure-environment-variables)
  - [🔧 Running the app.py](#-running-the-apppy)
    - [❌ if getting an library errros during uv sync](#-if-getting-an-library-errros-during-uv-sync)
  - [⚠️ Notes](#️-notes)

## 📌 Introduction

Athlete Nutritional & Training Recovery Dashboard is a lightweight and efficient monitoring designed for athletes to track their health and stuffs

This project reflects a preference for performance, transparency, and control, inspired by Linux-based workflows and terminal.

---

## 📖 Project Description

The Athlete Nutritional & Training Recovery Dashboard is a database-driven application that allows students and administrators to:

- Monitor Nutrition logs
- training_sessions
- recovery_logs
- recovery_logs

It is designed to be simple, fast, and practical—no unnecessary garbage features.

## 🎯 Objective of the System

- Centralized Athlete Data Management
- Support for CRUD Operations
- Data Organization Through Relational Database Design
- Performance and Health Monitoring
- Data-Driven Insights Generation
- User-Friendly Command-Line Interface and web app interface
- Foundation for Future Expansion

## ⬇️ Installation

### 📦 Install MariaDB or Mysql

Download and install MariaDB from the official site:

- 🔗 [https://mariadb.org/download/](https://mariadb.org/download/)
- 🔗 [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
- 🔗 [https://www.apachefriends.org/](https://www.apachefriends.org/)

---

## 🚀 Start the Database Server

### 🪟 Windows

#### 🧩 Option 1: Services (Recommended)

- Press **Win + R**
- Type:

  ```ps1
  services.msc
  ```

- Find:
  - `MariaDB` or `MySQL`
- Right-click → **Start**

---

#### 💻 Option 2: Command Line

Run in **Command Prompt (Admin)** or PowerShell:

```powershell
net start mysql
```

---

#### 🧰 Option 3: XAMPP

- Use XAMPP Control Panel
- Start **MySQL Module**

---

### 🐧 Linux (systemd)

Start MariaDB:

```bash
sudo systemctl start mariadb
```

Enable auto-start on boot:

```bash
sudo systemctl enable --now mariadb
```

---

## 👤 Setup Database User

### 🐬 MariaDB

Enter MariaDB shell:

```bash
sudo mariadb -u root
```

Then run:

```sql
CREATE DATABASE athlete_dashboard;

CREATE USER 'athlete_user'@'localhost' IDENTIFIED BY 'your_password_here';

GRANT ALL PRIVILEGES ON athlete_dashboard.* TO 'athlete_user'@'localhost';

FLUSH PRIVILEGES;
```

---

### 🐬 MySQL

Enter MySQL shell:

```bash
sudo mysql -u root -p
```

> (Or open it via XAMPP if you're using that)

Then run:

```sql
CREATE DATABASE athlete_dashboard;

CREATE USER 'athlete_user'@'localhost' IDENTIFIED BY 'your_password_here';

GRANT ALL PRIVILEGES ON athlete_dashboard.* TO 'athlete_user'@'localhost';

FLUSH PRIVILEGES;
```

---

## 🔧 Configure Environment Variables

Edit your `.env` file:

```env
DB_SERVER=localhost
DB_USER=athlete_user
DB_PASSWORD=yourpassword
DB_DATABASE=athlete_dashboard
DB_PORT=6969
```

## 🔧 Running the app.py

**Via uv(most recommended both windows and linux):**

```ps1
# if first time running:
uv run Firstrun.py

# install dependencies
uv sync

# Runit
uv run app.py

# With Gunicorn if ready
uv run gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

*Copy the site paste it in your browser and enjoy!!*

![alt text](image.png)

### ❌ if getting an library errros during uv sync

**You may need to install this dependencies if encountered an error:**

- libmariadb-dev
- build-essential
- mariadb-libs
- python3-dev

---

## ⚠️ Notes

- Do NOT use `root` for your Flask app (unless you enjoy chaos)
- MariaDB and MySQL use almost identical SQL syntax
- Port `5000` is the default for flask
- Python app uses **PyMySQL**, so it works with both servers

![Kaguya](https://media1.tenor.com/m/klBPU9I_898AAAAC/mokou-kaguya.gif)
