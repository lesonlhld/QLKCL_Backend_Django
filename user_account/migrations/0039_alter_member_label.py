# Generated by Django 3.2.7 on 2022-02-18 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0038_auto_20220211_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='label',
            field=models.CharField(choices=[('F0', 'F0'), ('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3'), ('FROM_EPIDEMIC_AREA', 'From Epidemic Area'), ('ABROAD', 'Abroad')], default='F1', max_length=32),
        ),
    ]
