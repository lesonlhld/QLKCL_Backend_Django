# QLKCL Project (Backend)
Branch `Staging` được tự động deploy khi mỗi có commit mới vào branch này.

Deploy tại https://qlkcl.herokuapp.com/

QLKCL Backend


## Version info
* Postgresql 13.3
* Django 3.2.7
* Python 3.9.5

## Create database
```
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

# Authors
1. [Lê Trung Sơn](https://github.com/lesonlhld)
2. [Châu Thanh Tân](https://github.com/cttan2000)
3. [Nguyễn Bá Tiến](https://github.com/batiencd09)
4. [Trương Ngọc Minh Châu](https://github.com/chauandvi4) (Contribute the system in the first stage)
