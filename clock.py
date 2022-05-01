#========================================
# Scheduler Jobs
#========================================

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qlkcl.settings")

import django
django.setup()

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from user_account.views import send_notification_is_last_test

scheduler = BackgroundScheduler()

vntz = pytz.timezone('Asia/Saigon')

scheduler.configure(timezone=vntz)

scheduler.add_job(send_notification_is_last_test, 'cron', hour=2, minute=50)
scheduler.start()