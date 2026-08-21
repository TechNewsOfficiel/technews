import os
import json
import re

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY est introuvable dans les variables d'environnement."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# PROMPT
# ============================================================

prompt = """
Tu es journaliste pour TechNews, un site français
consacré aux nouvelles technologies.

Rédige un article original sur l'intelligence artificielle.

L'article doit :

- être entièrement en français
- faire environ 700 mots
- avoir un titre sérieux et intéressant
- avoir un chapeau de 2 à 3 phrases
- contenir plusieurs sections
- être agréable et naturel à lire
- ne pas inventer de chiffres
- ne pas inventer de citations
- ne pas inventer de sources
- ne pas présenter comme certain quelque chose d'incertain

Retourne uniquement les données correspondant à la structure JSON demandée.
"""


# ============================================================
# GENERATION
# ============================================================

print("Generation de l'article...")

try:

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

except Exception as erreur:

    print("")
    print("ERREUR GEMINI")
    print(erreur)
    raise


# ============================================================
# VERIFIER LA REPONSE
# ============================================================

if not response.text:
    raise RuntimeError(
        "Gemini n'a retourne aucun texte."
    )

texte = response.text.strip()


# ============================================================
# NETTOYER LES BLOCS MARKDOWN EVENTUELS
# ============================================================

texte = re.sub(
    r"^```json\s*",
    "",
    texte,
    flags=re.IGNORECASE
)

texte = re.sub(
    r"\s*```$",
    "",
    texte
)

texte = texte.strip()


# ============================================================
# CONVERTIR EN JSON
# ============================================================

try:

    article = json.loads(texte)

except json.JSONDecodeError as erreur:

    print("")
    print("REPONSE RECUE DE GEMINI :")
    print("--------------------------------")
    print(texte)
    print("--------------------------------")

    raise RuntimeError(
        f"Le JSON retourne par Gemini est invalide : {erreur}"
    )


# ============================================================
# VERIFICATIONS
# ============================================================

champs_obligatoires = [
    "titre",
    "categorie",
    "chapeau",
    "sections",
    "conclusion"
]

for champ in champs_obligatoires:

    if champ not in article:

        raise RuntimeError(
            f"Le champ '{champ}' manque dans la reponse Gemini."
        )


if not isinstance(article["sections"], list):

    raise RuntimeError(
        "Le champ 'sections' doit etre une liste."
    )


# ============================================================
# AFFICHER L'ARTICLE
# ============================================================

print("")
print("========================================")
print("ARTICLE GENERE AVEC SUCCES")
print("========================================")

print("")
print("TITRE")
print(article["titre"])

print("")
print("CATEGORIE")
print(article["categorie"])

print("")
print("CHAPEAU")
print(article["chapeau"])

print("")

for section in article["sections"]:

    print("----------------------------------------")
    print(section["titre"])
    print("----------------------------------------")

    for paragraphe in section["paragraphes"]:

        print(paragraphe)
        print("")


print("----------------------------------------")
print("CONCLUSION")
print("----------------------------------------")

print(article["conclusion"])


# ============================================================
# SAUVEGARDER L'ARTICLE
# ============================================================

with open(
    "article.json",
    "w",
    encoding="utf-8"
) as fichier:

    json.dump(
        article,
        fichier,
        ensure_ascii=False,
        indent=4
    )


print("")
print("Article sauvegarde dans : article.json")
