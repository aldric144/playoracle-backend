import httpx
from typing import List, Dict, Optional
from app.config import get_settings

settings = get_settings()

class TheSportsDBService:
    BASE_URL = "https://www.thesportsdb.com/api/v1/json"
    
    def __init__(self):
        self.api_key = settings.thesportsdb_api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_leagues(self, sport: str) -> List[Dict]:
        """Get all leagues for a sport"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.api_key}/all_leagues.php"
            )
            data = response.json()
            leagues = data.get("leagues", [])
            if sport:
                leagues = [l for l in leagues if l.get("strSport", "").lower() == sport.lower()]
            return leagues
        except Exception as e:
            print(f"Error fetching leagues: {e}")
            return []
    
    async def get_teams_by_league(self, league_id: str) -> List[Dict]:
        """Get all teams in a league"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.api_key}/lookup_all_teams.php?id={league_id}"
            )
            data = response.json()
            return data.get("teams", [])
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    async def get_next_events_by_league(self, league_id: str) -> List[Dict]:
        """Get upcoming events for a league"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.api_key}/eventsnextleague.php?id={league_id}"
            )
            data = response.json()
            return data.get("events", []) or []
        except Exception as e:
            print(f"Error fetching next events: {e}")
            return []
    
    async def get_last_events_by_league(self, league_id: str) -> List[Dict]:
        """Get recent events for a league"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.api_key}/eventspastleague.php?id={league_id}"
            )
            data = response.json()
            return data.get("events", []) or []
        except Exception as e:
            print(f"Error fetching past events: {e}")
            return []
    
    async def get_team_details(self, team_id: str) -> Optional[Dict]:
        """Get team details"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.api_key}/lookupteam.php?id={team_id}"
            )
            data = response.json()
            teams = data.get("teams", [])
            return teams[0] if teams else None
        except Exception as e:
            print(f"Error fetching team details: {e}")
            return None
    
    async def search_teams(self, team_name: str) -> List[Dict]:
        """Search for teams by name"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.api_key}/searchteams.php?t={team_name}"
            )
            data = response.json()
            return data.get("teams", []) or []
        except Exception as e:
            print(f"Error searching teams: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()
