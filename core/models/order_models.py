from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'In Preparation'),
        ('READY', 'Ready'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
         ('PENDING', 'Pending'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        
    ]

    ORDER_TYPE_CHOICES = [
        ('RESTAURANT', 'Restaurant'),
        ('ONLINE', 'Online'),
    ]

    orderID = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    totalIva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  
    grandTotal = models.DecimalField(max_digits=10, decimal_places=2,default=Decimal('0.00'))
    paymentStatus = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    orderType = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.orderID} ({self.orderType})"
    
    def update_payment_status(self):
        if self.payments.filter(payment_status='COMPLETED').exists():
            self.paymentStatus = 'PAID'
        else:
            self.paymentStatus = 'PENDING'
        self.save()
