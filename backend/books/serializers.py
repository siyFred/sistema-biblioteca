from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False)
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'publisher',
            'publication_date',
            'genre',
            'language',
            'description',
            'cover_image',
            'cover_url',
            'total_copies',
            'available_copies',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')
    
class ISBNImportSerializer(serializers.Serializer):
    isbn = serializers.CharField(max_length=13)