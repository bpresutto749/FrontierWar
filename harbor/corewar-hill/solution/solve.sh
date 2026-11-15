#!/bin/bash
# Reference run: the human expert warrior Toxic (John Metcalf), the #1 warrior
# of the CodeClash CC:Ladder Elo ranking of 264 human warriors. It was fixed as
# the reference before any agent run. Submitted through the same MCP tool as an
# agent would. It does NOT write /app/submission.red: if the MCP server is
# unreachable the oracle must fail visibly instead of being rescued by the fallback.
set -e
python3 /solution/submit.py /solution/reference.red
