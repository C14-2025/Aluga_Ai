import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

LOG_DIR = Path(__file__).resolve().parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'predictions.log'

def _record_line(data: Dict[str, Any]) -> None:
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception:
        # Não quebrar o fluxo de predição por erros de I/O
        pass

def log_prediction(input_features: Dict[str, Any], predicted: float, method: str, details: Dict[str, Any] | None = None, metadata: Dict[str, Any] | None = None) -> None:
    payload = {
        'ts': datetime.utcnow().isoformat() + 'Z',
        'input': input_features,
        'predicted': float(predicted),
        'method': method,
        'details': details or {},
        'metadata': metadata or {},
    }
    _record_line(payload)

def read_last(n: int = 20):
    """Retorna as últimas n linhas do log (decode de JSON)."""
    out = []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines[-n:]:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    except FileNotFoundError:
        return []
    return out
