import os
from google import genai


api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY introuvable.")


client = genai.Client(api_key=api_key)


prompt = """
Tu es journaliste pour TechNews, un site français
consacré aux nouvelles technologies.

Écris un article original d'environ 700 mots sur
l'intelligence artificielle.

L'article doit :

- être entièrement en français
- avoir un titre
- avoir une introduction
- contenir plusieurs sous-titres
- contenir plusieurs paragraphes
- avoir une conclusion
- être naturel et agréable à lire
- ne pas inventer de chiffres
- ne pas inventer de citations
- ne pas inventer de sources

Format :

TITRE :
...

INTRODUCTION :
...

SOUS-TITRE :
...

...

CONCLUSION :
...

Retourne uniquement l'article.
"""


print("Generation de l'article...")


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)


if not response.text:
    raise RuntimeError(
        "Gemini n'a retourne aucun article."
    )


article = response.text.strip()


with open(
    "article.txt",
    "w",
    encoding="utf-8"
) as fichier:
    fichier.write(article)


print("Article genere avec succes.")
print("Fichier : article.txt")

import os
import base64
from openai import OpenAI


api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY introuvable.")


client = OpenAI(api_key=api_key)


# ============================================================
# LIRE L'ARTICLE
# ============================================================

with open(
    "article.txt",
    "r",
    encoding="utf-8"
) as fichier:

    article = fichier.read()


# ============================================================
# PROMPT IMAGE
# ============================================================

prompt = f"""
Create a professional editorial image for a French
technology news website.

The image must illustrate this article:

{article[:4000]}

Style:

- professional technology journalism
- realistic
- modern
- cinematic
- high quality
- horizontal composition
- suitable as a news article hero image

Important:

- no text
- no letters
- no logo
- no watermark
"""


print("Generation de l'image...")


result = client.images.generate(
    model="gpt-image-1",
    prompt=prompt,
    size="1536x1024"
)


image_base64 = result.data[0].b64_json


if not image_base64:
    raise RuntimeError(
        "OpenAI n'a pas retourne d'image."
    )


image_data = base64.b64decode(
    image_base64
)


os.makedirs(
    "articles/images",
    exist_ok=True
)


with open(
    "articles/images/article.png",
    "wb"
) as fichier:

    fichier.write(image_data)


print("Image generee avec succes.")
print("Fichier : articles/images/article.png")
