"""
PandaScore Client - eSports Data Integration
Provides eSports data for LoL, CS2, Valorant, and other competitive gaming
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PandaScoreClient:
    """
    Client for PandaScore API
    Handles eSports data fetching with rate limiting and error handling
    """
    
    BASE_URL = "https://api.pandascore.co"
    
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
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Make API request with error handling and rate limiting"""
        await self._rate_limit()
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    logger.error("PandaScore API authentication failed - invalid API key")
                    return None
                elif response.status == 429:
                    logger.warning("PandaScore rate limit exceeded")
                    return None
                else:
                    logger.error(f"PandaScore API error: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"PandaScore request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"PandaScore request failed: {e}")
            return None
    
    async def get_lol_matches(self) -> List[Dict[str, Any]]:
        """Get League of Legends matches - stub for future implementation"""
        logger.info("LoL matches - using mock data (PandaScore integration pending)")
        return []
    
    async def get_cs2_matches(self) -> List[Dict[str, Any]]:
        """Get CS2 matches - stub for future implementation"""
        logger.info("CS2 matches - using mock data (PandaScore integration pending)")
        return []
    
    async def get_valorant_matches(self) -> List[Dict[str, Any]]:
        """Get Valorant matches - stub for future implementation"""
        logger.info("Valorant matches - using mock data (PandaScore integration pending)")
        return []
