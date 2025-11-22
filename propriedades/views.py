from django.shortcuts import render, get_object_or_404, redirect
from .models import Propriedade, PropriedadeImagem
from django.db.models import Q
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
    # Aplicar filtros simples via GET (para a seção "Filtros de recomendação" atuar como filtros)
    try:
        city = (request.GET.get("city") or "").strip()
        neighborhood = (request.GET.get("neighborhood") or "").strip()
        ptype = (request.GET.get("property_type") or "").strip()
        min_area = request.GET.get("min_area")
        max_area = request.GET.get("max_area")
        bedrooms = request.GET.get("bedrooms")
        bathrooms = request.GET.get("bathrooms")
        parking = request.GET.get("parking")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        amenities = request.GET.getlist("amenities")

        if city:
            props = props.filter(city__icontains=city)
        if neighborhood:
            props = props.filter(endereco__icontains=neighborhood)
        if ptype:
            # campo 'tipo' pode não existir em todos os registros; tentar filtrar por atributo
            props = props.filter(Q(tipo__icontains=ptype) | Q(property_type__icontains=ptype) | Q(titulo__icontains=ptype))
        if min_area:
            try:
                props = props.filter(area_m2__gte=int(min_area))
            except Exception:
                pass
        if max_area:
            try:
                props = props.filter(area_m2__lte=int(max_area))
            except Exception:
                pass
        if bedrooms:
            try:
                props = props.filter(quartos__gte=int(bedrooms))
            except Exception:
                pass
        if bathrooms:
            try:
                props = props.filter(banheiros__gte=int(bathrooms))
            except Exception:
                pass
        if parking:
            try:
                props = props.filter(vagas_garagem__gte=int(parking))
            except Exception:
                pass
        if min_price:
            try:
                props = props.filter(preco_por_noite__gte=float(min_price))
            except Exception:
                pass
        if max_price:
            try:
                props = props.filter(preco_por_noite__lte=float(max_price))
            except Exception:
                pass
        # amenidades: exigir que cada amenity esteja contida no JSONField 'comodidades'
        for a in [x.strip().lower() for x in amenities if x]:
            props = props.filter(comodidades__icontains=a) if a else props
    except Exception:
        # se qualquer erro de parsing ocorrer, ignorar filtros
        pass
    # Recomendações: somente pessoais, exibidas após usuário favoritar imóveis.
    recomendadas = []
    # Se usuário autenticado, tentar carregar recomendações personalizadas persistidas
    if request.user.is_authenticated:
        try:
            from favoritos.models import UserRecommendation
            user_recs = UserRecommendation.objects.filter(user=request.user, source='personal').order_by('-score')[:6]
            if user_recs:
                recomendadas = [{
                    'prop': rec.propriedade,
                    'predicted_price': float(rec.predicted_price),
                    'score': rec.score,
                    'season_applied': False,
                } for rec in user_recs]
        except Exception:
            pass

    # Para facilitar a lógica no template (evita chamadas a .filter/.exists no template),
    # transformamos a lista/queryset em lista materializada e marcamos um atributo
    # booleano `is_favorito` em cada propriedade para o usuário atual.
    try:
        props_list = list(props) if not isinstance(props, list) else props
        if request.user.is_authenticated:
            from favoritos.models import Favorito
            fav_ids = set(Favorito.objects.filter(user=request.user, propriedade__in=props_list).values_list('propriedade_id', flat=True))
        else:
            fav_ids = set()
        for p in props_list:
            p.is_favorito = (p.id in fav_ids)
    except Exception:
        # Em caso de erro inesperado, garantimos que `propriedades` ainda esteja disponível
        props_list = list(props) if not isinstance(props, list) else props
        for p in props_list:
            p.is_favorito = False

    # Lista de amenidades selecionadas para marcar checkboxes no template
    selected_amenities = request.GET.getlist("amenities")
    return render(
        request,
        "propriedades/lista.html",
        {
            "propriedades": props_list,
            "recomendadas": recomendadas,
            "selected_amenities": selected_amenities,
        },
    )

from .models import AMENITIES_CHOICES

def detalhe_propriedade(request, pk):
    prop = get_object_or_404(Propriedade, pk=pk)
    return render(request, "propriedades/detalhe.html", {"propriedade": prop, "amenities_choices": AMENITIES_CHOICES})

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
