
from django.db import migrations
from lab_results_backend_db.models import Group, Mouse, Pilot


def populate_mice(apps, schema_editor):
    # Get or create the pilot
    pilot_4 = Pilot.objects.get(name='Pilot 4')

    # Iterate over groups titled "Control 1" to "Control 4" and "Group 1" to "Group 4"
    for group_name in ["Control 1", "Control 2", "Control 3", "Control 4", "Group 1", "Group 2", "Group 3", "Group 4"]:
        group = Group.objects.create(
            pilot=pilot_4, name=group_name)
    # Add mice for each group
        for i in range(1, 6):  # Assuming mice are numbered from 1 to 5
            mouse_name = f"Mouse {i}"
            Mouse.objects.get_or_create(
                group=group, name=mouse_name, status="alive")


class Migration(migrations.Migration):
    dependencies = [
        ('lab_results_backend_db', '0003_auto_20240404_0501'),
    ]

    operations = [
        migrations.RunPython(populate_mice),
    ]
