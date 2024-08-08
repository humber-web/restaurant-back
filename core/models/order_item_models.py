from django.db import models
from .order_models import Order

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # changed related_name to 'items'
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.order.orderID} - Item {self.menu_item.name}"