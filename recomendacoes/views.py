from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from propriedades.models import Propriedade

@require_GET
def index(request):
    # mostra algumas propriedades ativas (se o app estiver registrado)
    props = Propriedade.objects.filter(ativo=True)[:6]
    return render(request, "recomendacoes/index.html", {"propriedades": props})

@login_required
def lista_recomendacoes(request):
    """Página interativa para obter recomendações via endpoint /api/ml/recommend/."""
    return render(request, "recomendacoes/lista.html")
