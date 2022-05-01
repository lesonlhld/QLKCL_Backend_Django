#========================================
# Scheduler Jobs
#========================================

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qlkcl.settings")

import django
django.setup()

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from user_account.views import send_notification_is_last_test

scheduler = BlockingScheduler()

vntz = pytz.timezone('Asia/Saigon')

scheduler.configure(timezone=vntz)

scheduler.add_job(send_notification_is_last_test, 'cron', hour=1, minute=30)
scheduler.start()