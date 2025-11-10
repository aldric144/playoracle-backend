"""
Volleyball Intelligence Service
Handles volleyball match data, team stats, and DCI computation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

class VolleyballDCIService:
    """
    Volleyball-specific DCI (Dynamic Confidence Index) scoring
    
    DCI Formula:
    dci = (attack_efficiency * 0.20) + (blocks_per_set * 0.15) + (serve_aces * 0.10)
          + (reception_pct * 0.15) + (stamina * 0.10) + (form * 0.10)
          + (team_chemistry * 0.10) + (defensive_conversion * 0.10)
    
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
        Compute DCI scores for both teams in a volleyball matchup
        
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
        """Extract and derive volleyball-specific factors for DCI calculation"""
        
        attack_efficiency = team.get("attack_efficiency", 45.0)
        
        blocks_per_set = team.get("blocks_per_set", 2.5)
        blocks_score = min(100, blocks_per_set * 20)
        
        serve_aces = team.get("serve_aces_per_set", 1.5)
        aces_score = min(100, serve_aces * 25)
        
        reception_pct = team.get("reception_pct", 65.0)
        
        stamina = team.get("stamina_index", 70.0)
        
        recent_wins = team.get("recent_wins", 3)
        recent_matches = team.get("recent_matches", 5)
        form = (recent_wins / recent_matches * 100) if recent_matches > 0 else 50.0
        
        team_chemistry = team.get("team_chemistry", 75.0)
        
        defensive_conversion = team.get("defensive_conversion", 60.0)
        
        return {
            "attack_efficiency": attack_efficiency,
            "blocks_per_set": blocks_score,
            "serve_aces": aces_score,
            "reception_pct": reception_pct,
            "stamina": stamina,
            "form": form,
            "team_chemistry": team_chemistry,
            "defensive_conversion": defensive_conversion
        }
    
    @classmethod
    def _calculate_score(cls, factors: Dict[str, float]) -> float:
        """Calculate raw DCI score from factors"""
        return (
            factors["attack_efficiency"] * 0.20 +
            factors["blocks_per_set"] * 0.15 +
            factors["serve_aces"] * 0.10 +
            factors["reception_pct"] * 0.15 +
            factors["stamina"] * 0.10 +
            factors["form"] * 0.10 +
            factors["team_chemistry"] * 0.10 +
            factors["defensive_conversion"] * 0.10
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
        if factors["attack_efficiency"] > 70:
            strengths.append("powerful attack")
        if factors["blocks_per_set"] > 70:
            strengths.append("strong blocking")
        if factors["reception_pct"] > 70:
            strengths.append("excellent reception")
        if factors["form"] > 70:
            strengths.append("hot streak")
        
        strength_text = ", ".join(strengths) if strengths else "balanced performance"
        
        return f"{name} shows {classification.lower()} with {strength_text}. DCI: {score:.1f}"


def get_mock_volleyball_events() -> List[Dict[str, Any]]:
    """Generate mock volleyball events for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "sport_type": "volleyball",
            "league": "FIVB World Championship",
            "event_name": "FIVB World Championship 2026 - Semifinals",
            "date": "2026-09-20T18:00:00Z",
            "venue": "Arena Stožice, Ljubljana",
            "team_one": {
                "id": str(uuid.uuid4()),
                "name": "Brazil",
                "country": "BRA",
                "ranking": 1,
                "attack_efficiency": 52.5,
                "blocks_per_set": 3.2,
                "serve_aces_per_set": 2.1,
                "reception_pct": 72.0,
                "stamina_index": 85.0,
                "recent_wins": 8,
                "recent_matches": 10,
                "team_chemistry": 88.0,
                "defensive_conversion": 68.0
            },
            "team_two": {
                "id": str(uuid.uuid4()),
                "name": "Poland",
                "country": "POL",
                "ranking": 2,
                "attack_efficiency": 51.0,
                "blocks_per_set": 3.0,
                "serve_aces_per_set": 1.8,
                "reception_pct": 70.0,
                "stamina_index": 82.0,
                "recent_wins": 7,
                "recent_matches": 10,
                "team_chemistry": 85.0,
                "defensive_conversion": 65.0
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "volleyball",
            "league": "FIVB World Championship",
            "event_name": "FIVB World Championship 2026 - Quarterfinals",
            "date": "2026-09-18T16:00:00Z",
            "venue": "Arena Stožice, Ljubljana",
            "team_one": {
                "id": str(uuid.uuid4()),
                "name": "USA",
                "country": "USA",
                "ranking": 3,
                "attack_efficiency": 49.5,
                "blocks_per_set": 2.8,
                "serve_aces_per_set": 1.9,
                "reception_pct": 68.0,
                "stamina_index": 80.0,
                "recent_wins": 6,
                "recent_matches": 10,
                "team_chemistry": 82.0,
                "defensive_conversion": 63.0
            },
            "team_two": {
                "id": str(uuid.uuid4()),
                "name": "Italy",
                "country": "ITA",
                "ranking": 4,
                "attack_efficiency": 50.0,
                "blocks_per_set": 2.9,
                "serve_aces_per_set": 2.0,
                "reception_pct": 69.0,
                "stamina_index": 81.0,
                "recent_wins": 7,
                "recent_matches": 10,
                "team_chemistry": 83.0,
                "defensive_conversion": 64.0
            }
        }
    ]
