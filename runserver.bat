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
@REM heroku pg:psql -a <application_name>
@REM \encoding UTF8
@REM \copy address_city FROM 'C:\Users\leson\Downloads\city.csv' (format csv, header true, delimiter ',', encoding 'UTF8');


@REM pip install virtualenv
@REM virtualenv env
@REM env\Scripts\activate
@REM deactivate
