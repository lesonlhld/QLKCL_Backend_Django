# Generated by Django 3.2.7 on 2022-01-26 03:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('form', '0011_alter_medicaldeclaration_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vaccine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('manufacturer', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='VaccineDose',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('injection_date', models.DateTimeField(blank=True, null=True)),
                ('injection_place', models.TextField(blank=True, null=True)),
                ('batch_number', models.CharField(blank=True, max_length=64, null=True)),
                ('symptom_after_injected', models.CharField(blank=True, max_length=256, null=True)),
                ('custom_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vaccine_dose_x_custom_user', to=settings.AUTH_USER_MODEL)),
                ('vaccine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vaccine_dose_x_vaccine', to='form.vaccine')),
            ],
        ),
    ]
