from rest_framework import serializers
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'user', 'book', 'book_title', 'loan_date', 'due_date', 'return_date', 'status']
        read_only_fields = ['loan_date', 'return_date', 'status', 'due_date']
