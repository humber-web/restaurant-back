from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from core.serializers import TableSerializer
from core.models.table_models import Table
from django.http import Http404
from ..check_manager import IsManager
from ..models.historyc_models import OperationLog


class CreateTableView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body to include the new object's ID
            request.body_data['object_id'] = item.tableid
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TableListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Table.objects.all()
        serializer = TableSerializer(items, many=True)
        return Response(serializer.data)
    
class TableDetailView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                item = Table.objects.get(pk=pk)
                serializer = TableSerializer(item)
                return Response(serializer.data)
            except Table.DoesNotExist:
                raise Http404
        else:
            status = request.query_params.get('status')
            capacity = request.query_params.get('capacity')
            
            queryset = Table.objects.all()
            
            if status:
                queryset = queryset.filter(status__icontains=status)
            if capacity:
                queryset = queryset.filter(capacity__icontains=capacity)
            if not queryset.exists():
                raise Http404
        serializer = TableSerializer(queryset,many=True)
        return Response(serializer.data)
    
class TableUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        table = Table.objects.get(pk=pk)
        serializer = TableSerializer(table, data=request.data,partial=True)
        if serializer.is_valid():
            table = serializer.save()
            # Update request body to include the new object's ID
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
class TableDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        content_type = ContentType.objects.get_for_model(table)
        
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=table.tableid,
            object_repr=f"table {table.tableid}",
            change_message=f"User {request.user} performed DELETE on table {table.tableid}"
        )
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)