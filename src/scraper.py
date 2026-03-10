import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

BASE_URL = "https://www.skitour.fr"

# Identifiants de massifs skitour (à adapter selon ta région)
# Exemples : 1=Belledonne, 2=Chartreuse, 3=Vercors, 4=Écrins, 5=Mercantour, etc.
# Voir https://www.skitour.fr/sorties/
MASSIFS = {
    1: "Belledonne",
    4: "Écrins",
    # Ajoute tes massifs ici
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SkitourDigest/1.0; contact: ton@email.com)"
}


def fetch_recent_sorties(massif_id: int, days_back: int = 2) -> list[dict]:
    """Scrape les sorties récentes d'un massif."""
    url = f"{BASE_URL}/sorties/liste/?massif={massif_id}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    sorties = []
    cutoff = datetime.now() - timedelta(days=days_back)

    rows = soup.select("table.liste tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        # Date
        date_text = cells[0].get_text(strip=True)
        try:
            date = datetime.strptime(date_text, "%d/%m/%Y")
        except ValueError:
            continue
        if date < cutoff:
            continue

        # Titre + lien
        title_cell = cells[1]
        link_tag = title_cell.find("a")
        title = link_tag.get_text(strip=True) if link_tag else title_cell.get_text(strip=True)
        link = BASE_URL + link_tag["href"] if link_tag and link_tag.get("href") else ""

        # Cotation / infos
        cotation = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        auteur = cells[3].get_text(strip=True) if len(cells) > 3 else ""

        sortie = {
            "date": date.strftime("%d/%m/%Y"),
            "title": title,
            "link": link,
            "cotation": cotation,
            "auteur": auteur,
            "massif": MASSIFS.get(massif_id, f"Massif {massif_id}"),
        }

        # Récupère le détail si on a un lien
        if link:
            sortie["detail"] = fetch_sortie_detail(link)

        sorties.append(sortie)

    return sorties


def fetch_sortie_detail(url: str) -> str:
    """Récupère le texte de description d'une sortie."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Le compte-rendu est généralement dans un div avec classe "cr" ou "texte"
        for selector in ["div.cr", "div.texte", "div#cr", "article"]:
            block = soup.select_one(selector)
            if block:
                text = block.get_text(separator=" ", strip=True)
                # Limiter à 800 chars pour éviter les prompts trop longs
                return text[:800]
    except Exception:
        pass
    return ""


def fetch_conditions_nivo(massif_id: int) -> str:
    """Récupère les dernières conditions nivologiques du massif."""
    url = f"{BASE_URL}/conditions/?massif={massif_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Cherche le dernier bulletin de conditions
        for selector in ["div.conditions", "div.bulletin", "div.texte", "article"]:
            block = soup.select_one(selector)
            if block:
                text = block.get_text(separator=" ", strip=True)
                return text[:1000]
    except Exception:
        pass
    return ""


def collect_all_data(massif_ids: list[int]) -> dict:
    """Collecte toutes les données pour les massifs demandés."""
    data = {}
    for mid in massif_ids:
        name = MASSIFS.get(mid, f"Massif {mid}")
        print(f"  → Scraping {name}...")
        data[name] = {
            "sorties": fetch_recent_sorties(mid),
            "conditions": fetch_conditions_nivo(mid),
        }
    return data
