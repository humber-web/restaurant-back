from django.db import models
from .order_models import Order
from .menu_item_models import MenuItem

CHOICES_STATUS = (
    ('1', 'Pending'),
    ('2', 'Preparing'),
    ('3', 'Ready'),
    ('4', 'CANCELED'),
)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # changed related_name to 'items'
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    to_be_prepared_in = models.CharField(max_length=1, default='3')
    status = models.CharField(max_length=1, choices=CHOICES_STATUS, default='1')
    
    def save(self, *args, **kwargs):
        if self.menu_item and self.menu_item.categoryID:
            self.to_be_prepared_in = self.menu_item.categoryID.prepared_in
            self.to_be_prepared_in = self.menu_item.categoryID.prepared_in
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order.orderID} - Item {self.menu_item.name}"