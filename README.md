# AI Sales Bot (Telegram)

Telegram-бот для консультаций и продажи товаров:
- Диалоговый ИИ (текст/голос)
- RAG (FAISS + OpenAI Embeddings)
- Интеграция с SQL
- Фото (визуальная классификация через GPT-4o-mini)
- Имитация оплаты

## Структура проекта
```
ai-sales-bot/
├─ app/
│  ├─ database/
│  │  ├─ db.py                 # SQLAlchemy модели и запросы
│  │  └─ schemas.py
│  ├─ __init__.py
│  ├─ ai_client.py             # работа с chatGPT
│  ├─ config.py                # конфигурационный файл
│  ├─ handlers.py              # телеграм хендлеры
│  ├─ loader.py                # файл загрузки необходимых модулей
│  ├─ rag.py                   # индексация и поиск (FAISS + OpenAI embeddings)
│  ├─ run_bot.py               # запуск бота
│  └─ utils.py                 # утилиты для файлов/валидации
├─ data/
│  ├─ faiss_index.bin
│  ├─ faiss_meta.json
│  └─ knowledge_base.json
├─ .env.example
├─ README.md
└─ requirements.txt
```
## Запуск

1) `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2) `pip install -r requirements.txt`
3) Скопируйте `env.example` в `.env`, заполните `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY` и `POSTGRES_URL`
4) Установите ffmpeg и добавьте в PATH
5) Запустите бота: `python run_bot.py`

При первом запуске RAG-индекс соберётся автоматически.

