"""Validation errors for user preferences (edge-cases §3, architecture §8)."""

from __future__ import annotations


class PreferenceValidationError(Exception):
    """Raised when user preferences fail validation."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        suggestions: list[str] | None = None,
        error_code: str = "VALIDATION_ERROR",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.field = field
        self.suggestions = suggestions or []
        self.error_code = error_code

    def to_dict(self) -> dict:
        return {
            "success": False,
            "error_code": self.error_code,
            "message": self.message,
            "field": self.field,
            "suggestions": self.suggestions,
        }
