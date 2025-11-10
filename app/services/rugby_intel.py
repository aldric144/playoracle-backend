"""
Rugby Intelligence Service
Handles rugby match data, team stats, and DCI computation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

class RugbyDCIService:
    """
    Rugby-specific DCI (Dynamic Confidence Index) scoring
    
    DCI Formula:
    dci = (possession_pct * 0.20) + (tackles_made * 0.15) + (line_breaks * 0.10)
          + (kick_accuracy * 0.10) + (try_conversion * 0.15) + (stamina * 0.10)
          + (home_advantage * 0.10) + (discipline * 0.10)
    
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
        Compute DCI scores for both teams in a rugby matchup
        
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
        """Extract and derive rugby-specific factors for DCI calculation"""
        
        possession_pct = team.get("possession_pct", 50.0)
        
        tackles_made = team.get("tackles_per_game", 120)
        tackles_score = min(100, (tackles_made / 150) * 100)
        
        line_breaks = team.get("line_breaks_per_game", 8)
        line_breaks_score = min(100, line_breaks * 10)
        
        kick_accuracy = team.get("kick_accuracy", 70.0)
        
        try_conversion = team.get("try_conversion_rate", 75.0)
        
        stamina = team.get("stamina_index", 75.0)
        
        is_home = team.get("is_home", False)
        home_advantage = 65.0 if is_home else 35.0
        
        penalties_per_game = team.get("penalties_per_game", 10)
        discipline = max(0, 100 - (penalties_per_game * 5))
        
        return {
            "possession_pct": possession_pct,
            "tackles_made": tackles_score,
            "line_breaks": line_breaks_score,
            "kick_accuracy": kick_accuracy,
            "try_conversion": try_conversion,
            "stamina": stamina,
            "home_advantage": home_advantage,
            "discipline": discipline
        }
    
    @classmethod
    def _calculate_score(cls, factors: Dict[str, float]) -> float:
        """Calculate raw DCI score from factors"""
        return (
            factors["possession_pct"] * 0.20 +
            factors["tackles_made"] * 0.15 +
            factors["line_breaks"] * 0.10 +
            factors["kick_accuracy"] * 0.10 +
            factors["try_conversion"] * 0.15 +
            factors["stamina"] * 0.10 +
            factors["home_advantage"] * 0.10 +
            factors["discipline"] * 0.10
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
        if factors["possession_pct"] > 55:
            strengths.append("strong possession")
        if factors["tackles_made"] > 70:
            strengths.append("dominant defense")
        if factors["line_breaks"] > 70:
            strengths.append("explosive attack")
        if factors["discipline"] > 70:
            strengths.append("excellent discipline")
        
        strength_text = ", ".join(strengths) if strengths else "balanced gameplay"
        
        return f"{name} shows {classification.lower()} with {strength_text}. DCI: {score:.1f}"


def get_mock_rugby_events() -> List[Dict[str, Any]]:
    """Generate mock rugby events for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "sport_type": "rugby",
            "league": "Rugby World Cup",
            "event_name": "Rugby World Cup 2027 - Final",
            "date": "2027-10-28T19:00:00Z",
            "venue": "Stadium Australia, Sydney",
            "team_one": {
                "id": str(uuid.uuid4()),
                "name": "New Zealand All Blacks",
                "country": "NZL",
                "ranking": 1,
                "possession_pct": 54.0,
                "tackles_per_game": 135,
                "line_breaks_per_game": 12,
                "kick_accuracy": 78.0,
                "try_conversion_rate": 82.0,
                "stamina_index": 88.0,
                "is_home": False,
                "penalties_per_game": 8
            },
            "team_two": {
                "id": str(uuid.uuid4()),
                "name": "South Africa Springboks",
                "country": "RSA",
                "ranking": 2,
                "possession_pct": 52.0,
                "tackles_per_game": 140,
                "line_breaks_per_game": 10,
                "kick_accuracy": 76.0,
                "try_conversion_rate": 80.0,
                "stamina_index": 86.0,
                "is_home": False,
                "penalties_per_game": 9
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "rugby",
            "league": "Six Nations Championship",
            "event_name": "Six Nations 2026 - England vs Ireland",
            "date": "2026-03-14T15:00:00Z",
            "venue": "Twickenham Stadium, London",
            "team_one": {
                "id": str(uuid.uuid4()),
                "name": "England",
                "country": "ENG",
                "ranking": 4,
                "possession_pct": 51.0,
                "tackles_per_game": 130,
                "line_breaks_per_game": 9,
                "kick_accuracy": 74.0,
                "try_conversion_rate": 77.0,
                "stamina_index": 82.0,
                "is_home": True,
                "penalties_per_game": 10
            },
            "team_two": {
                "id": str(uuid.uuid4()),
                "name": "Ireland",
                "country": "IRL",
                "ranking": 3,
                "possession_pct": 53.0,
                "tackles_per_game": 132,
                "line_breaks_per_game": 11,
                "kick_accuracy": 77.0,
                "try_conversion_rate": 79.0,
                "stamina_index": 84.0,
                "is_home": False,
                "penalties_per_game": 9
            }
        }
    ]
