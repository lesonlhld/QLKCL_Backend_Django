echo "Starting server........................................."

@REM django-admin startproject qlkcl
@REM django-admin startapp api

python manage.py runserver

@REM python manage.py makemigrations
@REM python manage.py migrate

@REM python manage.py createsuperuser

@REM echo "web: gunicorn qlkcl.wsgi --log-file -" >> Procfile
@REM pip freeze > requirements.txt
@REM pip install -r requirements.txt

@REM heroku addons:create heroku-postgresql:hobby-dev
@REM heroku logs --tail
@REM git push heroku master
@REM heroku run python manage.py migrate
@REM heroku git:remote -a qlkcl
@REM heroku run bash


@REM pip install virtualenv
@REM virtualenv env
@REM env\Scripts\activate
@REM deactivate