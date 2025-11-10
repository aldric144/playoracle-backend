"""
Cricket Intelligence Service
Handles cricket match data, team/player stats, and DCI computation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

class CricketDCIService:
    """
    Cricket-specific DCI (Dynamic Confidence Index) scoring
    
    DCI Formula:
    dci = (runs_per_over * 0.15) + (wickets_taken * 0.15) + (strike_rate * 0.15)
          + (bowling_economy * 0.10) + (fielding_pct * 0.10) + (player_form * 0.15)
          + (toss_win_pct * 0.10) + (momentum_score * 0.10)
    
    Classifications:
    - 85-100: Dominant Edge
    - 65-84: Balanced Advantage
    - 50-64: Even Matchup
    - <50: Potential Upset
    """
    
    @classmethod
    def compute_dci(
        cls,
        team_one: Dict[str, Any],
        team_two: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Compute DCI scores for both teams in a cricket matchup
        
        Args:
            team_one: First team stats
            team_two: Second team stats
            
        Returns:
            Tuple of (team_one_dci, team_two_dci) with scores and analysis
        """
        t1_factors = cls._extract_factors(team_one, team_two)
        t2_factors = cls._extract_factors(team_two, team_one)
        
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
                "reasoning": cls._generate_reasoning(team_one, t1_factors, t1_normalized)
            },
            {
                "team_name": team_two.get("name", "Team 2"),
                "dci_score": t2_normalized,
                "classification": cls._get_classification(t2_normalized),
                "factors": t2_factors,
                "reasoning": cls._generate_reasoning(team_two, t2_factors, t2_normalized)
            }
        )
    
    @classmethod
    def _extract_factors(cls, team: Dict[str, Any], opponent: Dict[str, Any]) -> Dict[str, float]:
        """Extract and derive cricket-specific factors for DCI calculation"""
        
        runs_per_over = team.get("runs_per_over", 6.0)
        runs_score = min(100, (runs_per_over / 8.0) * 100)
        
        wickets_per_match = team.get("wickets_per_match", 7)
        wickets_score = min(100, (wickets_per_match / 10) * 100)
        
        strike_rate = team.get("strike_rate", 130.0)
        strike_rate_score = min(100, (strike_rate / 150) * 100)
        
        bowling_economy = team.get("bowling_economy", 6.5)
        economy_score = max(0, 100 - (bowling_economy * 10))
        
        fielding_pct = team.get("fielding_efficiency", 75.0)
        
        recent_wins = team.get("recent_wins", 3)
        recent_matches = team.get("recent_matches", 5)
        player_form = (recent_wins / recent_matches * 100) if recent_matches > 0 else 50.0
        
        toss_wins = team.get("toss_wins", 5)
        total_tosses = team.get("total_tosses", 10)
        toss_win_pct = (toss_wins / total_tosses * 100) if total_tosses > 0 else 50.0
        
        momentum_score = team.get("momentum_index", 70.0)
        
        return {
            "runs_per_over": runs_score,
            "wickets_taken": wickets_score,
            "strike_rate": strike_rate_score,
            "bowling_economy": economy_score,
            "fielding_pct": fielding_pct,
            "player_form": player_form,
            "toss_win_pct": toss_win_pct,
            "momentum_score": momentum_score
        }
    
    @classmethod
    def _calculate_score(cls, factors: Dict[str, float]) -> float:
        """Calculate raw DCI score from factors"""
        return (
            factors["runs_per_over"] * 0.15 +
            factors["wickets_taken"] * 0.15 +
            factors["strike_rate"] * 0.15 +
            factors["bowling_economy"] * 0.10 +
            factors["fielding_pct"] * 0.10 +
            factors["player_form"] * 0.15 +
            factors["toss_win_pct"] * 0.10 +
            factors["momentum_score"] * 0.10
        )
    
    @classmethod
    def _normalize_score(cls, score: float, opponent_score: float) -> float:
        """Normalize score to 0-100 range relative to opponent"""
        total = score + opponent_score
        if total == 0:
            return 50.0
        normalized = (score / total) * 100
        return round(normalized, 2)
    
    @classmethod
    def _get_classification(cls, score: float) -> str:
        """Get DCI classification label"""
        if score >= 85:
            return "Dominant Edge"
        elif score >= 65:
            return "Balanced Advantage"
        elif score >= 50:
            return "Even Matchup"
        else:
            return "Potential Upset"
    
    @classmethod
    def _generate_reasoning(cls, team: Dict[str, Any], factors: Dict[str, float], score: float) -> str:
        """Generate human-readable reasoning for DCI score"""
        name = team.get("name", "Team")
        classification = cls._get_classification(score)
        
        strengths = []
        if factors["runs_per_over"] > 70:
            strengths.append("explosive batting")
        if factors["wickets_taken"] > 70:
            strengths.append("lethal bowling")
        if factors["fielding_pct"] > 75:
            strengths.append("sharp fielding")
        if factors["player_form"] > 70:
            strengths.append("excellent form")
        
        strength_text = ", ".join(strengths) if strengths else "balanced squad"
        
        return f"{name} shows {classification.lower()} with {strength_text}. DCI: {score:.1f}"


def get_mock_cricket_events() -> List[Dict[str, Any]]:
    """Generate mock cricket events for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "sport_type": "cricket",
            "league": "ICC Cricket World Cup",
            "event_name": "ICC Cricket World Cup 2027 - Final",
            "date": "2027-11-19T09:30:00Z",
            "venue": "Narendra Modi Stadium, Ahmedabad",
            "format": "ODI",
            "team_one": {
                "id": str(uuid.uuid4()),
                "name": "India",
                "country": "IND",
                "ranking": 1,
                "runs_per_over": 6.8,
                "wickets_per_match": 8,
                "strike_rate": 142.0,
                "bowling_economy": 5.8,
                "fielding_efficiency": 82.0,
                "recent_wins": 9,
                "recent_matches": 10,
                "toss_wins": 6,
                "total_tosses": 10,
                "momentum_index": 88.0
            },
            "team_two": {
                "id": str(uuid.uuid4()),
                "name": "Australia",
                "country": "AUS",
                "ranking": 2,
                "runs_per_over": 6.5,
                "wickets_per_match": 7,
                "strike_rate": 138.0,
                "bowling_economy": 6.0,
                "fielding_efficiency": 80.0,
                "recent_wins": 8,
                "recent_matches": 10,
                "toss_wins": 5,
                "total_tosses": 10,
                "momentum_index": 85.0
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "cricket",
            "league": "ICC T20 World Cup",
            "event_name": "ICC T20 World Cup 2026 - Semifinals",
            "date": "2026-06-13T14:00:00Z",
            "venue": "Lord's Cricket Ground, London",
            "format": "T20",
            "team_one": {
                "id": str(uuid.uuid4()),
                "name": "England",
                "country": "ENG",
                "ranking": 3,
                "runs_per_over": 7.2,
                "wickets_per_match": 6,
                "strike_rate": 145.0,
                "bowling_economy": 7.5,
                "fielding_efficiency": 78.0,
                "recent_wins": 7,
                "recent_matches": 10,
                "toss_wins": 5,
                "total_tosses": 10,
                "momentum_index": 82.0
            },
            "team_two": {
                "id": str(uuid.uuid4()),
                "name": "Pakistan",
                "country": "PAK",
                "ranking": 4,
                "runs_per_over": 6.9,
                "wickets_per_match": 7,
                "strike_rate": 140.0,
                "bowling_economy": 7.0,
                "fielding_efficiency": 76.0,
                "recent_wins": 6,
                "recent_matches": 10,
                "toss_wins": 4,
                "total_tosses": 10,
                "momentum_index": 78.0
            }
        }
    ]
