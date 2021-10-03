echo "Starting server........................................."

@REM django-admin startproject qlkcl

python manage.py runserver

@REM python manage.py migrate

@REM python manage.py createsuperuser

@REM nano Procfile
@REM pip install django gunicorn
@REM pip install django psycopg2 dj-database-url
@REM pip freeze > requirements.txt

@REM heroku addons:create heroku-postgresql:hobby-dev
@REM heroku logs --tail
@REM git push heroku master
@REM heroku run python manage.py migrate