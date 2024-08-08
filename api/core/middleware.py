import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from .models.historyc_models import OperationLog

logger = logging.getLogger(__name__)

class RequestBodyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method in ['POST', 'PUT']:
            try:
                request.body_data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                request.body_data = {}
                logger.error("Failed to decode JSON from request body.")
            except Exception as e:
                request.body_data = {}
                logger.error(f"Error processing request body: {str(e)}")
        return None

class OperationLogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.method in ['POST', 'PUT']:
            user = request.user
            if user.is_authenticated:
                request_body = getattr(request, 'body_data', {})
                model_name = request_body.get('model')
                operation = request_body.get('operation')
                object_id = request_body.get('object_id')

                if not model_name or not operation:
                    logger.error("Model name or operation type not provided in the request body.")
                    return response

                logger.debug(f"Model name: {model_name}, Operation: {operation}")

                # Validate the operation type
                if operation not in ["CREATE", "UPDATE"]:
                    logger.error(f"Invalid operation type: {operation}")
                    return response

                try:
                    content_type = ContentType.objects.get(model=model_name)
                except ContentType.DoesNotExist:
                    logger.error(f"ContentType for model '{model_name}' does not exist.")
                    return response

                object_repr = f"{model_name} {object_id}" if object_id else model_name
                change_message = f"User {user} performed {operation} on {object_repr}"

                # Only create log if object_id is available
                if object_id:
                    OperationLog.objects.create(
                        user=user,
                        action=operation,
                        content_type=content_type,
                        object_id=object_id,
                        object_repr=object_repr,
                        change_message=change_message,
                    )
                else:
                    logger.error(f"Object ID is missing for operation {operation} on model {model_name}")

        return response
