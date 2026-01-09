from __future__ import annotations


class ServiceErrorException(Exception):
    """Base exception for service-layer errors."""


class ServiceValidationException(ServiceErrorException):
    """Raised when input validation fails before execution."""
