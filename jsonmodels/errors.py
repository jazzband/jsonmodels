"""Errors classes for jsonmodels."""


class ValidationError(RuntimeError):

    """Validation error."""


class FieldNotFound(RuntimeError):

    """Field not found error."""
