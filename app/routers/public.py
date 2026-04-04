from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter(tags=["Public"])

@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для проверки: работает ли приложение и есть ли связь с БД.
    """
    try:
        # Простой математический запрос к БД
        result = await db.execute(text("SELECT 100 + 55"))
        value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        return {"db_status": False, "error": str(e)}
