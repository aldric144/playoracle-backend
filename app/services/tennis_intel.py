"""
Tennis Intelligence Service
Handles tennis player data, match scheduling, and DCI computation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

class TennisDCIService:
    """
    Tennis-specific DCI (Dynamic Confidence Index) scoring
    
    DCI Formula:
    dci = (first_serve_pct * 0.20) + (break_points_saved * 0.15) + (aces_per_match * 0.10)
          + (unforced_errors * -0.10) + (stamina_index * 0.15) + (ranking_factor * 0.10)
          + (surface_win_rate * 0.10) + (recent_form * 0.10)
    
    Classifications:
    - 85-100: Dominant Edge
    - 65-84: Technical Advantage
    - 50-64: Balanced Match
    - <50: Potential Upset
    """
    
    @classmethod
    def compute_dci(
        cls,
        player_one: Dict[str, Any],
        player_two: Dict[str, Any],
        surface: str = "hard"
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Compute DCI scores for both players in a tennis match
        
        Args:
            player_one: First player stats
            player_two: Second player stats
            surface: Court surface (hard, clay, grass)
            
        Returns:
            Tuple of (player_one_dci, player_two_dci) with scores and analysis
        """
        p1_factors = cls._extract_factors(player_one, player_two, surface)
        p2_factors = cls._extract_factors(player_two, player_one, surface)
        
        p1_score = cls._calculate_score(p1_factors)
        p2_score = cls._calculate_score(p2_factors)
        
        p1_normalized = cls._normalize_score(p1_score, p2_score)
        p2_normalized = cls._normalize_score(p2_score, p1_score)
        
        return (
            {
                "player_name": player_one.get("name", "Player 1"),
                "dci_score": p1_normalized,
                "classification": cls._get_classification(p1_normalized),
                "factors": p1_factors,
                "reasoning": cls._generate_reasoning(player_one, p1_factors, p1_normalized, surface)
            },
            {
                "player_name": player_two.get("name", "Player 2"),
                "dci_score": p2_normalized,
                "classification": cls._get_classification(p2_normalized),
                "factors": p2_factors,
                "reasoning": cls._generate_reasoning(player_two, p2_factors, p2_normalized, surface)
            }
        )
    
    @classmethod
    def _extract_factors(cls, player: Dict[str, Any], opponent: Dict[str, Any], surface: str) -> Dict[str, float]:
        """Extract and derive tennis-specific factors for DCI calculation"""
        
        first_serve_pct = player.get("first_serve_pct", 65.0)
        
        break_points_saved = player.get("break_points_saved_pct", 60.0)
        
        aces_per_match = player.get("aces_per_match", 8.0)
        aces_normalized = min(100, aces_per_match * 5)
        
        unforced_errors = player.get("unforced_errors_per_match", 25.0)
        errors_penalty = min(100, unforced_errors * 2)
        
        stamina_index = player.get("stamina_index")
        if stamina_index is None:
            matches_played = player.get("matches_played", 50)
            five_setters = player.get("five_set_wins", 5)
            stamina_index = 50 + (five_setters * 5) + min(20, matches_played / 5)
            stamina_index = min(100, stamina_index)
        
        ranking = player.get("ranking", 50)
        ranking_factor = max(0, 100 - ranking)
        
        surface_stats = player.get("surface_stats", {})
        surface_win_rate = surface_stats.get(surface, {}).get("win_pct", 50.0)
        
        recent_matches = player.get("last_10_matches", {})
        wins = recent_matches.get("wins", 5)
        recent_form = wins * 10
        
        return {
            "first_serve_pct": first_serve_pct,
            "break_points_saved": break_points_saved,
            "aces_per_match": aces_normalized,
            "unforced_errors": errors_penalty,
            "stamina_index": stamina_index,
            "ranking_factor": ranking_factor,
            "surface_win_rate": surface_win_rate,
            "recent_form": recent_form
        }
    
    @classmethod
    def _calculate_score(cls, factors: Dict[str, float]) -> float:
        """Calculate raw DCI score from factors"""
        return (
            factors["first_serve_pct"] * 0.20 +
            factors["break_points_saved"] * 0.15 +
            factors["aces_per_match"] * 0.10 -
            factors["unforced_errors"] * 0.10 +
            factors["stamina_index"] * 0.15 +
            factors["ranking_factor"] * 0.10 +
            factors["surface_win_rate"] * 0.10 +
            factors["recent_form"] * 0.10
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
    def _generate_reasoning(cls, player: Dict[str, Any], factors: Dict[str, float], score: float, surface: str) -> str:
        """Generate human-readable reasoning for DCI score"""
        name = player.get("name", "Player")
        classification = cls._get_classification(score)
        
        strengths = []
        if factors["first_serve_pct"] > 70:
            strengths.append("powerful serve")
        if factors["break_points_saved"] > 70:
            strengths.append("clutch defense")
        if factors["surface_win_rate"] > 65:
            strengths.append(f"strong {surface} court record")
        if factors["recent_form"] > 70:
            strengths.append("excellent recent form")
        
        strength_text = ", ".join(strengths) if strengths else "balanced game"
        
        return f"{name} shows {classification.lower()} with {strength_text}. DCI: {score:.1f}"


def get_mock_tennis_events() -> List[Dict[str, Any]]:
    """Generate mock tennis events for testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "sport_type": "tennis",
            "league": "ATP",
            "tournament": "Australian Open 2026",
            "round": "Quarterfinals",
            "date": "2026-01-28T09:00:00Z",
            "venue": "Rod Laver Arena, Melbourne",
            "surface": "hard",
            "player_one": {
                "id": str(uuid.uuid4()),
                "name": "Rafael Nadal",
                "ranking": 2,
                "age": 39,
                "nationality": "Spain",
                "handedness": "Left",
                "first_serve_pct": 72.5,
                "break_points_saved_pct": 68.0,
                "aces_per_match": 6.5,
                "unforced_errors_per_match": 18.0,
                "stamina_index": 92.0,
                "surface_stats": {
                    "hard": {"win_pct": 78.5},
                    "clay": {"win_pct": 91.2},
                    "grass": {"win_pct": 75.0}
                },
                "last_10_matches": {"wins": 8, "losses": 2}
            },
            "player_two": {
                "id": str(uuid.uuid4()),
                "name": "Carlos Alcaraz",
                "ranking": 1,
                "age": 22,
                "nationality": "Spain",
                "handedness": "Right",
                "first_serve_pct": 70.0,
                "break_points_saved_pct": 65.0,
                "aces_per_match": 8.2,
                "unforced_errors_per_match": 22.0,
                "stamina_index": 88.0,
                "surface_stats": {
                    "hard": {"win_pct": 82.0},
                    "clay": {"win_pct": 80.5},
                    "grass": {"win_pct": 76.0}
                },
                "last_10_matches": {"wins": 9, "losses": 1}
            }
        },
        {
            "id": str(uuid.uuid4()),
            "sport_type": "tennis",
            "league": "WTA",
            "tournament": "Miami Open 2026",
            "round": "Semifinals",
            "date": "2026-03-29T19:00:00Z",
            "venue": "Hard Rock Stadium, Miami",
            "surface": "hard",
            "player_one": {
                "id": str(uuid.uuid4()),
                "name": "Iga Swiatek",
                "ranking": 1,
                "age": 24,
                "nationality": "Poland",
                "handedness": "Right",
                "first_serve_pct": 68.0,
                "break_points_saved_pct": 70.0,
                "aces_per_match": 4.5,
                "unforced_errors_per_match": 20.0,
                "stamina_index": 90.0,
                "surface_stats": {
                    "hard": {"win_pct": 80.0},
                    "clay": {"win_pct": 88.5},
                    "grass": {"win_pct": 72.0}
                },
                "last_10_matches": {"wins": 9, "losses": 1}
            },
            "player_two": {
                "id": str(uuid.uuid4()),
                "name": "Coco Gauff",
                "ranking": 3,
                "age": 21,
                "nationality": "USA",
                "handedness": "Right",
                "first_serve_pct": 66.0,
                "break_points_saved_pct": 64.0,
                "aces_per_match": 5.2,
                "unforced_errors_per_match": 24.0,
                "stamina_index": 85.0,
                "surface_stats": {
                    "hard": {"win_pct": 76.0},
                    "clay": {"win_pct": 70.0},
                    "grass": {"win_pct": 74.0}
                },
                "last_10_matches": {"wins": 7, "losses": 3}
            }
        }
    ]
