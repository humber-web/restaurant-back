from django.db import models
from .menu_item_models import MenuItem

class InventoryItemN(models.Model):
    itemID = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    reserved_quantity = models.IntegerField(default=0)
    oversell_quantity = models.IntegerField(default=0)  # New field to track oversell quantity
    supplier = models.CharField(max_length=255)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='inventory_itemsn')
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.supplier}"
