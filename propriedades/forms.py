from django import forms
from .models import Propriedade, AMENITIES_CHOICES
from usuarios.forms import BRAZIL_STATE_CHOICES



class PropriedadeForm(forms.ModelForm):
    # Deixe coerente com o modelo (city/state são opcionais no model -> required=False no form)
    descricao = forms.CharField(label="Descrição", required=False, widget=forms.Textarea)
    endereco = forms.CharField(label="Endereço", required=False)
    city = forms.CharField(label="Cidade", required=False,
        widget=forms.TextInput(attrs={"placeholder": "Cidade"}))
    state = forms.ChoiceField(label="Estado", required=False, choices=BRAZIL_STATE_CHOICES)
    comodidades = forms.MultipleChoiceField(
        label="Comodidades",
        choices=AMENITIES_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Propriedade
        fields = ["titulo", "descricao", "endereco", "city", "state", "preco_por_noite", "comodidades"]

    def clean_titulo(self):
        t = self.cleaned_data.get("titulo", "").strip()
        if len(t) < 5:
            raise forms.ValidationError("O título deve ter pelo menos 5 caracteres.")
        return t

    def clean_preco_por_noite(self):
        p = self.cleaned_data.get("preco_por_noite")
        if p is None or p <= 0:
            raise forms.ValidationError("O preço deve ser um valor positivo.")
        return p