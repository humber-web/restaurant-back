from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class CashRegister(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operations_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_transfer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operations_check = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    def close_register(self, declared_cash, declared_card):
        self.final_amount = self.initial_amount + self.operations_cash + self.operations_card
        self.end_time = timezone.now()
        self.is_open = False
        self.save()

        expected_cash = self.initial_amount + self.operations_cash
        expected_card = self.operations_card

        cash_difference = declared_cash - expected_cash
        card_difference = declared_card - expected_card

        return {
            'expected_cash': expected_cash,
            'declared_cash': declared_cash,
            'cash_difference': cash_difference,
            'expected_card': expected_card,
            'declared_card': declared_card,
            'card_difference': card_difference,
        }
    
    def add_transaction(self, amount, payment_method):
        amount = Decimal(amount) 
        
        if payment_method == 'CASH':
            self.operations_cash += amount
        elif payment_method == 'CARD':
            self.operations_card += amount
        else:
            self.operations_other += amount
        self.final_amount += amount
        self.save()

    def insert_money(self, amount):
        self.operations_cash += amount
        self.final_amount = (self.final_amount or self.initial_amount) + amount
        self.save()

    def extract_money(self, amount):
        self.operations_cash -= amount
        self.final_amount = (self.final_amount or self.initial_amount) - amount
        self.save()
