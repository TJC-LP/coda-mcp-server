# python-mcp-template
A simple template repo for building MCP servers with Python.

## Installing Locally


1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1)
2. Run `uv sync`
3. Run `cp .env.example .env` and set your `CODA_API_KEY` in `.env`
4. Run `uv run mcp install src/coda_mcp_server/server.py -f .env` to install to Claude Desktop
