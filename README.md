# 🎿 Skitour Daily Digest

Résumé quotidien automatisé des sorties et conditions skitour.fr, envoyé par email chaque matin via GitHub Actions + Claude AI.

---

## Architecture

```
GitHub Actions (cron 7h) → scraper.py → summarizer.py (Claude) → emailer.py → 📧
```

---

## Installation

### 1. Fork / clone ce repo sur GitHub

### 2. Configure les massifs

Dans `src/scraper.py`, édite le dictionnaire `MASSIFS` avec les IDs de tes massifs :

| ID | Massif |
|----|--------|
| 1  | Belledonne |
| 2  | Chartreuse |
| 3  | Vercors |
| 4  | Écrins |
| 5  | Mercantour |
| 6  | Vanoise |
| 7  | Mont-Blanc |
| 8  | Aravis |

→ Trouve les IDs dans l'URL skitour.fr : `https://www.skitour.fr/sorties/liste/?massif=ID`

### 3. Ajoute les Secrets GitHub

Dans ton repo : **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Description | Exemple |
|--------|-------------|---------|
| `GEMINI_API_KEY` | Clé API Google AI Studio | `AIza...` |
| `SMTP_HOST` | Serveur SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP SSL | `465` |
| `SMTP_USER` | Login SMTP | `toi@gmail.com` |
| `SMTP_PASSWORD` | Mot de passe SMTP | voir ci-dessous |
| `FROM_EMAIL` | Expéditeur | `toi@gmail.com` |
| `TO_EMAILS` | Destinataires (virgule) | `toi@gmail.com,ami@gmail.com` |

Pour la variable (pas secret) :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `MASSIF_IDS` | IDs des massifs | `1,4` |

### 4. Config Gmail (recommandé)

Gmail nécessite un **mot de passe d'application** (pas ton vrai mot de passe) :
1. Active la validation en 2 étapes sur ton compte Google
2. Va sur https://myaccount.google.com/apppasswords
3. Crée un mot de passe pour "Mail" → utilise ce code 16 caractères comme `SMTP_PASSWORD`

### 5. Test manuel

Dans l'onglet **Actions** de GitHub → **Skitour Daily Digest** → **Run workflow**

---

## Structure du projet

```
skitour-digest/
├── .github/
│   └── workflows/
│       └── daily-digest.yml   # Cron GitHub Actions
├── src/
│   ├── main.py                # Point d'entrée
│   ├── scraper.py             # Scraping skitour.fr
│   ├── summarizer.py          # Résumé via Claude API
│   └── emailer.py             # Envoi email HTML
├── requirements.txt
└── README.md
```

---

## Personnalisation

**Changer l'heure d'envoi** : modifie le cron dans `.github/workflows/daily-digest.yml`
- `"0 6 * * *"` = 7h Paris (hiver, UTC+1)
- `"0 5 * * *"` = 7h Paris (été, UTC+2)

**Modifier le prompt** : édite `src/summarizer.py`, fonction `build_prompt()`

**Ajouter des massifs** : édite `MASSIFS` dans `src/scraper.py` et `MASSIF_IDS` dans les variables GitHub

---

## Coût estimé

- **GitHub Actions** : gratuit (2000 min/mois inclus, ce script utilise ~1 min/jour)
- **Gemini 2.0 Flash** : gratuit jusqu'à 1500 requêtes/jour (on en utilise 1)
- **Total** : 0 € 🎉

Clé API Gemini sur https://aistudio.google.com/apikey
