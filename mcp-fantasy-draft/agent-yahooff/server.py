import json
import os

from dotenv import load_dotenv
from yahoo_oauth import OAuth2
import yahoo_fantasy_api.league as yfl
import yahoo_fantasy_api.team as yft
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name='yahoo-fantasy-football-agent'
)

# Load environment variables from .env file
load_dotenv()
oauth_path = os.getenv("OAUTH2_PATH") or "../oauth2.json"
if not os.path.exists(oauth_path):
    raise RuntimeError(
        f"OAuth2 credentials file not found at '{oauth_path}'. "
        "Set OAUTH2_PATH in your .env or ensure oauth2.json exists."
    )

oauth = OAuth2(None, None, from_file=oauth_path)
if not oauth.token_is_valid():
    oauth.refresh_access_token()

# Load league and team IDs from environment variables
league_id = os.getenv("LEAGUE_ID")
team_id = os.getenv("TEAM_ID")


@mcp.tool()
def get_my_team_roster(team_id: str = team_id) -> str:
    """Get your fantasy football team's roster with player names and eligible positions."""
    try:
        team = yft.Team(oauth, team_id)
        roster = team.roster()
        filtered = [
            {
                "name": p["name"],
                "eligible_positions": p.get("eligible_positions", [])
            }
            for p in roster
            if "name" in p
        ]
        return json.dumps(filtered, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error fetching team roster: {e}"})


@mcp.tool()
def get_drafted_players(league_id: str = league_id) -> str:
    """Get all players that have been drafted in your fantasy league, including their positions and percent owned."""
    try:
        league = yfl.League(oauth, league_id)
        drafted_players = league.taken_players()
        filtered = [
            {
                "name": p.get("name", ""),
                "eligible_positions": p.get("eligible_positions", []),
                "percent_owned": p.get("percent_owned", None)
            }
            for p in drafted_players
            if "name" in p
        ]
        return json.dumps(filtered, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error fetching drafted players: {e}"})


@mcp.tool()
def search_available_players(
    league_id: str = league_id,
    position: str = None,
    name_filter: str = None,
    limit: int = 50
) -> str:
    """Search for available players on the waiver wire. Filter by position (e.g., 'QB', 'RB', 'WR', 'TE') and/or name. Returns up to 'limit' results."""
    try:
        league = yfl.League(oauth, league_id)
        
        # Get free agents (available players)
        available_players = league.free_agents(position if position else "ALL")
        
        # Apply name filter if provided
        if name_filter:
            name_filter_lower = name_filter.lower()
            available_players = [
                p for p in available_players 
                if name_filter_lower in p.get("name", "").lower()
            ]
        
        # Limit results
        available_players = available_players[:limit]
        
        # Filter to relevant fields
        filtered = [
            {
                "name": p.get("name", ""),
                "eligible_positions": p.get("eligible_positions", []),
                "percent_owned": p.get("percent_owned", None),
                "status": p.get("status", "")
            }
            for p in available_players
            if "name" in p
        ]
        
        return json.dumps(filtered, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error fetching available players: {e}"})


# Run server
if __name__ == "__main__":
    mcp.run(transport="stdio")
