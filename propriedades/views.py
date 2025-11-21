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
    # Recomendações no topo da home (SSR) usando o modelo atual
    # opção de data (sazonalidade)
    import datetime
    raw_date = request.GET.get('date')  # formato yyyy-mm-dd
    season_date = None
    try:
        if raw_date:
            season_date = datetime.datetime.strptime(raw_date, '%Y-%m-%d').date()
    except Exception:
        season_date = None

    try:
        from recomendacoes.services.ml.services.model import PriceModel
        from recomendacoes.services.ml.services.recommender import recommend as reco_recommend
        # sazonalidade simples
        season_factor_map = {1:1.15,2:1.10,3:1.05,4:1.00,5:1.00,6:1.08,7:1.20,8:1.18,9:1.04,10:1.03,11:1.07,12:1.25}
        def apply_season(price: float) -> float:
            if not season_date:
                return price
            return price * season_factor_map.get(season_date.month, 1.0)

        # orçamento/cidade opcionais via GET; defaults razoáveis
        try:
            budget = float(request.GET.get("budget", 500) or 500)
        except Exception:
            budget = 500.0
        city = (request.GET.get("city") or "").strip() or None

        model = PriceModel.instance()
        recs = reco_recommend(model=model, candidates=None, budget=budget, city=city, limit=6)
        # mapear para objetos do Django e anexar metadados
        id_to_prop = {p.id: p for p in Propriedade.objects.filter(id__in=[r["id"] for r in recs])}
        recomendadas = []
        for r in recs:
            p = id_to_prop.get(r["id"])
            if p is not None:
                base_pred = float(r.get("predicted_price") or 0.0)
                recomendadas.append({
                    "prop": p,
                    "predicted_price": apply_season(base_pred),
                    "score": r.get("score"),
                    "season_applied": bool(season_date),
                })

        # reordenar lista principal opcionalmente quando rank=recommend
        if (request.GET.get("rank") or "").lower() in ("1", "true", "recommend", "reco"):
            score_map = {r["id"]: r.get("score", 0.0) for r in recs}
            props = sorted(list(props), key=lambda p: score_map.get(p.id, 0.0), reverse=True)

    except Exception:
        recomendadas = []
        budget = None

    # Se usuário autenticado, tentar carregar recomendações personalizadas persistidas (substitui bloco genérico se existir)
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

    return render(request, "propriedades/lista.html", {"propriedades": props, "recomendadas": recomendadas, "reco_budget": budget, 'season_date': season_date})

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
