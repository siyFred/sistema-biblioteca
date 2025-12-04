from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, ImportBookView

router = DefaultRouter()
router.register(r'', BookViewSet)

urlpatterns = [
    path('import/', ImportBookView.as_view(), name='book-import'),
    path('', include(router.urls)),
]
