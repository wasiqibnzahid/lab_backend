# Generated by Django 5.0.3 on 2024-04-04 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_results_backend_db', '0004_auto_20240404_0543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ivisdata',
            name='week',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='tumorvolume',
            name='week',
            field=models.PositiveBigIntegerField(),
        ),
    ]
