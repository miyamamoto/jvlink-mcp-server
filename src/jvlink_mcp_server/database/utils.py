"""Shared database utilities"""

import re

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_NAR_TABLE_NAME_RE = re.compile(
    r"(?i)(?:NAR_[A-Za-z0-9_]+|[A-Za-z_][A-Za-z0-9_]*_NAR)"
)
_SQL_TOKEN_RE = re.compile(
    r'"(?:""|[^"])*"|`[^`]*`|\[[^\]]*\]|[A-Za-z_][A-Za-z0-9_]*|[().,]'
)
_FROM_CLAUSE_END = {
    "WHERE",
    "GROUP",
    "HAVING",
    "ORDER",
    "LIMIT",
    "UNION",
    "EXCEPT",
    "INTERSECT",
}


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


def _mask_sql_literals_and_comments(query: str) -> str:
    """Mask literal/comment contents while retaining SQL identifier positions."""
    masked = list(query)
    index = 0
    while index < len(query):
        if query.startswith("--", index):
            end = query.find("\n", index + 2)
            end = len(query) if end < 0 else end
            masked[index:end] = " " * (end - index)
            index = end
            continue
        if query.startswith("/*", index):
            start = index
            depth = 1
            index += 2
            while index < len(query) and depth:
                if query.startswith("/*", index):
                    depth += 1
                    index += 2
                elif query.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            masked[start:index] = " " * (index - start)
            continue
        if query[index] == "'":
            start = index
            index += 1
            while index < len(query):
                if query[index] == "'":
                    if index + 1 < len(query) and query[index + 1] == "'":
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            masked[start:index] = " " * (index - start)
            continue
        if query[index] == "$":
            match = re.match(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$", query[index:])
            if match:
                delimiter = match.group(0)
                end = query.find(delimiter, index + len(delimiter))
                end = len(query) if end < 0 else end + len(delimiter)
                masked[index:end] = " " * (end - index)
                index = end
                continue
        index += 1
    return "".join(masked)


def _identifier_value(token: str) -> str:
    if token.startswith('"'):
        return token[1:-1].replace('""', '"')
    if token.startswith("`") or token.startswith("["):
        return token[1:-1]
    return token


def _referenced_tables(query: str):
    """Yield table identifiers appearing in FROM/JOIN positions."""
    tokens = _SQL_TOKEN_RE.findall(_mask_sql_literals_and_comments(query))
    in_from_clause = False
    expect_table = False
    index = 0
    while index < len(tokens):
        token = tokens[index]
        upper = _identifier_value(token).upper()
        if upper in {"FROM", "JOIN", "TABLE"}:
            in_from_clause = True
            expect_table = True
            index += 1
            continue
        if upper in _FROM_CLAUSE_END:
            in_from_clause = False
            expect_table = False
            index += 1
            continue
        if expect_table:
            if upper == "ONLY":
                index += 1
                continue
            if token == "(":
                expect_table = False
                index += 1
                continue
            if token not in {".", ",", ")"}:
                table_token = token
                if (
                    index + 2 < len(tokens)
                    and tokens[index + 1] == "."
                    and tokens[index + 2] not in {".", ",", "(", ")"}
                ):
                    table_token = tokens[index + 2]
                    index += 2
                yield _identifier_value(table_token)
                expect_table = False
        elif in_from_clause and token == ",":
            expect_table = True
        index += 1


def reject_unsupported_nar_table_reference(query: str) -> None:
    """Reject SQL that refers to a physical NAR provider table."""
    if any(
        _NAR_TABLE_NAME_RE.fullmatch(table) for table in _referenced_tables(query)
    ):
        raise ValueError("NAR tables are not supported by JVLink MCP Server.")
