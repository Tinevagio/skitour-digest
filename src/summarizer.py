import requests
import time
from datetime import datetime


def build_prompt(data: dict) -> str:
    """Construit le prompt à envoyer à Gemini à partir des données skitour."""
    today = datetime.now().strftime("%A %d %B %Y")
    lines = [f"Voici les données récentes de skitour.fr pour le {today}.\n"]

    for massif, content in data.items():
        lines.append(f"## Massif : {massif}")

        conditions = content.get("conditions", [])
        if conditions:
            for c in conditions[:2]:
                lines.append(f"**Conditions [{c.get('date','')}] :** {c.get('texte','')[:400]}\n")

        sorties = content.get("sorties", [])
        if sorties:
            lines.append(f"**Sorties récentes ({len(sorties)}) :**")
            for s in sorties[:5]:
                lines.append(
                    f"- [{s['date']}] {s['title']} (cot. {s['cotation']}, D+ {s['denivele']}m) — par {s['auteur']}"
                )
                if s.get("resume"):
                    lines.append(f"  {s['resume'][:300]}")
        else:
            lines.append("Aucune sortie récente trouvée.")

        lines.append("")

    raw_data = "\n".join(lines)

    return f"""{raw_data}

---

Tu es un assistant spécialisé ski de rando. À partir de ces données skitour.fr, rédige un résumé quotidien en français de 150 à 250 mots, structuré ainsi :

1. **Conditions générales** : enneigement, stabilité du manteau, températures si mentionnés
2. **Sorties notables** : 2-3 sorties marquantes avec leurs conditions terrain
3. **Tendance** : ce qu'on peut en déduire pour les prochains jours / ce à quoi s'attendre

Ton ton est direct, utile, comme un topo partagé entre randonneurs. Pas de remplissage. Mentionne les massifs concernés. Si les données sont insuffisantes pour un massif, dis-le brièvement.

Réponds UNIQUEMENT avec le résumé, sans intro ni outro.
"""


def generate_summary(data: dict, api_key: str) -> str:
    """Appelle l'API Gemini avec retry automatique sur 429."""
    prompt = build_prompt(data)

    # On essaie gemini-1.5-flash en priorité (limites gratuites plus souples),
    # puis gemini-2.0-flash en fallback
    models = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 600, "temperature": 0.4},
    }

    for model in models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        # 3 tentatives avec backoff exponentiel
        for attempt in range(3):
            resp = requests.post(url, json=payload, timeout=30)

            if resp.status_code == 429:
                wait = 15 * (2 ** attempt)   # 15s, 30s, 60s
                print(f"  ⚠️  Rate limit ({model}), attente {wait}s...")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data_resp = resp.json()
            print(f"  ✓ Résumé généré avec {model}")
            return data_resp["candidates"][0]["content"]["parts"][0]["text"]

        print(f"  ✗ {model} indisponible, essai du modèle suivant...")

    raise RuntimeError("Tous les modèles Gemini sont indisponibles (rate limit). Réessaie dans quelques minutes.")
