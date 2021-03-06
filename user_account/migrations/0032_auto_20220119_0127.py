# Generated by Django 3.2.7 on 2022-01-18 18:27

from django.db import migrations
from utils.enums import CustomUserStatus

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    CustomUser = apps.get_model("user_account", "CustomUser")
    db_alias = schema_editor.connection.alias
    users = CustomUser.objects.using(db_alias).filter(status=CustomUserStatus.REFUSED, member_x_custom_user__quarantine_room__isnull=False)
    for user in list(users):
        if hasattr(user, 'member_x_custom_user'):
            member = user.member_x_custom_user
            member.quarantine_room = None
            member.save()

def reverse_func(apps, schema_editor):
    ...

class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0031_remove_member_abroad'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
