from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from core.serializers import MenuCategorySerializer
from core.models import MenuCategory
from ..models.historyc_models import OperationLog

class CreateMenuCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MenuCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            # Update request body to include the new object's ID
            request.body_data['object_id'] = category.categoryID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MenuCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = MenuCategory.objects.all()
        serializer = MenuCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class MenuCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        category = MenuCategory.objects.get(pk=pk)
        serializer = MenuCategorySerializer(category)
        return Response(serializer.data)

class MenuCategoryUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        category = MenuCategory.objects.get(pk=pk)
        serializer = MenuCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            # Update request body to include the new object's ID
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    
class MenuCategoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        category = get_object_or_404(MenuCategory, pk=pk)
        content_type = ContentType.objects.get_for_model(category)
        
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=category.categoryID,
            object_repr=f"menucategory {category.categoryID}",
            change_message=f"User {request.user} performed DELETE on menucategory {category.categoryID}"
        )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)