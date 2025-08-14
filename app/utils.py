import base64

from database.db import list_categories
from pydub import AudioSegment


async def guess_category_from_text(t: str) -> str | None:
    t = t.lower()
    categories = await list_categories()
    for key in categories:
        if key[0] in t:
            return key
    return None


async def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def convert_ogg_to_mp3(input_path: str, output_path: str):
    audio = AudioSegment.from_ogg(input_path)
    audio.export(output_path, format="mp3")
