# Generated by Django 5.0.4 on 2024-05-19 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_results_backend_db', '0010_pilot_end_date_pilot_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='mouse',
            name='date_of_birth',
            field=models.CharField(default='', max_length=50),
        ),
    ]