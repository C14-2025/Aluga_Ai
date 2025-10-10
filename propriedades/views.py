from django.shortcuts import render, redirect, get_object_or_404
from .models import Propriedade, PropriedadeImagem
from django.contrib.auth.decorators import login_required

def lista_propriedades(request):
    q = request.GET.get("q", "")
    props = Propriedade.objects.filter(ativo=True)
    if q:
        props = props.filter(titulo__icontains=q)
    return render(request, "propriedades/lista.html", {"propriedades": props})

def detalhe_propriedade(request, pk):
    prop = get_object_or_404(Propriedade, pk=pk)
    return render(request, "propriedades/detalhe.html", {"propriedade": prop})

@login_required
def criar_propriedade(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descricao = request.POST.get("descricao")
        preco = request.POST.get("preco")
        prop = Propriedade.objects.create(owner=request.user, titulo=titulo, descricao=descricao, preco_por_noite=preco)
        # imagens
        for f in request.FILES.getlist("imagens"):
            PropriedadeImagem.objects.create(propriedade=prop, imagem=f)
        return redirect("propriedades:detalhe", pk=prop.pk)
    return render(request, "propriedades/criar.html")
