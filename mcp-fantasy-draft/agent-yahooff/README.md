# Yahoo Fantasy Football Agent

A minimal MCP (Model Context Protocol) agent for interacting with Yahoo Fantasy Football via GitHub Copilot CLI.

## Features

This agent provides three core tools:

1. **`get_my_team_roster`** - View your team's roster with player names and positions
2. **`get_drafted_players`** - See all players drafted in your league with ownership stats
3. **`search_available_players`** - Search the waiver wire by position and/or name

## Requirements

- Python 3.12+ (see `.python-version` in parent directory)
- GitHub Copilot CLI
- Yahoo OAuth2 credentials (shared from parent directory)
- Package manager: `uv` (recommended) or `pip`

## Quick Start

### 1. Set Up OAuth (if not already done)

If you haven't set up OAuth credentials yet, go to the parent directory and run:

```bash
cd ..
python utils/auth_setup.py
```

This creates `oauth2.json` which will be shared with this agent.

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your values
# OAUTH2_PATH=../oauth2.json (or full path)
# LEAGUE_ID=461.l.xxxxxx
# TEAM_ID=461.l.xxxxxx.t.x
```

**Finding Your IDs:**
- Go to your Yahoo Fantasy Football league page
- Look at the URL: `https://football.fantasysports.yahoo.com/f1/461.l.123456`
- League ID: `461.l.123456`
- Team ID: Click your team, URL will show: `461.l.123456.t.7`

### 3. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Test the Agent

Test that the server runs correctly:

```bash
python server.py
```

The server should start and wait for MCP protocol messages on stdio. Press `Ctrl+C` to exit.

## Using with Copilot CLI

### Configure as Custom Agent

Add this agent to your Copilot CLI configuration. The exact method depends on your Copilot CLI setup:

**Option 1: Via MCP Configuration File**

Create or edit your MCP configuration file (typically in `~/.config/mcp/` or project-specific):

```json
{
  "mcpServers": {
    "yahoo-fantasy": {
      "command": "python",
      "args": ["/full/path/to/agent-yahooff/server.py"],
      "env": {
        "OAUTH2_PATH": "/full/path/to/oauth2.json",
        "LEAGUE_ID": "461.l.xxxxxx",
        "TEAM_ID": "461.l.xxxxxx.t.x"
      }
    }
  }
}
```

**Option 2: Local Project Configuration**

You can also run the agent directly when needed:

```bash
# From this directory
python server.py
```

### Example Interactions

Once configured, you can ask Copilot CLI questions like:

- "Show me my fantasy team roster"
- "Who are the top available running backs on waivers?"
- "List all drafted quarterbacks in my league"
- "Find available wide receivers named Brown"

The agent will invoke the appropriate tools and return structured data.

## Tools Reference

### `get_my_team_roster(team_id: str = None)`

Returns your team's current roster.

**Parameters:**
- `team_id` (optional): Defaults to `TEAM_ID` from environment

**Returns:** JSON array of players with names and eligible positions

### `get_drafted_players(league_id: str = None)`

Returns all drafted players in the league.

**Parameters:**
- `league_id` (optional): Defaults to `LEAGUE_ID` from environment

**Returns:** JSON array of players with names, positions, and ownership percentage

### `search_available_players(league_id: str = None, position: str = None, name_filter: str = None, limit: int = 50)`

Search available players on the waiver wire.

**Parameters:**
- `league_id` (optional): Defaults to `LEAGUE_ID` from environment
- `position` (optional): Filter by position (e.g., 'QB', 'RB', 'WR', 'TE')
- `name_filter` (optional): Filter by player name (case-insensitive substring match)
- `limit` (optional): Maximum results to return (default: 50)

**Returns:** JSON array of available players with names, positions, ownership %, and status

## Troubleshooting

### "OAuth2 credentials file not found"
- Ensure `OAUTH2_PATH` in `.env` points to the correct location
- Run the auth setup from parent directory if needed

### "Token expired"
- Run `python ../utils/auth_setup.py` to refresh

### Agent not responding in Copilot CLI
- Check that the server runs successfully: `python server.py`
- Verify MCP configuration file has correct paths
- Check environment variables are set correctly

## Architecture

This is a lightweight MCP server using:
- **FastMCP** - Python framework for building MCP servers
- **yahoo-fantasy-api** - Python wrapper for Yahoo Fantasy API
- **yahoo-oauth** - OAuth2 authentication for Yahoo APIs

The agent runs locally and communicates via stdio with Copilot CLI.

## Security

- Never commit `oauth2.json` or `.env` files
- OAuth tokens are stored locally and refreshed automatically
- All operations are read-only (no add/drop/trade capabilities yet)

## Future Enhancements

Potential features (not yet implemented):
- Add/drop players
- Propose trades
- Player statistics and projections
- Matchup analysis
- Lineup optimization

## License

MIT License - See parent directory for full license details.
