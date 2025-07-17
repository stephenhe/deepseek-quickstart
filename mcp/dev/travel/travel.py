from typing import Any
import httpx
# Update the import path below if FastMCP is located elsewhere, or install the mcp package if missing.
# Example alternative import if FastMCP is in the same directory or a parent directory:
# from fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel")

if __name__ == "__main__":
    mcp.run(transport='stdio')