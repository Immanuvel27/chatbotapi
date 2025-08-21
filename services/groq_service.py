from groq import Groq
from config import settings
from fastapi import UploadFile
import tempfile
import os

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)

def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

async def audio_to_text(file: UploadFile) -> str:
    import tempfile, os

    suffix = os.path.splitext(file.filename)[-1] or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            # Use translations instead of transcriptions
            transcription = client.audio.translations.create(
                model="whisper-large-v3",
                file=(file.filename, audio_file.read()),
                language="en",  # optional
                response_format="json",
                temperature=0.0,
            )

        if hasattr(transcription, "text"):
            return transcription.text
        elif isinstance(transcription, dict) and "text" in transcription:
            return transcription["text"]
        else:
            raise ValueError(f"Unexpected response: {transcription}")

    finally:
        os.remove(tmp_path)
