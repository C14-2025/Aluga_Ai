import os
import csv
from typing import List, Dict, Optional

BASE_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(os.path.dirname(BASE_APP_DIR), 'data', 'sample_properties.csv')

def _load_sample_candidates() -> List[Dict]:
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

def recommend(model, candidates: Optional[List[Dict]], budget: float, city: Optional[str], limit: int = 10) -> List[Dict]:
    items = candidates if candidates else _load_sample_candidates()
    if city:
        items = [x for x in items if x.get("city", "").lower() == city.lower()]

    out = []
    for x in items:
        features = {
            "city": x.get("city"),
            "neighborhood": x.get("neighborhood"),
            "area": x.get("area"),
            "bedrooms": x.get("bedrooms"),
            "bathrooms": x.get("bathrooms"),
            "parking": x.get("parking"),
            "property_type": x.get("property_type"),
        }
        price, _method, _details = model.predict(features, return_details=False)
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
