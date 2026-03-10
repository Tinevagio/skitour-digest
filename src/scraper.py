import requests
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


def fetch_sortie_detail(sortie_id: str, api_key: str) -> str:
    """Récupère le compte-rendu complet d'une sortie via /api/sortie/{id}."""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/sortie/{sortie_id}",
            headers=_headers(api_key),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        # Le CR est dans "texte" ou "resume" selon la version de l'API
        texte = data.get("texte") or data.get("resume") or ""
        # Conditions liées à la sortie
        conditions = data.get("conditions", [])
        cond_texte = ""
        if conditions:
            c = conditions[0]
            cond_texte = c.get("texte") or c.get("resume") or ""
        full = f"{texte}\n{cond_texte}".strip()
        return full[:700]
    except Exception:
        return ""


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

        # Texte de base depuis le flux
        resume = (s.get("texte") or s.get("resume") or "").strip()

        # Si vide, on va chercher le détail complet
        if not resume and sortie_id:
            resume = fetch_sortie_detail(sortie_id, api_key)

        result.append({
            "id":       sortie_id,
            "date":     s.get("date", ""),
            "title":    s.get("titre", s.get("title", "")),
            "massif":   MASSIFS.get(massif_id, f"Massif {massif_id}"),
            "cotation": s.get("dif_ski", ""),
            "denivele": s.get("denivele", ""),
            "auteur":   auteur,
            "resume":   resume[:700],
            "link":     f"{BASE_URL}/sorties/{sortie_id}",
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
        texte = (c.get("texte") or c.get("resume") or "").strip()
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
