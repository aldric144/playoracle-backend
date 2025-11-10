"""
DCI (Dynamic Confidence Index) Service - Layer 3 AI Engine
Computes confidence scores for sports events and boxing matches
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DCIResult:
    """DCI scoring result with classification"""
    def __init__(self, score: float, classification: str, reasoning: str, factors: Dict[str, Any]):
        self.score = score
        self.classification = classification
        self.reasoning = reasoning
        self.factors = factors
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dci_score": self.score,
            "dci_class": self.classification,
            "reasoning": self.reasoning,
            "factors": self.factors
        }

class BoxingDCIService:
    """Boxing-specific DCI scoring implementation"""
    
    @staticmethod
    def normalize(value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-100 range"""
        if max_val == min_val:
            return 50.0
        return max(0.0, min(100.0, ((value - min_val) / (max_val - min_val)) * 100))
    
    @staticmethod
    def derive_power_index(ko_pct: Optional[float], recent_ko_wins: int = 0) -> float:
        """Derive power index from KO percentage and recent KO wins"""
        if ko_pct is not None:
            base_power = ko_pct
        else:
            base_power = 50.0
        
        ko_bonus = min(recent_ko_wins * 5, 20)
        return min(100.0, base_power + ko_bonus)
    
    @staticmethod
    def derive_speed_index(age: Optional[int], recent_fight_frequency: int = 0) -> float:
        """Derive speed index from age and recent fight activity"""
        if age is None:
            age = 28
        
        if age < 22:
            age_factor = 70.0
        elif age <= 28:
            age_factor = 85.0
        elif age <= 32:
            age_factor = 75.0
        elif age <= 35:
            age_factor = 60.0
        else:
            age_factor = 45.0
        
        activity_bonus = min(recent_fight_frequency * 3, 15)
        return min(100.0, age_factor + activity_bonus)
    
    @staticmethod
    def derive_stamina_index(decision_wins_ratio: float, recent_distance_fights: int = 0) -> float:
        """Derive stamina index from decision wins ratio and fights going the distance"""
        base_stamina = decision_wins_ratio * 100
        distance_bonus = min(recent_distance_fights * 5, 20)
        return min(100.0, base_stamina + distance_bonus)
    
    @staticmethod
    def derive_defense_score(ko_losses_ratio: float, total_losses: int) -> float:
        """Derive defense score from KO losses ratio"""
        if total_losses == 0:
            return 90.0
        
        ko_defense = (1.0 - ko_losses_ratio) * 100
        loss_penalty = min(total_losses * 2, 20)
        return max(30.0, ko_defense - loss_penalty)
    
    @staticmethod
    def calculate_reach_advantage(reach_cm_f1: Optional[float], reach_cm_f2: Optional[float]) -> float:
        """Calculate reach advantage normalized to 0-100"""
        if reach_cm_f1 is None or reach_cm_f2 is None:
            return 50.0
        
        diff = reach_cm_f1 - reach_cm_f2
        return BoxingDCIService.normalize(diff, -15, 15)
    
    @staticmethod
    def calculate_age_factor(age: Optional[int]) -> float:
        """Calculate age factor (peak age 28-32)"""
        if age is None:
            return 50.0
        
        if 28 <= age <= 32:
            return 100.0
        elif 25 <= age < 28:
            return 90.0
        elif 32 < age <= 35:
            return 85.0
        elif 22 <= age < 25:
            return 75.0
        elif 35 < age <= 38:
            return 60.0
        else:
            return 40.0
    
    @staticmethod
    def calculate_experience_factor(total_fights: int) -> float:
        """Calculate experience factor (capped at 30 fights)"""
        return min(100.0, (total_fights / 30.0) * 100)
    
    @staticmethod
    def calculate_win_streak_score(win_streak: int) -> float:
        """Calculate win streak score (capped at 7)"""
        return min(100.0, (min(win_streak, 7) / 7.0) * 100)
    
    @classmethod
    def compute_dci(
        cls,
        fighter_one: Dict[str, Any],
        fighter_two: Dict[str, Any]
    ) -> Tuple[DCIResult, DCIResult]:
        """
        Compute DCI scores for both fighters in a matchup
        
        Returns: (fighter_one_dci, fighter_two_dci)
        """
        f1_factors = cls._extract_fighter_factors(fighter_one)
        f2_factors = cls._extract_fighter_factors(fighter_two)
        
        f1_dci = cls._calculate_fighter_dci(f1_factors, f2_factors)
        f2_dci = cls._calculate_fighter_dci(f2_factors, f1_factors)
        
        f1_reasoning = cls._generate_reasoning(fighter_one.get("name", "Fighter 1"), f1_factors, f2_factors)
        f2_reasoning = cls._generate_reasoning(fighter_two.get("name", "Fighter 2"), f2_factors, f1_factors)
        
        f1_result = DCIResult(
            score=f1_dci,
            classification=cls._classify_dci(f1_dci),
            reasoning=f1_reasoning,
            factors=f1_factors
        )
        
        f2_result = DCIResult(
            score=f2_dci,
            classification=cls._classify_dci(f2_dci),
            reasoning=f2_reasoning,
            factors=f2_factors
        )
        
        return f1_result, f2_result
    
    @classmethod
    def _extract_fighter_factors(cls, fighter: Dict[str, Any]) -> Dict[str, float]:
        """Extract and compute all DCI factors for a fighter"""
        age = fighter.get("age")
        record_wins = fighter.get("record_wins", 0)
        record_losses = fighter.get("record_losses", 0)
        record_draws = fighter.get("record_draws", 0)
        ko_pct = fighter.get("ko_pct")
        reach_cm = fighter.get("reach_cm")
        
        total_fights = record_wins + record_losses + record_draws
        
        if ko_pct is None and total_fights > 0:
            ko_wins = fighter.get("ko_wins", int(record_wins * 0.6))
            ko_pct = (ko_wins / total_fights) * 100 if total_fights > 0 else 50.0
        
        decision_wins = record_wins - fighter.get("ko_wins", int(record_wins * 0.6))
        decision_wins_ratio = decision_wins / record_wins if record_wins > 0 else 0.3
        
        ko_losses = fighter.get("ko_losses", int(record_losses * 0.4))
        ko_losses_ratio = ko_losses / record_losses if record_losses > 0 else 0.0
        
        win_streak = fighter.get("win_streak", 0)
        
        power_index = fighter.get("power_idx") or cls.derive_power_index(ko_pct, fighter.get("recent_ko_wins", 0))
        speed_index = fighter.get("speed_idx") or cls.derive_speed_index(age, fighter.get("recent_fight_frequency", 0))
        stamina_index = fighter.get("stamina_idx") or cls.derive_stamina_index(decision_wins_ratio, fighter.get("recent_distance_fights", 0))
        defense_score = fighter.get("defense_idx") or cls.derive_defense_score(ko_losses_ratio, record_losses)
        age_factor = cls.calculate_age_factor(age)
        experience = cls.calculate_experience_factor(total_fights)
        win_streak_score = cls.calculate_win_streak_score(win_streak)
        
        return {
            "power_index": power_index,
            "speed_index": speed_index,
            "stamina_index": stamina_index,
            "defense_score": defense_score,
            "age_factor": age_factor,
            "experience": experience,
            "win_streak_score": win_streak_score,
            "reach_cm": reach_cm,
            "ko_pct": ko_pct or 50.0,
            "record_wins": record_wins,
            "record_losses": record_losses,
            "total_fights": total_fights
        }
    
    @classmethod
    def _calculate_fighter_dci(cls, fighter_factors: Dict[str, float], opponent_factors: Dict[str, float]) -> float:
        """
        Calculate DCI score using weighted formula
        
        DCI = (power * 0.25) + (speed * 0.20) + (stamina * 0.15) + (reach_adv * 0.10) 
              + (defense * 0.10) + (win_streak * 0.10) + (age * 0.05) + (experience * 0.05)
        """
        reach_advantage = cls.calculate_reach_advantage(
            fighter_factors.get("reach_cm"),
            opponent_factors.get("reach_cm")
        )
        
        dci = (
            (fighter_factors["power_index"] * 0.25) +
            (fighter_factors["speed_index"] * 0.20) +
            (fighter_factors["stamina_index"] * 0.15) +
            (reach_advantage * 0.10) +
            (fighter_factors["defense_score"] * 0.10) +
            (fighter_factors["win_streak_score"] * 0.10) +
            (fighter_factors["age_factor"] * 0.05) +
            (fighter_factors["experience"] * 0.05)
        )
        
        return max(0.0, min(100.0, dci))
    
    @staticmethod
    def _classify_dci(score: float) -> str:
        """Classify DCI score into categories"""
        if score >= 85:
            return "Dominant Edge"
        elif score >= 65:
            return "Balanced Advantage"
        elif score >= 50:
            return "Even Matchup"
        else:
            return "Potential Upset"
    
    @classmethod
    def _generate_reasoning(cls, fighter_name: str, fighter_factors: Dict[str, float], opponent_factors: Dict[str, float]) -> str:
        """Generate human-readable reasoning for DCI score"""
        reasons = []
        
        if fighter_factors["power_index"] > 75:
            reasons.append(f"strong power index ({fighter_factors['power_index']:.0f}%)")
        
        if fighter_factors["ko_pct"] > 70:
            reasons.append(f"high KO rate ({fighter_factors['ko_pct']:.0f}%)")
        
        reach_diff = (fighter_factors.get("reach_cm") or 0) - (opponent_factors.get("reach_cm") or 0)
        if reach_diff > 5:
            reasons.append(f"reach advantage (+{reach_diff:.0f}cm)")
        elif reach_diff < -5:
            reasons.append(f"reach disadvantage ({reach_diff:.0f}cm)")
        
        if fighter_factors["defense_score"] > 80:
            reasons.append("excellent defense")
        elif fighter_factors["defense_score"] < 50:
            reasons.append("defensive vulnerabilities")
        
        if fighter_factors["win_streak_score"] > 70:
            reasons.append("strong win streak")
        
        if fighter_factors["stamina_index"] > 80:
            reasons.append("superior stamina")
        
        if fighter_factors["experience"] > opponent_factors["experience"] + 20:
            reasons.append("experience advantage")
        elif fighter_factors["experience"] < opponent_factors["experience"] - 20:
            reasons.append("experience disadvantage")
        
        if not reasons:
            reasons.append("balanced attributes")
        
        return f"{fighter_name}: {'; '.join(reasons)}"

class GameDCIService:
    """Game-specific DCI scoring (for traditional sports)"""
    
    @staticmethod
    def compute_game_dci(
        home_team: Dict[str, Any],
        away_team: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> DCIResult:
        """Compute DCI for a game between two teams"""
        home_win_pct = home_team.get("win_percentage", 50.0)
        away_win_pct = away_team.get("win_percentage", 50.0)
        
        home_advantage = 5.0
        
        base_confidence = home_win_pct - away_win_pct + home_advantage
        
        dci_score = max(0.0, min(100.0, 50.0 + base_confidence))
        
        if dci_score >= 85:
            classification = "Dominant Edge"
        elif dci_score >= 65:
            classification = "Balanced Advantage"
        elif dci_score >= 50:
            classification = "Even Matchup"
        else:
            classification = "Potential Upset"
        
        reasoning = f"Home team win% {home_win_pct:.1f}% vs Away {away_win_pct:.1f}% with home advantage"
        
        return DCIResult(
            score=dci_score,
            classification=classification,
            reasoning=reasoning,
            factors={
                "home_win_pct": home_win_pct,
                "away_win_pct": away_win_pct,
                "home_advantage": home_advantage
            }
        )
