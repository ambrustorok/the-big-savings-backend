# transactions/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import Category, Transaction, TransactionSplit
from .serializers import CategorySerializer, RecursiveCategorySerializer, TransactionSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=['GET'])
    def tree(self, request):
        root_categories = Category.objects.filter(parent=None)
        serializer = RecursiveCategorySerializer(root_categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        categories = Category.objects.annotate(
            total_income=Sum(
                'splits__amount',
                filter=F('splits__transaction__type') == 'INCOME'
            ),
            total_expense=Sum(
                'splits__amount',
                filter=F('splits__transaction__type') == 'EXPENSE'
            )
        )
        
        total_income = Transaction.objects.filter(type='INCOME').aggregate(
            total=Sum('total_amount'))['total'] or 0
        total_expense = Transaction.objects.filter(type='EXPENSE').aggregate(
            total=Sum('total_amount'))['total'] or 0

        data = {
            'categories': CategorySerializer(categories, many=True).data,
            'totals': {
                'income': float(total_income),
                'expense': float(total_expense),
                'balance': float(total_income - total_expense)
            }
        }
        return Response(data)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().prefetch_related('splits', 'splits__category')
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        transactions = self.get_queryset()
        total_income = sum(t.total_amount for t in transactions if t.type == 'INCOME')
        total_expense = sum(t.total_amount for t in transactions if t.type == 'EXPENSE')
        
        data = {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(total_income - total_expense)
        }
        return Response(data)

