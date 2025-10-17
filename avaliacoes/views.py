from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Avaliacao
from propriedades.models import Propriedade
from django.contrib import messages

@login_required
def nova_avaliacao(request, prop_id):
    prop = get_object_or_404(Propriedade, id=prop_id)
    if request.method == "POST":
        nota = int(request.POST.get("nota"))
        comentario = request.POST.get("comentario", "")
        if nota < 1 or nota > 5:
            messages.error(request, "Nota inválida.")
            return redirect("propriedades:detalhe", pk=prop.id)
        Avaliacao.objects.create(autor=request.user, propriedade=prop, nota=nota, comentario=comentario)
        messages.success(request, "Avaliação publicada.")
        return redirect("propriedades:detalhe", pk=prop.id)
    return render(request, "avaliacoes/nova.html", {"propriedade": prop})
