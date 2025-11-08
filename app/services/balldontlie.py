import httpx
from typing import List, Dict, Optional

class BallDontLieService:
    BASE_URL = "https://api.balldontlie.io/v1"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_teams(self) -> List[Dict]:
        """Get all NBA teams"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/teams")
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching NBA teams: {e}")
            return []
    
    async def get_games(self, season: int = 2024, page: int = 1) -> List[Dict]:
        """Get NBA games for a season"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/games",
                params={"seasons[]": season, "page": page, "per_page": 25}
            )
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching NBA games: {e}")
            return []
    
    async def get_player_stats(self, player_id: int, season: int = 2024) -> List[Dict]:
        """Get player stats for a season"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/stats",
                params={"player_ids[]": player_id, "seasons[]": season}
            )
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()
