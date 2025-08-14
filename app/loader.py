import os

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, DOWNLOAD_IMAMGE_DIR, OPENAI_API_KEY

os.makedirs(DOWNLOAD_IMAMGE_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
