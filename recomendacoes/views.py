from django.shortcuts import render
from propriedades.models import Propriedade

def index(request):
    # apenas mostra algumas propriedades (se houver)
    props = Propriedade.objects.filter(ativo=True)[:6] if 'propriedades' in __import__('pkgutil').iter_modules() else []
    return render(request, "recomendacoes/index.html", {"propriedades": props})
