from django.db import models

class Table(models.Model):
    class StatusChoices(models.TextChoices):
        AVAILABLE = 'AV', 'Available'
        OCCUPIED = 'OC', 'Occupied'
        RESERVED = 'RE', 'Reserved'

    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE,
    )

    tableid = models.AutoField(primary_key=True)
    capacity = models.IntegerField()