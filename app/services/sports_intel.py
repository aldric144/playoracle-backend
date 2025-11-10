"""
Sports Intelligence Aggregator - Hybrid Data Engine
Merges data from multiple providers (TheSportsDB, SportsDataIO, etc.) with AI DCI scoring
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid
import logging

from app.services.providers.thesportsdb_client import TheSportsDBClient, LEAGUE_IDS
from app.services.dci_service import BoxingDCIService, GameDCIService, DCIResult
from app.database import SportsEvent, Fighter, FightHistory, SportsCache, SportsCategoryEnum
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SportsIntelAggregator:
    """Orchestrates data fetching, merging, and DCI computation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.use_mock = settings.thesportsdb_api_key == "3" or not settings.thesportsdb_api_key
        self.boxing_dci = BoxingDCIService()
        self.game_dci = GameDCIService()
    
    async def fetch_schedule(self, sport: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Fetch schedule for a sport with caching"""
        cache_key = f"schedule:{sport}"
        
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Cache hit for {cache_key}")
                return cached
        
        if self.use_mock:
            events = self._get_mock_schedule(sport)
        else:
            events = await self._fetch_schedule_from_providers(sport)
        
        self._save_to_cache(cache_key, events, ttl_hours=12)
        
        return events
    
    async def _fetch_schedule_from_providers(self, sport: str) -> List[Dict[str, Any]]:
        """Fetch schedule from TheSportsDB and other providers"""
        league_id = LEAGUE_IDS.get(sport.lower())
        
        if not league_id:
            logger.warning(f"No league ID found for sport: {sport}")
            return []
        
        async with TheSportsDBClient(settings.thesportsdb_api_key) as client:
            events = await client.get_upcoming_events_by_league(league_id)
        
        merged_events = []
        for event in events:
            merged_event = self._merge_event_data(event, sport)
            merged_events.append(merged_event)
        
        return merged_events
    
    def _merge_event_data(self, event: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """Merge event data from multiple sources"""
        return {
            "id": event.get("idEvent"),
            "sport_type": sport,
            "league": event.get("strLeague"),
            "home_team": event.get("strHomeTeam"),
            "away_team": event.get("strAwayTeam"),
            "start_time": event.get("dateEvent"),
            "venue": event.get("strVenue"),
            "sources_used": ["thesportsdb"],
            "premium_data_available": False,
            "missing_fields": [],
            "merged_payload": event
        }
    
    async def fetch_upcoming_boxing(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Fetch upcoming boxing events"""
        cache_key = "boxing:upcoming"
        
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Cache hit for {cache_key}")
                return cached
        
        if self.use_mock:
            events = self._get_mock_boxing_events()
        else:
            events = await self._fetch_boxing_from_providers()
        
        self._save_to_cache(cache_key, events, ttl_hours=24)
        
        return events
    
    async def _fetch_boxing_from_providers(self) -> List[Dict[str, Any]]:
        """Fetch boxing events from TheSportsDB"""
        async with TheSportsDBClient(settings.thesportsdb_api_key) as client:
            events = await client.get_upcoming_boxing_events()
        
        merged_events = []
        for event in events:
            merged_event = self._merge_boxing_event(event)
            merged_events.append(merged_event)
        
        return merged_events
    
    def _merge_boxing_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Merge boxing event data"""
        fighter_one = event.get("strHomeTeam", "Fighter 1")
        fighter_two = event.get("strAwayTeam", "Fighter 2")
        
        return {
            "id": event.get("idEvent"),
            "sport_type": "boxing",
            "fighter_one": fighter_one,
            "fighter_two": fighter_two,
            "start_time": event.get("dateEvent"),
            "venue": event.get("strVenue"),
            "weight_class": event.get("strLeague", "Unknown"),
            "sources_used": ["thesportsdb"],
            "premium_data_available": False,
            "merged_payload": event
        }
    
    async def compute_boxing_dci(self, fight_id: str) -> Optional[Dict[str, Any]]:
        """Compute DCI for a boxing match"""
        event = self.db.query(SportsEvent).filter(
            SportsEvent.id == fight_id,
            SportsEvent.sport_type == "boxing"
        ).first()
        
        if not event:
            logger.error(f"Boxing event {fight_id} not found")
            return None
        
        fighter_one = self.db.query(Fighter).filter(Fighter.id == event.fighter_one_id).first()
        fighter_two = self.db.query(Fighter).filter(Fighter.id == event.fighter_two_id).first()
        
        if not fighter_one or not fighter_two:
            logger.warning(f"Fighters not found for event {fight_id}, using mock data")
            fighter_one_data = self._get_mock_fighter_data("Fighter 1")
            fighter_two_data = self._get_mock_fighter_data("Fighter 2")
        else:
            fighter_one_data = self._fighter_to_dict(fighter_one)
            fighter_two_data = self._fighter_to_dict(fighter_two)
        
        f1_dci, f2_dci = self.boxing_dci.compute_dci(fighter_one_data, fighter_two_data)
        
        event.dci_score = f1_dci.score
        event.dci_class = f1_dci.classification
        event.analysis_text = f"{f1_dci.reasoning} | {f2_dci.reasoning}"
        event.computed_at = datetime.utcnow()
        self.db.commit()
        
        return {
            "fight_id": fight_id,
            "fighter_one": {
                "name": fighter_one_data.get("name"),
                "dci": f1_dci.to_dict()
            },
            "fighter_two": {
                "name": fighter_two_data.get("name"),
                "dci": f2_dci.to_dict()
            },
            "prediction": f1_dci.classification if f1_dci.score > f2_dci.score else f2_dci.classification
        }
    
    def _fighter_to_dict(self, fighter: Fighter) -> Dict[str, Any]:
        """Convert Fighter model to dict"""
        return {
            "name": fighter.name,
            "age": fighter.age,
            "record_wins": fighter.record_wins,
            "record_losses": fighter.record_losses,
            "record_draws": fighter.record_draws,
            "ko_pct": fighter.ko_pct,
            "ko_wins": fighter.ko_wins,
            "ko_losses": fighter.ko_losses,
            "reach_cm": fighter.reach_cm,
            "power_idx": fighter.power_idx,
            "speed_idx": fighter.speed_idx,
            "stamina_idx": fighter.stamina_idx,
            "defense_idx": fighter.defense_idx,
            "win_streak": fighter.win_streak
        }
    
    async def sync_sports_data(self) -> Dict[str, Any]:
        """Background sync job to fetch and cache all sports data"""
        results = {
            "synced_at": datetime.utcnow().isoformat(),
            "sports": {},
            "boxing": {}
        }
        
        sports = ["nfl", "nba", "mlb", "nhl", "premier_league", "formula1"]
        
        for sport in sports:
            try:
                events = await self.fetch_schedule(sport, use_cache=False)
                results["sports"][sport] = {
                    "count": len(events),
                    "status": "success"
                }
                logger.info(f"Synced {len(events)} events for {sport}")
            except Exception as e:
                results["sports"][sport] = {
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"Failed to sync {sport}: {e}")
        
        try:
            boxing_events = await self.fetch_upcoming_boxing(use_cache=False)
            results["boxing"] = {
                "count": len(boxing_events),
                "status": "success"
            }
            logger.info(f"Synced {len(boxing_events)} boxing events")
        except Exception as e:
            results["boxing"] = {
                "count": 0,
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Failed to sync boxing: {e}")
        
        return results
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get data from cache if not expired"""
        cached = self.db.query(SportsCache).filter(SportsCache.cache_key == cache_key).first()
        
        if cached and cached.expires_at > datetime.utcnow():
            return cached.payload
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: List[Dict[str, Any]], ttl_hours: int = 24):
        """Save data to cache with TTL"""
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        cached = self.db.query(SportsCache).filter(SportsCache.cache_key == cache_key).first()
        
        if cached:
            cached.payload = data
            cached.expires_at = expires_at
            cached.created_at = datetime.utcnow()
        else:
            cached = SportsCache(
                cache_key=cache_key,
                payload=data,
                expires_at=expires_at
            )
            self.db.add(cached)
        
        self.db.commit()
    
    def _get_mock_schedule(self, sport: str) -> List[Dict[str, Any]]:
        """Return mock schedule data for testing"""
        now = datetime.utcnow()
        
        return [
            {
                "id": f"mock-{sport}-1",
                "sport_type": sport,
                "league": f"{sport.upper()} League",
                "home_team": "Team A",
                "away_team": "Team B",
                "start_time": (now + timedelta(days=1)).isoformat(),
                "venue": "Stadium A",
                "sources_used": ["mock"],
                "premium_data_available": False,
                "mock_data": True
            },
            {
                "id": f"mock-{sport}-2",
                "sport_type": sport,
                "league": f"{sport.upper()} League",
                "home_team": "Team C",
                "away_team": "Team D",
                "start_time": (now + timedelta(days=2)).isoformat(),
                "venue": "Stadium B",
                "sources_used": ["mock"],
                "premium_data_available": False,
                "mock_data": True
            }
        ]
    
    def _get_mock_boxing_events(self) -> List[Dict[str, Any]]:
        """Return mock boxing events for testing"""
        now = datetime.utcnow()
        
        return [
            {
                "id": "mock-boxing-1",
                "sport_type": "boxing",
                "fighter_one": "Gervonta Davis",
                "fighter_two": "Devin Haney",
                "start_time": (now + timedelta(days=30)).isoformat(),
                "venue": "MGM Grand, Las Vegas",
                "weight_class": "Lightweight",
                "sources_used": ["mock"],
                "premium_data_available": False,
                "mock_data": True
            },
            {
                "id": "mock-boxing-2",
                "sport_type": "boxing",
                "fighter_one": "Canelo Alvarez",
                "fighter_two": "Dmitry Bivol",
                "start_time": (now + timedelta(days=45)).isoformat(),
                "venue": "T-Mobile Arena, Las Vegas",
                "weight_class": "Super Middleweight",
                "sources_used": ["mock"],
                "premium_data_available": False,
                "mock_data": True
            }
        ]
    
    def _get_mock_fighter_data(self, name: str) -> Dict[str, Any]:
        """Return mock fighter data for DCI computation"""
        if "Davis" in name or "Fighter 1" in name:
            return {
                "name": name,
                "age": 29,
                "record_wins": 29,
                "record_losses": 0,
                "record_draws": 0,
                "ko_pct": 93.1,
                "ko_wins": 27,
                "ko_losses": 0,
                "reach_cm": 170,
                "power_idx": 95.0,
                "speed_idx": 88.0,
                "stamina_idx": 75.0,
                "defense_idx": 82.0,
                "win_streak": 29
            }
        else:
            return {
                "name": name,
                "age": 25,
                "record_wins": 31,
                "record_losses": 0,
                "record_draws": 0,
                "ko_pct": 48.4,
                "ko_wins": 15,
                "ko_losses": 0,
                "reach_cm": 178,
                "power_idx": 72.0,
                "speed_idx": 92.0,
                "stamina_idx": 90.0,
                "defense_idx": 88.0,
                "win_streak": 31
            }
