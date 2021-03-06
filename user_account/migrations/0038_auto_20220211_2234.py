# Generated by Django 3.2.7 on 2022-02-11 15:34

import datetime
from django.db import migrations

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Member = apps.get_model("user_account", "Member")
    db_alias = schema_editor.connection.alias
    members = Member.objects.using(db_alias).filter(quarantined_at__isnull=False)
    for member in list(members):
        number_of_days = int(member.custom_user.quarantine_ward.quarantine_time)
        member.quarantined_finish_expected_at = member.quarantined_at + datetime.timedelta(days=number_of_days)
        member.save()

def reverse_func(apps, schema_editor):
    ...

class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0037_member_quarantined_finish_expected_at'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
