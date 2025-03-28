import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.types import ASGIApp
from utils.logger import get_logger

logger = get_logger("fastapi.middleware")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log requests and responses in FastAPI.
    Logs the request method, URL, response status, and processing time.
    Also logs the request and response bodies for non-200 status codes.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        try:
            logger.info(f"⬅️ Request: {request.method} {request.url.path}")

            response = await call_next(request)

            process_time = (time.time() - start_time) * 1000
            formatted_time = f"{process_time:.2f}ms"

            if response.status_code not in {200, 201}:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                new_response = StreamingResponse(
                    content=iter([body]),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )

                logger.warning(
                    f"⚠️ Error Response: {request.method} {request.url.path} "
                    f"Status: {response.status_code} Time: {formatted_time} "
                    f"Body: {body.decode('utf-8', errors='ignore')}"
                )
                return new_response
            logger.info(
                f"➡️ Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} Time: {formatted_time}"
            )
            return response

        except Exception as e:
            logger.exception(f"💥 Exception on {request.method} {request.url.path}: {e}")
            raise e
