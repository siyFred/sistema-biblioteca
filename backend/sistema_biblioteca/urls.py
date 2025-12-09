from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Importações
from users.views import (
    RegisterView, 
    CustomLoginView, 
    check_username, 
    check_email, 
    dashboard_stats,
    UserViewSet 
)
from loans.views import LoanViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Router para Users e Loans (Books saiu daqui!)
router = DefaultRouter()
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/books/', include('books.urls')),

    # Router Principal (Loans e Users)
    path('api/', include(router.urls)),

    # Autenticação e Utilitários
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomLoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/check-username/', check_username, name='check_username'),
    path('api/check-email/', check_email, name='check_email'),
    path('api/dashboard/', dashboard_stats, name='dashboard_stats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)