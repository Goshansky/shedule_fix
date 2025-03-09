import json
from datetime import datetime

from app.database import get_db
from app.models.request_status import RequestStatus
from app.services.schedule_service import get_schedule, get_different_buildings, get_long_breaks, \
    get_short_breaks_different_campus


async def process_request(query: str, request_id: int, request_type: str):
    """Фоновая обработка запроса."""
    try:
        # Определяем, какую функцию вызвать
        if request_type == "schedule":
            result = await get_schedule(query)
        elif request_type == "different-buildings":
            result = await get_different_buildings(query)
        elif request_type == "long-breaks":
            result = await get_long_breaks(query)
        elif request_type == "short-breaks-different-campus":
            result = await get_short_breaks_different_campus(query)
        else:
            raise ValueError(f"Unknown request type: {request_type}")

        # Функция для сериализации объектов в JSON
        def to_dict(obj):
            if isinstance(obj, list):
                return [to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: to_dict(value) for key, value in obj.items()}
            elif hasattr(obj, 'to_dict'):  # Если есть метод to_dict()
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):  # SQLAlchemy-объект
                return {key: to_dict(value) for key, value in obj.__dict__.items() if not key.startswith('_')}
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj

        # Сериализуем результат
        result_dict = to_dict(result)

        # Открываем новую сессию БД
        with next(get_db()) as db:
            request_status = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
            if request_status:
                request_status.status = "completed"
                request_status.result = json.dumps(result_dict)  # Сохраняем результат как JSON-строку
                db.commit()
            else:
                print(f"Request {request_id} not found.")
    except Exception as e:
        print(f"Error processing request {request_id}: {e}")
        with next(get_db()) as db:
            request_status = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
            if request_status:
                request_status.status = "failed"
                request_status.result = json.dumps({"error": str(e)})
                db.commit()
