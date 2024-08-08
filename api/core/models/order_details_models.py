from django.db import models
from .order_models import Order
from .table_models import Table

class OrderDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='details')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_details')    
    online_order_info = models.TextField(null=True, blank=True)  # Any specific info related to online orders

    def __str__(self):
        return f"Details for Order {self.order.orderID}"