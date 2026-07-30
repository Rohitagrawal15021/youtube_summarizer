from config import client
from google.genai import types
from langdetect import detect, LangDetectException


def translate_chunk(chunk):


    try:
        language = detect(chunk)

        if language == "en":
            return chunk

    except LangDetectException:
        print("Could not detect language. Translating...")

    prompt = f"""
You are an expert translator.

Translate the following text into natural English.

Instructions:
- Preserve the original meaning.
- Keep technical terms accurate.
- Do NOT summarize.
- Do NOT add explanations.
- Return ONLY the translated text.

Text:
{chunk}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0
        )
    )

    return response.text.strip()


def translate_chunks(chunks):
    """
    Translate all chunks one by one.
    """

    translated_chunks = []

    for i, chunk in enumerate(chunks, start=1):

        print(f"Translating Chunk {i}...")

        translated_chunk = translate_chunk(chunk)

        translated_chunks.append(translated_chunk)

    return translated_chunks

if __name__ == "__main__":

    chunks = [
        "Artificial Intelligence is changing the world.",
        "La inteligencia artificial está cambiando el mundo.",
        "L'apprentissage automatique est une branche de l'intelligence artificielle."
    ]

    translated = translate_chunks(chunks)

    print("\nTranslated Chunks\n")

    for i, chunk in enumerate(translated, start=1):
        print(f"Chunk {i}")
        print(chunk)
        print("-" * 50)