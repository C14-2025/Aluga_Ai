from django import forms
from .models import Propriedade

#Cria um widget customizado que permite múltiplos arquivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PropriedadeForm(forms.ModelForm):
    imagens = forms.ImageField(
        required=False,
        widget=MultipleFileInput(attrs={"multiple": True}),
        label="Imagens (opcional, pode selecionar várias)",
    )

    class Meta:
        model = Propriedade
        fields = ["titulo", "descricao", "endereco", "city", "state", "preco_por_noite"]
