"""
app/core/exceptions.py
───────────────────────
Custom exception hierarchy for the Rugpull Detection API.
All exceptions produce consistent JSON error responses.
"""

from __future__ import annotations

from typing import Any


class RugpullBaseException(Exception):
    """Base exception for all application-level errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.details = details or {}
        super().__init__(self.message)


# ── 400 Bad Request ───────────────────────────────────────────
class ValidationException(RugpullBaseException):
    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Request validation failed."


class InvalidAddressException(RugpullBaseException):
    status_code = 400
    error_code = "INVALID_ADDRESS"
    message = "The provided blockchain address is invalid."


class InvalidChainException(RugpullBaseException):
    status_code = 400
    error_code = "INVALID_CHAIN"
    message = "Unsupported blockchain network."


# ── 401 Unauthorized ─────────────────────────────────────────
class AuthenticationException(RugpullBaseException):
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"
    message = "Authentication credentials are missing or invalid."


# ── 403 Forbidden ────────────────────────────────────────────
class PermissionDeniedException(RugpullBaseException):
    status_code = 403
    error_code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."


# ── 404 Not Found ─────────────────────────────────────────────
class NotFoundException(RugpullBaseException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "The requested resource was not found."


class TokenNotFoundException(NotFoundException):
    error_code = "TOKEN_NOT_FOUND"
    message = "Token not found."


class PredictionNotFoundException(NotFoundException):
    error_code = "PREDICTION_NOT_FOUND"
    message = "Prediction not found."


class ExplanationNotFoundException(NotFoundException):
    error_code = "EXPLANATION_NOT_FOUND"
    message = "Explanation not found."


# ── 409 Conflict ──────────────────────────────────────────────
class DuplicateResourceException(RugpullBaseException):
    status_code = 409
    error_code = "DUPLICATE_RESOURCE"
    message = "Resource already exists."


# ── 422 Unprocessable Entity ─────────────────────────────────
class FeatureEngineeringException(RugpullBaseException):
    status_code = 422
    error_code = "FEATURE_ENGINEERING_FAILED"
    message = "Feature engineering pipeline failed."


class GraphConstructionException(RugpullBaseException):
    status_code = 422
    error_code = "GRAPH_CONSTRUCTION_FAILED"
    message = "Transaction graph construction failed."


# ── 429 Rate Limited ─────────────────────────────────────────
class RateLimitException(RugpullBaseException):
    status_code = 429
    error_code = "RATE_LIMITED"
    message = "External API rate limit exceeded. Please retry later."


# ── 500 Internal Server Error ─────────────────────────────────
class ModelInferenceException(RugpullBaseException):
    status_code = 500
    error_code = "MODEL_INFERENCE_FAILED"
    message = "ML model inference failed."


class ModelNotLoadedException(RugpullBaseException):
    status_code = 500
    error_code = "MODEL_NOT_LOADED"
    message = "No trained model is loaded. Please train a model first."


class BlockchainCollectionException(RugpullBaseException):
    status_code = 500
    error_code = "COLLECTION_FAILED"
    message = "Blockchain data collection failed."


class DatabaseException(RugpullBaseException):
    status_code = 500
    error_code = "DATABASE_ERROR"
    message = "Database operation failed."


# ── 503 Service Unavailable ───────────────────────────────────
class ExternalAPIException(RugpullBaseException):
    status_code = 503
    error_code = "EXTERNAL_API_UNAVAILABLE"
    message = "External blockchain API is unavailable."
