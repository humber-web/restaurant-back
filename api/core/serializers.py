# serializers.py
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Profile, MenuCategory, MenuItem, InventoryItemN, Table, Order, OrderItem, OrderDetails, Payment, CashRegister
from .calculate_total import *
from django.db.models import Sum
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'groups']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
        
        
class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
    
 

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItemN
        fields = '__all__'
        
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'name','quantity', 'price', 'status', 'to_be_prepared_in']
        read_only_fields = ['price', 'name', 'to_be_prepared_in']
        
    def get_name(self, obj):
        return obj.menu_item.name
        
class OrderDetailsSerializer(serializers.ModelSerializer):
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), allow_null=True, required=False)

    class Meta:
        model = OrderDetails
        fields = ['table', 'online_order_info']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    details = OrderDetailsSerializer()

    class Meta:
        model = Order
        fields = ['orderID', 'customer', 'items', 'status', 'totalAmount',  'totalIva', 'grandTotal', 'paymentStatus', 'orderType', 'created_at', 'updated_at', 'last_updated_by', 'details']
        read_only_fields = ['totalAmount', 'totalIva',  'created_at', 'updated_at', 'last_updated_by','grandTotal']
        
        
    def validate(self, data):
        # Check if the table already has a pending order
        table = data.get('details', {}).get('table')
        if table and Order.objects.filter(details__table=table, paymentStatus='PENDING').exists():
            raise serializers.ValidationError(f"Table {table.tableid} already has a pending order.")
        return data

    def create(self, validated_data):
        order_items_data = validated_data.pop('items')
        order_details_data = validated_data.pop('details')
        total_amount = sum(item['menu_item'].price * item['quantity'] for item in order_items_data)
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva
        order = Order.objects.create(**validated_data, totalAmount=total_amount, totalIva=total_iva, grandTotal=grand_total)

        for item_data in order_items_data:
            menu_item = item_data['menu_item']

            if menu_item.is_quantifiable:
                inventory_item = menu_item.inventory_itemsn.first()  # Assuming you want the first inventory item associated with the menu item
                
                if inventory_item.quantity < item_data['quantity']:
                    oversell_qty = item_data['quantity'] - inventory_item.quantity
                    inventory_item.oversell_quantity += oversell_qty
                    inventory_item.quantity = 0
                else:
                    inventory_item.quantity -= item_data['quantity']
                
                inventory_item.reserved_quantity += item_data['quantity']
                inventory_item.save()

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item_data['quantity'],
                price=menu_item.price,
            )

        
        OrderDetails.objects.create(order=order, **order_details_data)
        
        table = order_details_data.get('table')
        if table:
            table.status = 'OC'
            table.save()
        
        order.totalAmount = total_amount
        order.totalIva = total_iva
        order.grandTotal = grand_total
        
        return order
    
    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('items', None)
        if order_items_data:
            for item_data in order_items_data:
                menu_item = item_data.get('menu_item')
                menu_item_id = menu_item.itemID
                quantity = item_data.get('quantity', 0)
                if quantity > 0:
                    # Add or update item
                    order_item, created = OrderItem.objects.get_or_create(
                        order=instance,
                        menu_item_id=menu_item_id,
                    
                        defaults={'quantity': quantity, 'price': MenuItem.objects.get(pk=menu_item_id).price}
                    )
                    if created:
                        self.update_inventory(menu_item, quantity)
                    else:
                        old_quantity = order_item.quantity
                        order_item.quantity = quantity
                        quantity_changed = quantity - old_quantity
                        order_item.price = order_item.menu_item.price
                        self.update_inventory(menu_item, quantity_changed)
                        order_item.save()
                else:
                    # Remove item
                    order_item = OrderItem.objects.filter(order=instance, menu_item_id=menu_item_id).first()
                    if order_item:
                        self.update_inventory(menu_item, -order_item.quantity)
                        order_item.delete()

        total_amount = sum(item.menu_item.price * item.quantity for item in instance.items.all())
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva

        instance.totalAmount = total_amount
        instance.totalIva = total_iva
        instance.grandTotal = grand_total
        if instance.totalAmount == 0:
            instance.status = 'CANCELED'

        instance.save()
        return instance
    
    def update_inventory(self, menu_item, quantity_change):
        if menu_item.is_quantifiable:
            inventory_item = menu_item.inventory_itemsn.first()
            if inventory_item:
                inventory_item.reserved_quantity += quantity_change
                inventory_item.quantity -= quantity_change
                inventory_item.save()
    

         


    

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['paymentID', 'order', 'amount', 'payment_method', 'payment_status', 'transaction_id', 'created_at', 'updated_at', 'processed_by']
        read_only_fields = ['payment_status', 'created_at', 'updated_at', 'processed_by']

    def validate(self, attrs):
        order = attrs.get('order')
        amount = attrs.get('amount')

        if amount != order.totalAmount:
            raise serializers.ValidationError("The payment amount does not match the total amount of the order.")

        return attrs

    def create(self, validated_data):
        validated_data['payment_status'] = 'COMPLETED'
        payment = super().create(validated_data)
        order = payment.order
        order.paymentStatus = 'PAID'
        order.save()
        return payment
    
    
class CashRegisterSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CashRegister
        fields = [
            'initial_amount', 
            'operations_cash', 
            'operations_card', 
            'operations_other', 
            'final_amount', 
            'start_time', 
            'end_time'
        ]
        
        
        
class StartCashRegisterSerializer(serializers.Serializer):
    initial_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class InsertMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class ExtractMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)