from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    UserViewSet, 
    CustomLoginView, 
    check_username, 
    check_email, 
    dashboard_stats
)

# Router padrão
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Rotas específicas (Autenticação e Utilitários)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('check-username/', check_username, name='check_username'),
    path('check-email/', check_email, name='check_email'),
    path('dashboard/', dashboard_stats, name='dashboard_stats'),
    
    path('', include(router.urls)),
]