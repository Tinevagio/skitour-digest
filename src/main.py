#!/usr/bin/env python3
"""
Skitour Daily Digest
API skitour.fr → résumé IA → email quotidien
"""

import os
import sys
from scraper import collect_all_data, MASSIFS
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

    # --- Config depuis les variables d'environnement ---
    skitour_api_key = get_env("SKITOUR_API_KEY")
    groq_api_key  = get_env("GROQ_API_KEY")

    smtp_config = {
        "smtp_host":     get_env("SMTP_HOST"),
        "smtp_port":     get_env("SMTP_PORT"),
        "smtp_user":     get_env("SMTP_USER"),
        "smtp_password": get_env("SMTP_PASSWORD"),
        "from_email":    get_env("FROM_EMAIL"),
        "to_emails":     [e.strip() for e in get_env("TO_EMAILS").split(",")],
    }

    # IDs des massifs (variables GitHub, ex: "1,4")
    massif_ids_raw = get_env("MASSIF_IDS", required=False) or "1,4"
    massif_ids = [int(x.strip()) for x in massif_ids_raw.split(",") if x.strip().isdigit()]
    print(f"  Massifs : {[MASSIFS.get(m, str(m)) for m in massif_ids]}")

    # --- API skitour ---
    print("📡 Récupération via API skitour.fr...")
    data = collect_all_data(massif_ids, skitour_api_key)

    total_sorties = sum(len(v["sorties"]) for v in data.values())
    print(f"  {total_sorties} sortie(s) récente(s) trouvée(s)")

    if total_sorties == 0:
        summary = ("Aucune sortie récente trouvée sur skitour.fr pour les massifs surveillés. "
                   "Pas de conditions à rapporter aujourd'hui.")
    else:
        print("🤖 Génération du résumé (Groq)...")
        summary = generate_summary(data, groq_api_key)
        print(f"  Résumé : {len(summary.split())} mots")

    print("📧 Envoi de l'email...")
    massif_names = [MASSIFS.get(m, str(m)) for m in massif_ids]
    send_email(summary, massif_names, smtp_config)

    print("✅ Digest envoyé avec succès !")


if __name__ == "__main__":
    main()
