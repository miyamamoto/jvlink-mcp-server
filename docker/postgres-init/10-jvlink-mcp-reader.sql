-- The importer owns/writes the physical tables.  MCP queries always SET ROLE
-- to this non-login principal before planning or executing user-provided SQL.
CREATE ROLE jvlink_mcp_reader
    NOLOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOINHERIT
    NOREPLICATION
    NOBYPASSRLS;

GRANT CONNECT ON DATABASE jvlink TO jvlink_mcp_reader;
GRANT USAGE ON SCHEMA public TO jvlink_mcp_reader;

-- jrvltsql creates tables after the PostgreSQL container is initialized.
-- Future tables therefore receive read access without making the MCP role an
-- owner.  If a mixed-provider NAR table is ever created, the server's runtime
-- boundary detects the grant and fails closed until it is revoked.
ALTER DEFAULT PRIVILEGES FOR ROLE jvlink_writer IN SCHEMA public
    GRANT SELECT ON TABLES TO jvlink_mcp_reader;
