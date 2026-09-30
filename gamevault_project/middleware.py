import uuid
import logging

logger = logging.getLogger(__name__)

class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request_id = str(uuid.uuid4())
        request.request_id = request_id

        response = self.get_response(request)
        logger.info("Request id: %s Request method: %s Request path: %s Response status code: %s", request.request_id, request.method, request.path, response.status_code)
        response['X-Request-Id'] = request_id

        return response