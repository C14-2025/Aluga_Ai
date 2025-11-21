from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from propriedades.models import Propriedade
from .models import Favorito

@login_required
@require_POST
def add_favorito(request, propriedade_id):
    prop = get_object_or_404(Propriedade, pk=propriedade_id, ativo=True)
    fav, created = Favorito.objects.get_or_create(user=request.user, propriedade=prop)
    return JsonResponse({'status': 'ok', 'favorited': True, 'created': created})

@login_required
@require_POST
def remove_favorito(request, propriedade_id):
    prop = get_object_or_404(Propriedade, pk=propriedade_id)
    Favorito.objects.filter(user=request.user, propriedade=prop).delete()
    return JsonResponse({'status': 'ok', 'favorited': False})

@login_required
def list_favoritos(request):
    favs = Favorito.objects.filter(user=request.user).select_related('propriedade')
    data = [
        {
            'id': f.propriedade.id,
            'titulo': f.propriedade.titulo,
            'preco_por_noite': float(f.propriedade.preco_por_noite),
        }
        for f in favs
    ]
    return JsonResponse({'status': 'ok', 'results': data})
