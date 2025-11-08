import httpx
from typing import List, Dict, Optional
from app.config import get_settings

settings = get_settings()

class FootballDataService:
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self):
        self.api_key = settings.footballdata_api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"X-Auth-Token": self.api_key} if self.api_key else {}
        )
    
    async def get_competitions(self) -> List[Dict]:
        """Get all competitions"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/competitions")
            data = response.json()
            return data.get("competitions", [])
        except Exception as e:
            print(f"Error fetching competitions: {e}")
            return []
    
    async def get_matches(self, competition_id: str) -> List[Dict]:
        """Get matches for a competition"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/competitions/{competition_id}/matches")
            data = response.json()
            return data.get("matches", [])
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return []
    
    async def get_standings(self, competition_id: str) -> List[Dict]:
        """Get standings for a competition"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/competitions/{competition_id}/standings")
            data = response.json()
            return data.get("standings", [])
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []
    
    async def get_team(self, team_id: str) -> Optional[Dict]:
        """Get team details"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/teams/{team_id}")
            return response.json()
        except Exception as e:
            print(f"Error fetching team: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()
