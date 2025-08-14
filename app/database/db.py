from config import DB_URL
from database.schemas import Base, Product
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

engine = create_engine(DB_URL, echo=False, future=True)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def list_products():
    """Возвращает список товаров."""
    with SessionLocal() as session:
        return session.query(Product).all()


async def list_categories():
    """Возвращает список категорий."""
    with SessionLocal() as session:
        return session.query(Product.category).all()


async def get_product_by_name_like(name: str, limit: int = 5):
    """Ищет товары по части имени."""
    with SessionLocal() as session:
        return session.query(Product)\
            .filter(Product.name.ilike(f"%{name}%"))\
            .limit(limit).all()


async def get_products_by_category(category: str, limit: int = 5):
    """Ищет товары по категории."""
    with SessionLocal() as session:
        return session.query(Product)\
            .filter(Product.category.ilike(f"%{category}%"))\
            .limit(limit).all()


def search_items_by_tags(tags: list[str], limit: int = 10):
    """Ищет товары по списку тегов."""
    if not tags:
        return []
    with SessionLocal() as session:
        conditions = [Product.name.ilike(f"%{tag}%") for tag in tags]
        rows = session.query(Product.name)\
            .filter(or_(*conditions))\
            .limit(limit).all()
        return [row.name for row in rows]
