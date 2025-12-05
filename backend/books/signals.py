from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Book
from loans.models import Loan

@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def clear_book_cache(sender, instance, **kwargs):
    cache.delete(f'book_detail_{instance.pk}')

@receiver(post_save, sender=Loan)
def clear_book_cache_from_loan(sender, instance, **kwargs):
    cache.delete(f'book_detail_{instance.book.pk}')
