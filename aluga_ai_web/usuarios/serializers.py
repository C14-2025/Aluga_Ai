from django.contrib.auth.models import User
from rest_framework import serializers
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password', 'email')

    def validate_email(self, value):
        """Validação personalizada para email"""
        if not value:
            raise serializers.ValidationError("Email é obrigatório")
        
        # Verifica se o email já existe
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso")
        
        # Validação básica de formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Formato de email inválido")
        
        return value

    def validate_password(self, value):
        """Validação de força da senha"""
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número")
        
        return value

    def validate(self, attrs):
        """Validação cruzada dos campos"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As senhas não coincidem")
        return attrs

    def create(self, validated_data):
        # Remove confirm_password antes de criar o usuário
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de usuários"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'is_active')
        read_only_fields = ('id', 'date_joined', 'is_active')