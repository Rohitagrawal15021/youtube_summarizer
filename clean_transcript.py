import re

def clean_transcript(text):

    # Remove [Music]
    text = re.sub(r"\[Music\]", "", text, flags=re.IGNORECASE)

    # Remove [Applause]
    text = re.sub(r"\[Applause\]", "", text, flags=re.IGNORECASE)

    # Remove [Laughter]
    text = re.sub(r"\[Laughter\]", "", text, flags=re.IGNORECASE)

    # Remove [Laugh]
    text = re.sub(r"\[Laughs?\]", "", text, flags=re.IGNORECASE)

    # Remove [Silence]
    text = re.sub(r"\[Silence\]", "", text, flags=re.IGNORECASE)

    # Remove [Background Music]
    text = re.sub(r"\[Background Music\]", "", text, flags=re.IGNORECASE)

    # Remove [Cheering]
    text = re.sub(r"\[Cheering\]", "", text, flags=re.IGNORECASE)

    # Remove [Audience]
    text = re.sub(r"\[Audience\]", "", text, flags=re.IGNORECASE)

    # Remove extra spaces, tabs and new lines
    text = re.sub(r"\s+", " ", text)

    # Remove spaces from beginning and end
    text = text.strip()

    return text


if __name__ == "__main__":

    sample = """
    [Music]

    Hello everyone.

    [Applause]

    Today we are learning Python.

    [Laughter]

    Python is very easy.

    """

    cleaned = clean_transcript(sample)

    print(cleaned)