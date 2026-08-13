import os
import json
import re
from datetime import date
from html import escape

from google import genai


# ============================================================
# 1. CONNEXION À GEMINI
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("La variable GEMINI_API_KEY est introuvable.")

client = genai.Client(api_key=api_key)


# ============================================================
# 2. DEMANDE À GEMINI
# ============================================================

prompt = """
Tu es le rédacteur du site TechNews.

Écris un article en français sur l'intelligence artificielle et les
nouvelles technologies.

L'article doit être intéressant pour les lecteurs d'un site technologique.

Règles :
- environ 700 mots
- titre accrocheur mais sérieux
- introduction courte
- plusieurs parties avec des sous-titres
- paragraphes courts
- conclusion
- style journalistique naturel
- ne pas inventer de chiffres
- ne pas inventer de citations
- ne pas prétendre qu'une information est récente si tu n'en es pas sûr

Réponds UNIQUEMENT avec ce JSON :

{
  "titre": "titre de l'article",
  "categorie": "Intelligence artificielle",
  "chapeau": "courte introduction de l'article",
  "sections": [
    {
      "titre": "titre de la première partie",
      "paragraphes": [
        "premier paragraphe",
        "deuxième paragraphe"
      ]
    },
    {
      "titre": "titre de la deuxième partie",
      "paragraphes": [
        "premier paragraphe",
        "deuxième paragraphe"
      ]
    }
  ],
  "conclusion": "conclusion de l'article"
}
"""


# ============================================================
# 3. GÉNÉRATION
# ============================================================

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

texte = response.text.strip()

if not texte:
    raise RuntimeError("Gemini n'a retourné aucun texte.")


# ============================================================
# 4. NETTOYAGE DU JSON
# ============================================================

# Gemini peut parfois entourer le JSON avec ```json ... ```
if texte.startswith("```"):
    texte = re.sub(r"^```(?:json)?\s*", "", texte)
    texte = re.sub(r"\s*```$", "", texte)

try:
    data = json.loads(texte)

except json.JSONDecodeError as erreur:
    print("Réponse reçue de Gemini :")
    print(texte)
    raise RuntimeError(
        f"Impossible de lire le JSON généré par Gemini : {erreur}"
    )


# ============================================================
# 5. VÉRIFICATION
# ============================================================

champs_obligatoires = [
    "titre",
    "categorie",
    "chapeau",
    "sections",
    "conclusion"
]

for champ in champs_obligatoires:
    if champ not in data:
        raise RuntimeError(
            f"Le champ obligatoire '{champ}' manque dans la réponse Gemini."
        )


titre = str(data["titre"]).strip()
categorie = str(data["categorie"]).strip()
chapeau = str(data["chapeau"]).strip()
sections = data["sections"]
conclusion = str(data["conclusion"]).strip()

if not titre:
    raise RuntimeError("Le titre est vide.")

if not sections:
    raise RuntimeError("Aucune section n'a été générée.")


# ============================================================
# 6. DATE
# ============================================================

date_du_jour = date.today().strftime("%d/%m/%Y")


# ============================================================
# 7. CRÉATION DU NOM DU FICHIER
# ============================================================

slug = titre.lower()

remplacements = {
    "à": "a",
    "â": "a",
    "ä": "a",
    "é": "e",
    "è": "e",
    "ê": "e",
    "ë": "e",
    "î": "i",
    "ï": "i",
    "ô": "o",
    "ö": "o",
    "ù": "u",
    "û": "u",
    "ü": "u",
    "ç": "c",
    "œ": "oe",
    "æ": "ae"
}

for ancien, nouveau in remplacements.items():
    slug = slug.replace(ancien, nouveau)

slug = re.sub(r"[^a-z0-9]+", "-", slug)
slug = slug.strip("-")

# Évite un nom de fichier trop long
slug = slug[:70].rstrip("-")

date_fichier = date.today().isoformat()

nom_fichier = f"article-{date_fichier}-{slug}.html"


# ============================================================
# 8. IMAGE
# ============================================================

# Image temporaire pour notre premier test.
# Elle sera remplacée ensuite par le système d'images automatique.

image = (
    "https://images.unsplash.com/"
    "photo-1677442136019-21780ecad995"
    "?auto=format&fit=crop&w=1200&q=80"
)


# ============================================================
# 9. CONSTRUCTION DES SECTIONS HTML
# ============================================================

contenu_sections = ""

for section in sections:

    titre_section = escape(
        str(section.get("titre", "")).strip()
    )

    if not titre_section:
        continue

    contenu_sections += f"""
<h2>
{titre_section}
</h2>
"""

    paragraphes = section.get("paragraphes", [])

    for paragraphe in paragraphes:

        paragraphe = escape(
            str(paragraphe).strip()
        )

        if paragraphe:
            contenu_sections += f"""
<p>
{paragraphe}
</p>
"""


# ============================================================
# 10. PROTECTION DES TEXTES HTML
# ============================================================

titre_html = escape(titre)
categorie_html = escape(categorie)
chapeau_html = escape(chapeau)
conclusion_html = escape(conclusion)


# ============================================================
# 11. HTML DE L'ARTICLE
# ============================================================

html = f"""<!DOCTYPE html>
<html lang="fr">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>TechNews - {titre_html}</title>

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
alt="{titre_html}"
>


<h1>
{titre_html}
</h1>


<p class="date">
{date_du_jour} • {categorie_html}
</p>


<p class="chapeau">

<strong>
{chapeau_html}
</strong>

</p>


{contenu_sections}


<h2>
Conclusion
</h2>


<p>
{conclusion_html}
</p>


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
'{titre_html.replace("'", "\\'")}',
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


# ============================================================
# 12. CRÉATION DU DOSSIER ARTICLES
# ============================================================

os.makedirs("articles", exist_ok=True)


# ============================================================
# 13. ÉCRITURE DU FICHIER
# ============================================================

chemin = os.path.join(
    "articles",
    nom_fichier
)

with open(
    chemin,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(html)


# ============================================================
# 14. MESSAGE FINAL
# ============================================================

print("")
print("==============================================")
print("       ARTICLE TECHNEWS CRÉÉ AVEC SUCCÈS")
print("==============================================")
print("")
print(f"Titre     : {titre}")
print(f"Catégorie : {categorie}")
print(f"Date      : {date_du_jour}")
print(f"Fichier   : {chemin}")
print("")
print("==============================================")
