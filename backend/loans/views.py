from rest_framework import viewsets, status, exceptions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend 
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Loan
from books.models import Book
from .serializers import LoanSerializer
from decimal import Decimal

# Create your views here.

class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'user', 'book']
    search_fields = ['user__username', 'book__title']
    ordering_fields = ['loan_date', 'due_date']
    ordering = ['-loan_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Loan.objects.all().order_by('-loan_date')
        return Loan.objects.filter(user=user).order_by('-loan_date')

    def perform_create(self, serializer):
        book = serializer.validated_data['book']

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

            book_locked.available_copies -= 1
            book_locked.save()
            
            serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        loan = self.get_object()

        if loan.status != 'PENDING':
             return Response(
                 {"error": "Este empréstimo não está pendente de aprovação."}, 
                 status=status.HTTP_400_BAD_REQUEST
               )
        
        loan.status = 'ACTIVE' 
        loan.loan_date = timezone.now()
        loan.due_date = timezone.now() + timedelta(days=7)
        loan.save()

        return Response(self.get_serializer(loan).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        loan = self.get_object()

        if loan.status != 'PENDING':
             return Response(
                 {"error": "Só é possível rejeitar solicitações pendentes."}, 
                 status=status.HTTP_400_BAD_REQUEST
               )

        with transaction.atomic():
            book_locked = Book.objects.select_for_update().get(pk=loan.book.pk)
            book_locked.available_copies += 1
            book_locked.save()
            
            loan.status = 'REJECTED'
            loan.save()

        return Response({'status': 'Solicitação rejeitada e estoque devolvido.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def return_book(self, request, pk=None):
        loan = self.get_object()

        if loan.status in ['RETURNED', 'REJECTED']:
            return Response({"error": "Este empréstimo já foi finalizado."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            book_locked = Book.objects.select_for_update().get(pk=loan.book.pk)
            book_locked.available_copies += 1
            book_locked.save()
            now = timezone.now()
            loan.apply_fines_until(now)
            loan.return_date = now
            loan.status = 'RETURNED'
            loan.save()

        return Response(self.get_serializer(loan).data)

    @action(detail=False, methods=['get'])
    def lendo_agora(self, request):
        user = self.request.user
        loans = self.get_queryset().filter(status__in=['PENDING', 'ACTIVE', 'OVERDUE']).order_by('-loan_date')
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def historico(self, request):
        user = self.request.user
        loans = self.get_queryset().filter(status__in=['RETURNED', 'REJECTED']).order_by('-return_date') 
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        loan = self.get_object()

        if loan.fine_amount is None or loan.fine_amount <= 0:
            return Response({"error": "Não há multa a pagar."}, status=status.HTTP_400_BAD_REQUEST)

        if getattr(loan, 'paid', False):
            return Response({"error": "A multa já foi paga."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        loan.paid = True
        loan.paid_date = now
        loan.fine_amount = Decimal('0.00')
        loan.fine_last_updated = now
        loan.save()

        return Response(self.get_serializer(loan).data)
