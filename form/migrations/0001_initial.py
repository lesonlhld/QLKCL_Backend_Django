# Generated by Django 3.2.7 on 2021-10-22 09:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BackgroundDisease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('trash', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Symptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('type', models.CharField(choices=[('MAIN', 'Main'), ('EXTRA', 'Extra')], default='MAIN', max_length=16)),
                ('trash', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, unique=True)),
                ('status', models.CharField(choices=[('WAITING', 'Waiting'), ('DONE', 'Done')], default='WAITING', max_length=16)),
                ('result', models.CharField(choices=[('NEGATIVE', 'Negative'), ('POSITIVE', 'Positive')], default='NEGATIVE', max_length=16)),
                ('type', models.CharField(choices=[('QUICK', 'Quick'), ('RT-PCR', 'Rt Pcr')], default='QUICK', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='test_x_created_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='test_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MedicalDeclaration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heartbeat', models.IntegerField(blank=True, null=True)),
                ('temperature', models.FloatField(blank=True, null=True)),
                ('breathing', models.IntegerField(blank=True, null=True)),
                ('spo2', models.FloatField(blank=True, null=True)),
                ('blood_pressure', models.FloatField(blank=True, null=True)),
                ('main_symptoms', models.TextField(blank=True, null=True)),
                ('extra_symptoms', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medical_declaration_x_created_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medical_declaration_x_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
