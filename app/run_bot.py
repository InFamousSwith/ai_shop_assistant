import asyncio
import os

from handlers import cmd_list, cmd_start, handle_files, handle_photo, handle_text_or_voice
from loader import bot, dp
from rag import build_index


async def on_startup():
    from rag import INDEX_PATH, META_PATH
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
        print("Building RAG index...")
        await build_index()
        print("RAG index ready.")


async def main():
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
