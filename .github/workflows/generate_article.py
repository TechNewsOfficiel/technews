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

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY est introuvable.")

client = genai.Client(api_key=api_key)


# ============================================================
# GENERATION DE L'ARTICLE
# ============================================================

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

print("Generation de l'article...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json"
    }
)

texte = response.text.strip()

texte = re.sub(r"^```json\s*", "", texte)
texte = re.sub(r"\s*```$", "", texte)

data = json.loads(texte)

titre = data["titre"]
categorie = data["categorie"]
chapeau = data["chapeau"]
sections = data["sections"]
conclusion = data["conclusion"]


# ============================================================
# DATE + SLUG
# ============================================================

date_du_jour = date.today().isoformat()

slug = re.sub(
    r"[^a-z0-9]+",
    "-",
    titre.lower()
)

slug = slug.strip("-")

nom_fichier = f"article-{date_du_jour}-{slug}.html"


# ============================================================
# DOSSIERS
# ============================================================

os.makedirs("articles", exist_ok=True)
os.makedirs("articles/images", exist_ok=True)


# ============================================================
# IMAGE
# ============================================================

nom_image = f"{date_du_jour}-{slug}.png"

chemin_image = os.path.join(
    "articles",
    "images",
    nom_image
)

print("Generation de l'image...")


prompt_image = f"""
Create a professional editorial image for a French technology news website.

Article title:
{titre}

Article summary:
{chapeau}

Create an image that visually represents the subject of this article.

Style:
- realistic
- professional technology journalism
- modern
- cinematic
- clean
- horizontal 16:9
- no text
- no words
- no letters
- no logo
"""


image_config = types.ImageConfig(
    aspect_ratio="16:9",
    image_size="1K"
)


image_response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=prompt_image,
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=image_config
    )
)


image_saved = False


for part in image_response.parts:

    if part.inline_data is not None:

        image = part.as_image()

        image.save(chemin_image)

        image_saved = True

        print(
            "Image sauvegardee :",
            chemin_image
        )

        break


if not image_saved:

    raise RuntimeError(
        "Gemini n'a pas retourne d'image."
    )


# ============================================================
# CONTENU ARTICLE
# ============================================================

contenu = ""

for section in sections:

    contenu += f"""
<h2>
{escape(section["titre"])}
</h2>
"""

    for paragraphe in section["paragraphes"]:

        contenu += f"""
<p>
{escape(paragraphe)}
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
# CHEMIN IMAGE DANS ARTICLE
# ============================================================

image_article = f"images/{nom_image}"


# ============================================================
# HTML ARTICLE
# ============================================================

html = f"""<!DOCTYPE html>

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
src="{image_article}"
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


# ============================================================
# SAUVEGARDE ARTICLE
# ============================================================

chemin_article = os.path.join(
    "articles",
    nom_fichier
)

with open(
    chemin_article,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(html)


# ============================================================
# ARTICLES.JSON
# ============================================================

fichier_json = "articles.json"


if os.path.exists(fichier_json):

    with open(
        fichier_json,
        "r",
        encoding="utf-8"
    ) as fichier:

        articles = json.load(fichier)

else:

    articles = []


article = {
    "titre": titre,
    "description": chapeau,
    "categorie": categorie,
    "date": date_du_jour,
    "image": f"articles/images/{nom_image}",
    "lien": f"articles/{nom_fichier}"
}


articles.insert(0, article)


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


# ============================================================
# AJOUT A L'ACCUEIL
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


titre_safe = escape(titre)

chapeau_safe = escape(chapeau)

categorie_safe = escape(categorie)

lien_safe = escape(
    f"articles/{nom_fichier}",
    quote=True
)

image_safe = escape(
    f"articles/images/{nom_image}",
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


marqueur = '<div id="articles-generes"></div>'


if marqueur not in index_html:

    raise RuntimeError(
        "Le marqueur articles-generes n'existe pas dans index.html."
    )


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


# ============================================================
# FIN
# ============================================================

print("")
print("====================================")
print("ARTICLE CREE AVEC SUCCES")
print("====================================")
print("Titre :", titre)
print("Article :", chemin_article)
print("Image :", chemin_image)
print("Accueil : index.html mis a jour")
print("====================================")
