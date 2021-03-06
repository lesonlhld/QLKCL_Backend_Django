# Generated by Django 3.2.7 on 2022-01-05 16:47

from django.db import migrations
from datetime import datetime
import pytz

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Member = apps.get_model("user_account", "Member")
    db_alias = schema_editor.connection.alias
    members = Member.objects.using(db_alias).all()
    vntz = pytz.timezone('Asia/Saigon')
    for member in members:
        if member.quarantined_at:
            new_time = datetime.strptime(member.quarantined_at + ' 7', '%d/%m/%Y %I')
            new_time = new_time.astimezone(vntz)
            member.new_quarantined_at = new_time
        if member.quarantined_finished_at:
            new_finish_time = datetime.strptime(member.quarantined_finished_at + ' 7', '%d/%m/%Y %I')
            new_finish_time = new_finish_time.astimezone(vntz)
            member.new_quarantined_finished_at = new_finish_time
        member.save()

def reverse_func(apps, schema_editor):
    ...

class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0025_auto_20220105_2342'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
