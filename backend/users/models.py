from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        LIBRARIAN = 'LIBRARIAN', 'Bibliotecário'
        READER = 'READER', 'Leitor'
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.READER, verbose_name='Função')
