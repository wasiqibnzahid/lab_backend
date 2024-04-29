from django.db import models


class Pilot(models.Model):
    name = models.CharField(max_length=100)
    # Add other fields as needed


class Group(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default="")
    started_at = models.CharField(max_length=100, default="")
    # Add other fields as needed


class Mouse(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)  # dead, alive, sacrificed
    updated_at = models.CharField(max_length=50, default="")
    treatment_start = models.CharField(max_length=50, default="")
    first_screening = models.CharField(max_length=50, default="")
    # Add other fields as needed


class TumorVolume(models.Model):
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=100)  # e.g., "B4L", "B4R", etc.
    week = models.PositiveBigIntegerField()
    volume = models.FloatField()
    # Add other fields as needed


class IvisData(models.Model):
    mouse = models.ForeignKey(Mouse, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=100)  # e.g., "B4L", "B4R", etc.
    week = models.PositiveBigIntegerField()
    value = models.FloatField()
    # Add other fields as needed
