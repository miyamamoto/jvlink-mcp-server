"""Shared database utilities"""

import re

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_identifier(name: str, kind: str = "identifier") -> str:
    """Validate a SQL identifier (table name or column name) to prevent injection.

    Only alphanumeric characters and underscores are allowed, and the name
    must start with a letter or underscore.

    Raises:
        ValueError: if the name contains invalid characters
    """
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Invalid {kind} {name!r}: only letters, digits, and underscores are allowed."
        )
    return name
