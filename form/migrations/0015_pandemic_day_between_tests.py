# Generated by Django 3.2.7 on 2022-04-20 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0014_auto_20220312_0136'),
    ]

    operations = [
        migrations.AddField(
            model_name='pandemic',
            name='day_between_tests',
            field=models.IntegerField(default=5),
        ),
    ]