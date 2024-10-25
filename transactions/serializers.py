# transactions/serializers.py
from rest_framework import serializers
from .models import Category, Transaction, TransactionSplit

class RecursiveCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories', 'created_at']

    def get_subcategories(self, obj):
        serializer = self.__class__(obj.subcategories.all(), many=True)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'created_at']

class TransactionSplitSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = TransactionSplit
        fields = ['id', 'category', 'category_name', 'amount', 'percentage', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    splits = TransactionSplitSerializer(many=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'description', 'date', 'type', 'total_amount', 'splits', 'created_at']

    def validate_splits(self, splits):
        if not splits:
            raise serializers.ValidationError("At least one split is required")
        
        total_percentage = sum(split['percentage'] for split in splits)
        if abs(total_percentage - 100) > 0.01:  # Allow small rounding differences
            raise serializers.ValidationError("Split percentages must sum to 100%")
        
        return splits

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        transaction = Transaction.objects.create(**validated_data)
        
        for split_data in splits_data:
            percentage = split_data['percentage']
            amount = (transaction.total_amount * percentage) / 100
            TransactionSplit.objects.create(
                transaction=transaction,
                amount=amount,
                **split_data
            )
        
        return transaction

    def update(self, instance, validated_data):
        splits_data = validated_data.pop('splits', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if splits_data is not None:
            instance.splits.all().delete()
            for split_data in splits_data:
                percentage = split_data['percentage']
                amount = (instance.total_amount * percentage) / 100
                TransactionSplit.objects.create(
                    transaction=instance,
                    amount=amount,
                    **split_data
                )
        
        return instance