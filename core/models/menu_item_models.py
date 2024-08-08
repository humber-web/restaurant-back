from django.db import models
from .menu_category_models import MenuCategory

class MenuItem(models.Model):
    itemID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    ingredients = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    categoryID = models.ForeignKey(MenuCategory, on_delete=models.CASCADE)
    is_quantifiable = models.BooleanField(default=True)  

    def __str__(self):
        return self.name
