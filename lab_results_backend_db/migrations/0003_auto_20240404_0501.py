from django.db import migrations


def populate_data(apps, schema_editor):
    Pilot = apps.get_model('lab_results_backend_db', 'Pilot')
    Group = apps.get_model('lab_results_backend_db', 'Group')
    Mouse = apps.get_model('lab_results_backend_db', 'Mouse')

    # Create Pilots
    Pilot.objects.create(name='Pilot 2')
    pilot_3 = Pilot.objects.create(name='Pilot 3')
    Pilot.objects.create(name='Pilot 4')
    Pilot.objects.create(name='Pilot 5')

    # Create Groups for Pilot 3
    group_a = Group.objects.create(pilot=pilot_3, name='Group A')
    group_b = Group.objects.create(pilot=pilot_3, name='Group B')
    group_c = Group.objects.create(pilot=pilot_3, name='Group C')

    # Create Mice
    mice_names = ['Mouse 1', 'Mouse 2', 'Mouse 3', 'Mouse 4', 'Mouse 5']
    for group in [group_a, group_b, group_c]:
        for name in mice_names:
            Mouse.objects.create(group=group, name=name, status='alive')

    # Create Mouse for Group 7
    group_7 = Group.objects.create(pilot=pilot_3, name='Group 7')
    Mouse.objects.create(group=group_7, name='Group 7 Mouse', status='alive')


class Migration(migrations.Migration):
    dependencies = [
        ('lab_results_backend_db', '0002_ivisdata'),
    ]

    operations = [
        migrations.RunPython(populate_data),
    ]
