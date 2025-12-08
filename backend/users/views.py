from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.management import call_command
from .serializers import UserSerializer, CustomTokenObtainPairSerializer

try:
    from books.models import Book
    from loans.models import Loan
except ImportError:
    pass

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

def check_username(request):
    username = request.GET.get('username', None)
    if not username:
        return JsonResponse({'exists': False})
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})

def check_email(request):
    email = request.GET.get('email', None)
    if not email:
        return JsonResponse({'exists': False})
    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r'\d+' 

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all().order_by('username')
        return User.objects.filter(id=user.id)

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        if not user.is_staff:
            data.pop('email', None)
            data.pop('role', None)
            data.pop('is_superuser', None)
        
        serializer = self.get_serializer(self.get_object(), data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        data = request.data.copy()
        if not user.is_staff:
            data.pop('email', None)
            data.pop('role', None)

        serializer = self.get_serializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def promote(self, request, pk=None):
        user = self.get_object()
        if user.role == 'LIBRARIAN':
            user.role = 'READER'
            user.is_staff = False
        else:
            user.role = 'LIBRARIAN'
            user.is_staff = True
        user.save()
        return Response(UserSerializer(user).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    try:
        call_command('update_status')
    except Exception:
        pass

    try:
        from books.models import Book
        from loans.models import Loan
    except ImportError:
        return Response({"error": "Configuração incompleta"}, status=503)

    user = request.user
    data = {}

    if getattr(user, 'role', 'READER') == 'LIBRARIAN' or user.is_staff:
        data = {
            'total_books': Book.objects.count(),
            'total_users': User.objects.count(),
            'active_loans': Loan.objects.filter(status='ACTIVE').count(),
            'overdue_loans': Loan.objects.filter(status='OVERDUE').count(),
            'pending_loans': Loan.objects.filter(status='PENDING').count(),
            'is_admin': True
        }
    else:
        data = {
            'my_active_loans': Loan.objects.filter(user=user, status__in=['ACTIVE', 'PENDING']).count(),
            'my_history': Loan.objects.filter(user=user, status='RETURNED').count(),
            'my_overdue': Loan.objects.filter(user=user, status='OVERDUE').count(),
            'is_admin': False
        }

    return Response(data)