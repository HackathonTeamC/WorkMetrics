import logging
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Global error handling middleware.
    
    Catches and handles various types of exceptions, returning appropriate
    HTTP responses with error details.
    """
    try:
        response = await call_next(request)
        return response
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database error",
                "message": "An error occurred while accessing the database.",
                "detail": str(e) if logger.level <= logging.DEBUG else None,
            },
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation error", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred.",
                "detail": str(e) if logger.level <= logging.DEBUG else None,
            },
        )
