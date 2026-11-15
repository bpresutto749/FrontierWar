#!/usr/bin/env python3
"""Command-line access to the corewar MCP server (handy for scripted sweeps).

  python3 tools/spar.py my.red                   # battle all sparring warriors, 100 rounds
  python3 tools/spar.py my.red --rounds 300 --opponents s01 s04
  python3 tools/spar.py --submit my.red          # set the final submission
  python3 tools/spar.py --status

The server address comes from $COREWAR_MCP_URL (default http://arena:8000/mcp).
"""
import argparse
import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = os.environ.get("COREWAR_MCP_URL", "http://arena:8000/mcp")


async def call(tool, args):
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool(tool, args)
            return "\n".join(c.text for c in res.content if hasattr(c, "text"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("warrior", nargs="?")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--opponents", nargs="*")
    ap.add_argument("--submit", metavar="FILE")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        print(asyncio.run(call("status", {})))
    elif a.submit:
        print(asyncio.run(call("submit", {"source": open(a.submit).read()})))
    elif a.warrior:
        args = {"source": open(a.warrior).read(), "rounds": a.rounds}
        if a.opponents:
            args["opponents"] = a.opponents
        print(asyncio.run(call("battle", args)))
    else:
        ap.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
