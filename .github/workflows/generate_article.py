import os
import json
import re
from datetime import date
from google import genai

# =========================
# CONFIGURATION
# =========================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY est introuvable.")

client = genai.Client(api_key=api_key)

# =========================
# GENERATION DE L'ARTICLE
# =========================

prompt = """
Tu es journaliste pour TechNews, un site français consacré à la technologie.

Crée un article original sur un sujet intéressant concernant l'intelligence
artificielle.

IMPORTANT :
- Ne fabrique pas de chiffres, de citations ou de faits précis.
- Le texte doit être naturel et agréable à lire.
- Environ 700 mots.
- Le titre doit être accrocheur mais sérieux.
- Le contenu doit être adapté à un site d'actualité technologique.

Retourne UNIQUEMENT un JSON valide avec exactement ces champs :

{
  "titre": "...",
  "categorie": "Intelligence artificielle",
  "chapeau": "...",
  "sections": [
    {
      "titre": "...",
      "paragraphes": ["...", "..."]
    }
  ],
  "conclusion": "..."
}
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json"
    }
)

texte = response.text.strip()

# Retirer d'éventuels ```json ... ```
texte = re.sub(r"^```json\s*", "", texte)
texte = re.sub(r"\s*```$", "", texte)

data = json.loads(texte)

titre = data["titre"]
categorie = data["categorie"]
chapeau = data["chapeau"]
sections = data["sections"]
conclusion = data["conclusion"]

# =========================
# DATE ET NOM DU FICHIER
# =========================

date_du_jour = date.today().isoformat()

slug = re.sub(r"[^a-z0-9]+", "-", titre.lower())
slug = slug.strip("-")

nom_fichier = f"article-{date_du_jour}-{slug}.html"

# =========================
# IMAGE
# =========================

# Image de test pour la catégorie IA.
# Nous remplacerons ensuite cette partie par une génération
# automatique d'images.

image = (
    "https://images.unsplash.com/"
    "photo-1677442136019-21780ecad995"
    "?auto=format&fit=crop&w=1200&q=80"
)

# =========================
# CONSTRUCTION DU CONTENU
# =========================

contenu = ""

for section in sections:
    contenu += f"""
<h2>
{section["titre"]}
</h2>
"""

    for paragraphe in section["paragraphes"]:
        contenu += f"""
<p>
{paragraphe}
</p>
"""

contenu += f"""
<h2>
Conclusion
</h2>

<p>
{conclusion}
</p>
"""

# =========================
# HTML COMPLET
# =========================

html = f"""<!DOCTYPE html>
<html lang="fr">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>TechNews - {titre}</title>

<link rel="stylesheet" href="../style.css">

</head>

<body>

<header>

<div class="header">

<h1>TechNews</h1>

<p>
L'actualité des technologies, de l'IA et du numérique
</p>

</div>

<nav>

<a href="../index.html">Accueil</a>
<a href="../ia.html">IA</a>
<a href="../smartphones.html">Smartphones</a>
<a href="../jeux.html">Gaming</a>
<a href="../cybersecurite.html">Cybersécurité</a>

</nav>

</header>

<main>

<article class="article-page">

<img
src="{image}"
class="article-image"
alt="{titre}"
>

<h1>
{titre}
</h1>

<p class="date">
{date_du_jour} • {categorie}
</p>

<p class="chapeau">

<strong>
{chapeau}
</strong>

</p>

{contenu}

</article>

</main>

<div class="reaction-box">

<h4>
Votre avis sur cet article ?
</h4>

<div class="reaction-buttons">

<button class="like-btn" onclick="aimerArticle(this)">
👍
<span>J'aime</span>
</button>

<button class="dislike-btn" onclick="retirerFavori(this)">
👎
<span>Je n'aime pas</span>
</button>

</div>

<div class="favorite-box">

<button
class="favorite-btn"
onclick="ajouterFavori(
'{titre.replace("'", "\\'")}',
'../ia.html',
'{image}'
)"
>
⭐ Ajouter aux favoris
</button>

</div>

</div>

<footer>

<p>
© 2026 TechNews - Tous droits réservés
</p>

</footer>

<script src="../script.js"></script>

</body>

</html>
"""

# =========================
# CREATION DU DOSSIER
# =========================

os.makedirs("articles", exist_ok=True)

chemin = os.path.join("articles", nom_fichier)

with open(chemin, "w", encoding="utf-8") as fichier:
    fichier.write(html)

print("====================================")
print("Article créé avec succès !")
print(f"Fichier : {chemin}")
print(f"Titre   : {titre}")
print("====================================")
