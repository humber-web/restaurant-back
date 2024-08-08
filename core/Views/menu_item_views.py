from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from core.serializers import MenuItemSerializer
from core.models import MenuItem
from ..models.historyc_models import OperationLog
from django.http import Http404
from ..models.menu_category_models import MenuCategory
from ..check_manager import IsManager

class CreateMenuItemView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body to include the new object's ID
            request.body_data['object_id'] = item.itemID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MenuItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)
    
class MenuItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        # If a primary key (pk) is provided in the URL, attempt to get the item by ID
        if pk:
            # Fetch the item by primary key
            try:
                item = MenuItem.objects.get(pk=pk)
                serializer = MenuItemSerializer(item)
                return Response(serializer.data)
            except MenuItem.DoesNotExist:
                raise Http404
        else:
            # If no pk is provided, check for name and category_name query parameters
            item_name = request.query_params.get('name')
            category_name = request.query_params.get('categoryName')
            queryset = MenuItem.objects.all()

            if item_name:
                queryset = queryset.filter(name__icontains=item_name)
            if category_name:
                queryset = queryset.filter(categoryID__name__icontains=category_name)

            # If no items match the query, return a 404
            if not queryset.exists():
                raise Http404

            # If there are multiple items, you might want to return the first one or handle it differently
            # item = queryset.first()

        serializer = MenuItemSerializer(queryset,many=True)
        return Response(serializer.data)

class MenuItemUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        item = MenuItem.objects.get(pk=pk)
        serializer = MenuItemSerializer(item, data=request.data,partial=True)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body to include the new object's ID
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
class MenuItemDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk)
        content_type = ContentType.objects.get_for_model(item)
        
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=item.itemID,
            object_repr=f"menuitem {item.itemID}",
            change_message=f"User {request.user} performed DELETE on menuitem {item.itemID}"
        )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)