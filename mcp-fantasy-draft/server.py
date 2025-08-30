from typing import Any, Optional, Dict, List
import random
import os
import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league, team, game

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


mcp = FastMCP(
    name='yahoo-fantasy-helper',
    stateless_http=True,
)

# Global OAuth instance - initialized lazily
_oauth_instance = None

def get_oauth_instance() -> Optional[OAuth2]:
    """Get or create Yahoo OAuth instance with proper error handling."""
    global _oauth_instance
    
    if _oauth_instance is not None:
        return _oauth_instance
    
    try:
        client_id = os.getenv('YAHOO_CLIENT_ID')
        client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("Yahoo OAuth credentials not found in environment variables")
            return None
            
        redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'oob')
        token_file = os.getenv('YAHOO_TOKEN_FILE', 'oauth_token.json')
        
        _oauth_instance = OAuth2(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            base_url='https://fantasysports.yahooapis.com/'
        )
        
        # Try to load existing token
        token_path = Path(token_file)
        if token_path.exists():
            logger.info("Loading existing OAuth token")
            _oauth_instance.token_file = str(token_path)
        
        return _oauth_instance
        
    except Exception as e:
        logger.error(f"Failed to initialize Yahoo OAuth: {e}")
        return None

def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with error handling."""
    try:
        oauth = get_oauth_instance()
        if not oauth:
            return "Error: Yahoo OAuth not configured. Please check your environment variables."
        
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return f"Error: API call failed - {str(e)}"


@mcp.tool()
def hello_tool(input: str) -> str:
    """A playful greeting tool that echoes messages with fun additions.
    
    Use for casual greetings, testing tool functionality, or adding whimsy to conversations. 
    Adds 'Hello,' prefix, 'foo foo!' suffix, and a random number between 1-102.
    """
    num = random.randint(1, 100)
    return f"Hello, {input} foo foo! {num}"

@mcp.tool()
def get_available_players(league_id: str, position: str = "ALL") -> str:
    """Checks Yahoo Fantasy API to see what players are available for drafting.
    
    Args:
        league_id: Yahoo league ID (format: game_key.league_id, e.g., '423.l.12345')
        position: Player position filter (QB, RB, WR, TE, K, DEF, or ALL)
    """
    def _get_players():
        oauth = get_oauth_instance()
        lg = league.League(oauth, league_id)
        
        # Get free agents
        free_agents = lg.free_agents(position if position != "ALL" else None)
        
        if not free_agents:
            return f"No available players found in league {league_id} for position {position}"
        
        player_list = []
        for player in free_agents[:20]:  # Limit to top 20
            player_info = f"{player.get('name', 'Unknown')} ({player.get('position_type', 'N/A')})"
            if 'player_points' in player:
                player_info += f" - {player['player_points']['total']} pts"
            player_list.append(player_info)
        
        return f"Available players in league {league_id} ({position}):\n" + "\n".join(player_list)
    
    return safe_api_call(_get_players)

@mcp.tool()
def get_team_roster(league_id: str, team_id: str = None) -> str:
    """Checks Yahoo Fantasy API to see what players are on a specific team's roster.
    
    Args:
        league_id: Yahoo league ID (format: game_key.league_id, e.g., '423.l.12345')
        team_id: Team ID (if not provided, gets user's own team)
    """
    def _get_roster():
        oauth = get_oauth_instance()
        lg = league.League(oauth, league_id)
        
        if team_id:
            tm = team.Team(oauth, f"{league_id}.t.{team_id}")
        else:
            # Get user's team
            teams = lg.teams()
            user_teams = [t for t in teams if t.get('is_owned_by_current_login') == '1']
            if not user_teams:
                return f"No team found for current user in league {league_id}"
            tm = team.Team(oauth, user_teams[0]['team_key'])
        
        roster = tm.roster()
        
        if not roster:
            return f"No roster found for team {team_id or 'current user'} in league {league_id}"
        
        player_list = []
        for player in roster:
            player_info = f"{player.get('name', 'Unknown')} ({player.get('position_type', 'N/A')})"
            if 'player_points' in player:
                player_info += f" - {player['player_points']['total']} pts"
            player_list.append(player_info)
        
        team_name = tm.team_name() if hasattr(tm, 'team_name') else team_id or "Current user"
        return f"Roster for {team_name} in league {league_id}:\n" + "\n".join(player_list)
    
    return safe_api_call(_get_roster)

@mcp.tool()
def get_player_stats(player_key: str, season: str = "2024") -> str:
    """Fetches available stats for a specific player.
    
    Args:
        player_key: Yahoo player key (format: game_key.p.player_id, e.g., '423.p.12345')
        season: Season year (default: 2024)
    """
    def _get_stats():
        oauth = get_oauth_instance()
        
        # Parse player key to get game key and player ID
        parts = player_key.split('.')
        if len(parts) < 3:
            return f"Invalid player key format: {player_key}. Expected format: game_key.p.player_id"
        
        game_key = parts[0]
        player_id = parts[2]
        
        # Get player stats using the API
        # Note: This is a simplified approach - the actual API might require different calls
        try:
            from yahoo_fantasy_api.yhandler import YHandler
            yh = YHandler(oauth)
            
            # Get player information and stats
            url = f"https://fantasysports.yahooapis.com/fantasy/v2/player/{player_key}/stats"
            response = yh.get(url)
            
            # Parse response (this would need to be adjusted based on actual API response format)
            if response and 'fantasy_content' in response:
                player_data = response['fantasy_content']['player']
                name = player_data.get('name', {}).get('full', 'Unknown Player')
                stats = player_data.get('player_stats', {}).get('stats', [])
                
                if stats:
                    stat_lines = [f"Player: {name}"]
                    for stat in stats:
                        stat_id = stat.get('stat_id')
                        value = stat.get('value', 'N/A')
                        stat_lines.append(f"Stat {stat_id}: {value}")
                    
                    return "\n".join(stat_lines)
                else:
                    return f"No stats found for player {name} ({player_key})"
            else:
                return f"No data found for player {player_key}"
                
        except Exception as e:
            return f"Error fetching stats for player {player_key}: {str(e)}"
    
    return safe_api_call(_get_stats)

@mcp.tool()
def get_player_projected_stats(player_key: str, week: str = "current") -> str:
    """Fetches projected weekly stats for a specific player.
    
    Args:
        player_key: Yahoo player key (format: game_key.p.player_id, e.g., '423.p.12345')
        week: Week number or 'current' for current week
    """
    def _get_projected():
        oauth = get_oauth_instance()
        
        try:
            from yahoo_fantasy_api.yhandler import YHandler
            yh = YHandler(oauth)
            
            # Get projected stats
            url = f"https://fantasysports.yahooapis.com/fantasy/v2/player/{player_key}/stats;type=projected_stats"
            if week != "current":
                url += f";week={week}"
            
            response = yh.get(url)
            
            if response and 'fantasy_content' in response:
                player_data = response['fantasy_content']['player']
                name = player_data.get('name', {}).get('full', 'Unknown Player')
                stats = player_data.get('player_stats', {}).get('stats', [])
                
                if stats:
                    stat_lines = [f"Projected stats for {name} (Week {week}):"]
                    for stat in stats:
                        stat_id = stat.get('stat_id')
                        value = stat.get('value', 'N/A')
                        stat_lines.append(f"Stat {stat_id}: {value}")
                    
                    return "\n".join(stat_lines)
                else:
                    return f"No projected stats found for player {name} ({player_key})"
            else:
                return f"No projected data found for player {player_key}"
                
        except Exception as e:
            return f"Error fetching projected stats for player {player_key}: {str(e)}"
    
    return safe_api_call(_get_projected)

@mcp.tool()
def get_league_info(league_id: str) -> str:
    """Get basic information about a Yahoo Fantasy league.
    
    Args:
        league_id: Yahoo league ID (format: game_key.league_id, e.g., '423.l.12345')
    """
    def _get_league_info():
        oauth = get_oauth_instance()
        lg = league.League(oauth, league_id)
        
        settings = lg.settings()
        teams = lg.teams()
        
        info_lines = [
            f"League: {settings.get('name', 'Unknown League')}",
            f"Season: {settings.get('season', 'Unknown')}",
            f"Number of Teams: {len(teams)}",
            f"Scoring Type: {settings.get('scoring_type', 'Unknown')}",
            f"Draft Status: {settings.get('draft_status', 'Unknown')}",
        ]
        
        if 'trade_end_date' in settings:
            info_lines.append(f"Trade Deadline: {settings['trade_end_date']}")
        
        return "\n".join(info_lines)
    
    return safe_api_call(_get_league_info)

@mcp.tool()
def get_draft_results(league_id: str) -> str:
    """Get draft results for a Yahoo Fantasy league.
    
    Args:
        league_id: Yahoo league ID (format: game_key.league_id, e.g., '423.l.12345')
    """
    def _get_draft_results():
        oauth = get_oauth_instance()
        lg = league.League(oauth, league_id)
        
        try:
            draft_results = lg.draft_results()
            
            if not draft_results:
                return f"No draft results found for league {league_id}. Draft may not be completed yet."
            
            result_lines = ["Draft Results:"]
            for pick in draft_results[:50]:  # Show first 50 picks
                round_num = pick.get('round', 'Unknown')
                pick_num = pick.get('pick', 'Unknown')
                player_name = pick.get('player_name', 'Unknown Player')
                team_name = pick.get('team_name', 'Unknown Team')
                
                result_lines.append(f"Round {round_num}, Pick {pick_num}: {player_name} to {team_name}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Unable to fetch draft results: {str(e)}"
    
    return safe_api_call(_get_draft_results)

@mcp.tool()
def get_player_rankings(league_id: str, position: str = "ALL", count: int = 20) -> str:
    """Get player rankings for draft assistance.
    
    Args:
        league_id: Yahoo league ID (format: game_key.league_id, e.g., '423.l.12345')
        position: Player position (QB, RB, WR, TE, K, DEF, or ALL)
        count: Number of players to return (default: 20)
    """
    def _get_rankings():
        oauth = get_oauth_instance()
        lg = league.League(oauth, league_id)
        
        # Get available players (free agents) and sort by projected points
        free_agents = lg.free_agents(position if position != "ALL" else None)
        
        if not free_agents:
            return f"No available players found for position {position} in league {league_id}"
        
        # Sort by projected points or other ranking criteria
        ranked_players = []
        for player in free_agents[:count]:
            name = player.get('name', 'Unknown')
            pos = player.get('position_type', 'N/A')
            
            # Try to get projected points or other ranking info
            points = 'N/A'
            if 'player_points' in player:
                points = player['player_points'].get('total', 'N/A')
            
            ranked_players.append({
                'name': name,
                'position': pos,
                'points': points,
                'rank': len(ranked_players) + 1
            })
        
        if not ranked_players:
            return f"No ranking data available for position {position}"
        
        ranking_lines = [f"Top {len(ranked_players)} Available Players ({position}):"]
        for player in ranked_players:
            ranking_lines.append(
                f"{player['rank']}. {player['name']} ({player['position']}) - {player['points']} pts"
            )
        
        return "\n".join(ranking_lines)
    
    return safe_api_call(_get_rankings)

@mcp.tool()
def setup_oauth() -> str:
    """Initialize OAuth setup for Yahoo Fantasy API access."""
    try:
        client_id = os.getenv('YAHOO_CLIENT_ID')
        client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return """
OAuth Setup Required:

1. Visit https://developer.yahoo.com/apps/
2. Create a new app or use an existing one
3. Copy your Client ID and Client Secret
4. Create a .env file with:
   YAHOO_CLIENT_ID=your_client_id_here
   YAHOO_CLIENT_SECRET=your_client_secret_here

See .env.example for a template.
"""
        
        oauth = get_oauth_instance()
        if oauth:
            return "OAuth configured successfully. You may need to authenticate via browser on first API call."
        else:
            return "OAuth configuration failed. Please check your credentials."
            
    except Exception as e:
        return f"OAuth setup error: {str(e)}"


# run server
if __name__ == "__main__":  
    mcp.run(transport="stdio") 