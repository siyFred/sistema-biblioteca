from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    author = models.CharField(max_length=255, verbose_name="Autor")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    publisher = models.CharField(max_length=255, verbose_name="Editora")
    publication_date = models.DateField(null=True, blank=True, verbose_name="Data de Publicação")
    genre = models.CharField(max_length=50, verbose_name="Gênero")
    language = models.CharField(max_length=50, verbose_name="Idioma")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True, verbose_name="Capa (Arquivo local)")
    cover_url = models.URLField(null=True, blank=True, verbose_name="Capa (URL externa)")
    
    total_copies = models.PositiveIntegerField(default=1, verbose_name="Total de Cópias")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Cópias Disponíveis")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovada'),
        ('REJECTED', 'Rejeitada'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_requests')
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True) 

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitação: {self.title} por {self.user.username}"