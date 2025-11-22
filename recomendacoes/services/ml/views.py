from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    PriceInputSerializer,
    PriceOutputSerializer,
    RecommendationInputSerializer,
    RecommendationOutputItemSerializer,
    SurveyInputSerializer,
)
from .services.model import PriceModel
from .services.recommender import recommend as reco_recommend


class PricePredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = PriceInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        model = PriceModel.instance()
        pred, method, details = model.predict(ser.validated_data, return_details=True)
        out = PriceOutputSerializer({
            "predicted_price": float(pred),
            "method": method,
            "details": {k: float(v) for k, v in (details or {}).items()} if details else None
        })
        return Response(out.data, status=status.HTTP_200_OK)


class RecommendationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RecommendationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        budget = serializer.validated_data["budget"]
        city = serializer.validated_data.get("city")
        limit = serializer.validated_data.get("limit", 10)
        candidates = serializer.validated_data.get("candidates")

        model = PriceModel.instance()
        items = reco_recommend(model=model, candidates=candidates, budget=budget, city=city, limit=limit)

        out = RecommendationOutputItemSerializer(items, many=True)
        return Response(out.data, status=status.HTTP_200_OK)


class SurveyRecommendationView(APIView):
    """Recebe respostas do usuário (survey) e retorna recomendações.

    Usa o conjunto de candidatos de amostra quando `candidates` não é enviado.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ser = SurveyInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        data = ser.validated_data
        budget = data.get('budget')
        city = data.get('city')
        neighborhood = data.get('neighborhood')
        ptype = data.get('property_type')
        min_area = data.get('min_area')
        max_area = data.get('max_area')
        bedrooms = data.get('bedrooms')
        bathrooms = data.get('bathrooms')
        parking = data.get('parking')
        limit = data.get('limit', 10)
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        amenities = set([a.strip().lower() for a in (data.get('amenities') or []) if a])

        # candidatos: banco primeiro; se vazio, CSV de amostra
        from .services.recommender import _load_candidates_from_db, _load_sample_candidates
        candidates = _load_candidates_from_db() or _load_sample_candidates()

        # filtrar por preferências do usuário
        def match(c):
            if city and c.get('city', '').lower() != city.lower():
                return False
            if neighborhood and c.get('neighborhood', '').lower() != neighborhood.lower():
                return False
            if ptype and c.get('property_type', '').lower() != ptype.lower():
                return False
            if min_area and c.get('area', 0) < min_area:
                return False
            if max_area and c.get('area', 0) > max_area:
                return False
            if bedrooms is not None and c.get('bedrooms', 0) < bedrooms:
                return False
            if bathrooms is not None and c.get('bathrooms', 0) < bathrooms:
                return False
            if parking is not None and c.get('parking', 0) < parking:
                return False
            # faixa de preço real da propriedade (quando disponível)
            price = c.get('price')
            if min_price is not None and isinstance(price, (int, float)) and price < min_price:
                return False
            if max_price is not None and isinstance(price, (int, float)) and price > max_price:
                return False
            # amenidades: exigir que o conjunto desejado esteja contido nas amenidades do candidato
            if amenities:
                cand_am = set([str(x).strip().lower() for x in (c.get('amenities') or [])])
                if not amenities.issubset(cand_am):
                    return False
            return True

        filtered = [c for c in candidates if match(c)]

        model = PriceModel.instance()
        items = reco_recommend(model=model, candidates=filtered or candidates, budget=budget, city=city, limit=limit)

        out = RecommendationOutputItemSerializer(items, many=True)
        return Response(out.data, status=status.HTTP_200_OK)


class RetrainView(APIView):
    """Endpoint para disparar ETL + treino. Somente staff/admin pode usar."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        # executar ETL e treino síncrono (pode demorar)
        try:
            from dados.etl import ETLPipeline
            from recomendacoes.train_model import ModelTrainer

            pipeline = ETLPipeline()
            out = pipeline.run()

            trainer = ModelTrainer()
            metrics = trainer.train_simple()

            return Response({
                'status': 'ok',
                'etl_output': str(out),
                'metrics': metrics,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def compute_personal_recommendations_for_user(user, limit: int = 10):
    """Compute personal recommendations for `user` and persist them.

    Returns a dict compatible with the view response: {'status':..., 'results': [...], 'avg_price': ...}
    """
    try:
        from favoritos.models import Favorito, UserRecommendation
        from propriedades.models import Propriedade
    except Exception:
        return {'status': 'error', 'detail': 'Imports failed', 'results': [], 'avg_price': 0.0}

    favs = Favorito.objects.filter(user=user).select_related('propriedade')
    if not favs:
        return {'status': 'empty', 'detail': 'Nenhum favorito; personalize adicionando alguns.', 'results': [], 'avg_price': 0.0}

    tipos = {}
    cidades = {}
    amenities_freq = {}
    prices = []
    for f in favs:
        p = f.propriedade
        t = (p.quartos, p.banheiros, p.vagas_garagem)
        tipo = (getattr(p, 'tipo', None) or 'Apartamento')
        tipos[tipo] = tipos.get(tipo, 0) + 1
        if p.city:
            cidades[p.city] = cidades.get(p.city, 0) + 1
        prices.append(float(p.preco_por_noite))
        for a in (p.comodidades or []):
            amenities_freq[a] = amenities_freq.get(a, 0) + 1

    avg_price = sum(prices) / len(prices) if prices else 0.0
    tipo_pref = max(tipos, key=tipos.get) if tipos else None
    cidade_pref = max(cidades, key=cidades.get) if cidades else None
    amenity_top = {a for a, c in amenities_freq.items() if c >= 2}

    # candidatos: ativos não favoritados
    cand_qs = Propriedade.objects.filter(ativo=True).exclude(id__in=[f.propriedade.id for f in favs])
    model = PriceModel.instance()
    results = []
    for p in cand_qs[:500]:
        features_model = {
            'tipo': getattr(p, 'tipo', tipo_pref),
            'cidade': p.city,
            'area_m2': p.area_m2 or 0,
            'quartos': p.quartos or 0,
            'banheiros': p.banheiros or 0,
            'vagas_garagem': p.vagas_garagem or 0,
            'condominio': float(p.condominio or 0),
            'iptu': float(p.iptu or 0),
        }
        pred, _method, _details = model.predict(features_model, return_details=False)
        budget_diff = abs(pred - avg_price)
        price_fit = max(0.0, 1.0 - (budget_diff / max(avg_price, 1.0)))
        sim = 0.0
        overlap = set()
        if tipo_pref and getattr(p, 'tipo', tipo_pref) == tipo_pref:
            sim += 0.3
        if cidade_pref and p.city and p.city == cidade_pref:
            sim += 0.2
        if amenity_top:
            overlap = amenity_top.intersection(set(p.comodidades or []))
            sim += 0.1 * min(len(overlap), 3)
        final_score = round(price_fit * 0.5 + sim * 0.5, 4)
        reasons = []
        if tipo_pref and getattr(p, 'tipo', tipo_pref) == tipo_pref:
            reasons.append('Tipo que você favoritou')
        if cidade_pref and p.city == cidade_pref:
            reasons.append('Cidade de seus favoritos')
        if overlap:
            reasons.append(f"Amenidades em comum: {', '.join(list(overlap)[:3])}")
        if price_fit > 0.7:
            reasons.append('Dentro da sua faixa de preço média')
        results.append({
            'id': p.id,
            'titulo': p.titulo,
            'predicted_price': pred,
            'score': final_score,
            'reasons': reasons,
        })

    # ordenar e limitar
    results.sort(key=lambda r: r['score'], reverse=True)
    top = results[:limit]

    # Persistir recomendações (limpa antigas da mesma fonte)
    try:
        UserRecommendation.objects.filter(user=user, source='personal').delete()
        bulk = [
            UserRecommendation(
                user=user,
                propriedade_id=r['id'],
                score=r['score'],
                predicted_price=float(r['predicted_price']),
                source='personal'
            ) for r in top
        ]
        UserRecommendation.objects.bulk_create(bulk, ignore_conflicts=True)
    except Exception:
        pass

    return {'status': 'ok', 'results': top, 'avg_price': avg_price}


class PersonalRecommendationView(APIView):
    """Recomendações personalizadas baseadas nos favoritos do usuário.

    Estratégia simples:
    - Extrai médias e modos dos favoritos (preço, tipo, cidade)
    - Calcula similaridade por tipo e amenidades
    - Combina com score do modelo de preço (proximidade ao orçamento médio)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        limit = int(request.data.get('limit', 10))
        out = compute_personal_recommendations_for_user(request.user, limit=limit)
        return Response(out, status=200)
