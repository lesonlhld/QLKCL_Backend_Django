# Generated by Django 3.2.7 on 2022-01-17 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quarantine_ward', '0003_alter_quarantineward_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='quarantineward',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
    ]
