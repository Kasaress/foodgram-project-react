import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_slug(value):
    """Валидация slug в соответствии с ТЗ."""
    if not re.fullmatch(settings.TAG_SLUG_PATTERN, value):
        raise ValidationError(settings.TAG_SLUG_ERROR_MESSAGE)
    return value
