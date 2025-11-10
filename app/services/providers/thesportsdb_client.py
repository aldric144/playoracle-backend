"""
TheSportsDB API Client - Layer 1 Data Provider
Provides team names, event schedules, fighter lists, match results (free tier)
"""
import httpx
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TheSportsDBClient:
    """Async client for TheSportsDB API with retry logic and rate limiting"""
    
    BASE_URL = "https://www.thesportsdb.com/api/v1/json"
    
    def __init__(self, api_key: str, timeout: float = 5.0, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(5)
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic and exponential backoff"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        
        url = f"{self.BASE_URL}/{self.api_key}/{endpoint}"
        
        async with self._semaphore:
            for attempt in range(self.max_retries):
                try:
                    response = await self._client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        wait_time = (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                        logger.warning(f"Rate limited, waiting {wait_time:.2f}s")
                        await asyncio.sleep(wait_time)
                        continue
                    logger.error(f"HTTP error {e.response.status_code}: {e}")
                    raise
                except httpx.TimeoutException:
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                        logger.warning(f"Timeout, retrying in {wait_time:.2f}s")
                        await asyncio.sleep(wait_time)
                        continue
                    logger.error("Request timed out after all retries")
                    raise
                except Exception as e:
                    logger.error(f"Request failed: {e}")
                    raise
        
        raise Exception("Max retries exceeded")
    
    async def get_upcoming_events_by_league(self, league_id: str) -> List[Dict[str, Any]]:
        """Get upcoming events for a specific league"""
        try:
            data = await self._request(f"eventsnextleague.php", {"id": league_id})
            return data.get("events", []) or []
        except Exception as e:
            logger.error(f"Failed to fetch upcoming events for league {league_id}: {e}")
            return []
    
    async def search_events(self, event_name: str) -> List[Dict[str, Any]]:
        """Search for events by name"""
        try:
            data = await self._request(f"searchevents.php", {"e": event_name})
            return data.get("event", []) or []
        except Exception as e:
            logger.error(f"Failed to search events for '{event_name}': {e}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed event information by ID"""
        try:
            data = await self._request(f"lookupevent.php", {"id": event_id})
            events = data.get("events", [])
            return events[0] if events else None
        except Exception as e:
            logger.error(f"Failed to fetch event {event_id}: {e}")
            return None
    
    async def search_team(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Search for team by name"""
        try:
            data = await self._request(f"searchteams.php", {"t": team_name})
            teams = data.get("teams", [])
            return teams[0] if teams else None
        except Exception as e:
            logger.error(f"Failed to search team '{team_name}': {e}")
            return None
    
    async def get_team_by_id(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get team details by ID"""
        try:
            data = await self._request(f"lookupteam.php", {"id": team_id})
            teams = data.get("teams", [])
            return teams[0] if teams else None
        except Exception as e:
            logger.error(f"Failed to fetch team {team_id}: {e}")
            return None
    
    async def get_upcoming_boxing_events(self) -> List[Dict[str, Any]]:
        """Get upcoming boxing events"""
        try:
            data = await self._request(f"searchevents.php", {"e": "boxing"})
            events = data.get("event", []) or []
            upcoming = []
            now = datetime.utcnow()
            
            for event in events:
                event_date_str = event.get("dateEvent")
                if event_date_str:
                    try:
                        event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                        if event_date > now:
                            upcoming.append(event)
                    except ValueError:
                        continue
            
            return upcoming
        except Exception as e:
            logger.error(f"Failed to fetch upcoming boxing events: {e}")
            return []
    
    async def search_fighter(self, fighter_name: str) -> Optional[Dict[str, Any]]:
        """Search for fighter/player by name"""
        try:
            data = await self._request(f"searchplayers.php", {"p": fighter_name})
            players = data.get("player", [])
            return players[0] if players else None
        except Exception as e:
            logger.error(f"Failed to search fighter '{fighter_name}': {e}")
            return None
    
    async def get_fighter_by_id(self, fighter_id: str) -> Optional[Dict[str, Any]]:
        """Get fighter/player details by ID"""
        try:
            data = await self._request(f"lookupplayer.php", {"id": fighter_id})
            players = data.get("players", [])
            return players[0] if players else None
        except Exception as e:
            logger.error(f"Failed to fetch fighter {fighter_id}: {e}")
            return None
    
    async def get_league_info(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Get league information"""
        try:
            data = await self._request(f"lookupleague.php", {"id": league_id})
            leagues = data.get("leagues", [])
            return leagues[0] if leagues else None
        except Exception as e:
            logger.error(f"Failed to fetch league {league_id}: {e}")
            return None

LEAGUE_IDS = {
    "nfl": "4391",
    "nba": "4387",
    "mlb": "4424",
    "nhl": "4380",
    "premier_league": "4328",
    "formula1": "4370",
    "ncaa_football": "4391",  # Using NFL ID as placeholder
    "boxing": None,  # Boxing doesn't have a league ID, use search
}
