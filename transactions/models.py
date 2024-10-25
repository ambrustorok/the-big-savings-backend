# transactions/models.py
from django.db import models
import uuid

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    date = models.DateField()
    type = models.CharField(max_length=7, choices=TransactionType.choices)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.description} ({self.total_amount})"

    def clean(self):
        from django.core.exceptions import ValidationError
        splits_sum = sum(split.percentage for split in self.splits.all())
        if splits_sum != 100:
            raise ValidationError('Transaction splits must sum to 100%')

class TransactionSplit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='splits')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='splits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (0 < self.percentage <= 100):
            raise ValidationError('Percentage must be between 0 and 100')
        # Verify amount matches percentage
        expected_amount = (self.transaction.total_amount * self.percentage) / 100
        if abs(self.amount - expected_amount) > 0.01:  # Allow for small rounding differences
            raise ValidationError('Amount does not match the specified percentage')

    class Meta:
        ordering = ['-created_at']