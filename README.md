# StudentHub — Student Management System

A Windows desktop student-record management application built with Python, CustomTkinter and MySQL.

## Features
- Add, list, search, update and delete student records
- MySQL persistence
- Dashboard counts for students, courses and semesters
- Input validation and parameterized SQL queries

## Requirements
- Windows 10/11
- Python 3.10+
- MySQL Server 8+

## Setup
1. Install Python and MySQL Server.
2. Open Command Prompt in this folder and run:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. In MySQL Workbench, create the database and a dedicated app user:

```sql
CREATE DATABASE IF NOT EXISTS student_management;
CREATE USER 'studentapp'@'localhost' IDENTIFIED BY 'Choose-A-Strong-Password';
GRANT ALL PRIVILEGES ON student_management.* TO 'studentapp'@'localhost';
FLUSH PRIVILEGES;
```

4. Set connection variables in the same Command Prompt window (replace the example password):

```cmd
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=studentapp
set DB_PASSWORD=Choose-A-Strong-Password
set DB_NAME=student_management
python main.py
```

The app creates its students table on first connection. See `docs/INSTALLATION.md` for details.

## Security
Never commit real passwords, tokens, `.env` files, or real student records. Use a dedicated database user, not MySQL root.

## License
MIT — see [LICENSE](LICENSE).
