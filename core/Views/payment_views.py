from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from core.models import Order, Payment, CashRegister
from decimal import Decimal
from django.contrib.auth.models import AnonymousUser

class ProcessPaymentView(APIView):
    def post(self, request):
        user = request.user
        if isinstance(user, AnonymousUser):
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        order_id = request.data.get('orderID')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        
        order = get_object_or_404(Order, pk=order_id)
        amount = Decimal(amount)
        # total_amount = Decimal(order.totalAmount)
        grand_total = Decimal(order.grandTotal)
        
        if amount < grand_total:
            return Response({'error': 'Insufficient payment amount.'})
        
        cash_register = CashRegister.objects.filter(user=request.user, is_open=True).first()
        
        if not cash_register:
            return Response({'error': 'No open cash register found for this user.'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            payment_method=payment_method,
            processed_by=request.user,
            cash_register=cash_register
        )
        
        cash_register.add_transaction(amount, payment_method)
        
        # Update order payment status
        if amount >= order.grandTotal:
            order.paymentStatus = 'PAID'
            self.update_inventory(order)
        else:
            order.paymentStatus = 'PARTIALLY_PAID'
        order.save()

        change_due = max(0, amount - order.grandTotal)

        return Response({'detail': 'Payment processed successfully.', 'change_due': change_due}, status=status.HTTP_201_CREATED)
    
    
    def update_inventory(self, order):
        for order_item in order.items.all():
            menu_item = order_item.menu_item
            if menu_item.is_quantifiable:
                inventory_item = menu_item.inventory_itemsn.first()
                if inventory_item:
                    reserved_quantity = order_item.quantity
                    inventory_item.reserved_quantity -= reserved_quantity
                    inventory_item.save()


