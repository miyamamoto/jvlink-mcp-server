"""Public-surface contract: JVLink MCP Server supports JRA only."""

from jvlink_mcp_server import server
from jvlink_mcp_server.database import high_level_api, query_templates, schema_info


def test_nar_support_is_not_exposed() -> None:
    """NAR belongs to a separate provider and must not leak into this MCP."""
    tool_names = set(server.mcp._tool_manager._tools)
    resource_uris = {str(uri) for uri in server.mcp._resource_manager._resources}

    assert not {name for name in tool_names if name.startswith("nar_")}
    assert not {uri for uri in resource_uris if "nar" in uri.casefold()}
    assert not {
        name for name in query_templates.QUERY_TEMPLATES if name.startswith("nar_")
    }
    assert not {
        name
        for name in schema_info.ALL_TABLES
        if name.endswith("_NAR") or name.startswith("NAR_")
    }
    assert not hasattr(high_level_api, "get_nar_favorite_performance")
    assert not hasattr(high_level_api, "get_nar_jockey_stats")
    assert not hasattr(high_level_api, "get_nar_horse_history")
