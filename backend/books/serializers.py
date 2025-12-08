from rest_framework import serializers
from .models import Book, PurchaseRequest  # <--- Adicionado PurchaseRequest

class BookSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False)
    status_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'publisher', 
            'publication_date', 'genre', 'language', 'description', 
            'cover_image', 'cover_url', 'total_copies', 
            'available_copies', 'created_at', 'updated_at',
            'status_usuario' 
        ]
        read_only_fields = ('created_at', 'updated_at', 'available_copies', 'status_usuario')

    def get_status_usuario(self, obj):
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            return 'disponivel'

        user = request.user

        try:
            from loans.models import Loan
        except ImportError:
            return 'disponivel'

        # Verifica status do livro para o usuário atual
        loan = Loan.objects.filter(
            user=user, 
            book=obj, 
            status__in=['PENDING', 'ACTIVE', 'OVERDUE']
        ).first()

        if not loan:
            return 'disponivel'
        
        if loan.status == 'PENDING':
            return 'solicitado'
        
        return 'alugado'

    def update(self, instance, validated_data):
        new_total = validated_data.get('total_copies')
        
        if new_total is not None:
            old_total = instance.total_copies
            diff = new_total - old_total
            instance.available_copies += diff
            
            if instance.available_copies < 0:
                raise serializers.ValidationError(
                    {"total_copies": f"Impossível reduzir para {new_total}. Existem {old_total - instance.available_copies} livros emprestados."}
                )

        return super().update(instance, validated_data)

class PurchaseRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = ['id', 'user', 'username', 'title', 'author', 'isbn', 'status', 'created_at']
        read_only_fields = ['user', 'created_at']