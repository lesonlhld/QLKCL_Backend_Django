# Generated by Django 3.2.7 on 2022-01-30 17:26

from django.db import migrations
from utils.enums import MemberQuarantinedStatus, CustomUserStatus

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Member = apps.get_model("user_account", "Member")
    db_alias = schema_editor.connection.alias
    members = Member.objects.using(db_alias).filter(quarantined_status=MemberQuarantinedStatus.COMPLETED, quarantine_room__isnull=True)
    for member in list(members):
        custom_user = member.custom_user
        custom_user.status = CustomUserStatus.LEAVE
        custom_user.save()

def reverse_func(apps, schema_editor):
    ...

class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0034_alter_customuser_status'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
