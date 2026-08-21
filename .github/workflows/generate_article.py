import os
import json
import re
import base64
from datetime import date
from html import escape

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY est introuvable."
    )

client = genai.Client(
    api_key=api_key
)


# ============================================================
# FONCTIONS
# ============================================================

def nettoyer_json(texte):

    texte = texte.strip()

    if texte.startswith("```json"):
        texte = texte[7:]

    elif texte.startswith("```"):
        texte = texte[3:]

    if texte.endswith("```"):
        texte = texte[:-3]

    return texte.strip()


def creer_slug(titre):

    titre = titre.lower()

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
        "ç": "c"
    }

    for ancien, nouveau in remplacements.items():
        titre = titre.replace(
            ancien,
            nouveau
        )

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        titre
    )

    return slug.strip("-")


# ============================================================
# DOSSIERS
# ============================================================

os.makedirs(
    "articles",
    exist_ok=True
)

os.makedirs(
    "articles/images",
    exist_ok=True
)


# ============================================================
# 1. GENERATION ARTICLE
# ============================================================

print("")
print("========================================")
print("GENERATION DE L'ARTICLE")
print("========================================")


prompt_article = """
Tu es journaliste pour TechNews, un site français consacré
à la technologie, à l'intelligence artificielle et au numérique.

Crée un article original sur un sujet intéressant concernant
l'intelligence artificielle.

Règles :

- environ 700 mots
- français naturel
- titre sérieux et accrocheur
- ne fabrique pas de chiffres
- ne fabrique pas de citations
- ne présente pas comme certain un fait incertain
- article adapté à un site d'actualité technologique

Retourne UNIQUEMENT un JSON valide avec exactement cette structure :

{
  "titre": "...",
  "categorie": "Intelligence artificielle",
  "chapeau": "...",
  "sections": [
    {
      "titre": "...",
      "paragraphes": [
        "...",
        "..."
      ]
    }
  ],
  "conclusion": "..."
}
"""


response_article = client.models.generate_content(

    model="gemini-3.6-flash",

    contents=prompt_article,

    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)


if not response_article.text:

    raise RuntimeError(
        "Gemini n'a retourne aucun article."
    )


texte_article = nettoyer_json(
    response_article.text
)


try:

    data = json.loads(
        texte_article
    )

except json.JSONDecodeError as erreur:

    print("Réponse Gemini :")
    print(response_article.text)

    raise RuntimeError(
        f"JSON article invalide : {erreur}"
    )


titre = str(
    data["titre"]
).strip()

categorie = str(
    data["categorie"]
).strip()

chapeau = str(
    data["chapeau"]
).strip()

sections = data["sections"]

conclusion = str(
    data["conclusion"]
).strip()


print("")
print("Titre genere :")
print(titre)


# ============================================================
# 2. DATE ET NOM
# ============================================================

date_du_jour = date.today().isoformat()

slug = creer_slug(
    titre
)

if not slug:

    slug = "article-ia"


nom_article = (
    f"article-{date_du_jour}-{slug}.html"
)

nom_image = (
    f"{date_du_jour}-{slug}.png"
)


chemin_article = os.path.join(
    "articles",
    nom_article
)

chemin_image = os.path.join(
    "articles",
    "images",
    nom_image
)


# ============================================================
# 3. GENERATION DE L'IMAGE
# ============================================================

print("")
print("========================================")
print("GENERATION DE L'IMAGE")
print("========================================")


prompt_image = f"""
Create a professional editorial image for a technology
news website.

The image must illustrate this article:

Title:
{titre}

Summary:
{chapeau}

Create a realistic, modern and professional technology
journalism image.

The subject must clearly relate to the article.

Requirements:

- realistic
- professional
- modern
- cinematic
- technology / artificial intelligence
- horizontal composition
- no text
- no words
- no letters
- no logos
- no watermark
"""


# IMPORTANT :
#
# AUCUN response_format ici.
#
# C'est volontaire.
# Cela évite complètement l'erreur
# GenerateContentConfig / response_format.


response_image = client.models.generate_content(

    model="gemini-3.1-flash-image",

    contents=prompt_image,

    config=types.GenerateContentConfig(

        response_modalities=[
            "IMAGE"
        ]

    )
)


# ============================================================
# 4. RECUPERATION IMAGE
# ============================================================

image_trouvee = False


for part in response_image.parts:

    if part.inline_data:

        print(
            "Image recue depuis Gemini."
        )

        image_bytes = part.inline_data.data

        if not image_bytes:

            raise RuntimeError(
                "Gemini a retourne une image vide."
            )

        with open(
            chemin_image,
            "wb"
        ) as fichier:

            fichier.write(
                image_bytes
            )

        image_trouvee = True

        break


if not image_trouvee:

    print("")
    print(
        "Réponse Gemini complète :"
    )

    print(
        response_image
    )

    raise RuntimeError(
        "Gemini n'a pas retourne de donnees image."
    )


print("")
print("Image sauvegardee :")
print(chemin_image)


# ============================================================
# 5. CONSTRUCTION ARTICLE
# ============================================================

contenu = ""


for section in sections:

    titre_section = escape(
        str(
            section["titre"]
        )
    )

    contenu += f"""
<h2>
{titre_section}
</h2>
"""

    for paragraphe in section["paragraphes"]:

        paragraphe_safe = escape(
            str(paragraphe)
        )

        contenu += f"""
<p>
{paragraphe_safe}
</p>
"""


contenu += f"""
<h2>
Conclusion
</h2>

<p>
{escape(conclusion)}
</p>
"""


# ============================================================
# 6. PAGE ARTICLE
# ============================================================

image_dans_article = (
    f"images/{nom_image}"
)


html_article = f"""<!DOCTYPE html>

<html lang="fr">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

<title>
TechNews - {escape(titre)}
</title>

<link
rel="stylesheet"
href="../style.css"
>

</head>

<body>

<header>

<div class="header">

<h1>
TechNews
</h1>

<p>
L'actualité des technologies, de l'IA et du numérique
</p>

</div>

<nav>

<a href="../index.html">
Accueil
</a>

<a href="../ia.html">
IA
</a>

<a href="../smartphones.html">
Smartphones
</a>

<a href="../gaming.html">
Gaming
</a>

<a href="../cybersecurite.html">
Cybersécurité
</a>

</nav>

</header>

<main>

<article class="article-page">

<img
src="{image_dans_article}"
class="article-image"
alt="{escape(titre)}"
>

<h1>
{escape(titre)}
</h1>

<p class="date">
{date_du_jour} • {escape(categorie)}
</p>

<p class="chapeau">

<strong>
{escape(chapeau)}
</strong>

</p>

{contenu}

</article>

</main>

<footer>

<p>
© 2026 TechNews - Tous droits réservés
</p>

</footer>

<script src="../script.js"></script>

</body>

</html>
"""


with open(
    chemin_article,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(
        html_article
    )


print("")
print("Article HTML cree :")
print(chemin_article)


# ============================================================
# 7. ARTICLES.JSON
# ============================================================

fichier_json = "articles.json"


if os.path.exists(
    fichier_json
):

    try:

        with open(
            fichier_json,
            "r",
            encoding="utf-8"
        ) as fichier:

            articles = json.load(
                fichier
            )

    except Exception:

        articles = []

else:

    articles = []


if not isinstance(
    articles,
    list
):

    articles = []


lien_article = (
    f"articles/{nom_article}"
)

image_index = (
    f"articles/images/{nom_image}"
)


nouvel_article = {

    "titre": titre,

    "description": chapeau,

    "categorie": categorie,

    "date": date_du_jour,

    "image": image_index,

    "lien": lien_article

}


# Eviter les doublons
articles = [

    article

    for article in articles

    if article.get("lien")
    != lien_article

]


articles.insert(
    0,
    nouvel_article
)


with open(
    fichier_json,
    "w",
    encoding="utf-8"
) as fichier:

    json.dump(
        articles,
        fichier,
        ensure_ascii=False,
        indent=4
    )


print(
    "articles.json mis a jour."
)


# ============================================================
# 8. AJOUT A L'ACCUEIL
# ============================================================

index_path = "index.html"


if not os.path.exists(
    index_path
):

    raise RuntimeError(
        "index.html est introuvable."
    )


with open(
    index_path,
    "r",
    encoding="utf-8"
) as fichier:

    index_html = fichier.read()


marqueur = (
    '<div id="articles-generes"></div>'
)


if marqueur not in index_html:

    raise RuntimeError(
        "Le marqueur "
        '<div id="articles-generes"></div>'
        " est absent de index.html."
    )


titre_safe = escape(
    titre
)

categorie_safe = escape(
    categorie
)

chapeau_safe = escape(
    chapeau
)

image_safe = escape(
    image_index,
    quote=True
)

lien_safe = escape(
    lien_article,
    quote=True
)


carte_article = f"""

<article class="card article-genere">

<img
src="{image_safe}"
alt="{titre_safe}"
>

<div class="content">

<small class="article-category">
{categorie_safe}
</small>

<h3>
{titre_safe}
</h3>

<p>
{chapeau_safe}
</p>

<a href="{lien_safe}">
Lire l'article
</a>

</div>

</article>

"""


index_html = index_html.replace(
    marqueur,
    marqueur + carte_article,
    1
)


with open(
    index_path,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(
        index_html
    )


# ============================================================
# FIN
# ============================================================

print("")
print("========================================")
print("ARTICLE TERMINE AVEC SUCCES")
print("========================================")

print(
    f"Article : {chemin_article}"
)

print(
    f"Image   : {chemin_image}"
)

print(
    "Index   : index.html"
)

print(
    "JSON    : articles.json"
)

print("========================================")
