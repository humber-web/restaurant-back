from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from core.serializers import OrderSerializer, OrderItemSerializer
from core.models.order_models import Order
from core.models.order_item_models import OrderItem
from django.http import Http404
from ..check_manager import IsManager
from ..models.historyc_models import OperationLog
from core.models.menu_item_models import MenuItem
from decimal import Decimal


class ListOrdersView(APIView):
    permission_classes = [IsAuthenticated, IsManager] 
    
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request, pk=None):
        if pk:
            try:
                order = Order.objects.get(pk=pk)
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            except Order.DoesNotExist:
                raise Http404
        else:
            customer = request.query_params.get('customer')
            status = request.query_params.get('status')
            payment_status = request.query_params.get('payment_status')
            order_type = request.query_params.get('order_type')
            table = request.query_params.get('table')
            
            queryset = Order.objects.all()
            
            if customer:
                queryset = queryset.filter(customer__username__icontains=customer)
            if status:
                queryset = queryset.filter(status__icontains=status)
            if payment_status:
                queryset = queryset.filter(paymentStatus__icontains=payment_status)
            if order_type:
                queryset = queryset.filter(orderType__icontains=order_type)
            if table:
                queryset = queryset.filter(details__table__tableid=table)
                queryset = queryset.exclude(paymentStatus='PAID')  # Exclude PAID orders only when searching by table
            if not queryset.exists():
                raise Http404
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(last_updated_by=request.user)
            request.body_data['object_id'] = order.orderID
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST,)
    
    
class UpdateOrderItemsView(APIView):
    def put(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save(last_updated_by=request.user)
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        order_items_data = request.data.get('items', [])

        for item_data in order_items_data:
            menu_item_id = item_data.get('menu_item')
            quantity = item_data.get('quantity', 0)

            if quantity > 0:
                # Add or update item
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    menu_item_id=menu_item_id,
                    defaults={'quantity': quantity, 'price': MenuItem.objects.get(pk=menu_item_id).price}
                )
                if not created:
                    order_item.quantity = quantity
                    order_item.price = order_item.menu_item.price
                    order_item.save()
            else:
                # Remove item
                OrderItem.objects.filter(order=order, menu_item_id=menu_item_id).delete()

        total_amount = sum(item.menu_item.price * item.quantity for item in order.items.all())
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage

        order.totalAmount = total_amount
        order.totalIva = total_iva
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)




class TransferOrderItemsView(APIView):
    def post(self, request, *args, **kwargs):
        source_order_id = request.data.get('source_order_id')
        target_order_id = request.data.get('target_order_id')

        if not source_order_id or not target_order_id:
            return Response({'detail': 'source_order_id and target_order_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            source_order = Order.objects.get(pk=source_order_id)
            target_order = Order.objects.get(pk=target_order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'One or both orders do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Transfer items and update target order
        for item in source_order.items.all():
            existing_item = target_order.items.filter(menu_item=item.menu_item).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.order = target_order
                item.save()

        # Delete source order
        source_order.delete()

        # Recalculate total amount and total IVA for the target order
        total_amount = sum(item.menu_item.price * item.quantity for item in target_order.items.all())
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage

        target_order.totalAmount = total_amount
        target_order.totalIva = total_iva
        target_order.save()

        # Serialize updated target order and return response
        serializer = OrderSerializer(target_order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class DeleteOrderView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    def delete(self, request, pk, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(Order)
        order = get_object_or_404(Order, pk=pk)
        
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=order.orderID,
            object_repr=f"User {request.user} performed DELETE on order {order.orderID}",
        )
        order.delete()
        return Response({'detail': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)