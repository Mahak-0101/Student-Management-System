# Windows Installation Guide

## 1. Install prerequisites
Install Python 3.10 or newer and MySQL Server 8.x. During Python setup, enable **Add Python to PATH**. Confirm the MySQL service is running.

## 2. Create database and app user
In MySQL Workbench, run the following SQL. Replace the example password with a strong password you choose:

```sql
CREATE DATABASE IF NOT EXISTS student_management;
CREATE USER 'studentapp'@'localhost' IDENTIFIED BY 'Choose-A-Strong-Password';
GRANT ALL PRIVILEGES ON student_management.* TO 'studentapp'@'localhost';
FLUSH PRIVILEGES;
```

## 3. Create a virtual environment
Open Command Prompt in the project directory:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Configure and launch
Set these variables in the same Command Prompt window, replacing the sample password:

```cmd
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=studentapp
set DB_PASSWORD=Choose-A-Strong-Password
set DB_NAME=student_management
python main.py
```

The variables set with `set` last only for that terminal session. Re-enter them in a new Command Prompt window. The application creates the `students` table automatically when it connects.

## Troubleshooting
- **Access denied:** verify the username/password and grants in MySQL.
- **Can't connect:** check that the MySQL service is running and the host/port are correct.
- **Missing Python module:** activate `.venv` and run `pip install -r requirements.txt` again.

Do not commit passwords, `.env` files, or real student information.
