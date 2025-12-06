from rest_framework import viewsets, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user).order_by('-loan_date')

    def perform_create(self, serializer):
        book = serializer.validated_data['book']

        with transaction.atomic():
            book_locked = Book.objects.select_for_update().get(pk=book.pk)

            if book_locked.available_copies <= 0:
                raise exceptions.ValidationError('Este livro não está disponível no momento.')

            book_locked.available_copies -= 1
            book_locked.save()
            due_date = timezone.now() + timedelta(days=7)
            serializer.save(user=self.request.user, due_date=due_date)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()

        if loan.status == 'RETURNED':
            return Response({"error": "Este empréstimo já foi devolvido."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            book_locked = Book.objects.select_for_update().get(pk=loan.book.pk)
            book_locked.available_copies += 1
            book_locked.save()
            now = timezone.now()
            loan.apply_fines_until(now)
            loan.return_date = now
            loan.status = 'RETURNED'
            loan.save()

        return Response(LoanSerializer(loan).data)

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

        return Response(LoanSerializer(loan).data)