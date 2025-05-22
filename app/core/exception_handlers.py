# app/core/exception_handlers.py

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class ExceptionHandlers:
    @staticmethod
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """
        Handles FastAPI's built-in HTTP exceptions (e.g., 404, 401).
        Returns a standardized JSON response with error context.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": f"https://httpstatuses.com/{exc.status_code}",
                "title": exc.detail,
                "status": exc.status_code,
                "instance": str(request.url),
            },
        )

    @staticmethod
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handles validation errors raised during request body/query parsing.
        Logs and returns a detailed 422 error with failed field info.
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "https://httpstatuses.com/422",
                "title": "Validation Error",
                "detail": exc.errors(),
                "status": 422,
                "instance": str(request.url),
            },
        )

    @staticmethod
    async def database_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        Handles errors from SQLAlchemy operations.
        Logs the error and returns a generic database failure message.
        """
        logger.error(f"Database error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://httpstatuses.com/500",
                "title": "Database Error",
                "detail": "An error occurred while accessing the database",
                "status": 500,
                "instance": str(request.url),
            },
        )

    @staticmethod
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catches all unhandled exceptions to avoid leaking internal errors.
        Logs the full traceback and returns a 500 error with a generic message.
        """
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://httpstatuses.com/500",
                "title": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status": 500,
                "instance": str(request.url),
            },
        )

    @classmethod
    def register_handlers(cls, app):
        """
        Registers all custom exception handlers to the FastAPI application.
        """
        app.add_exception_handler(HTTPException, cls.http_exception_handler)
        app.add_exception_handler(
            RequestValidationError, cls.validation_exception_handler
        )
        app.add_exception_handler(SQLAlchemyError, cls.database_exception_handler)
        app.add_exception_handler(Exception, cls.generic_exception_handler)
