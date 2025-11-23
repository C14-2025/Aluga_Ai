import os
import csv
from typing import List, Dict, Optional

BASE_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(os.path.dirname(BASE_APP_DIR), 'data', 'sample_properties.csv')

def _load_sample_candidates() -> List[Dict]:
    """Retorna candidatos de amostra do CSV (mantido por compatibilidade)."""
    items = []
    if not os.path.exists(DATA_CSV):
        return items
    with open(DATA_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append({
                "id": int(row["id"]),
                "title": row["title"],
                "city": row["city"],
                "neighborhood": row.get("neighborhood", "") or "",
                "area": float(row["area"]),
                "bedrooms": int(row["bedrooms"]),
                "bathrooms": int(row["bathrooms"]),
                "parking": int(row["parking"]),
                "property_type": row["property_type"],
            })
    return items


def _load_candidates_from_db() -> List[Dict]:
    """Carrega candidatos diretamente do modelo Propriedade no banco.

    Mapeia campos do modelo `propriedades.Propriedade` para o formato esperado
    pelo recommender (id, title, city, neighborhood, area, bedrooms, bathrooms, parking, property_type).
    """
    try:
        from propriedades.models import Propriedade
    except Exception:
        return []

    qs = Propriedade.objects.filter(ativo=True)
    items: List[Dict] = []
    def _normalize_type(value: str) -> str:
        if not value:
            return 'apartment'
        v = str(value).strip().lower()
        mapping = {
            'apartamento': 'apartment',
            'apartment': 'apartment',
            'studio': 'studio',
            'kitnet': 'kitnet',
            'casa': 'house',
            'house': 'house',
        }
        return mapping.get(v, v)

    def _to_pt_type(value: str) -> str:
        if not value:
            return 'Apartamento'
        v = str(value).strip().lower()
        mapping = {
            'apartment': 'Apartamento',
            'apartamento': 'Apartamento',
            'studio': 'Studio',
            'kitnet': 'Kitnet',
            'house': 'Casa',
            'casa': 'Casa',
        }
        return mapping.get(v, value)

    for p in qs:
        # mapear mínimos; alguns campos podem não existir exatamente — usar defaults
        ptype_raw = getattr(p, 'tipo', getattr(p, 'property_type', 'apartment'))
        items.append({
            "id": int(getattr(p, 'id')),
            "title": getattr(p, 'titulo', str(p)),
            "city": getattr(p, 'city', '') or '',
            "neighborhood": getattr(p, 'endereco', '') or '',
            # área e contagens podem não existir; tentar extrair de campos comuns
            "area": float(getattr(p, 'area_m2', getattr(p, 'area', 0) or 0)),
            "bedrooms": int(getattr(p, 'quartos', getattr(p, 'bedrooms', 0) or 0)),
            "bathrooms": int(getattr(p, 'banheiros', getattr(p, 'bathrooms', 0) or 0)),
            "parking": int(getattr(p, 'vagas_garagem', getattr(p, 'parking', 0) or 0)),
            "property_type": _normalize_type(ptype_raw),
            "tipo": getattr(p, 'tipo', None) or _to_pt_type(ptype_raw),
            # campos específicos do app
            "price": float(getattr(p, 'preco_por_noite', 0) or 0),
            "amenities": list(getattr(p, 'comodidades', []) or []),
        })
    return items

def recommend(model, candidates: Optional[List[Dict]], budget: float, city: Optional[str], limit: int = 10) -> List[Dict]:
    # Fonte de candidatos: prioridade para entrada explícita; depois banco; por fim CSV de amostra
    items = candidates if candidates else (_load_candidates_from_db() or _load_sample_candidates())
    if city:
        items = [x for x in items if x.get("city", "").lower() == city.lower()]

    out = []
    def en_to_pt_type(v: Optional[str]) -> str:
        if not v:
            return 'Apartamento'
        vv = str(v).strip().lower()
        mapping = {
            'apartment': 'Apartamento',
            'studio': 'Studio',
            'kitnet': 'Kitnet',
            'house': 'Casa',
        }
        return mapping.get(vv, v)
    for x in items:
        # Mapear candidatos para as features esperadas pelo modelo (PT-BR)
        features_model = {
            "tipo": x.get("tipo") or en_to_pt_type(x.get("property_type")),
            "cidade": x.get("city"),
            "area_m2": x.get("area") or 0.0,
            "quartos": x.get("bedrooms") or 0,
            "banheiros": x.get("bathrooms") or 0,
            "vagas_garagem": x.get("parking") or 0,
            "condominio": 0.0,
            "iptu": 0.0,
        }
        price, _method, _details = model.predict(features_model, return_details=False)
        diff = abs(price - budget)
        closeness = max(0.0, 1.0 - (diff / max(budget, 1.0)))  # 1 quando igual ao orçamento
        affordable_bonus = 0.2 if price <= budget else 0.0
        city_bonus = 0.1 if (city and x.get("city", "").lower() == city.lower()) else 0.0
        score = round(min(1.5, closeness + affordable_bonus + city_bonus), 4)
        out.append({
            "id": x["id"],
            "title": x["title"],
            "city": x["city"],
            "predicted_price": float(price),
            "score": float(score),
        })
    out.sort(key=lambda d: (d["score"], -d["predicted_price"] <= budget), reverse=True)
    return out[:limit]
