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
    raise RuntimeError("GEMINI_API_KEY est introuvable.")

client = genai.Client(api_key=API_KEY)


# ============================================================
# DOSSIERS
# ============================================================

os.makedirs("articles", exist_ok=True)
os.makedirs("articles/images", exist_ok=True)


# ============================================================
# 1. GENERER L'ARTICLE
# ============================================================

print("Generation de l'article...")


prompt = """
Tu es journaliste pour TechNews, un site français consacré
aux nouvelles technologies, à l'intelligence artificielle,
aux smartphones, au gaming et à la cybersécurité.

Crée un article original et intéressant sur l'intelligence
artificielle.

L'article doit :

- être en français
- faire environ 700 mots
- avoir un titre intéressant et sérieux
- avoir un chapeau court
- contenir plusieurs sections
- être agréable à lire
- ne pas inventer de chiffres
- ne pas inventer de citations
- ne pas inventer de sources
- ne pas présenter comme certain quelque chose qui ne l'est pas

Retourne UNIQUEMENT un JSON valide.

Format obligatoire :

{
    "titre": "Titre de l'article",
    "categorie": "Intelligence artificielle",
    "chapeau": "Résumé court de l'article",
    "sections": [
        {
            "titre": "Titre de la section",
            "paragraphes": [
                "Premier paragraphe.",
                "Deuxième paragraphe."
            ]
        }
    ],
    "conclusion": "Conclusion de l'article."
}
"""


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json"
    }
)


if not response.text:
    raise RuntimeError(
        "Gemini n'a retourne aucun article."
    )


texte = response.text.strip()


# ============================================================
# NETTOYER LES EVENTUELS BLOCS MARKDOWN
# ============================================================

texte = re.sub(
    r"^```json\s*",
    "",
    texte
)

texte = re.sub(
    r"\s*```$",
    "",
    texte
)

texte = texte.strip()


# ============================================================
# LIRE LE JSON
# ============================================================

try:

    data = json.loads(texte)

except json.JSONDecodeError as erreur:

    print("Réponse de Gemini :")
    print(texte)

    raise RuntimeError(
        f"Le JSON genere par Gemini est invalide : {erreur}"
    )


# ============================================================
# RECUPERER LES INFORMATIONS
# ============================================================

titre = str(data["titre"]).strip()

categorie = str(data["categorie"]).strip()

chapeau = str(data["chapeau"]).strip()

sections = data["sections"]

conclusion = str(data["conclusion"]).strip()


print(f"Titre : {titre}")


# ============================================================
# DATE
# ============================================================

date_du_jour = date.today().isoformat()


# ============================================================
# CREER UN SLUG
# ============================================================

slug = titre.lower()


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
    slug = slug.replace(
        ancien,
        nouveau
    )


slug = re.sub(
    r"[^a-z0-9]+",
    "-",
    slug
)

slug = slug.strip("-")


if not slug:
    slug = "article-ia"


# ============================================================
# NOMS DES FICHIERS
# ============================================================

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
# 2. GENERER L'IMAGE AVEC GEMINI
# ============================================================

print("Generation de l'image...")


prompt_image = f"""
Create a professional editorial image for a French
technology news website.

The image must illustrate this article:

TITLE:
{titre}

SUMMARY:
{chapeau}

Create a realistic and modern technology news image
that clearly matches the subject of the article.

Style:

- professional technology journalism
- realistic
- modern
- cinematic
- high quality
- horizontal 16:9 composition
- suitable for a website article card
- visually attractive

IMPORTANT:

- no text
- no letters
- no logo
- no watermark
"""


interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=prompt_image,
    response_format={
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "1K"
    }
)


if not interaction.output_image:

    raise RuntimeError(
        "Gemini n'a pas retourne d'image."
    )


image_data = interaction.output_image.data


if not image_data:

    raise RuntimeError(
        "Gemini a retourne une image vide."
    )


# ============================================================
# SAUVEGARDER L'IMAGE
# ============================================================

with open(
    chemin_image,
    "wb"
) as fichier:

    fichier.write(
        base64.b64decode(image_data)
    )


print(
    f"Image creee : {chemin_image}"
)


# ============================================================
# 3. CONSTRUIRE LE CONTENU DE L'ARTICLE
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
# 4. CREER LA PAGE HTML
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
src="{escape(image_dans_article, quote=True)}"
class="article-image"
alt="{escape(titre, quote=True)}"
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


print(
    f"Article cree : {chemin_article}"
)


# ============================================================
# 5. ARTICLES.JSON
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

    except json.JSONDecodeError:

        articles = []

else:

    articles = []


if not isinstance(articles, list):

    articles = []


nouvel_article = {

    "titre": titre,

    "description": chapeau,

    "categorie": categorie,

    "date": date_du_jour,

    "image": (
        f"articles/images/{nom_image}"
    ),

    "lien": (
        f"articles/{nom_article}"
    )
}


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
# 6. AJOUTER L'ARTICLE A INDEX.HTML
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
        "Le marqueur "
        "articles-generes "
        "n'existe pas dans index.html."
    )


image_accueil = (
    f"articles/images/{nom_image}"
)

lien_accueil = (
    f"articles/{nom_article}"
)


carte_article = f"""

<article class="card article-genere">

<img
src="{escape(image_accueil, quote=True)}"
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

<a href="{escape(lien_accueil, quote=True)}">
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

    fichier.write(index_html)


print(
    "index.html mis a jour."
)


# ============================================================
# FIN
# ============================================================

print("")
print("========================================")
print("ARTICLE GENERE AVEC SUCCES")
print("========================================")
print(f"Article : {chemin_article}")
print(f"Image   : {chemin_image}")
print("Accueil : index.html")
print("JSON    : articles.json")
print("========================================")
