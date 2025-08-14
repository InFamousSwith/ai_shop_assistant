import json
import os

import faiss
import numpy as np
from ai_client import embed_texts
from database.db import list_products

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index.bin")
META_PATH  = os.path.join(BASE_DIR, "data", "faiss_meta.json")
KB_PATH    = os.path.join(BASE_DIR, "data", "knowledge_base.json")


async def build_index():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        knowledge_base = json.load(f)
    texts = [f"Q: {x['q']}\nA: {x['a']}" for x in knowledge_base]
    all_products = list_products()
    products_description_list = [f"{product.name}. {product.description}" for product in all_products]
    texts.extend(products_description_list)

    embs = await embed_texts(texts)
    dim = len(embs[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embs, dtype="float32"))
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({"texts": texts}, f, ensure_ascii=False, indent=2)


def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta


async def retrieve(query: str, k: int = 3) -> list[str]:
    index, meta = load_index()
    if index is None:
        return []
    embeddings = (await embed_texts([query]))[0]
    D, I = index.search(np.array([embeddings], dtype="float32"), k)
    results = []
    for idx in I[0]:
        if 0 <= idx < len(meta["texts"]):
            results.append(meta["texts"][idx])
    return results
