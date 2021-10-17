# QLKCL Project (Backend)

QLKCL Backend


## Version info
Postgresql 13.3
Django 3.2.7
Python 3.9.5

## Create database
```
CREATE USER horus_dev SUPERUSER;

ALTER USER horus_dev WITH PASSWORD 'password';

CREATE DATABASE osn_dev WITH OWNER horus_dev;
```

or create by hand

## Install Virtual environment
```
py -m venv venv
```

## Activate the virtual environment
```
venv/Scripts/activate
```

## Install libraries
```
pip install -r requirements.txt
```

## Run development server
Make sure that virtual environment is activated, in `QLKCL_Backend_Django` directory:

```
py manage.py runserver
```

## Backup database
```
py manage.py dumpdata --indent 2 > initial_database.json
```

## Restore database
```
py manage.py loaddata initial_database.json
```

# Default admin account
Go to: http://localhost:8000/admin
Login with credentials
```
username:
password:
```
