# Generated by Django 3.2.7 on 2022-01-02 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0008_auto_20220103_0022'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicaldeclaration',
            name='code',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
