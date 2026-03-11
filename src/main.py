#!/usr/bin/env python3
"""
Skitour Daily Digest
API skitour.fr → résumé IA → un email par groupe de massifs
"""

import os
import sys
from scraper import collect_group_data, get_groups_for_ids, MASSIFS
from summarizer import generate_summary
from emailer import send_email


def get_env(key: str, required: bool = True) -> str:
    val = os.environ.get(key, "").strip()
    if required and not val:
        print(f"❌ Variable d'environnement manquante : {key}")
        sys.exit(1)
    return val


def main():
    print("🎿 Skitour Digest — démarrage")

    skitour_api_key = get_env("SKITOUR_API_KEY")
    groq_api_key    = get_env("GROQ_API_KEY")

    smtp_config = {
        "smtp_host":     get_env("SMTP_HOST"),
        "smtp_port":     get_env("SMTP_PORT"),
        "smtp_user":     get_env("SMTP_USER"),
        "smtp_password": get_env("SMTP_PASSWORD"),
        "from_email":    get_env("FROM_EMAIL"),
        "to_emails":     [e.strip() for e in get_env("TO_EMAILS").split(",")],
    }

    massif_ids_raw = os.environ.get("MASSIF_IDS", "").strip()
    print(f"  MASSIF_IDS lu : '{massif_ids_raw}'")
    if not massif_ids_raw:
        massif_ids_raw = "1,4"
        print("  ⚠️  MASSIF_IDS vide, défaut : 1,4")

    massif_ids = [int(x.strip()) for x in massif_ids_raw.split(",") if x.strip().isdigit()]

    # Groupe les massifs par région
    groups = get_groups_for_ids(massif_ids)
    print(f"  Groupes : {list(groups.keys())}")

    emails_sent = 0

    for group_name, group_ids in groups.items():
        print(f"\n📍 Groupe : {group_name} ({[MASSIFS.get(m, str(m)) for m in group_ids]})")

        print("  📡 Récupération API skitour...")
        data = collect_group_data(group_ids, skitour_api_key)

        total = sum(len(v["sorties"]) for v in data.values())
        print(f"  {total} sortie(s) trouvée(s)")

        if total == 0:
            summary = (f"Aucune sortie récente trouvée sur skitour.fr "
                       f"pour les massifs de {group_name}.")
        else:
            print("  🤖 Génération du résumé (Groq)...")
            summary = generate_summary(data, groq_api_key)
            print(f"  Résumé : {len(summary.split())} mots")

        print("  📧 Envoi de l'email...")
        massif_names = [MASSIFS.get(m, str(m)) for m in group_ids]
        send_email(summary, massif_names, smtp_config, group_name)
        emails_sent += 1

    print(f"\n✅ {emails_sent} email(s) envoyé(s) avec succès !")


if __name__ == "__main__":
    main()
