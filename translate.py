from config import client
from google.genai import types
def translate_into_english(transcript):
    prompt = f"""You are an expert translator.

If the given text is already in English,
return it exactly as it is.

Otherwise,
translate it into natural English.

Keep technical words accurate.

Return ONLY the translated text.
Transcript excerpt:
{transcript}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents = prompt,
        config=types.GenerateContentConfig(
            #i setted temperature =0 bcz i dosent want any creativity here from llm 
            temperature = 0
        )        

    )
    return response.text.strip()

if __name__ == "__main__":
    transcript = input("Enter the text here : ")
    english = translate_into_english(transcript)
    print("Translated text ---------------\n")
    print(english)