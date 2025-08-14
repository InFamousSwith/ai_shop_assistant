import os

from config import CHAT_MODEL, EMBEDDINGS_MODEL, TRANSCRIBE_MODEL
from openai import OpenAI
import requests
client = OpenAI()


async def chat_reply(system_prompt: str, user_content: list[dict]) -> str:
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": " ".join(user_content[0]["text"])}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return resp.choices[0].message.content


async def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBEDDINGS_MODEL, input=texts)
    return [d.embedding for d in resp.data]


async def transcribe(mp3_file):
    if not os.path.exists(mp3_file) or os.path.getsize(mp3_file) == 0:
        raise ValueError("MP3 file not found or empty after conversion")

    with open(mp3_file, "rb") as file_data:
        voice_to_text = client.audio.transcriptions.create(
            model=TRANSCRIBE_MODEL,
            file=file_data
        ).text
        return voice_to_text


async def analyze_image(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Назови все объекты на этом фото кратко через запятую."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    return response