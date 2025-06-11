"""A template MCP server."""

from mcp.server import FastMCP

mcp = FastMCP("Template server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Return a + b."""
    return a + b


@mcp.prompt()
def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"


@mcp.resource("file://resource")
def resource() -> str:
    """Return a resource."""
    return "This is a resource."


def main() -> None:
    """Run the server."""
    mcp.run()


if __name__ == "__main__":
    main()
