import httpx
from typing import List, Dict, Optional

class ErgastService:
    BASE_URL = "http://ergast.com/api/f1"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_current_season_races(self) -> List[Dict]:
        """Get current season F1 races"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/current.json")
            data = response.json()
            return data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        except Exception as e:
            print(f"Error fetching F1 races: {e}")
            return []
    
    async def get_driver_standings(self, season: str = "current") -> List[Dict]:
        """Get driver standings for a season"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/{season}/driverStandings.json")
            data = response.json()
            standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if standings_lists:
                return standings_lists[0].get("DriverStandings", [])
            return []
        except Exception as e:
            print(f"Error fetching driver standings: {e}")
            return []
    
    async def get_constructor_standings(self, season: str = "current") -> List[Dict]:
        """Get constructor standings for a season"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/{season}/constructorStandings.json")
            data = response.json()
            standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if standings_lists:
                return standings_lists[0].get("ConstructorStandings", [])
            return []
        except Exception as e:
            print(f"Error fetching constructor standings: {e}")
            return []
    
    async def get_race_results(self, season: str, round_num: str) -> List[Dict]:
        """Get race results"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/{season}/{round_num}/results.json")
            data = response.json()
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if races:
                return races[0].get("Results", [])
            return []
        except Exception as e:
            print(f"Error fetching race results: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()
