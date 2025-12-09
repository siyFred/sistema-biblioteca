from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    admin_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'role', 'admin_code',
            'first_name', 'last_name', 'cpf', 'phone',
            'cep', 'street', 'number', 'complement', 'district', 'city', 'state'
        )

        read_only_fields = ('role',) 

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        admin_code = validated_data.pop('admin_code', None)

        # Verifica chave mestra
        if admin_code == "BIBLIOTECA_ADMIN_2025":
            validated_data['role'] = User.Role.LIBRARIAN
            validated_data['is_staff'] = True
        else:
            validated_data['role'] = User.Role.READER
            validated_data['is_staff'] = False
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

    def update(self, instance, validated_data):
        validated_data.pop('email', None) 
        validated_data.pop('role', None)
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'role': self.user.role,
            'is_superuser': self.user.is_superuser
        }
        return data