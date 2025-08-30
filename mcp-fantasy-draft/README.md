# Yahoo Fantasy Football MCP Server

An MCP (Model Context Protocol) server for Yahoo Fantasy Football that provides draft assistance and league management tools.

## Features

- **OAuth Authentication**: Secure Yahoo API access
- **Draft Assistance**: Get available players with rankings
- **Team Management**: View team rosters and player stats
- **League Information**: Access league settings and draft results
- **Player Analytics**: Get current and projected player statistics

## Setup

### 1. Yahoo Developer Account Setup

1. Visit [Yahoo Developer Console](https://developer.yahoo.com/apps/)
2. Create a new application or use an existing one
3. Note your **Client ID** and **Client Secret**
4. Set redirect URI to `oob` (out-of-band) for command-line usage

### 2. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Yahoo credentials:
   ```
   YAHOO_CLIENT_ID=your_client_id_here
   YAHOO_CLIENT_SECRET=your_client_secret_here
   YAHOO_REDIRECT_URI=oob
   YAHOO_TOKEN_FILE=oauth_token.json
   ```

### 3. Installation

```bash
pip install -e .
```

### 4. Running the Server

```bash
python server.py
```

## Available Tools

### Core Functions

- `setup_oauth()` - Initialize OAuth authentication
- `get_league_info(league_id)` - Get league information
- `get_available_players(league_id, position="ALL")` - List available players for drafting
- `get_team_roster(league_id, team_id=None)` - View team rosters
- `get_player_stats(player_key, season="2024")` - Get player statistics
- `get_player_projected_stats(player_key, week="current")` - Get projected stats
- `get_draft_results(league_id)` - View completed draft picks
- `get_player_rankings(league_id, position="ALL", count=20)` - Get ranked available players

### Parameters

- **league_id**: Yahoo league ID in format `game_key.l.league_id` (e.g., `423.l.12345`)
- **player_key**: Yahoo player key in format `game_key.p.player_id` (e.g., `423.p.12345`)
- **position**: Player position (`QB`, `RB`, `WR`, `TE`, `K`, `DEF`, or `ALL`)

## Authentication Flow

On first use, you'll need to:

1. Run `setup_oauth()` to check configuration
2. Make your first API call (e.g., `get_league_info()`)
3. Follow the browser authentication flow
4. The OAuth token will be saved for future use

## Security Notes

- Never commit your `.env` file to version control
- OAuth tokens are stored locally in `oauth_token.json`
- API calls include proper error handling and rate limiting
- All sensitive data is handled through environment variables

## Example Usage

```python
# Get league information
get_league_info("423.l.12345")

# Find available running backs
get_available_players("423.l.12345", "RB")

# Get top 10 available players with rankings
get_player_rankings("423.l.12345", "ALL", 10)

# View your team's roster
get_team_roster("423.l.12345")
```

## Troubleshooting

- **"OAuth not configured"**: Check your `.env` file has valid credentials
- **"No data found"**: Ensure league ID format is correct (`game_key.l.league_id`)
- **Authentication errors**: Delete `oauth_token.json` and re-authenticate