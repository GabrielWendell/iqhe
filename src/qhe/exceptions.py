"""Project-specific exceptions used by later scientific modules."""


class QHEEJPError(Exception):
    """Base exception for project-specific failures."""


class ConventionError(QHEEJPError):
    """Raised when a calculation is attempted before conventions are frozen."""


class ValidationError(QHEEJPError):
    """Raised when a numerical or physical acceptance criterion is not met."""
