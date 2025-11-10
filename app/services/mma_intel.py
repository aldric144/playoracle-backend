"""
MMA/UFC Intelligence Service
Handles MMA fighter data, event scheduling, and DCI computation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

class MMADCIService:
    """
    MMA-specific DCI (Dynamic Confidence Index) scoring
    
    DCI Formula:
    dci = (strike_accuracy * 0.20) + (takedown_success * 0.15) + (stamina * 0.15)
          + (significant_strikes * 0.10) + (defense_efficiency * 0.10)
          + (reach_advantage * 0.10) + (recent_win_streak * 0.10)
          + (age_experience_factor * 0.10)
    
    Classifications:
    - 85-100: Dominant Edge
    - 65-84: Technical Advantage
    - 50-64: Balanced Match
    - <50: Potential Upset
    """
    
    @classmethod
    def compute_dci(
        cls,
        fighter_one: Dict[str, Any],
        fighter_two: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Compute DCI scores for both fighters in an MMA matchup
        
        Args:
            fighter_one: First fighter stats
            fighter_two: Second fighter stats
            
        Returns:
            Tuple of (fighter_one_dci, fighter_two_dci) with scores and analysis
        """
        f1_factors = cls._extract_factors(fighter_one, fighter_two)
        f2_factors = cls._extract_factors(fighter_two, fighter_one)
        
        f1_score = cls._calculate_score(f1_factors)
        f2_score = cls._calculate_score(f2_factors)
        
        f1_normalized = cls._normalize_score(f1_score, f2_score)
        f2_normalized = cls._normalize_score(f2_score, f1_score)
        
        return (
            {
                "fighter_name": fighter_one.get("name", "Fighter 1"),
                "dci_score": f1_normalized,
                "classification": cls._get_classification(f1_normalized),
                "factors": f1_factors,
                "reasoning": cls._generate_reasoning(fighter_one, f1_factors, f1_normalized)
            },
            {
                "fighter_name": fighter_two.get("name", "Fighter 2"),
                "dci_score": f2_normalized,
                "classification": cls._get_classification(f2_normalized),
                "factors": f2_factors,
                "reasoning": cls._generate_reasoning(fighter_two, f2_factors, f2_normalized)
            }
        )
    
    @classmethod
    def _extract_factors(cls, fighter: Dict[str, Any], opponent: Dict[str, Any]) -> Dict[str, float]:
        """Extract and derive MMA-specific factors for DCI calculation"""
        
        strike_accuracy = fighter.get("strike_accuracy")
        if strike_accuracy is None:
            total_strikes = fighter.get("total_strikes", 0)
            landed_strikes = fighter.get("landed_strikes", 0)
            strike_accuracy = (landed_strikes / total_strikes * 100) if total_strikes > 0 else 50.0
        
        takedown_success = fighter.get("takedown_success")
        if takedown_success is None:
            takedowns_attempted = fighter.get("takedowns_attempted", 0)
            takedowns_landed = fighter.get("takedowns_landed", 0)
            takedown_success = (takedowns_landed / takedowns_attempted * 100) if takedowns_attempted > 0 else 50.0
        
        stamina = fighter.get("stamina_index")
        if stamina is None:
            fights = fighter.get("total_fights", 10)
            finishes = fighter.get("finishes", 5)
            stamina = 50 + (fights - finishes) * 2
            stamina = min(100, max(0, stamina))
        
        significant_strikes = fighter.get("significant_strikes_per_min", 3.5)
        
        defense_efficiency = fighter.get("defense_efficiency")
        if defense_efficiency is None:
            strikes_absorbed = fighter.get("strikes_absorbed_per_min", 3.0)
            defense_efficiency = max(0, 100 - (strikes_absorbed * 10))
        
        reach_advantage = 0
        fighter_reach = fighter.get("reach_cm", 180)
        opponent_reach = opponent.get("reach_cm", 180)
        reach_diff = fighter_reach - opponent_reach
        reach_advantage = 50 + (reach_diff / 2)
        reach_advantage = min(100, max(0, reach_advantage))
        
        win_streak = fighter.get("win_streak", 0)
        recent_wins = min(100, win_streak * 20)
        
        age = fighter.get("age", 28)
        fights = fighter.get("total_fights", 10)
        age_experience = 50
        if 24 <= age <= 32:
            age_experience += 20
        if fights > 15:
            age_experience += 15
        elif fights > 10:
            age_experience += 10
        age_experience = min(100, age_experience)
        
        return {
            "strike_accuracy": strike_accuracy,
            "takedown_success": takedown_success,
            "stamina": stamina,
            "significant_strikes": significant_strikes * 10,
            "defense_efficiency": defense_efficiency,
            "reach_advantage": reach_advantage,
            "recent_win_streak": recent_wins,
            "age_experience_factor": age_experience
        }
    
    @classmethod
    def _calculate_score(cls, factors: Dict[str, float]) -> float:
        """Calculate raw DCI score from factors"""
        return (
            factors["strike_accuracy"] * 0.20 +
            factors["takedown_success"] * 0.15 +
            factors["stamina"] * 0.15 +
            factors["significant_strikes"] * 0.10 +
            factors["defense_efficiency"] * 0.10 +
            factors["reach_advantage"] * 0.10 +
            factors["recent_win_streak"] * 0.10 +
            factors["age_experience_factor"] * 0.10
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
            return "Technical Advantage"
        elif score >= 50:
            return "Balanced Match"
        else:
            return "Potential Upset"
    
    @classmethod
    def _generate_reasoning(cls, fighter: Dict[str, Any], factors: Dict[str, float], score: float) -> str:
        """Generate human-readable reasoning for DCI score"""
        name = fighter.get("name", "Fighter")
        classification = cls._get_classification(score)
        
        strengths = []
        if factors["strike_accuracy"] > 70:
            strengths.append("elite striking accuracy")
        if factors["takedown_success"] > 70:
            strengths.append("dominant wrestling")
        if factors["defense_efficiency"] > 70:
            strengths.append("exceptional defense")
        if factors["recent_win_streak"] > 60:
            strengths.append("strong momentum")
        
        strength_text = ", ".join(strengths) if strengths else "balanced skillset"
        
        return f"{name} shows {classification.lower()} with {strength_text}. DCI: {score:.1f}"


def get_mock_mma_events() -> List[Dict[str, Any]]:
    """Generate mock MMA events for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "sport_type": "mma",
            "league": "UFC",
            "event_name": "UFC 300: Championship Night",
            "date": "2025-12-15T22:00:00Z",
            "venue": "T-Mobile Arena, Las Vegas",
            "weight_class": "Lightweight",
            "fighter_one": {
                "id": str(uuid.uuid4()),
                "name": "Alex 'The Storm' Martinez",
                "record": "24-3-0",
                "age": 29,
                "reach_cm": 183,
                "stance": "Orthodox",
                "nationality": "USA",
                "strike_accuracy": 68.5,
                "takedown_success": 72.0,
                "stamina_index": 85.0,
                "significant_strikes_per_min": 4.2,
                "defense_efficiency": 75.0,
                "win_streak": 5,
                "total_fights": 27
            },
            "fighter_two": {
                "id": str(uuid.uuid4()),
                "name": "Dmitri 'Iron' Volkov",
                "record": "22-2-0",
                "age": 27,
                "reach_cm": 180,
                "stance": "Southpaw",
                "nationality": "Russia",
                "strike_accuracy": 71.2,
                "takedown_success": 65.0,
                "stamina_index": 82.0,
                "significant_strikes_per_min": 3.8,
                "defense_efficiency": 78.0,
                "win_streak": 6,
                "total_fights": 24
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "mma",
            "league": "UFC",
            "event_name": "UFC Fight Night: Rising Stars",
            "date": "2025-11-28T20:00:00Z",
            "venue": "UFC Apex, Las Vegas",
            "weight_class": "Welterweight",
            "fighter_one": {
                "id": str(uuid.uuid4()),
                "name": "Carlos 'El Toro' Rodriguez",
                "record": "18-5-0",
                "age": 31,
                "reach_cm": 185,
                "stance": "Orthodox",
                "nationality": "Brazil",
                "strike_accuracy": 64.0,
                "takedown_success": 58.0,
                "stamina_index": 78.0,
                "significant_strikes_per_min": 3.5,
                "defense_efficiency": 70.0,
                "win_streak": 3,
                "total_fights": 23
            },
            "fighter_two": {
                "id": str(uuid.uuid4()),
                "name": "James 'The Hammer' Thompson",
                "record": "20-4-0",
                "age": 28,
                "reach_cm": 183,
                "stance": "Southpaw",
                "nationality": "UK",
                "strike_accuracy": 66.5,
                "takedown_success": 70.0,
                "stamina_index": 80.0,
                "significant_strikes_per_min": 4.0,
                "defense_efficiency": 72.0,
                "win_streak": 4,
                "total_fights": 24
            }
        }
    ]
