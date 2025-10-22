from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

BRAZIL_STATE_CHOICES = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins"),
]

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
