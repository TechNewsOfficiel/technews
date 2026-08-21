import os
import json
import re
from datetime import date
from html import escape

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY est introuvable.")


client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# OUTILS
# ============================================================

def nettoyer_json(texte):

    texte = texte.strip()

    if texte.startswith("```json"):
        texte = texte[len("```json"):]

    elif texte.startswith("```"):
        texte = texte[len("```"):]

    if texte.endswith("```"):
        texte = texte[:-3]

    return texte.strip()


def creer_slug(titre):

    titre = titre.lower()

    accents = {
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

    for ancien, nouveau in accents.items():
        titre = titre.replace(ancien, nouveau)

    titre = re.sub(
        r"[^a-z0-9]+",
        "-",
        titre
    )

    return titre.strip("-")


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
# 1. GENERATION DE L'ARTICLE
# ============================================================

print()
print("========================================")
print("GENERATION DE L'ARTICLE")
print("========================================")


prompt_article = """
Tu es journaliste pour TechNews, un site français
consacré à la technologie, à l'intelligence artificielle
et au numérique.

Crée un article original sur un sujet intéressant
concernant l'intelligence artificielle.

Règles :

- environ 700 mots
- français naturel
- titre sérieux et accrocheur
- ne fabrique pas de chiffres
- ne fabrique pas de citations
- ne présente pas comme certain un fait incertain
- texte adapté à un site d'actualité technologique

Retourne UNIQUEMENT un JSON valide.

Structure obligatoire :

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
        "Gemini n'a retourné aucun article."
    )


texte = nettoyer_json(
    response_article.text
)


try:

    data = json.loads(texte)

except json.JSONDecodeError as erreur:

    print("Réponse Gemini reçue :")
    print(response_article.text)

    raise RuntimeError(
        f"JSON invalide : {erreur}"
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


print()
print("Titre généré :")
print(titre)


# ============================================================
# 2. NOM DES FICHIERS
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

print()
print("========================================")
print("GENERATION DE L'IMAGE")
print("========================================")


prompt_image = f"""
Create a professional editorial image for a French
technology news website.

The image must visually illustrate this article.

TITLE:
{titre}

SUMMARY:
{chapeau}

Create an image specifically related to the subject
described above.

Style:

- professional technology journalism
- realistic
- modern
- high quality
- cinematic lighting
- visually interesting
- horizontal composition
- suitable as a news website article thumbnail
- no text
- no letters
- no logos
- no watermark

The image must clearly represent the topic of the article.
"""


response_image = client.models.generate_content(

    model="gemini-3.1-flash-image",

    contents=[
        prompt_image
    ],

    config=types.GenerateContentConfig(

        response_modalities=[
            "IMAGE"
        ]

    )
)


image_saved = False


for part in response_image.parts:

    if part.inline_data is not None:

        image = part.as_image()

        image.save(
            chemin_image
        )

        image_saved = True

        print()
        print("Image générée avec succès.")
        print(
            f"Image : {chemin_image}"
        )

        break


if not image_saved:

    raise RuntimeError(
        "Gemini n'a retourné aucune image."
    )


# ============================================================
# 4. CONSTRUCTION DU CONTENU
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
# 5. PAGE ARTICLE
# ============================================================

image_article = (
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
src="{escape(image_article, quote=True)}"
class="article-image"
alt="{escape(titre, quote=True)}"
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


with open(
    chemin_article,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(
        html_article
    )


print()
print("Page article créée :")
print(chemin_article)


# ============================================================
# 6. ARTICLES.JSON
# ============================================================

fichier_json = "articles.json"


if os.path.exists(fichier_json):

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
    "articles.json mis à jour."
)


# ============================================================
# 7. AJOUT DE LA CARTE SUR INDEX.HTML
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


marqueur = (
    '<div id="articles-generes"></div>'
)


if marqueur not in index_html:

    raise RuntimeError(
        "Le marqueur articles-generes "
        "est absent de index.html."
    )


carte_article = f"""

<article class="card article-genere">

<img
src="{escape(image_index, quote=True)}"
alt="{escape(titre, quote=True)}"
>

<div class="content">

<small class="article-category">
{escape(categorie)}
</small>

<h3>
{escape(titre)}
</h3>

<p>
{escape(chapeau)}
</p>

<a href="{escape(lien_article, quote=True)}">
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


print(
    "index.html mis à jour."
)


# ============================================================
# FIN
# ============================================================

print()
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
