from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone # Adicionar import para defaults se necessário

class Loan(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendente'),  # NOVO STATUS
        ('ACTIVE', 'Ativo'),
        ('RETURNED', 'Devolvido'),
        ('OVERDUE', 'Atrasado'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='loans', verbose_name='Usuário')
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='loans', verbose_name='Livro')
    loan_date = models.DateTimeField(auto_now_add=True, verbose_name='Data da Solicitação') 
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Data de Devolução Prevista') # Precisa ser null/blank
    return_date = models.DateTimeField(null=True, blank=True, verbose_name='Data da Devolução Real')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Status') # NOVO DEFAULT

    def __str__(self):
        return f"{self.user} pegou {self.book} ({self.get_status_display()})"