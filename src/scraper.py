import requests
from datetime import datetime

BASE_URL = "https://skitour.fr"

# Liste des massifs connus (source : https://skitour.fr/api/massifs)
# Pour la liste complète, appelle fetch_massifs() avec ta clé API.
MASSIFS = {
    # --- Isère ---
    1:  "Belledonne",
    2:  "Chartreuse",
    3:  "Vercors",
    # --- Savoie / Haute-Savoie ---
    4:  "Bauges",
    5:  "Mont-Blanc",
    # --- Hautes-Alpes ---
    7:  "Queyras",
    # --- Alpes Maritimes ---
    6:  "Mercantour",
}


def _headers(api_key: str) -> dict:
    return {"cle": api_key, "User-Agent": "SkitourDigest/2.0"}


def fetch_massifs(api_key: str) -> list[dict]:
    """Récupère la liste complète des massifs (utile pour trouver les IDs)."""
    resp = requests.get(f"{BASE_URL}/api/massifs", headers=_headers(api_key), timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_recent_sorties(massif_id: int, api_key: str, days: int = 2) -> list[dict]:
    """Récupère les sorties récentes d'un massif via l'API officielle."""
    params = {"m": massif_id, "j": days, "c": 1, "l": 10}
    resp = requests.get(f"{BASE_URL}/api/sorties", headers=_headers(api_key), params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    sorties_raw = data.get("sorties", data) if isinstance(data, dict) else data

    result = []
    for s in sorties_raw:
        auteur = s.get("auteur", "")
        if isinstance(auteur, dict):
            auteur = auteur.get("pseudo", "")
        result.append({
            "id":       s.get("id", ""),
            "date":     s.get("date", ""),
            "title":    s.get("titre", s.get("title", "")),
            "massif":   MASSIFS.get(massif_id, f"Massif {massif_id}"),
            "cotation": s.get("dif_ski", ""),
            "denivele": s.get("denivele", ""),
            "auteur":   auteur,
            "resume":   s.get("resume", s.get("texte", ""))[:600],
            "link":     f"{BASE_URL}/sorties/{s.get('id', '')}",
        })
    return result


def fetch_conditions_nivo(massif_id: int, api_key: str) -> list[dict]:
    """Récupère les conditions récentes du massif."""
    params = {"m": massif_id}
    resp = requests.get(f"{BASE_URL}/api/conditions", headers=_headers(api_key), params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    conditions_raw = data.get("conditions", data) if isinstance(data, dict) else data

    result = []
    for c in conditions_raw[:5]:
        auteur = c.get("auteur", "")
        if isinstance(auteur, dict):
            auteur = auteur.get("pseudo", "")
        result.append({
            "date":   c.get("date", ""),
            "texte":  c.get("texte", c.get("resume", ""))[:500],
            "auteur": auteur,
        })
    return result


def collect_all_data(massif_ids: list[int], api_key: str) -> dict:
    """Collecte toutes les données pour les massifs demandés."""
    data = {}
    for mid in massif_ids:
        name = MASSIFS.get(mid, f"Massif {mid}")
        print(f"  → {name}...")
        data[name] = {
            "sorties":    fetch_recent_sorties(mid, api_key),
            "conditions": fetch_conditions_nivo(mid, api_key),
        }
    return data
