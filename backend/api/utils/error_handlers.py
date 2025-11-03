from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FluxoBaseException(Exception):
    def __init__(self, message: str, error_code: str = "FLUXO_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

async def fluxo_exception_handler(request: Request, exc: FluxoBaseException):
    logger.error(f"{exc.error_code}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
