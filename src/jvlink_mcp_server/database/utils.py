"""Shared database utilities"""

import re

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_NAR_TABLE_REFERENCE_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:NAR_[A-Za-z0-9_]+|[A-Za-z_][A-Za-z0-9_]*_NAR)"
    r"(?![A-Za-z0-9_])"
)


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


def reject_unsupported_nar_table_reference(query: str) -> None:
    """Reject SQL that refers to a physical NAR provider table."""
    if _NAR_TABLE_REFERENCE_RE.search(query):
        raise ValueError("NAR tables are not supported by JVLink MCP Server.")
