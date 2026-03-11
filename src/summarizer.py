import requests
from datetime import datetime


def build_prompt(data: dict) -> str:
    today = datetime.now().strftime("%A %d %B %Y")
    lines = [f"Voici les données récentes de skitour.fr pour le {today}.\n"]

    for massif, content in data.items():
        lines.append(f"## Massif : {massif}")

        conditions = content.get("conditions", [])
        if conditions:
            for c in conditions[:2]:
                if c.get("texte"):
                    lines.append(f"**Conditions [{c.get('date','')}] par {c.get('auteur','')} :** {c['texte']}\n")

        sorties = content.get("sorties", [])
        if sorties:
            lines.append(f"**Sorties récentes ({len(sorties)}) :**")
            for s in sorties[:5]:
                lines.append(
                    f"- [{s['date']}] **{s['title']}** — {s['auteur']} | "
                    f"cot. {s['cotation']} | D+ {s['denivele']}m | skiabilité {s['skiabilite']}/5"
                )
                if s.get("conditions"):
                    lines.append(f"  Conditions : {s['conditions']}")
                if s.get("recit"):
                    lines.append(f"  Récit : {s['recit']}")
        else:
            lines.append("Aucune sortie récente trouvée.")

        lines.append("")

    return "\n".join(lines) + """
---

Tu es un assistant spécialisé ski de rando. À partir de ces données skitour.fr, rédige un résumé quotidien en français de 150 à 250 mots, structuré ainsi :

1. **Conditions générales** : enneigement, stabilité du manteau, températures, skiabilité
2. **Sorties notables** : 2-3 sorties marquantes avec leurs conditions terrain concrètes


Ton ton est direct et concret, comme un topo partagé entre randonneurs. Cite des détails précis tirés des récits (altitude de chaussage, qualité de neige, expositions). Pas de remplissage ni de recommandations génériques.

Réponds UNIQUEMENT avec le résumé, sans intro ni outro.
"""


def generate_summary(data: dict, api_key: str) -> str:
    """Appelle l'API Groq pour générer le résumé."""
    prompt = build_prompt(data)

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.4,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
