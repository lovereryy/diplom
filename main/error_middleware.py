from django.http import JsonResponse
from django.db import IntegrityError, OperationalError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except IntegrityError as e:
            logger.error(f"Database Integrity Error: {e}")
            return JsonResponse({'error': 'Ошибка целостности данных. Возможно, вы уже оставляли отзыв.'}, status=400)
        except ObjectDoesNotExist as e:
            logger.error(f"Object Not Found: {e}")
            return JsonResponse({'error': 'Запрашиваемый объект не найден.'}, status=404)
        except ValidationError as e:
            logger.error(f"Validation Error: {e}")
            return JsonResponse({'error': 'Ошибка валидации данных.'}, status=400)
        except OperationalError as e:
            logger.critical(f"Database Error: {e}")
            return JsonResponse({'error': 'Ошибка базы данных. Попробуйте позже.'}, status=500)
        except Exception as e:
            logger.exception(f"Unhandled Exception: {e}")
            return JsonResponse({'error': 'Внутренняя ошибка сервера.'}, status=500)
