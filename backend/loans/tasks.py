from celery import shared_task
from django.utils import timezone
from .models import Loan

@shared_task
def check_overdue_loans():
    today = timezone.now()

    overdue_loans = Loan.objects.filter(
        status='ACTIVE',
        due_date__lt=today,
    )

    count = overdue_loans.count()

    if count > 0:
        overdue_loans.update(status='OVERDUE')
        return f'{count} empréstimos marcados como atrasados.'

    return 'Nenhum empréstimo atrasado encontrado.'