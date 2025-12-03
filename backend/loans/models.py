from django.db import models
from django.conf import settings
from books.models import Book

# Create your models here.

class Loan(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Ativo'),
        ('RETURNED', 'Devolvido'),
        ('OVERDUE', 'Atrasado'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='loans', verbose_name='Usuário')
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='loans', verbose_name='Livro')
    loan_date = models.DateTimeField(auto_now_add=True, verbose_name='Data do Empréstimo')
    due_date = models.DateTimeField(verbose_name='Data de Devolução Prevista')
    return_date = models.DateTimeField(null=True, blank=True, verbose_name='Data da Devolução Real')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE', verbose_name='Status')

    def __str__(self):
        return f"{self.user} pegou {self.book} ({self.get_status_display()})"