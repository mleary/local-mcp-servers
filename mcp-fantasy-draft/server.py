from typing import Any
import random

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name='yahoo-fantasy-helper',
    stateless_http=True,
)


@mcp.tool()
def hello_tool(input: str) -> str:
    """A playful greeting tool that echoes messages with fun additions.
    
    Use for casual greetings, testing tool functionality, or adding whimsy to conversations. 
    Adds 'Hello,' prefix, 'foo foo!' suffix, and a random number between 1-102.
    """
    num = random.randint(1, 100)
    return f"Hello, {input} foo foo! {num}"

@mcp.tool()
def get_available_players(league_id: str) -> str:
    """Checks Yahoo Fantasy API to see what players are available for drafting."""
    # Simulate fetching available players
    available_players = ["Player D", "Player E", "Player F"]
    return f"Available players in league {league_id}: {', '.join(available_players)}"

@mcp.tool()
def get_team_roster(league_id: str, team_id: str) -> str:
    """Checks Yahoo Fantasy API to see what players are on a specific team's roster."""
    # Simulate fetching team roster
    team_roster = ["Player A", "Player B", "Player C"]
    return f"Roster for team {team_id} in league {league_id}: {', '.join(team_roster)}"

@mcp.tool()
def get_player_stats(player_id: str) -> str:
    """Fetches available stats for a specific player."""

@mcp.tool()
def get_player_project_weekly_stats(player_id: str) -> str:
    """Fetches projected weekly stats for a specific player."""


# run server
if __name__ == "__main__":  
    mcp.run(transport="stdio") 