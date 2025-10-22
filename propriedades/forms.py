from django import forms
from .models import Propriedade

class PropriedadeForm(forms.ModelForm):
    class Meta:
        model = Propriedade
        fields = ["titulo", "descricao", "endereco", "city", "state", "preco_por_noite"]