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

def test_func():
    print('oke schedule')

# scheduler.add_job(send_notification_is_last_test, 'cron', hour=2, minute=50)
scheduler.add_job(test_func, 'interval', seconds=10)
scheduler.start()