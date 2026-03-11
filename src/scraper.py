import requests
import re
from datetime import datetime

BASE_URL = "https://skitour.fr"

MASSIFS = {
    1: "Belledonne",
    2: "Chartreuse",
    3: "Vercors",
    4: "Bauges",
    5: "Mont-Blanc",
    6: "Mercantour",
    7: "Queyras",
}


def _headers(api_key: str) -> dict:
    return {"cle": api_key, "User-Agent": "SkitourDigest/2.0"}


def _clean(text: str) -> str:
    """Supprime les balises HTML et nettoie le texte."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_sortie_detail(sortie_id: str, api_key: str) -> dict:
    """Récupère recit + conditions d'une sortie via /api/sortie/{id}."""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/sortie/{sortie_id}",
            headers=_headers(api_key),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "recit":      _clean(data.get("recit", ""))[:600],
            "conditions": _clean(data.get("conditions", ""))[:500],
            "skiabilite": data.get("skiabilite", ""),
        }
    except Exception:
        return {"recit": "", "conditions": "", "skiabilite": ""}


def fetch_recent_sorties(massif_id: int, api_key: str, days: int = 3) -> list[dict]:
    """Récupère les sorties récentes d'un massif avec leurs détails."""
    params = {"m": massif_id, "j": days, "c": 1, "l": 10}
    resp = requests.get(
        f"{BASE_URL}/api/sorties",
        headers=_headers(api_key),
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    sorties_raw = data.get("sorties", data) if isinstance(data, dict) else data

    result = []
    for s in sorties_raw:
        auteur = s.get("auteur", "")
        if isinstance(auteur, dict):
            auteur = auteur.get("pseudo", "")

        sortie_id = str(s.get("id", ""))

        # recit et cond sont déjà dans le flux avec c=1
        recit      = _clean(s.get("recit", ""))[:600]
        conditions = _clean(s.get("cond",  ""))[:500]

        # Si vides, on appelle /api/sortie/{id}
        if not recit and not conditions and sortie_id:
            detail     = fetch_sortie_detail(sortie_id, api_key)
            recit      = detail["recit"]
            conditions = detail["conditions"]

        result.append({
            "id":         sortie_id,
            "date":       s.get("date", ""),
            "title":      _clean(s.get("titre", "")),
            "massif":     MASSIFS.get(massif_id, f"Massif {massif_id}"),
            "cotation":   s.get("dif_ski", ""),
            "denivele":   s.get("denivele", ""),
            "skiabilite": s.get("skiabilite", ""),
            "auteur":     auteur,
            "recit":      recit,
            "conditions": conditions,
            "link":       f"{BASE_URL}/sorties/{sortie_id}",
        })
    return result


def fetch_conditions_nivo(massif_id: int, api_key: str) -> list[dict]:
    """Récupère les conditions récentes du massif."""
    params = {"m": massif_id}
    resp = requests.get(
        f"{BASE_URL}/api/conditions",
        headers=_headers(api_key),
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    conditions_raw = data.get("conditions", data) if isinstance(data, dict) else data

    result = []
    for c in conditions_raw[:5]:
        auteur = c.get("auteur", "")
        if isinstance(auteur, dict):
            auteur = auteur.get("pseudo", "")
        texte = _clean(c.get("texte") or c.get("conditions") or c.get("resume") or "")
        result.append({
            "date":   c.get("date", ""),
            "texte":  texte[:500],
            "auteur": auteur,
        })
    return result


def collect_all_data(massif_ids: list[int], api_key: str) -> dict:
    data = {}
    for mid in massif_ids:
        name = MASSIFS.get(mid, f"Massif {mid}")
        print(f"  → {name}...")
        data[name] = {
            "sorties":    fetch_recent_sorties(mid, api_key),
            "conditions": fetch_conditions_nivo(mid, api_key),
        }
    return data
