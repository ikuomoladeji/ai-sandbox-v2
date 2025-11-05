"""
Input validation and sanitization module for production security
Prevents injection attacks, path traversal, and malformed data
"""
import re
from pathlib import Path
from typing import Optional, Union
from modules.logger import get_logger

logger = get_logger(__name__)

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class InputValidator:
    """Validates and sanitizes user input for security"""

    # Regex patterns for validation
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.()]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_./]+$')

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'\.\.',  # Path traversal
        r'[<>:"|?*]',  # Invalid filename characters
        r'[\x00-\x1f]',  # Control characters
        r'(rm\s+-rf|del\s+/|drop\s+table)',  # Command injection patterns
    ]

    @classmethod
    def validate_organization_name(cls, name: str) -> str:
        """
        Validate and sanitize organization name

        Args:
            name: Organization name to validate

        Returns:
            Sanitized organization name

        Raises:
            ValidationError: If validation fails
        """
        if not name or not isinstance(name, str):
            raise ValidationError("Organization name must be a non-empty string")

        name = name.strip()

        if len(name) < 2:
            raise ValidationError("Organization name must be at least 2 characters")

        if len(name) > 100:
            raise ValidationError("Organization name must be less than 100 characters")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                logger.log_security_event(logger, f"Blocked dangerous pattern in org name: {name}", "warning")
                raise ValidationError("Organization name contains invalid characters")

        return name

    @classmethod
    def validate_vendor_name(cls, name: str) -> str:
        """
        Validate and sanitize vendor name

        Args:
            name: Vendor name to validate

        Returns:
            Sanitized vendor name

        Raises:
            ValidationError: If validation fails
        """
        if not name or not isinstance(name, str):
            raise ValidationError("Vendor name must be a non-empty string")

        name = name.strip()

        if len(name) < 2:
            raise ValidationError("Vendor name must be at least 2 characters")

        if len(name) > 100:
            raise ValidationError("Vendor name must be less than 100 characters")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                logger.log_security_event(logger, f"Blocked dangerous pattern in vendor name: {name}", "warning")
                raise ValidationError("Vendor name contains invalid characters")

        return name

    @classmethod
    def validate_score(cls, score: Union[int, str], min_val: int = 1, max_val: int = 5) -> int:
        """
        Validate and convert score to integer

        Args:
            score: Score to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Validated integer score

        Raises:
            ValidationError: If validation fails
        """
        try:
            score_int = int(score)
        except (ValueError, TypeError):
            raise ValidationError(f"Score must be a number between {min_val} and {max_val}")

        if score_int < min_val or score_int > max_val:
            raise ValidationError(f"Score must be between {min_val} and {max_val}")

        return score_int

    @classmethod
    def validate_risk_level(cls, level: str) -> str:
        """
        Validate risk level input

        Args:
            level: Risk level to validate

        Returns:
            Validated lowercase risk level

        Raises:
            ValidationError: If validation fails
        """
        if not level or not isinstance(level, str):
            raise ValidationError("Risk level must be a string")

        level = level.strip().lower()
        valid_levels = ['low', 'medium', 'high']

        if level not in valid_levels:
            raise ValidationError(f"Risk level must be one of: {', '.join(valid_levels)}")

        return level

    @classmethod
    def validate_filepath(cls, filepath: Union[str, Path], must_exist: bool = False) -> Path:
        """
        Validate file path for security

        Args:
            filepath: Path to validate
            must_exist: Whether file must exist

        Returns:
            Validated Path object

        Raises:
            ValidationError: If validation fails
        """
        if not filepath:
            raise ValidationError("File path cannot be empty")

        try:
            path = Path(filepath)
        except Exception as e:
            raise ValidationError(f"Invalid file path: {e}")

        # Check for path traversal attempts
        try:
            resolved = path.resolve()
        except Exception as e:
            raise ValidationError(f"Cannot resolve path: {e}")

        # Ensure path is within project directory
        from config import Config
        base_dir = Config.BASE_DIR.resolve()

        if not str(resolved).startswith(str(base_dir)):
            logger.log_security_event(logger, f"Path traversal attempt blocked: {filepath}", "critical")
            raise ValidationError("Path must be within project directory")

        if must_exist and not resolved.exists():
            raise ValidationError(f"File does not exist: {filepath}")

        return resolved

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename for safe file operations

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename

        Raises:
            ValidationError: If validation fails
        """
        if not filename or not isinstance(filename, str):
            raise ValidationError("Filename must be a non-empty string")

        filename = filename.strip()

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                logger.log_security_event(logger, f"Blocked dangerous filename: {filename}", "warning")
                raise ValidationError("Filename contains invalid characters")

        # Remove or replace unsafe characters
        safe_filename = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
        safe_filename = safe_filename.replace('..', '')

        if not safe_filename:
            raise ValidationError("Filename contains only invalid characters")

        if len(safe_filename) > 255:
            raise ValidationError("Filename too long (max 255 characters)")

        return safe_filename

    @classmethod
    def validate_menu_choice(cls, choice: str, valid_choices: list) -> str:
        """
        Validate menu choice

        Args:
            choice: User's menu choice
            valid_choices: List of valid choices

        Returns:
            Validated choice

        Raises:
            ValidationError: If validation fails
        """
        if not choice or not isinstance(choice, str):
            raise ValidationError("Invalid choice")

        choice = choice.strip()

        if choice not in [str(c) for c in valid_choices]:
            raise ValidationError(f"Choice must be one of: {', '.join(str(c) for c in valid_choices)}")

        return choice

    @classmethod
    def sanitize_text_input(cls, text: str, max_length: int = 5000) -> str:
        """
        Sanitize general text input

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be text")

        text = text.strip()

        if len(text) > max_length:
            raise ValidationError(f"Input too long (max {max_length} characters)")

        # Remove null bytes and control characters (except newlines and tabs)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

        return text
