# Generated by Django 3.2.7 on 2022-01-07 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0028_auto_20220106_0027'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='positive_test',
            new_name='positive_test_now',
        ),
    ]
