from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Nome", required=True)
    email = forms.EmailField(label="Email", required=True)
    phone_number = forms.CharField(label="Telefone", required=False)
    city = forms.CharField(label="Cidade", required=False)
    state = forms.CharField(label="Estado", required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
        labels = {"username": "Usuário (use seu email)"}
