# Generated by Django 3.2.7 on 2022-03-12 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0014_auto_20220312_0136'),
        ('quarantine_ward', '0004_quarantineward_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='quarantineward',
            name='pandemic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quarantine_ward_x_pandemic', to='form.pandemic'),
        ),
    ]