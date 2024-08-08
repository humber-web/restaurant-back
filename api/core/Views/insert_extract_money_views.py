from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import CashRegister
from ..serializers import InsertMoneySerializer, ExtractMoneySerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

class InsertMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InsertMoneySerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            cash_register = CashRegister.objects.filter(user=request.user, is_open=True).first()

            if not cash_register:
                return Response({'error': 'No open cash register found for this user.'}, status=status.HTTP_400_BAD_REQUEST)

            cash_register.insert_money(amount)
            return Response({'detail': 'Money inserted successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtractMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExtractMoneySerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            cash_register = CashRegister.objects.filter(user=request.user, is_open=True).first()

            if not cash_register:
                return Response({'error': 'No open cash register found for this user.'}, status=status.HTTP_400_BAD_REQUEST)

            if (cash_register.final_amount or cash_register.initial_amount) < amount:
                return Response({'error': 'Insufficient funds in cash register.'}, status=status.HTTP_400_BAD_REQUEST)

            cash_register.extract_money(amount)
            return Response({'detail': 'Money extracted successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
