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
    """Appelle l'API Groq (gratuite) pour générer le résumé."""
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
