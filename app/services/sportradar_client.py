"""
Sportradar Client - Sports Data Integration
Provides sports data for MotoGP, Cycling, Horse Racing, and other motorsports
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SportradarClient:
    """
    Client for Sportradar API
    Handles data fetching with rate limiting and error handling
    """
    
    BASE_URL = "https://api.sportradar.com"
    
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
        
        url = f"{self.BASE_URL}/{endpoint}"
        if not params:
            params = {}
        params["api_key"] = self.api_key
        
        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    logger.error("Sportradar API authentication failed - invalid API key")
                    return None
                elif response.status == 429:
                    logger.warning("Sportradar rate limit exceeded")
                    return None
                else:
                    logger.error(f"Sportradar API error: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Sportradar request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"Sportradar request failed: {e}")
            return None
    
    async def get_motogp_schedule(self) -> List[Dict[str, Any]]:
        """Get MotoGP schedule - stub for future implementation"""
        logger.info("MotoGP schedule - using mock data (Sportradar integration pending)")
        return []
    
    async def get_cycling_events(self) -> List[Dict[str, Any]]:
        """Get cycling events - stub for future implementation"""
        logger.info("Cycling events - using mock data (Sportradar integration pending)")
        return []
    
    async def get_horse_racing_schedule(self) -> List[Dict[str, Any]]:
        """Get horse racing schedule - stub for future implementation"""
        logger.info("Horse racing schedule - using mock data (Sportradar integration pending)")
        return []
