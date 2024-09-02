from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from core.serializers import InventoryItemSerializer
from core.models.inventory_item_models1 import InventoryItemN
from ..models.historyc_models import OperationLog
from django.http import Http404
from ..check_manager import IsManager


class CreateInventoryItemView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body to include the new object's ID
            request.body_data['object_id'] = item.itemID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class InventoryItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = InventoryItemN.objects.all().order_by('itemID')
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)


class InventoryItemDetailView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                item = InventoryItemN.objects.get(pk=pk)
                serializer = InventoryItemSerializer(item)
                return Response(serializer.data)
            except InventoryItemN.DoesNotExist:
                raise Http404
        else:
            supplier = request.query_params.get('supplier')
            menu_item = request.query_params.get('menu_item')
            menu_item_name = request.query_params.get('menu_item_name')
            
            queryset = InventoryItemN.objects.all()
            
            if supplier:
                queryset = queryset.filter(supplier__icontains=supplier)
            if menu_item:
                queryset = queryset.filter(menu_item__itemID__icontains=menu_item)
            if menu_item_name:
                queryset = queryset.filter(menu_item__name__icontains=menu_item_name)
            if not queryset.exists():
                raise Http404
        serializer = InventoryItemSerializer(queryset,many=True)
        return Response(serializer.data)
    

class InventoryItemUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        item = InventoryItemN.objects.get(pk=pk)
        serializer = InventoryItemSerializer(item, data=request.data,partial=True)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body to include the new object's ID
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class InventoryItemDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        item = get_object_or_404(InventoryItemN, pk=pk)
        content_type = ContentType.objects.get_for_model(item)
        
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=item.itemID,
            object_repr=f"inventoryitem {item.itemID}",
            change_message=f"User {request.user} performed DELETE on inventoryitem {item.itemID}"
        )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)