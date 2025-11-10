"""
TheSportsDB Client - Sports Data Integration
Provides sports data for Table Tennis, Olympics, and other global sports
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TheSportsDBClient:
    """
    Client for TheSportsDB API
    Handles data fetching with rate limiting and error handling
    """
    
    BASE_URL = "https://www.thesportsdb.com/api/v1/json"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_delay = 1.0  # 1 second between requests
        self._last_request_time = datetime.now()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        now = datetime.now()
        time_since_last = (now - self._last_request_time).total_seconds()
        
        if time_since_last < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - time_since_last)
        
        self._last_request_time = datetime.now()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make API request with error handling and rate limiting"""
        await self._rate_limit()
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}/{self.api_key}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    logger.error("TheSportsDB API authentication failed - invalid API key")
                    return None
                elif response.status == 429:
                    logger.warning("TheSportsDB rate limit exceeded")
                    return None
                else:
                    logger.error(f"TheSportsDB API error: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"TheSportsDB request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"TheSportsDB request failed: {e}")
            return None
    
    async def get_table_tennis_events(self, league: str = "Table Tennis") -> List[Dict[str, Any]]:
        """Get table tennis events"""
        data = await self._make_request(f"eventsnextleague.php?id=4424")  # Table Tennis league ID
        if data and "events" in data:
            return data["events"] or []
        return []
    
    async def get_table_tennis_results(self, league_id: str = "4424") -> List[Dict[str, Any]]:
        """Get table tennis past results"""
        data = await self._make_request(f"eventspastleague.php?id={league_id}")
        if data and "events" in data:
            return data["events"] or []
        return []
    
    async def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get detailed event information"""
        data = await self._make_request(f"lookupevent.php?id={event_id}")
        if data and "events" in data and data["events"]:
            return data["events"][0]
        return {}
    
    async def search_events(self, sport: str, date: str = None) -> List[Dict[str, Any]]:
        """Search for events by sport and optional date"""
        endpoint = f"searchevents.php?e={sport}"
        if date:
            endpoint += f"&d={date}"
        
        data = await self._make_request(endpoint)
        if data and "event" in data:
            return data["event"] or []
        return []
