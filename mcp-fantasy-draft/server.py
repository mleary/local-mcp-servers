import json
import os

from dotenv import load_dotenv
from yahoo_oauth import OAuth2
import yahoo_fantasy_api.league as yfl
import yahoo_fantasy_api.team as yft
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name='yahoo-fantasy-helper'
)


# Load environment variables from .env file
load_dotenv()
oauth_path = os.getenv("OAUTH2_PATH") or "./oauth2.json"
if not os.path.exists(oauth_path):
    raise RuntimeError(
        f"OAuth2 credentials file not found at '{oauth_path}'. "
        "Set OAUTH2_PATH in your .env or place oauth2.json in the project root."
    )

oauth = OAuth2(None, None, from_file=oauth_path)
if not oauth.token_is_valid():
    oauth.refresh_access_token()


# Load league and team IDs from environment variables
league_id = os.getenv("LEAGUE_ID")
team_id = os.getenv("TEAM_ID")
valid_positions = ['QB', 'WR', 'RB', 'TE', 'W/R/T', 'Q/W/R/T', 'K', 'DEF', 'D', 'DB', 'LB', 'BN', 'IR']

@mcp.tool()
def get_my_team_roster(team_id: str = team_id) -> str:
    """Checks Yahoo Fantasy API to see what players are on a specific team's roster."""
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
        return json.dumps(filtered)
    except Exception as e:
        return json.dumps({"error": f"Error fetching team roster: {e}"})


@mcp.tool()
def get_free_agents(league_id: str = league_id, position: str = "QB") -> str:
    """Checks Yahoo Fantasy API to see what players are available as free agents in a specific league. Valid positions are ['QB', 'WR', 'RB', 'TE', 'W/R/T', 'Q/W/R/T', 'K', 'DEF', 'D', 'DB', 'LB', 'BN', 'IR'] """
    try:
        # if position not in valid_positions:
        #     return json.dumps({"error": f"Invalid position '{position}'. Valid options are {valid_positions}."})
        league = yfl.League(oauth, league_id)
        free_agents = league.free_agents(position)
        filtered = [
            {
                "name": p.get("name", ""),
                "eligible_positions": p.get("eligible_positions", []),
                "percent_owned": p.get("percent_owned", None)
            }
            for p in free_agents
            if "name" in p
        ]
        return json.dumps(filtered)
    except Exception as e:
        return json.dumps({"error": f"Error fetching free agents: {e}"})

# @mcp.tool()
# def get_drafted_players(league_id: str = league_id) -> str:
#     """Checks Yahoo Fantasy API to see what players have been drafted in a specific league."""
#     try:
#         league = yfl.League(oauth, league_id)
#         drafted_players = league.taken_players()
#         filtered = [
#             {
#                 "name": p.get("name", ""),
#                 "eligible_positions": p.get("eligible_positions", []),
#                 "percent_owned": p.get("percent_owned", None)
#             }
#             for p in drafted_players
#             if "name" in p
#         ]
#         return json.dumps(filtered)
#     except Exception as e:
#         return json.dumps({"error": f"Error fetching drafted players: {e}"})


# run server
if __name__ == "__main__":  
    mcp.run(transport="stdio") 
