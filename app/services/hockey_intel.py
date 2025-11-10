"""
Hockey Intelligence Service
Handles NHL/International hockey data, game scheduling, and DCI computation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

class HockeyDCIService:
    """
    Hockey-specific DCI (Dynamic Confidence Index) scoring
    
    DCI Formula:
    dci = (shots_on_goal * 0.15) + (save_percentage * 0.15) + (powerplay_efficiency * 0.10)
          + (penalty_kill_success * 0.10) + (plus_minus_rating * 0.10)
          + (recent_wins * 0.15) + (fatigue_index * -0.10) + (home_advantage * 0.15)
    
    Classifications:
    - 85-100: Dominant Edge
    - 65-84: Technical Advantage
    - 50-64: Balanced Match
    - <50: Potential Upset
    """
    
    @classmethod
    def compute_dci(
        cls,
        team_one: Dict[str, Any],
        team_two: Dict[str, Any],
        is_team_one_home: bool = True
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Compute DCI scores for both teams in a hockey game
        
        Args:
            team_one: First team stats
            team_two: Second team stats
            is_team_one_home: Whether team_one is playing at home
            
        Returns:
            Tuple of (team_one_dci, team_two_dci) with scores and analysis
        """
        t1_factors = cls._extract_factors(team_one, is_team_one_home)
        t2_factors = cls._extract_factors(team_two, not is_team_one_home)
        
        t1_score = cls._calculate_score(t1_factors)
        t2_score = cls._calculate_score(t2_factors)
        
        t1_normalized = cls._normalize_score(t1_score, t2_score)
        t2_normalized = cls._normalize_score(t2_score, t1_score)
        
        return (
            {
                "team_name": team_one.get("name", "Team 1"),
                "dci_score": t1_normalized,
                "classification": cls._get_classification(t1_normalized),
                "factors": t1_factors,
                "reasoning": cls._generate_reasoning(team_one, t1_factors, t1_normalized, is_team_one_home)
            },
            {
                "team_name": team_two.get("name", "Team 2"),
                "dci_score": t2_normalized,
                "classification": cls._get_classification(t2_normalized),
                "factors": t2_factors,
                "reasoning": cls._generate_reasoning(team_two, t2_factors, t2_normalized, not is_team_one_home)
            }
        )
    
    @classmethod
    def _extract_factors(cls, team: Dict[str, Any], is_home: bool) -> Dict[str, float]:
        """Extract and derive hockey-specific factors for DCI calculation"""
        
        shots_on_goal = team.get("shots_on_goal_per_game", 30.0)
        shots_normalized = min(100, shots_on_goal * 2.5)
        
        save_percentage = team.get("save_percentage", 0.910)
        save_pct_normalized = save_percentage * 100
        
        powerplay_pct = team.get("powerplay_percentage", 20.0)
        
        penalty_kill_pct = team.get("penalty_kill_percentage", 80.0)
        
        plus_minus = team.get("plus_minus_rating", 0)
        plus_minus_normalized = 50 + (plus_minus * 2)
        plus_minus_normalized = min(100, max(0, plus_minus_normalized))
        
        recent_record = team.get("last_10_games", {})
        wins = recent_record.get("wins", 5)
        recent_wins_normalized = wins * 10
        
        games_in_last_week = team.get("games_in_last_7_days", 2)
        fatigue_penalty = games_in_last_week * 15
        fatigue_penalty = min(100, fatigue_penalty)
        
        home_advantage = 0
        if is_home:
            home_record = team.get("home_record", {})
            home_win_pct = home_record.get("win_pct", 55.0)
            home_advantage = home_win_pct
        else:
            away_record = team.get("away_record", {})
            away_win_pct = away_record.get("win_pct", 45.0)
            home_advantage = away_win_pct
        
        return {
            "shots_on_goal": shots_normalized,
            "save_percentage": save_pct_normalized,
            "powerplay_efficiency": powerplay_pct,
            "penalty_kill_success": penalty_kill_pct,
            "plus_minus_rating": plus_minus_normalized,
            "recent_wins": recent_wins_normalized,
            "fatigue_index": fatigue_penalty,
            "home_advantage": home_advantage
        }
    
    @classmethod
    def _calculate_score(cls, factors: Dict[str, float]) -> float:
        """Calculate raw DCI score from factors"""
        return (
            factors["shots_on_goal"] * 0.15 +
            factors["save_percentage"] * 0.15 +
            factors["powerplay_efficiency"] * 0.10 +
            factors["penalty_kill_success"] * 0.10 +
            factors["plus_minus_rating"] * 0.10 +
            factors["recent_wins"] * 0.15 -
            factors["fatigue_index"] * 0.10 +
            factors["home_advantage"] * 0.15
        )
    
    @classmethod
    def _normalize_score(cls, score: float, opponent_score: float) -> float:
        """Normalize score to 0-100 range relative to opponent"""
        total = abs(score) + abs(opponent_score)
        if total == 0:
            return 50.0
        normalized = (abs(score) / total) * 100
        return round(normalized, 2)
    
    @classmethod
    def _get_classification(cls, score: float) -> str:
        """Get DCI classification label"""
        if score >= 85:
            return "Dominant Edge"
        elif score >= 65:
            return "Technical Advantage"
        elif score >= 50:
            return "Balanced Match"
        else:
            return "Potential Upset"
    
    @classmethod
    def _generate_reasoning(cls, team: Dict[str, Any], factors: Dict[str, float], score: float, is_home: bool) -> str:
        """Generate human-readable reasoning for DCI score"""
        name = team.get("name", "Team")
        classification = cls._get_classification(score)
        
        strengths = []
        if factors["shots_on_goal"] > 75:
            strengths.append("high offensive pressure")
        if factors["save_percentage"] > 91:
            strengths.append("elite goaltending")
        if factors["powerplay_efficiency"] > 22:
            strengths.append("dangerous powerplay")
        if factors["recent_wins"] > 70:
            strengths.append("strong momentum")
        if is_home and factors["home_advantage"] > 60:
            strengths.append("home ice advantage")
        
        strength_text = ", ".join(strengths) if strengths else "balanced team play"
        location = "at home" if is_home else "on the road"
        
        return f"{name} shows {classification.lower()} {location} with {strength_text}. DCI: {score:.1f}"


def get_mock_hockey_events() -> List[Dict[str, Any]]:
    """Generate mock hockey events for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "sport_type": "hockey",
            "league": "NHL",
            "date": "2025-11-15T19:00:00Z",
            "venue": "TD Garden, Boston",
            "home_team": {
                "id": str(uuid.uuid4()),
                "name": "Boston Bruins",
                "city": "Boston",
                "abbreviation": "BOS",
                "shots_on_goal_per_game": 32.5,
                "save_percentage": 0.918,
                "powerplay_percentage": 24.5,
                "penalty_kill_percentage": 82.0,
                "plus_minus_rating": 12,
                "last_10_games": {"wins": 7, "losses": 3},
                "games_in_last_7_days": 2,
                "home_record": {"wins": 8, "losses": 2, "win_pct": 80.0},
                "away_record": {"wins": 5, "losses": 5, "win_pct": 50.0}
            },
            "away_team": {
                "id": str(uuid.uuid4()),
                "name": "Toronto Maple Leafs",
                "city": "Toronto",
                "abbreviation": "TOR",
                "shots_on_goal_per_game": 31.0,
                "save_percentage": 0.912,
                "powerplay_percentage": 22.0,
                "penalty_kill_percentage": 79.5,
                "plus_minus_rating": 8,
                "last_10_games": {"wins": 6, "losses": 4},
                "games_in_last_7_days": 3,
                "home_record": {"wins": 7, "losses": 3, "win_pct": 70.0},
                "away_record": {"wins": 4, "losses": 6, "win_pct": 40.0}
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "hockey",
            "league": "NHL",
            "date": "2025-11-16T22:00:00Z",
            "venue": "T-Mobile Arena, Las Vegas",
            "home_team": {
                "id": str(uuid.uuid4()),
                "name": "Vegas Golden Knights",
                "city": "Las Vegas",
                "abbreviation": "VGK",
                "shots_on_goal_per_game": 33.0,
                "save_percentage": 0.915,
                "powerplay_percentage": 23.5,
                "penalty_kill_percentage": 81.0,
                "plus_minus_rating": 10,
                "last_10_games": {"wins": 8, "losses": 2},
                "games_in_last_7_days": 1,
                "home_record": {"wins": 9, "losses": 1, "win_pct": 90.0},
                "away_record": {"wins": 6, "losses": 4, "win_pct": 60.0}
            },
            "away_team": {
                "id": str(uuid.uuid4()),
                "name": "Colorado Avalanche",
                "city": "Colorado",
                "abbreviation": "COL",
                "shots_on_goal_per_game": 34.5,
                "save_percentage": 0.920,
                "powerplay_percentage": 26.0,
                "penalty_kill_percentage": 83.5,
                "plus_minus_rating": 15,
                "last_10_games": {"wins": 7, "losses": 3},
                "games_in_last_7_days": 2,
                "home_record": {"wins": 8, "losses": 2, "win_pct": 80.0},
                "away_record": {"wins": 7, "losses": 3, "win_pct": 70.0}
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "hockey",
            "league": "NHL",
            "date": "2025-11-17T18:00:00Z",
            "venue": "Bell Centre, Montreal",
            "home_team": {
                "id": str(uuid.uuid4()),
                "name": "Montreal Canadiens",
                "city": "Montreal",
                "abbreviation": "MTL",
                "shots_on_goal_per_game": 28.5,
                "save_percentage": 0.908,
                "powerplay_percentage": 19.0,
                "penalty_kill_percentage": 78.0,
                "plus_minus_rating": -5,
                "last_10_games": {"wins": 4, "losses": 6},
                "games_in_last_7_days": 2,
                "home_record": {"wins": 5, "losses": 5, "win_pct": 50.0},
                "away_record": {"wins": 3, "losses": 7, "win_pct": 30.0}
            },
            "away_team": {
                "id": str(uuid.uuid4()),
                "name": "Tampa Bay Lightning",
                "city": "Tampa Bay",
                "abbreviation": "TBL",
                "shots_on_goal_per_game": 32.0,
                "save_percentage": 0.916,
                "powerplay_percentage": 25.0,
                "penalty_kill_percentage": 82.5,
                "plus_minus_rating": 11,
                "last_10_games": {"wins": 7, "losses": 3},
                "games_in_last_7_days": 2,
                "home_record": {"wins": 7, "losses": 3, "win_pct": 70.0},
                "away_record": {"wins": 6, "losses": 4, "win_pct": 60.0}
            }
        }
    ]
