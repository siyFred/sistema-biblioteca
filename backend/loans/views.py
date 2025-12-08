from rest_framework import viewsets, status, exceptions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend # Necessário para os filtros ?status=...
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Loan
from books.models import Book
from .serializers import LoanSerializer

# Create your views here.

class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    # --- CONFIGURAÇÃO DE FILTROS (Essencial para o Painel Admin funcionar) ---
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'user', 'book'] # Permite filtrar por ?status=PENDING
    search_fields = ['user__username', 'book__title'] # Permite busca por nome
    ordering_fields = ['loan_date', 'due_date']
    ordering = ['-loan_date']

    # 1. Ajuste do QuerySet: Bibliotecários veem tudo, Alunos veem apenas o próprio.
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Loan.objects.all().order_by('-loan_date')
        return Loan.objects.filter(user=user).order_by('-loan_date')

    # 2. Criação: Apenas solicita o livro (Status PENDING e sem due_date)
    def perform_create(self, serializer):
        book = serializer.validated_data['book']

        # Validação extra: Impede duplicidade de solicitação do mesmo livro
        existing_loan = Loan.objects.filter(
            user=self.request.user, 
            book=book, 
            status__in=['PENDING', 'ACTIVE']
        ).exists()
        
        if existing_loan:
            raise exceptions.ValidationError("Você já possui uma solicitação ou empréstimo ativo deste livro.")

        with transaction.atomic():
            book_locked = Book.objects.select_for_update().get(pk=book.pk)

            if book_locked.available_copies <= 0:
                raise exceptions.ValidationError('Este livro não está disponível no momento.')

            # Reserva a cópia
            book_locked.available_copies -= 1
            book_locked.save()
            
            # Removemos a linha do due_date. O status será PENDING (default no models.py)
            serializer.save(user=self.request.user)

    # 3. Aprovação: Ação exclusiva do Bibliotecário
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        loan = self.get_object()

        if loan.status != 'PENDING':
             return Response(
                 {"error": "Este empréstimo não está pendente de aprovação."}, 
                 status=status.HTTP_400_BAD_REQUEST
             )
        
        # Define o status como ativo e calcula a due_date (7 dias a partir da aprovação)
        loan.status = 'ACTIVE' 
        loan.loan_date = timezone.now() # A data oficial do empréstimo começa AGORA
        loan.due_date = timezone.now() + timedelta(days=7)
        loan.save()

        return Response(LoanSerializer(loan).data)

    # --- NOVA AÇÃO: REJEITAR (Conserta o erro 404) ---
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        loan = self.get_object()

        if loan.status != 'PENDING':
             return Response(
                 {"error": "Só é possível rejeitar solicitações pendentes."}, 
                 status=status.HTTP_400_BAD_REQUEST
             )

        with transaction.atomic():
            # 1. Devolve a cópia do livro para o estoque
            book_locked = Book.objects.select_for_update().get(pk=loan.book.pk)
            book_locked.available_copies += 1
            book_locked.save()
            
            # 2. Atualiza status para REJECTED
            loan.status = 'REJECTED'
            loan.save()

        return Response({'status': 'Solicitação rejeitada e estoque devolvido.'})

    # 4. Devolução: Mantido igual
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()

        if loan.status in ['RETURNED', 'REJECTED']:
            return Response({"error": "Este empréstimo já foi finalizado."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            book_locked = Book.objects.select_for_update().get(pk=loan.book.pk)
            book_locked.available_copies += 1
            book_locked.save()
            loan.return_date = timezone.now()
            loan.status = 'RETURNED'
            loan.save()

        return Response(LoanSerializer(loan).data)

    # 5. Action: Empréstimos ativos (Lendo Agora)
    @action(detail=False, methods=['get'])
    def lendo_agora(self, request):
        user = request.user
        # Considera empréstimos pendentes, ativos ou atrasados como "lendo agora"
        loans = Loan.objects.filter(user=user, status__in=['PENDING', 'ACTIVE', 'OVERDUE']).order_by('-loan_date')
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)

    # 6. Action: Histórico de empréstimos
    @action(detail=False, methods=['get'])
    def historico(self, request):
        user = request.user
        loans = Loan.objects.filter(user=user, status__in=['RETURNED', 'REJECTED']).order_by('-return_date')
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)