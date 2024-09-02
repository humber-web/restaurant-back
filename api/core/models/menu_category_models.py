from django.db import models

CHOICES_PREPARED_IN = (
    ('1', 'Kitchen'),
    ('2', 'Bar'),
    ('3', 'Both'),

)

class MenuCategory(models.Model):
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    prepared_in = models.CharField(max_length=1, choices=CHOICES_PREPARED_IN, default='3')

    def __str__(self):
        return self.name
