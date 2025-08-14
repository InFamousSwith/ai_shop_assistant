import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_URL = os.getenv("POSTGRES_URL")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL")
EMBEDDINGS_MODEL = os.getenv("OPENAI_EMBEDDINGS_MODEL")
TRANSCRIBE_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = (
    "Ты — вежливый и компетентный AI-консультант магазина. "
    "Помогаешь подобрать товары, уточняешь потребности, отрабатываешь возражения, доводишь до покупки."
)
DOWNLOAD_IMAMGE_DIR = "downloads"
