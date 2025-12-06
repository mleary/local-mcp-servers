# Quick Setup Guide

## What You Have

A fully functional MCP agent for Yahoo Fantasy Football that works with GitHub Copilot CLI.

## How to Use with Copilot CLI

### Method 1: Direct Configuration

Add this to your Copilot CLI MCP configuration file:

```json
{
  "mcpServers": {
    "yahoo-fantasy": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/Users/matt/local-mcp-servers/mcp-fantasy-draft/agent-yahooff",
      "env": {}
    }
  }
}
```

**Note:** Update the `cwd` path if you move this directory.

### Method 2: Use Provided Config

A pre-configured `mcp-config.json` is included. You can:

1. Copy it to your MCP config location
2. Merge it with existing MCP servers
3. Point Copilot CLI to use it

### Method 3: Manual Invocation

Run the server directly when needed:

```bash
cd /Users/matt/local-mcp-servers/mcp-fantasy-draft/agent-yahooff
python server.py
```

The server will wait for MCP protocol messages on stdin/stdout.

## Verify Installation

Test that everything works:

```bash
cd /Users/matt/local-mcp-servers/mcp-fantasy-draft/agent-yahooff
source ../.venv/bin/activate
python server.py
```

You should see:
- OAuth token validation messages
- Server waiting for input (this is correct!)

Press `Ctrl+C` to exit.

## Using the Agent

Once configured with Copilot CLI, you can ask questions like:

**View Your Team:**
- "Show me my fantasy team roster"
- "What players are on my team?"

**Check Drafted Players:**
- "Who are the drafted quarterbacks in my league?"
- "List all drafted players"

**Search Waiver Wire:**
- "Find available running backs"
- "Show me available players named Williams"
- "What tight ends are on waivers?"
- "Search for available WR named Brown"

## Troubleshooting

**"OAuth2 credentials file not found"**
- Ensure `..oauth2.json` exists in parent directory
- Or update `OAUTH2_PATH` in `.env`

**"Token expired"**
- Run: `python ../utils/auth_setup.py`

**Server doesn't start**
- Activate venv: `source ../.venv/bin/activate`
- Check Python version: `python --version` (should be 3.12+)

**Agent not responding in Copilot CLI**
- Verify MCP config has correct absolute path to `server.py`
- Check that `.env` file exists with correct IDs
- Test server manually to confirm it runs

## Environment Variables

The agent uses these from `.env`:

- `OAUTH2_PATH` - Path to oauth2.json (default: `../oauth2.json`)
- `LEAGUE_ID` - Your Yahoo league ID (e.g., `461.l.123456`)
- `TEAM_ID` - Your team ID (e.g., `461.l.123456.t.7`)

## Next Steps

1. ✅ Agent is created and tested
2. Configure Copilot CLI to use the agent (see Method 1-3 above)
3. Start asking questions about your fantasy team!

## Files Overview

- `server.py` - Main MCP server with 3 tools
- `mcp-config.json` - Pre-configured MCP server definition
- `.env` - Your configuration (already set up)
- `README.md` - Full documentation
- `SETUP.md` - This file

For complete documentation, see `README.md`.
