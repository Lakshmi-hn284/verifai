"""
VERIFAI - Standardized Error Hierarchy & Exception Handlers
Provides uniform domain error types and response structures.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class VerifaiException(Exception):
    """Base domain exception for VERIFAI."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(VerifaiException):
    def __init__(self, message: str = "Invalid credentials or expired token"):
        super().__init__(message=message, code="AUTHENTICATION_FAILED", status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(VerifaiException):
    def __init__(self, message: str = "Access denied: insufficient permissions"):
        super().__init__(message=message, code="FORBIDDEN", status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(VerifaiException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)}
        )


class VaultSecurityError(VerifaiException):
    def __init__(self, message: str):
        super().__init__(message=message, code="VAULT_SECURITY_ERROR", status_code=status.HTTP_400_BAD_REQUEST)


class PrivacyPolicyError(VerifaiException):
    def __init__(self, message: str):
        super().__init__(message=message, code="PRIVACY_POLICY_VIOLATION", status_code=status.HTTP_400_BAD_REQUEST)


class EligibilityEngineError(VerifaiException):
    def __init__(self, message: str):
        super().__init__(message=message, code="ELIGIBILITY_ENGINE_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_error_response(status_code: int, code: str, message: str, details: Optional[Dict[str, Any]] = None) -> JSONResponse:
    """Format a consistent JSON error response conforming to API design spec."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            },
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
    )


async def verifai_exception_handler(request: Request, exc: VerifaiException) -> JSONResponse:
    return create_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": exc.errors()}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return create_error_response(
        status_code=exc.status_code,
        code="HTTP_ERROR",
        message=str(exc.detail)
    )
