# Generated by Django 5.2 on 2025-04-21 13:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_customuser_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfessionalVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('collecteur', 'Collecteur'), ('recycleur', 'Recycleur')], max_length=20)),
                ('entreprise', models.CharField(max_length=255)),
                ('ifu', models.CharField(max_length=100)),
                ('rccm', models.CharField(max_length=100)),
                ('email_entreprise', models.EmailField(max_length=254)),
                ('adresse_entreprise', models.CharField(max_length=255)),
                ('type_dechets', models.CharField(max_length=255)),
                ('nbre_equipe', models.PositiveIntegerField()),
                ('preuve_impot', models.FileField(upload_to='verifications/impots/')),
                ('zones_intervention', models.JSONField(blank=True, null=True)),
                ('is_validated', models.BooleanField(default=False)),
                ('rejected_reason', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
