import json
import os
from functools import lru_cache
from typing import List, Dict, Any

def _resolve_json_path() -> str:
    # 1) Env var tem prioridade
    env_path = os.environ.get('ALUGAAI_DADOS_JSON')
    if env_path and os.path.exists(env_path):
        return env_path

    # 2) settings.AI_DADOS_JSON_PATH (opcional)
    try:
        from django.conf import settings  # type: ignore
        conf_path = getattr(settings, 'AI_DADOS_JSON_PATH', None)
        if conf_path and os.path.exists(conf_path):
            return conf_path
    except Exception:
        pass

    # 3) Caminho relativo por nome de pasta "Dados/imoveis_gerados.json"
    cur = os.path.dirname(os.path.abspath(__file__))
    while True:
        candidate = os.path.join(cur, 'Dados', 'imoveis_gerados.json')
        if os.path.exists(candidate):
            return candidate

        # Alternativa quando a raiz se chama Aluga_Ai
        if os.path.basename(cur).lower() == 'aluga_ai':
            alt = os.path.join(cur, 'aluga_ai_web', 'Dados', 'imoveis_gerados.json')
            if os.path.exists(alt):
                return alt

        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    raise FileNotFoundError(
        "Não foi possível localizar Dados/imoveis_gerados.json. "
        "Defina ALUGAAI_DADOS_JSON ou settings.AI_DADOS_JSON_PATH."
    )

@lru_cache(maxsize=1)
def load_raw() -> List[Dict[str, Any]]:
    path = _resolve_json_path()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def iter_flattened() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for idx, r in enumerate(load_raw(), start=1):
        end = r.get('endereco', {}) or {}
        items.append({
            'id': idx,
            'tipo': r.get('tipo'),
            'cidade': end.get('cidade'),
            'bairro': end.get('bairro', '') or '',
            'area_m2': float(r.get('area_m2') or 0.0),
            'quartos': int(r.get('quartos') or 0),
            'banheiros': int(r.get('banheiros') or 0),
            'vagas_garagem': int(r.get('vagas_garagem') or 0),
            'preco_aluguel': float(r.get('preco_aluguel') or 0.0),
            'condominio': float(r.get('condominio') or 0.0),
            'iptu': float(r.get('iptu') or 0.0),
            'status': r.get('status') or 'ativo',
        })
    return items
