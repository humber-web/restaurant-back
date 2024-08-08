from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from core.models import CashRegister
from core.serializers import StartCashRegisterSerializer
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal


class StartCashRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartCashRegisterSerializer(data=request.data)
        if serializer.is_valid():
            initial_amount = serializer.validated_data['initial_amount']
            cash_register = CashRegister.objects.create(
                user=request.user,
                initial_amount=initial_amount,
                final_amount=initial_amount
            )
            return Response({'detail': 'Cash register started successfully.', 'cash_register_id': cash_register.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CashRegisterSummaryView(APIView):
    def get(self, request):
        cash_register = CashRegister.objects.filter(user=request.user, is_open=False).last()
        if not cash_register:
            return Response({'error': 'No cash register data found for this user.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'initial_amount': cash_register.initial_amount,
            'operations_cash': cash_register.operations_cash,
            'operations_card': cash_register.operations_card,
            'operations_other': cash_register.operations_other,
            'final_amount': cash_register.final_amount,
            'start_time': cash_register.start_time,
            'end_time': cash_register.end_time,
        }
        return Response(data, status=status.HTTP_200_OK)
    
    
class CloseCashRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cash_register = CashRegister.objects.filter(user=request.user, is_open=True).first()
        if not cash_register:
            return Response({'error': 'No open cash register found.'}, status=status.HTTP_400_BAD_REQUEST)

        declared_cash = Decimal(request.data.get('declared_cash', 0))
        declared_card = Decimal(request.data.get('declared_card', 0))

        results = cash_register.close_register(declared_cash, declared_card)

        return Response({
            'detail': 'Cash register closed successfully.',
            'results': results
        }, status=status.HTTP_200_OK)
