import requests
from datetime import datetime


def build_prompt(data: dict) -> str:
    """Construit le prompt à envoyer à Claude à partir des données scrapées."""
    today = datetime.now().strftime("%A %d %B %Y")
    lines = [f"Voici les données récentes de skitour.fr pour le {today}.\n"]

    for massif, content in data.items():
        lines.append(f"## Massif : {massif}")

        conditions = content.get("conditions", "")
        if conditions:
            lines.append(f"**Conditions nivologiques :** {conditions[:500]}\n")

        sorties = content.get("sorties", [])
        if sorties:
            lines.append(f"**Sorties récentes ({len(sorties)}) :**")
            for s in sorties[:5]:  # Max 5 sorties par massif
                lines.append(
                    f"- [{s['date']}] {s['title']} (cot. {s['cotation']}) — par {s['auteur']}"
                )
                if s.get("detail"):
                    lines.append(f"  Compte-rendu : {s['detail'][:300]}")
        else:
            lines.append("Aucune sortie récente trouvée.")

        lines.append("")

    raw_data = "\n".join(lines)

    prompt = f"""{raw_data}

---

Tu es un assistant spécialisé ski de rando. À partir de ces données skitour.fr, rédige un résumé quotidien en français de 150 à 250 mots, structuré ainsi :

1. **Conditions générales** : enneigement, stabilité du manteau, températures si mentionnés
2. **Sorties notables** : 2-3 sorties marquantes avec leurs conditions terrain
3. **Tendance** : ce qu'on peut en déduire pour les prochains jours / ce à quoi s'attendre

Ton ton est direct, utile, comme un topo partagé entre randonneurs. Pas de remplissage. Mentionne les massifs concernés. Si les données sont insuffisantes pour un massif, dis-le brièvement.

Réponds UNIQUEMENT avec le résumé, sans intro ni outro.
"""
    return prompt


def generate_summary(data: dict, api_key: str) -> str:
    """Appelle l'API Gemini Flash (gratuite) pour générer le résumé."""
    prompt = build_prompt(data)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 600, "temperature": 0.4},
    }

    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data_resp = resp.json()

    return data_resp["candidates"][0]["content"]["parts"][0]["text"]
