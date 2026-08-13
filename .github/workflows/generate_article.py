import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("La clé GEMINI_API_KEY est introuvable.")

client = genai.Client(api_key=api_key)

prompt = """
Tu es le rédacteur du site TechNews.

Rédige un article d'actualité technologique en français.

Sujet :
Les nouveautés récentes dans l'intelligence artificielle.

Contraintes :
- environ 700 mots
- titre accrocheur
- introduction
- plusieurs sous-titres
- texte clair et naturel
- ne pas inventer de chiffres ou de faits précis
- terminer par une conclusion
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

article = response.text

with open("article-test.md", "w", encoding="utf-8") as f:
    f.write("# Article TechNews\n\n")
    f.write(article)

print("Article généré avec succès !")
