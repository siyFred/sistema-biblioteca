from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
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

    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Multa')
    fine_last_updated = models.DateTimeField(null=True, blank=True, verbose_name='Última atualização da multa')

    def apply_fines_until(self, when=None):
        if when is None:
            when = timezone.now()

        if self.due_date >= when:
            return

        from django.conf import settings as dj_settings
        from decimal import Decimal

        daily_str = getattr(dj_settings, 'FINE_DAILY_AMOUNT', '1.00')
        try:
            daily = Decimal(str(daily_str))
        except Exception:
            daily = Decimal('1.00')

        last_point = self.fine_last_updated or self.due_date

        days = (when.date() - last_point.date()).days
        if days <= 0:
            return

        additional = daily * Decimal(days)
        self.fine_amount = (self.fine_amount or Decimal('0.00')) + additional
        self.fine_last_updated = when
        return additional