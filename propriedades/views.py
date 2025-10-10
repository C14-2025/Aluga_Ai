from django.shortcuts import render, get_object_or_404, redirect
from .models import Propriedade, PropriedadeImagem
from .forms import PropriedadeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
        form = PropriedadeForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()
            imagens = request.FILES.getlist("imagens")
            for f in imagens:
                PropriedadeImagem.objects.create(propriedade=prop, imagem=f)
            messages.success(request, "Propriedade criada com sucesso.")
            return redirect("propriedades:detalhe", pk=prop.pk)
    else:
        form = PropriedadeForm()
    return render(request, "propriedades/criar.html", {"form": form})
