import os
import json
import re
import base64
from datetime import date
from html import escape

from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY est introuvable dans GitHub Secrets.")

client = genai.Client(api_key=API_KEY)


# ============================================================
# OUTILS
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

    titre = (
        titre.replace("à", "a")
        .replace("â", "a")
        .replace("ä", "a")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("ë", "e")
        .replace("î", "i")
        .replace("ï", "i")
        .replace("ô", "o")
        .replace("ö", "o")
        .replace("ù", "u")
        .replace("û", "u")
        .replace("ü", "u")
        .replace("ç", "c")
    )

    slug = re.sub(r"[^a-z0-9]+", "-", titre)

    return slug.strip("-")


# ============================================================
# DOSSIERS
# ============================================================

os.makedirs("articles", exist_ok=True)
os.makedirs("articles/images", exist_ok=True)


# ============================================================
# GENERATION DE L'ARTICLE
# ============================================================

print("")
print("========================================")
print("GENERATION DE L'ARTICLE")
print("========================================")


prompt_article = """
Tu es journaliste pour TechNews, un site français consacré
à la technologie, à l'intelligence artificielle et au numérique.

Crée un article original et intéressant sur l'intelligence
artificielle.

Règles :

- environ 700 mots
- français naturel
- titre sérieux et accrocheur
- ne fabrique pas de chiffres
- ne fabrique pas de citations
- ne présente pas comme certain un fait dont tu n'es pas sûr
- article adapté à un site d'actualité technologique

Retourne UNIQUEMENT un JSON valide.

Format obligatoire :

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


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt_article,
    config={
        "response_mime_type": "application/json"
    }
)


if not response.text:
    raise RuntimeError(
        "Gemini n'a retourne aucun texte pour l'article."
    )


texte = nettoyer_json(response.text)

try:
    data = json.loads(texte)

except json.JSONDecodeError as erreur:

    print("Réponse Gemini reçue :")
    print(response.text)

    raise RuntimeError(
        f"Le JSON de l'article est invalide : {erreur}"
    )


# ============================================================
# RECUPERATION DES DONNEES
# ============================================================

titre = str(data["titre"]).strip()

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


if not titre:
    raise RuntimeError("Le titre est vide.")

if not chapeau:
    raise RuntimeError("Le chapeau est vide.")

if not isinstance(sections, list):
    raise RuntimeError("Les sections de l'article sont invalides.")


print("")
print("Titre :")
print(titre)


# ============================================================
# DATE + SLUG
# ============================================================

date_du_jour = date.today().isoformat()

slug = creer_slug(titre)

if not slug:
    slug = "article-intelligence-artificielle"


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
# GENERATION DE L'IMAGE AVEC GEMINI
# ============================================================

print("")
print("========================================")
print("GENERATION DE L'IMAGE")
print("========================================")


prompt_image = f"""
Create a professional editorial image for a French technology
news website.

The image must visually represent this article:

TITLE:
{titre}

SUMMARY:
{chapeau}

Create a realistic and modern technology journalism image.

Requirements:

- professional editorial photography
- realistic
- modern
- cinematic lighting
- technology / artificial intelligence theme
- visually connected to the article subject
- horizontal 16:9 composition
- no text
- no words
- no letters
- no logos
- no watermark
"""


# IMPORTANT :
# response_format est utilisé ici avec INTERACTIONS API.
# Il n'est PAS utilisé avec GenerateContentConfig.

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=prompt_image,
    response_format={
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "1K"
    }
)


# ============================================================
# RECUPERATION DE L'IMAGE
# ============================================================

if not interaction.output_image:

    raise RuntimeError(
        "Gemini n'a pas retourné d'image."
    )


image_base64 = interaction.output_image.data


if not image_base64:

    raise RuntimeError(
        "Gemini a retourné une image vide."
    )


try:

    image_bytes = base64.b64decode(
        image_base64
    )

except Exception as erreur:

    raise RuntimeError(
        f"Impossible de décoder l'image Gemini : {erreur}"
    )


if len(image_bytes) == 0:

    raise RuntimeError(
        "Le fichier image généré est vide."
    )


# ============================================================
# SAUVEGARDE DE L'IMAGE
# ============================================================

with open(
    chemin_image,
    "wb"
) as fichier:

    fichier.write(image_bytes)


print("")
print("Image créée :")
print(chemin_image)

print(
    f"Taille de l'image : {len(image_bytes)} octets"
)


# ============================================================
# CONSTRUCTION DU CONTENU HTML
# ============================================================

contenu = ""


for section in sections:

    titre_section = escape(
        str(section["titre"])
    )

    contenu += f"""
<h2>
{titre_section}
</h2>
"""

    paragraphes = section.get(
        "paragraphes",
        []
    )

    for paragraphe in paragraphes:

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
# CHEMINS
# ============================================================

# Depuis articles/article.html
# vers articles/images/image.png

image_dans_article = (
    f"images/{nom_image}"
)


# Depuis index.html
# vers articles/images/image.png

image_depuis_index = (
    f"articles/images/{nom_image}"
)


lien_article = (
    f"articles/{nom_article}"
)


# ============================================================
# CREATION DE LA PAGE ARTICLE
# ============================================================

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
{escape(date_du_jour)} • {escape(categorie)}
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


# ============================================================
# SAUVEGARDE DE LA PAGE ARTICLE
# ============================================================

with open(
    chemin_article,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(
        html_article
    )


print("")
print("Page article créée :")
print(chemin_article)


# ============================================================
# ARTICLES.JSON
# ============================================================

fichier_json = "articles.json"


if os.path.exists(fichier_json):

    try:

        with open(
            fichier_json,
            "r",
            encoding="utf-8"
        ) as fichier:

            articles = json.load(fichier)

        if not isinstance(articles, list):
            articles = []

    except Exception:

        articles = []

else:

    articles = []


nouvel_article = {

    "titre": titre,

    "description": chapeau,

    "categorie": categorie,

    "date": date_du_jour,

    "image": image_depuis_index,

    "lien": lien_article
}


# Eviter un doublon si l'action est relancée
articles = [
    article
    for article in articles
    if article.get("lien") != lien_article
]


articles.insert(
    0,
    nouvel_article
]


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


print("")
print("articles.json mis à jour.")


# ============================================================
# AJOUT SUR INDEX.HTML
# ============================================================

index_path = "index.html"


if not os.path.exists(index_path):

    raise RuntimeError(
        "index.html est introuvable."
    )


with open(
    index_path,
    "r",
    encoding="utf-8"
) as fichier:

    index_html = fichier.read()


# ============================================================
# MARQUEUR
# ============================================================

marqueur = (
    '<div id="articles-generes"></div>'
)


if marqueur not in index_html:

    raise RuntimeError(
        "Le marqueur "
        '<div id="articles-generes"></div>'
        " est introuvable dans index.html."
    )


# ============================================================
# CARTE ACCUEIL
# ============================================================

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
    image_depuis_index,
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


# ============================================================
# INSERTION
# ============================================================

index_html = index_html.replace(
    marqueur,
    marqueur + carte_article,
    1
)


# ============================================================
# SAUVEGARDE INDEX
# ============================================================

with open(
    index_path,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(
        index_html
    )


print("")
print("index.html mis à jour.")


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
    "Accueil : index.html"
)

print(
    "JSON    : articles.json"
)

print("========================================")
