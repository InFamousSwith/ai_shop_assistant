
import os

from ai_client import analyze_image, chat_reply, transcribe
from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import DOWNLOAD_IMAMGE_DIR, SYSTEM_PROMPT
from database.db import *
from loader import bot, dp
from rag import retrieve
from utils import convert_ogg_to_mp3, encode_image, guess_category_from_text

user_last_product = {}


async def transcribe_voice(message: Message):
    ogg_file = f"temp_{message.from_user.id}.ogg"
    mp3_file = f"temp_{message.from_user.id}.mp3"
    file = await message.bot.get_file(message.voice.file_id)

    await message.bot.download_file(file_path=file.file_path, destination=ogg_file)
    await convert_ogg_to_mp3(ogg_file, mp3_file)
    text = await transcribe(mp3_file)
    return text


async def process_purchase(message: Message, product):
    await message.answer(f"Вы собираетесь купить {product.name} за {product.price:.0f}₽")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", callback_data="pay_confirm")]
    ])
    await message.answer("Нажмите кнопку для оплаты:", reply_markup=kb)


async def get_db_data(text: str, message: Message):
    found_by_name = await get_product_by_name_like(text, 5)
    category = await guess_category_from_text(text)
    found_by_cat = await get_products_by_category(category, 5) if category else []

    db_summary = ""
    if found_by_name:
        db_summary += "Найдено по названию:\n" + "\n".join(
            [f"- {p.name} — {p.price:.0f}₽ ({'есть' if p.in_stock else 'нет'})" for p in found_by_name]
        )
        user_last_product[message.from_user.id] = found_by_name[0]
        db_summary += "\n\nНапишите 'Хочу купить', чтобы оформить заказ."
    if found_by_cat:
        db_summary += ("\n\n" if db_summary else "") + "Похожие по категории:\n" + "\n".join(
            [f"- {p.name} — {p.price:.0f}₽ ({'есть' if p.in_stock else 'нет'})" for p in found_by_cat]
        )
    return db_summary if db_summary else "По базе данных ничего не найдено."


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я AI-консультант. Опишите, что ищете. "
        "Могу понимать голос и фото. Команды: /list — показать товары."
    )


@dp.message(Command("list"))
async def cmd_list(message: Message):
    prods = await list_products()
    if not prods:
        await message.answer("Товары не найдены.")
        return
    lines = [
        f"{p.id}. {p.name} — {p.price:.0f}₽ ({'в наличии' if p.in_stock else 'нет'})"
        for p in prods
    ]
    await message.answer("\n".join(lines))


@dp.message(~F.text & ~F.command & ~F.voice & ~F.photo)
async def handle_files(message: Message):
    await message.answer("Извините, я такой формат не поддерживаю.")


@dp.message(F.text | F.voice)
async def handle_text_or_voice(message: Message):
    if message.text:
        text = message.text.strip()
    elif message.voice:
        text = await transcribe_voice(message)
    else:
        await message.answer("Не удалось извлечь текст.")
        return
    
    if "хочу купить" in text.lower():
        product = user_last_product.get(message.from_user.id)
        if not product:
            await message.answer("Сначала выберите товар, чтобы оформить заказ.")
            return
        await process_purchase(message, product)
        return

    rag_ctx = await retrieve(text, k=3)
    db_summary = await get_db_data(text, message)
    print(db_summary)
    user_content = [{
        "type": "text",
        "text": f"Вопрос пользователя: {text}\n\nRAG контекст:\n{rag_ctx}\n\n"
                f"Данные из SQL:\n{db_summary}\n\n"
                f"Дай ответ и предложи оформить покупку при заинтересованности."
    }]
    reply = await chat_reply(SYSTEM_PROMPT, user_content)
    await message.answer(reply)


@dp.callback_query(F.data == "pay_confirm")
async def buy_callback(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Оплата прошла успешно ✅")
    await call.answer()


@dp.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    local_path = os.path.join(DOWNLOAD_IMAMGE_DIR, f"{photo.file_id}.jpg")
    await bot.download_file(file_info.file_path, destination=local_path)

    base64_image = await encode_image(local_path)
    response = await analyze_image(base64_image)
    resp_json = response.json()
    text_output = resp_json["choices"][0]["message"]["content"].strip()
    tags = [tag.strip() for tag in text_output.split(",") if tag.strip()]

    results = search_items_by_tags(tags)
    reply = f"Найдено товаров в каталоге по фото:\n\n" + "\n".join(results) + "\n\nЧто вас интересует?" if results else "Совпадений не найдено."
    
    await message.answer(reply)
