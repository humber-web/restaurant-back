from django.db import models
from .menu_item_models import MenuItem

class InventoryItemN(models.Model):
    itemID = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    reserved_quantity = models.IntegerField(default=0)
    supplier = models.CharField(max_length=255)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='inventory_itemsn')
    oversell_quantity = models.IntegerField(default=0)  # Adding the oversell quantity field

    def __str__(self):
        return f"{self.menu_item.name} - {self.supplier}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_menu_item_availability()

    def update_menu_item_availability(self):
        if self.quantity > 0:
            self.menu_item.availability = True
        else:
            self.menu_item.availability = False
        self.menu_item.save()
