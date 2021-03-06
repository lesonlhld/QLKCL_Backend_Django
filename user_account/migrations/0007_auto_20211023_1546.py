# Generated by Django 3.2.7 on 2021-10-23 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0006_auto_20211023_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='passport_number',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='other_background_disease',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='quarantined_at',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
