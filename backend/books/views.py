from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Book
from .serializers import BookSerializer, ISBNImportSerializer
from .services import GoogleBooksService

from drf_spectacular.utils import extend_schema, extend_schema_view

# Schema manual para garantir upload de arquivo no Swagger
BOOK_SCHEMA = {
    'multipart/form-data': {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'author': {'type': 'string'},
            'isbn': {'type': 'string'},
            'publisher': {'type': 'string'},
            'publication_date': {'type': 'string', 'format': 'date'},
            'genre': {'type': 'string'},
            'language': {'type': 'string'},
            'description': {'type': 'string'},
            'cover_image': {'type': 'string', 'format': 'binary'}, # O pulo do gato
            'cover_url': {'type': 'string', 'format': 'uri'},
            'total_copies': {'type': 'integer'},
            'available_copies': {'type': 'integer'},
        }
    }
}

@extend_schema_view(
    create=extend_schema(description="Cria um novo livro", request=BOOK_SCHEMA),
    update=extend_schema(description="Atualiza um livro", request=BOOK_SCHEMA),
    partial_update=extend_schema(description="Atualização parcial", request=BOOK_SCHEMA),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)


class ImportBookView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=ISBNImportSerializer,
        responses={201: BookSerializer},
        description="Importa um livro do Google Books via ISBN"
    )
    def post(self, request):
        serializer = ISBNImportSerializer(data=request.data)
        if serializer.is_valid():
            isbn = serializer.validated_data['isbn']
            
            if Book.objects.filter(isbn=isbn).exists():
                return Response(
                    {"error": "Livro com este ISBN já está cadastrado."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            service = GoogleBooksService()
            book_data = service.get_book_by_isbn(isbn)
            if not book_data:
                return Response(
                    {"error": "Livro não encontrado no Google Books."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            book = Book.objects.create(**book_data)
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
