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
# DATE ET SLUG
# =========================

date_du_jour = date.today().isoformat()


slug = re.sub(
    r"[^a-z0-9]+",
    "-",
    titre.lower()
)

slug = slug.strip("-")


nom_fichier = (
    f"article-{date_du_jour}-{slug}.html"
)


# =========================
# IMAGE
# =========================

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

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

<title>
TechNews - {titre}
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

os.makedirs(
    "articles",
    exist_ok=True
)


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


# =========================
# CREATION / MISE A JOUR
# DE ARTICLES.JSON
# =========================

fichier_json = "articles.json"


# Si articles.json existe déjà
if os.path.exists(fichier_json):

    with open(
        fichier_json,
        "r",
        encoding="utf-8"
    ) as fichier:

        articles = json.load(fichier)

else:

    articles = []


# =========================
# INFORMATIONS DE L'ARTICLE
# =========================

article = {

    "titre": titre,

    "description": chapeau,

    "categorie": categorie,

    "date": date_du_jour,

    "image": image,

    "lien": f"articles/{nom_fichier}"

}


# Ajouter le nouvel article
articles.insert(
    0,
    article
)


# =========================
# SAUVEGARDE JSON
# =========================

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


# =========================
# AJOUT DE L'ARTICLE A L'ACCUEIL
# =========================

from html import escape


index_path = "index.html"


# Vérifier que index.html existe
if not os.path.exists(index_path):

    raise RuntimeError(
        "index.html est introuvable."
    )


# Lire index.html
with open(
    index_path,
    "r",
    encoding="utf-8"
) as fichier:

    index_html = fichier.read()


# Sécuriser les informations
titre_safe = escape(titre)

chapeau_safe = escape(chapeau)

categorie_safe = escape(categorie)

lien_safe = escape(
    f"articles/{nom_fichier}",
    quote=True
)

image_safe = escape(
    image,
    quote=True
)


# Créer la carte
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


# Marqueur dans index.html
marqueur = '<div id="articles-generes"></div>'


# Vérifier que le marqueur existe
if marqueur not in index_html:

    raise RuntimeError(
        "Le marqueur articles-generes "
        "n'existe pas dans index.html."
    )


# Ajouter l'article
index_html = index_html.replace(
    marqueur,
    marqueur + carte_article,
    1
)


# Sauvegarder index.html
with open(
    index_path,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(index_html)


print("====================================")
print("Article créé avec succès !")
print(f"Fichier : {chemin}")
print(f"Titre   : {titre}")
print("Article ajouté à l'accueil !")
print("====================================")
