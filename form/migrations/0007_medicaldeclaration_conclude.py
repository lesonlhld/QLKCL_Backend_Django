# Generated by Django 3.2.7 on 2021-11-17 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0006_alter_test_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicaldeclaration',
            name='conclude',
            field=models.CharField(choices=[('NORMAL', 'Normal'), ('UNWELL', 'Unwell'), ('SERIOUS', 'Serious')], default='NORMAL', max_length=32),
        ),
    ]
