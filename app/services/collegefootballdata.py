import httpx
from typing import List, Dict, Optional

class CollegeFootballDataService:
    BASE_URL = "https://api.collegefootballdata.com"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_teams(self) -> List[Dict]:
        """Get all college football teams"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/teams")
            return response.json()
        except Exception as e:
            print(f"Error fetching college football teams: {e}")
            return []
    
    async def get_games(self, year: int = 2024, week: Optional[int] = None) -> List[Dict]:
        """Get college football games"""
        try:
            params = {"year": year}
            if week:
                params["week"] = week
            response = await self.client.get(f"{self.BASE_URL}/games", params=params)
            return response.json()
        except Exception as e:
            print(f"Error fetching college football games: {e}")
            return []
    
    async def get_team_records(self, year: int = 2024) -> List[Dict]:
        """Get team records for a season"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/records", params={"year": year})
            return response.json()
        except Exception as e:
            print(f"Error fetching team records: {e}")
            return []
    
    async def get_rankings(self, year: int = 2024, week: Optional[int] = None) -> List[Dict]:
        """Get team rankings"""
        try:
            params = {"year": year}
            if week:
                params["week"] = week
            response = await self.client.get(f"{self.BASE_URL}/rankings", params=params)
            return response.json()
        except Exception as e:
            print(f"Error fetching rankings: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()
