from django.shortcuts import render, get_object_or_404, redirect
from .models import Propriedade, PropriedadeImagem
from .forms import PropriedadeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

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
        # debug: veja o que chegou
        print("=== DEBUG criar_propriedade ===")
        print("POST keys:", list(request.POST.keys()))
        print("FILES keys:", list(request.FILES.keys()))
        # agora valide o form (apenas campos do modelo)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()

            # pegar arquivos enviados no campo 'imagens' (input name='imagens')
            imagens = request.FILES.getlist("imagens")
            print("getlist('imagens') count:", len(imagens))
            if not imagens:
                messages.info(request, "Nenhuma imagem enviada.")
            else:
                for f in imagens:
                    # opcional: checar content_type
                    if not getattr(f, "content_type", "").startswith("image/"):
                        messages.warning(request, f"Arquivo ignorado (não é imagem): {f.name}")
                        continue
                    try:
                        img = PropriedadeImagem(propriedade=prop, imagem=f)
                        img.save()  # salva tanto o registro quanto o arquivo em MEDIA_ROOT
                        print("Saved imagem:", img.imagem.name, "id:", img.pk)
                    except Exception as e:
                        logger.exception("Erro salvando imagem")
                        messages.error(request, f"Erro ao salvar imagem {f.name}: {e}")

            messages.success(request, "Propriedade criada com sucesso.")
            return redirect("propriedades:detalhe", pk=prop.pk)
        else:
            # debug errors
            print("Form inválido. errors:", form.errors.as_data())
            messages.error(request, "Erro no formulário. Verifique os campos.")
    else:
        form = PropriedadeForm()
    return render(request, "propriedades/criar.html", {"form": form})


@login_required
def excluir_propriedade(request, pk):
    prop = get_object_or_404(Propriedade, pk=pk)
    if prop.owner != request.user:
        messages.error(request, "Você não tem permissão para excluir esta propriedade.")
        return redirect("propriedades:detalhe", pk=pk)

    if request.method == "POST":
        prop.delete()
        messages.success(request, "Propriedade excluída.")
        return redirect("propriedades:lista")

    return render(request, "propriedades/confirm_delete.html", {"propriedade": prop})
