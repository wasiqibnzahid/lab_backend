from django.core.management.base import BaseCommand
from lab_results_backend_db.models import Pilot, Group, Mouse, TumorVolume


class Command(BaseCommand):
    help = 'Load dummy data for testing purposes'

    def handle(self, *args, **options):
        # Create a pilot
        pilot = Pilot.objects.create(name='Test Pilot')

        # Create groups
        group1 = Group.objects.create(pilot=pilot, name='Group 1')
        group2 = Group.objects.create(pilot=pilot, name='Group 2')

        # Create mice
        mouse1 = Mouse.objects.create(
            group=group1, name='Mouse 1', status='alive')
        mouse2 = Mouse.objects.create(
            group=group2, name='Mouse 2', status='alive')

        # Create tumor volumes
        TumorVolume.objects.create(
            mouse=mouse1, identifier='B4L', week=1, volume=10.5)
        TumorVolume.objects.create(
            mouse=mouse1, identifier='B4R', week=1, volume=8.2)
        TumorVolume.objects.create(
            mouse=mouse2, identifier='C2L', week=1, volume=15.3)
        TumorVolume.objects.create(
            mouse=mouse2, identifier='C2R', week=1, volume=12.7)

        self.stdout.write(self.style.SUCCESS('Dummy data loaded successfully'))
