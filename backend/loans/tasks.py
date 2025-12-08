from celery import shared_task
from django.utils import timezone
from .models import Loan

@shared_task
def check_overdue_loans():
    today = timezone.now()
    active_overdue = Loan.objects.filter(
        status='ACTIVE',
        due_date__lt=today,
    )

    count_active = active_overdue.count()
    for loan in active_overdue.select_related('user'):
        loan.apply_fines_until(today)
        loan.status = 'OVERDUE'
        loan.save()

    already_overdue = Loan.objects.filter(status='OVERDUE')
    count_already = already_overdue.count()

    for loan in already_overdue:
        updated = loan.apply_fines_until(today)
        if updated:
            loan.save()

    total_changed = count_active + count_already

    if total_changed > 0:
        return f'{total_changed} empréstimos processados para multa/atraso.'

    return 'Nenhum empréstimo atrasado encontrado.'