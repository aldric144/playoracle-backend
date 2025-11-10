"""
SportsDataIO Client - Live Sports Data Integration
Provides real-time sports data for all supported sports with caching and rate limiting
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SportType(str, Enum):
    """Supported sports in SportsDataIO"""
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    SOCCER = "soccer"
    GOLF = "golf"
    NASCAR = "nascar"
    TENNIS = "tennis"
    MMA = "mma"
    BOXING = "boxing"
    COLLEGE_FOOTBALL = "cfb"
    VOLLEYBALL = "volleyball"
    RUGBY = "rugby"
    CRICKET = "cricket"


class SportsDataIOClient:
    """
    Client for SportsDataIO API
    Handles live data fetching with rate limiting and error handling
    """
    
    BASE_URLS = {
        SportType.NFL: "https://api.sportsdata.io/v3/nfl",
        SportType.NBA: "https://api.sportsdata.io/v3/nba",
        SportType.MLB: "https://api.sportsdata.io/v3/mlb",
        SportType.NHL: "https://api.sportsdata.io/v3/nhl",
        SportType.SOCCER: "https://api.sportsdata.io/v4/soccer",
        SportType.GOLF: "https://api.sportsdata.io/v2/golf",
        SportType.NASCAR: "https://api.sportsdata.io/v2/nascar",
        SportType.TENNIS: "https://api.sportsdata.io/v2/tennis",
        SportType.MMA: "https://api.sportsdata.io/v3/mma",
        SportType.BOXING: "https://api.sportsdata.io/v3/boxing",
        SportType.COLLEGE_FOOTBALL: "https://api.sportsdata.io/v3/cfb",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_delay = 1.0  # 1 second between requests for free tier
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
    
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make API request with error handling and rate limiting"""
        await self._rate_limit()
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    logger.error("SportsDataIO API authentication failed - invalid API key")
                    return None
                elif response.status == 429:
                    logger.warning("SportsDataIO rate limit exceeded")
                    return None
                else:
                    logger.error(f"SportsDataIO API error: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"SportsDataIO request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"SportsDataIO request failed: {e}")
            return None
    
    async def get_nfl_schedules(self, season: str = "2025") -> List[Dict[str, Any]]:
        """Get NFL schedules for current season"""
        url = f"{self.BASE_URLS[SportType.NFL]}/scores/json/Schedules/{season}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_nfl_scores(self, season: str = "2025", week: int = 1) -> List[Dict[str, Any]]:
        """Get NFL scores for specific week"""
        url = f"{self.BASE_URLS[SportType.NFL]}/scores/json/ScoresByWeek/{season}/{week}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_nfl_standings(self, season: str = "2025") -> List[Dict[str, Any]]:
        """Get NFL standings"""
        url = f"{self.BASE_URLS[SportType.NFL]}/scores/json/Standings/{season}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_nba_games(self, date: str) -> List[Dict[str, Any]]:
        """Get NBA games for specific date (YYYY-MM-DD)"""
        url = f"{self.BASE_URLS[SportType.NBA]}/scores/json/GamesByDate/{date}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_nba_standings(self, season: str = "2025") -> List[Dict[str, Any]]:
        """Get NBA standings"""
        url = f"{self.BASE_URLS[SportType.NBA]}/scores/json/Standings/{season}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_mlb_games(self, date: str) -> List[Dict[str, Any]]:
        """Get MLB games for specific date (YYYY-MM-DD)"""
        url = f"{self.BASE_URLS[SportType.MLB]}/scores/json/GamesByDate/{date}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_mlb_standings(self, season: str = "2025") -> List[Dict[str, Any]]:
        """Get MLB standings"""
        url = f"{self.BASE_URLS[SportType.MLB]}/scores/json/Standings/{season}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_nhl_games(self, date: str) -> List[Dict[str, Any]]:
        """Get NHL games for specific date (YYYY-MM-DD)"""
        url = f"{self.BASE_URLS[SportType.NHL]}/scores/json/GamesByDate/{date}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_nhl_standings(self, season: str = "2025") -> List[Dict[str, Any]]:
        """Get NHL standings"""
        url = f"{self.BASE_URLS[SportType.NHL]}/scores/json/Standings/{season}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_soccer_games(self, competition: str = "EPL") -> List[Dict[str, Any]]:
        """Get soccer games for specific competition"""
        url = f"{self.BASE_URLS[SportType.SOCCER]}/scores/json/GamesByDate/{competition}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_soccer_standings(self, competition: str = "EPL") -> List[Dict[str, Any]]:
        """Get soccer standings"""
        url = f"{self.BASE_URLS[SportType.SOCCER]}/scores/json/Standings/{competition}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_golf_tournaments(self) -> List[Dict[str, Any]]:
        """Get current golf tournaments"""
        url = f"{self.BASE_URLS[SportType.GOLF]}/scores/json/Tournaments"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_golf_leaderboard(self, tournament_id: int) -> Dict[str, Any]:
        """Get golf tournament leaderboard"""
        url = f"{self.BASE_URLS[SportType.GOLF]}/scores/json/Leaderboard/{tournament_id}"
        data = await self._make_request(url)
        return data if data else {}
    
    async def get_tennis_matches(self) -> List[Dict[str, Any]]:
        """Get current tennis matches"""
        url = f"{self.BASE_URLS[SportType.TENNIS]}/scores/json/Matches"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_mma_events(self) -> List[Dict[str, Any]]:
        """Get upcoming MMA events"""
        url = f"{self.BASE_URLS[SportType.MMA]}/scores/json/Schedule"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_mma_event_details(self, event_id: int) -> Dict[str, Any]:
        """Get MMA event details"""
        url = f"{self.BASE_URLS[SportType.MMA]}/scores/json/Event/{event_id}"
        data = await self._make_request(url)
        return data if data else {}
    
    async def get_boxing_schedule(self) -> List[Dict[str, Any]]:
        """Get boxing schedule"""
        url = f"{self.BASE_URLS[SportType.BOXING]}/scores/json/Schedule"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_boxing_fight_details(self, fight_id: int) -> Dict[str, Any]:
        """Get boxing fight details"""
        url = f"{self.BASE_URLS[SportType.BOXING]}/scores/json/Fight/{fight_id}"
        data = await self._make_request(url)
        return data if data else {}
    
    async def get_cfb_games(self, season: str = "2025", week: int = 1) -> List[Dict[str, Any]]:
        """Get college football games"""
        url = f"{self.BASE_URLS[SportType.COLLEGE_FOOTBALL]}/scores/json/GamesByWeek/{season}/{week}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_cfb_standings(self, season: str = "2025") -> List[Dict[str, Any]]:
        """Get college football standings"""
        url = f"{self.BASE_URLS[SportType.COLLEGE_FOOTBALL]}/scores/json/Standings/{season}"
        data = await self._make_request(url)
        return data if data else []
    
    async def get_generic_schedule(self, sport: str) -> List[Dict[str, Any]]:
        """Fallback for sports not yet supported by SportsDataIO"""
        logger.warning(f"Sport {sport} not yet supported by SportsDataIO - using fallback")
        return []


class LiveDataService:
    """
    High-level service for managing live sports data
    Handles caching, fallbacks, and data transformation
    """
    
    def __init__(self, api_key: str, use_mock: bool = False):
        self.api_key = api_key
        self.use_mock = use_mock or not api_key or api_key == "test"
        self.client: Optional[SportsDataIOClient] = None
    
    async def get_upcoming_games(self, sport: str) -> List[Dict[str, Any]]:
        """Get upcoming games for any sport with fallback to mock data"""
        if self.use_mock:
            return self._get_mock_games(sport)
        
        try:
            async with SportsDataIOClient(self.api_key) as client:
                sport_type = self._map_sport_to_type(sport)
                
                if sport_type == SportType.NFL:
                    return await client.get_nfl_schedules()
                elif sport_type == SportType.NBA:
                    today = datetime.now().strftime("%Y-%m-%d")
                    return await client.get_nba_games(today)
                elif sport_type == SportType.MLB:
                    today = datetime.now().strftime("%Y-%m-%d")
                    return await client.get_mlb_games(today)
                elif sport_type == SportType.NHL:
                    today = datetime.now().strftime("%Y-%m-%d")
                    return await client.get_nhl_games(today)
                elif sport_type == SportType.SOCCER:
                    return await client.get_soccer_games()
                elif sport_type == SportType.GOLF:
                    return await client.get_golf_tournaments()
                elif sport_type == SportType.TENNIS:
                    return await client.get_tennis_matches()
                elif sport_type == SportType.MMA:
                    return await client.get_mma_events()
                elif sport_type == SportType.BOXING:
                    return await client.get_boxing_schedule()
                elif sport_type == SportType.COLLEGE_FOOTBALL:
                    return await client.get_cfb_games()
                else:
                    return await client.get_generic_schedule(sport)
        except Exception as e:
            logger.error(f"Failed to fetch live data for {sport}: {e}")
            return self._get_mock_games(sport)
    
    async def get_scores(self, sport: str) -> List[Dict[str, Any]]:
        """Get live scores for any sport"""
        if self.use_mock:
            return self._get_mock_scores(sport)
        
        try:
            async with SportsDataIOClient(self.api_key) as client:
                sport_type = self._map_sport_to_type(sport)
                
                if sport_type == SportType.NFL:
                    return await client.get_nfl_scores()
                elif sport_type == SportType.NBA:
                    today = datetime.now().strftime("%Y-%m-%d")
                    return await client.get_nba_games(today)
                elif sport_type == SportType.MLB:
                    today = datetime.now().strftime("%Y-%m-%d")
                    return await client.get_mlb_games(today)
                elif sport_type == SportType.NHL:
                    today = datetime.now().strftime("%Y-%m-%d")
                    return await client.get_nhl_games(today)
                else:
                    return []
        except Exception as e:
            logger.error(f"Failed to fetch scores for {sport}: {e}")
            return self._get_mock_scores(sport)
    
    async def get_standings(self, sport: str) -> List[Dict[str, Any]]:
        """Get standings for any sport"""
        if self.use_mock:
            return self._get_mock_standings(sport)
        
        try:
            async with SportsDataIOClient(self.api_key) as client:
                sport_type = self._map_sport_to_type(sport)
                
                if sport_type == SportType.NFL:
                    return await client.get_nfl_standings()
                elif sport_type == SportType.NBA:
                    return await client.get_nba_standings()
                elif sport_type == SportType.MLB:
                    return await client.get_mlb_standings()
                elif sport_type == SportType.NHL:
                    return await client.get_nhl_standings()
                elif sport_type == SportType.SOCCER:
                    return await client.get_soccer_standings()
                elif sport_type == SportType.COLLEGE_FOOTBALL:
                    return await client.get_cfb_standings()
                else:
                    return []
        except Exception as e:
            logger.error(f"Failed to fetch standings for {sport}: {e}")
            return self._get_mock_standings(sport)
    
    def _map_sport_to_type(self, sport: str) -> SportType:
        """Map sport string to SportType enum"""
        sport_map = {
            "nfl": SportType.NFL,
            "nba": SportType.NBA,
            "mlb": SportType.MLB,
            "nhl": SportType.NHL,
            "soccer": SportType.SOCCER,
            "premier_league": SportType.SOCCER,
            "golf": SportType.GOLF,
            "tennis": SportType.TENNIS,
            "mma": SportType.MMA,
            "boxing": SportType.BOXING,
            "college_football": SportType.COLLEGE_FOOTBALL,
            "cfb": SportType.COLLEGE_FOOTBALL,
            "volleyball": SportType.VOLLEYBALL,
            "rugby": SportType.RUGBY,
            "cricket": SportType.CRICKET,
        }
        return sport_map.get(sport.lower(), SportType.NFL)
    
    def _get_mock_games(self, sport: str) -> List[Dict[str, Any]]:
        """Return mock game data for testing"""
        now = datetime.now()
        return [
            {
                "id": f"mock-{sport}-1",
                "sport": sport,
                "home_team": "Team A",
                "away_team": "Team B",
                "start_time": (now + timedelta(days=1)).isoformat(),
                "venue": "Stadium A",
                "status": "Scheduled",
                "is_live": False,
                "mock_data": True
            },
            {
                "id": f"mock-{sport}-2",
                "sport": sport,
                "home_team": "Team C",
                "away_team": "Team D",
                "start_time": (now + timedelta(days=2)).isoformat(),
                "venue": "Stadium B",
                "status": "Scheduled",
                "is_live": False,
                "mock_data": True
            }
        ]
    
    def _get_mock_scores(self, sport: str) -> List[Dict[str, Any]]:
        """Return mock score data"""
        return [
            {
                "id": f"mock-{sport}-score-1",
                "sport": sport,
                "home_team": "Team A",
                "away_team": "Team B",
                "home_score": 24,
                "away_score": 21,
                "status": "Final",
                "is_live": False,
                "mock_data": True
            }
        ]
    
    def _get_mock_standings(self, sport: str) -> List[Dict[str, Any]]:
        """Return mock standings data"""
        return [
            {
                "team": "Team A",
                "wins": 10,
                "losses": 2,
                "ties": 0,
                "win_pct": 0.833,
                "rank": 1,
                "mock_data": True
            },
            {
                "team": "Team B",
                "wins": 8,
                "losses": 4,
                "ties": 0,
                "win_pct": 0.667,
                "rank": 2,
                "mock_data": True
            }
        ]
