import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY est introuvable.")

client = genai.Client(api_key=api_key)

prompt = """
Tu es le rédacteur de TechNews, un site français consacré aux nouvelles technologies.

Rédige un article en français sur les nouveautés récentes de l'intelligence artificielle.

L'article doit contenir :
- un titre
- une introduction
- plusieurs sous-titres
- environ 700 mots
- un style journalistique simple et naturel
- aucune information inventée

Termine par une conclusion.
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

with open("article-test.md", "w", encoding="utf-8") as f:
    f.write("# Article TechNews\n\n")
    f.write(response.text)

print("Article généré avec succès !")
