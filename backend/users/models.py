from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        LIBRARIAN = 'LIBRARIAN', 'Bibliotecário'
        READER = 'READER', 'Leitor'
    
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.READER, verbose_name='Função')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True, verbose_name="CPF")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone/WhatsApp")
    cep = models.CharField(max_length=9, null=True, blank=True, verbose_name="CEP")
    street = models.CharField(max_length=255, null=True, blank=True, verbose_name="Logradouro")
    number = models.CharField(max_length=10, null=True, blank=True, verbose_name="Número")
    complement = models.CharField(max_length=255, null=True, blank=True, verbose_name="Complemento")
    district = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bairro")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Cidade")
    state = models.CharField(max_length=2, null=True, blank=True, verbose_name="UF")