from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Book, PurchaseRequest
from .serializers import BookSerializer, PurchaseRequestSerializer
from .services import GoogleBooksService
from .filters import BookFilter
from .permissions import IsLibrarianOrReadOnly
from django.db.models import Q 
import random

# Definindo o limite máximo de resultados para a API (40 é o máximo seguro do Google)
MAX_API_LIMIT = 40

@extend_schema_view(
    create=extend_schema(description="Cria um novo livro", request=BookSerializer),
    update=extend_schema(description="Atualiza um livro", request=BookSerializer),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsLibrarianOrReadOnly] 

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'isbn', 'genre', 'publisher', 'description']
    ordering_fields = ['title', 'publication_date', 'created_at', 'available_copies']
    ordering = ['-created_at']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = request.data
        if partial:
            new_data = data.copy()
            for key, value in data.items():
                if value == '' and key not in ['cover_image']:
                     if key in new_data:
                         new_data.pop(key)
            data = new_data
        return super().update(request, data=data, partial=partial, *args, **kwargs)

class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        page = int(request.query_params.get('page', 1))
        genre = request.query_params.get('genre', 'ALL')
        source = request.query_params.get('source', 'local') # local (default) | google
        min_year = request.query_params.get('min_year')
        max_year = request.query_params.get('max_year')
        available = request.query_params.get('available')
        ordering = request.query_params.get('ordering', '-created_at') # Default sorting
        
        google_service = GoogleBooksService()
        local_data = []

        if source == 'google':
             if not query: return Response([]) 
             google_books = google_service.search_books(query, page, genre, MAX_API_LIMIT)
             return Response(google_books)

        local_queryset = Book.objects.all().order_by(ordering)

        if query:
            local_queryset = local_queryset.filter(
                Q(title__icontains=query) | 
                Q(author__icontains=query) | 
                Q(isbn__icontains=query)
            )
        
        if genre != 'ALL':
                local_queryset = local_queryset.filter(genre__icontains=genre)
        
        if min_year:
            local_queryset = local_queryset.filter(publication_date__year__gte=min_year)
        
        if max_year:
            local_queryset = local_queryset.filter(publication_date__year__lte=max_year)

        if available == 'true':
            local_queryset = local_queryset.filter(available_copies__gt=0)

        local_books = local_queryset
        
        start = (page - 1) * MAX_API_LIMIT
        end = start + MAX_API_LIMIT
        local_books_page = local_books[start:end]

        local_serializer = BookSerializer(local_books_page, many=True, context={'request': request})
        local_data = local_serializer.data
        for b in local_data: 
            b['is_google'] = False

        return Response(local_data)

class PurchaseRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        
        title = data.get('title')
        isbn = data.get('isbn')

        if PurchaseRequest.objects.filter(user=user, title=title).exists():
            return Response(
                {'detail': 'Você já solicitou a compra deste livro.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        PurchaseRequest.objects.create(
            user=user,
            title=title,
            author=data.get('author'),
            isbn=isbn
        )
        
        return Response({'success': True, 'message': 'Solicitação enviada!'}, status=status.HTTP_201_CREATED)

class GoogleBookDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, google_id):
        service = GoogleBooksService()
        data = service.get_book_by_google_id(google_id)
        if data:
            return Response(data)
        return Response({'error': 'Livro não encontrado'}, status=404)

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = None 
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        base_queryset = PurchaseRequest.objects.all().order_by('-created_at')
        if not self.request.user.is_staff:
            return base_queryset.filter(user=self.request.user)
        return base_queryset

    def perform_update(self, serializer):
        serializer.save() 
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)