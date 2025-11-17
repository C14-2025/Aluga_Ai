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
    phone_number = forms.CharField(label="Telefone", required=False,
        widget=forms.TextInput(attrs={"placeholder": "(99) 91234-5678"}))
    city = forms.CharField(label="Cidade", required=False,
        widget=forms.TextInput(attrs={"placeholder": "São Paulo"}))
    state = forms.ChoiceField(label="Estado", required=False, choices=BRAZIL_STATE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
        labels = {"username": "Usuário (use seu email)"}

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "")
        if phone:
            # basic validation: digits and common punctuation
            import re
            if not re.match(r"^[0-9()\-\s+]{8,20}$", phone):
                raise forms.ValidationError("Telefone inválido.")
        return phone
