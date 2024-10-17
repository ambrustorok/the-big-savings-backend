from django.shortcuts import render

from rest_framework import viewsets
from .models import Category, Transaction, Balance
from .serializers import CategorySerializer, TransactionSerializer, BalanceSerializer
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['get'])
    def category_summary(self, request):
        summary = (
            Transaction.objects
            .values('splits__category__name')
            .annotate(total=Sum('splits__amount'))
            .order_by('-total')
        )
        return Response(summary)

class BalanceViewSet(viewsets.ModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer

    @action(detail=False, methods=['get'])
    def current_balance(self, request):
        latest_balance = Balance.objects.order_by('-date').first()
        if latest_balance:
            return Response({'balance': latest_balance.amount})
        return Response({'balance': 0})