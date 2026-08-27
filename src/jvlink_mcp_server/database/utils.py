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
_DYNAMIC_SQL_FUNCTIONS = {
    "CONNECTBY",
    "CROSSTAB",
    "CROSSTAB2",
    "CROSSTAB3",
    "CROSSTAB4",
    "CURSOR_TO_XML",
    "CURSOR_TO_XMLSCHEMA",
    "DATABASE_TO_XML",
    "DATABASE_TO_XML_AND_XMLSCHEMA",
    "DATABASE_TO_XMLSCHEMA",
    "DBLINK",
    "DBLINK_EXEC",
    "DBLINK_OPEN",
    "QUERY_TO_XML",
    "QUERY_TO_XML_AND_XMLSCHEMA",
    "QUERY_TO_XMLSCHEMA",
    "SCHEMA_TO_XML",
    "SCHEMA_TO_XML_AND_XMLSCHEMA",
    "SCHEMA_TO_XMLSCHEMA",
    "TABLE_TO_XML",
    "TABLE_TO_XML_AND_XMLSCHEMA",
    "TABLE_TO_XMLSCHEMA",
    "TS_STAT",
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


def _skip_parenthesized(tokens: list[str], index: int) -> int:
    """Return the first token after a balanced parenthesized expression."""
    depth = 0
    while index < len(tokens):
        if tokens[index] == "(":
            depth += 1
        elif tokens[index] == ")":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return index


def _cte_names(tokens: list[str]) -> set[str]:
    """Collect CTE identifiers without hiding physical tables in CTE bodies."""
    names = set()
    for start, token in enumerate(tokens):
        if _identifier_value(token).upper() != "WITH":
            continue

        index = start + 1
        if (
            index < len(tokens)
            and _identifier_value(tokens[index]).upper() == "RECURSIVE"
        ):
            index += 1

        while index < len(tokens):
            name_token = tokens[index]
            if name_token in {"(", ")", ".", ","}:
                break
            name = _identifier_value(name_token)
            index += 1

            if index < len(tokens) and tokens[index] == "(":
                index = _skip_parenthesized(tokens, index)
            if (
                index >= len(tokens)
                or _identifier_value(tokens[index]).upper() != "AS"
            ):
                break
            index += 1

            if index < len(tokens):
                modifier = _identifier_value(tokens[index]).upper()
                if modifier == "NOT":
                    index += 1
                    if (
                        index >= len(tokens)
                        or _identifier_value(tokens[index]).upper()
                        != "MATERIALIZED"
                    ):
                        break
                    index += 1
                elif modifier == "MATERIALIZED":
                    index += 1

            if index >= len(tokens) or tokens[index] != "(":
                break
            names.add(name.casefold())
            index = _skip_parenthesized(tokens, index)
            if index >= len(tokens) or tokens[index] != ",":
                break
            index += 1
    return names


def _called_functions(query: str):
    """Yield function identifiers while ignoring literal and comment text."""
    tokens = _SQL_TOKEN_RE.findall(_mask_sql_literals_and_comments(query))
    for index, token in enumerate(tokens[:-1]):
        if token not in {"(", ")", ".", ","} and tokens[index + 1] == "(":
            yield _identifier_value(token)


def _referenced_tables(query: str):
    """Yield table identifiers appearing in FROM/JOIN positions."""
    tokens = _SQL_TOKEN_RE.findall(_mask_sql_literals_and_comments(query))
    cte_names = _cte_names(tokens)
    in_from_clause = False
    expect_table = False
    only_modifier = False
    index = 0
    while index < len(tokens):
        token = tokens[index]
        upper = _identifier_value(token).upper()
        if upper in {"FROM", "JOIN", "TABLE"}:
            in_from_clause = True
            expect_table = True
            only_modifier = False
            index += 1
            continue
        if upper in _FROM_CLAUSE_END:
            in_from_clause = False
            expect_table = False
            only_modifier = False
            index += 1
            continue
        if expect_table:
            if upper == "ONLY":
                only_modifier = True
                index += 1
                continue
            if token == "(":
                if only_modifier:
                    index += 1
                    continue
                expect_table = False
                index += 1
                continue
            if token not in {".", ",", ")"}:
                table_token = token
                qualified = False
                while (
                    index + 2 < len(tokens)
                    and tokens[index + 1] == "."
                    and tokens[index + 2] not in {".", ",", "(", ")"}
                ):
                    table_token = tokens[index + 2]
                    index += 2
                    qualified = True
                table_name = _identifier_value(table_token)
                if qualified or table_name.casefold() not in cte_names:
                    yield table_name
                expect_table = False
                only_modifier = False
        elif in_from_clause and token == ",":
            expect_table = True
            only_modifier = False
        index += 1


def reject_unsupported_nar_table_reference(query: str) -> None:
    """Reject SQL that refers to a physical NAR provider table."""
    if any(
        function.upper() in _DYNAMIC_SQL_FUNCTIONS
        or function.upper().startswith("DBLINK_")
        for function in _called_functions(query)
    ):
        raise ValueError("Server-side dynamic SQL functions are not permitted.")
    if any(
        _NAR_TABLE_NAME_RE.fullmatch(table) for table in _referenced_tables(query)
    ):
        raise ValueError("NAR tables are not supported by JVLink MCP Server.")
