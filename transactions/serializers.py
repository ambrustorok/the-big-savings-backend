from rest_framework import serializers
from .models import Category, Transaction, TransactionSplit, Balance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class TransactionSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionSplit
        fields = ['id', 'category', 'amount', 'percentage']

class TransactionSerializer(serializers.ModelSerializer):
    splits = TransactionSplitSerializer(many=True, required=False)

    class Meta:
        model = Transaction
        fields = ['id', 'date', 'amount', 'description', 'transaction_type', 'splits']

    def create(self, validated_data):
        splits_data = validated_data.pop('splits', [])
        transaction = Transaction.objects.create(**validated_data)
        for split_data in splits_data:
            TransactionSplit.objects.create(transaction=transaction, **split_data)
        return transaction

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ['id', 'date', 'amount']