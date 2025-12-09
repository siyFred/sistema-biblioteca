from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet, 
    GlobalSearchView, 
    PurchaseRequestView, # Usada para POST de Solicitação
    GoogleBookDetailView, 
    PurchaseRequestViewSet # Usada para GET/PATCH de Gestão
)

router = DefaultRouter()
router.register(r'requests', PurchaseRequestViewSet, basename='purchase-request')
router.register(r'', BookViewSet, basename='book')

urlpatterns = [
    path('search-global/', GlobalSearchView.as_view(), name='global-search'),
    path('request-purchase/', PurchaseRequestView.as_view(), name='request-purchase'),
    path('google/<str:google_id>/', GoogleBookDetailView.as_view(), name='google-detail'),
    path('', include(router.urls)),
]