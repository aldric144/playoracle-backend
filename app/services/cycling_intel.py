"""
Cycling Intelligence Service
Provides DCI scoring and analytics for Cycling/Tour de France races
"""
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CyclingIntelligence:
    """Cycling DCI and analytics service"""
    
    DCI_FACTORS = [
        "climb_percentage",
        "time_gap",
        "heart_rate_stability",
        "cadence",
        "endurance",
        "descent_control",
        "team_pacing",
        "terrain_adaptation"
    ]
    
    def calculate_dci(self, rider_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Dynamic Confidence Index for a cyclist
        
        DCI Factors (8):
        - Climb % (20%)
        - Time Gap (15%)
        - Heart Rate Zone Stability (10%)
        - Cadence (15%)
        - Endurance (15%)
        - Descent Control (10%)
        - Team Pacing (10%)
        - Terrain Adaptation (5%)
        """
        
        climb_percentage = rider_stats.get("climb_percentage", 0.75)  # 0-1
        time_gap = rider_stats.get("time_gap", 0.80)  # 0-1 (smaller gap = better)
        heart_rate_stability = rider_stats.get("heart_rate_stability", 0.70)  # 0-1
        cadence = rider_stats.get("cadence", 0.75)  # 0-1
        endurance = rider_stats.get("endurance", 0.85)  # 0-1
        descent_control = rider_stats.get("descent_control", 0.70)  # 0-1
        team_pacing = rider_stats.get("team_pacing", 0.80)  # 0-1
        terrain_adaptation = rider_stats.get("terrain_adaptation", 0.75)  # 0-1
        
        dci_score = (
            climb_percentage * 0.20 +
            time_gap * 0.15 +
            heart_rate_stability * 0.10 +
            cadence * 0.15 +
            endurance * 0.15 +
            descent_control * 0.10 +
            team_pacing * 0.10 +
            terrain_adaptation * 0.05
        ) * 100
        
        if dci_score >= 80:
            confidence = "Excellent"
            color = "green"
        elif dci_score >= 70:
            confidence = "Strong"
            color = "blue"
        elif dci_score >= 60:
            confidence = "Moderate"
            color = "yellow"
        else:
            confidence = "Weak"
            color = "red"
        
        return {
            "dci_score": round(dci_score, 1),
            "confidence_level": confidence,
            "color": color,
            "factors": {
                "climb_percentage": round(climb_percentage * 100, 1),
                "time_gap": round(time_gap * 100, 1),
                "heart_rate_stability": round(heart_rate_stability * 100, 1),
                "cadence": round(cadence * 100, 1),
                "endurance": round(endurance * 100, 1),
                "descent_control": round(descent_control * 100, 1),
                "team_pacing": round(team_pacing * 100, 1),
                "terrain_adaptation": round(terrain_adaptation * 100, 1)
            },
            "breakdown": {
                "climb_percentage": round(climb_percentage * 20, 1),
                "time_gap": round(time_gap * 15, 1),
                "heart_rate_stability": round(heart_rate_stability * 10, 1),
                "cadence": round(cadence * 15, 1),
                "endurance": round(endurance * 15, 1),
                "descent_control": round(descent_control * 10, 1),
                "team_pacing": round(team_pacing * 10, 1),
                "terrain_adaptation": round(terrain_adaptation * 5, 1)
            }
        }
    
    def get_mock_races(self) -> List[Dict[str, Any]]:
        """Get mock race data for testing"""
        now = datetime.now()
        
        return [
            {
                "id": "mock-cycling-1",
                "name": "Tour de France 2025",
                "stage": "Stage 15 - Mountain Stage",
                "route": "Loudenvielle to Plateau de Beille",
                "location": "French Pyrenees",
                "race_date": "2025-07-20",
                "status": "Upcoming",
                "distance": "197.7 km",
                "elevation_gain": "4,850m",
                "category": "Mountain Stage",
                "top_riders": [
                    {
                        "name": "Tadej Pogačar",
                        "number": 1,
                        "team": "UAE Team Emirates",
                        "nationality": "Slovenia",
                        "dci": self.calculate_dci({
                            "climb_percentage": 0.95,
                            "time_gap": 0.92,
                            "heart_rate_stability": 0.88,
                            "cadence": 0.90,
                            "endurance": 0.93,
                            "descent_control": 0.87,
                            "team_pacing": 0.90,
                            "terrain_adaptation": 0.92
                        })
                    },
                    {
                        "name": "Jonas Vingegaard",
                        "number": 2,
                        "team": "Visma-Lease a Bike",
                        "nationality": "Denmark",
                        "dci": self.calculate_dci({
                            "climb_percentage": 0.93,
                            "time_gap": 0.90,
                            "heart_rate_stability": 0.90,
                            "cadence": 0.88,
                            "endurance": 0.92,
                            "descent_control": 0.85,
                            "team_pacing": 0.88,
                            "terrain_adaptation": 0.90
                        })
                    },
                    {
                        "name": "Primož Roglič",
                        "number": 3,
                        "team": "Red Bull-BORA-hansgrohe",
                        "nationality": "Slovenia",
                        "dci": self.calculate_dci({
                            "climb_percentage": 0.90,
                            "time_gap": 0.87,
                            "heart_rate_stability": 0.85,
                            "cadence": 0.86,
                            "endurance": 0.90,
                            "descent_control": 0.88,
                            "team_pacing": 0.86,
                            "terrain_adaptation": 0.88
                        })
                    }
                ],
                "mock_data": True
            },
            {
                "id": "mock-cycling-2",
                "name": "Giro d'Italia 2025",
                "stage": "Stage 16 - Queen Stage",
                "route": "Livigno to Santa Cristina Val Gardena",
                "location": "Italian Alps",
                "race_date": "2025-05-27",
                "status": "Upcoming",
                "distance": "202.0 km",
                "elevation_gain": "5,400m",
                "category": "Mountain Stage",
                "top_riders": [
                    {
                        "name": "Egan Bernal",
                        "number": 11,
                        "team": "INEOS Grenadiers",
                        "nationality": "Colombia",
                        "dci": self.calculate_dci({
                            "climb_percentage": 0.92,
                            "time_gap": 0.88,
                            "heart_rate_stability": 0.86,
                            "cadence": 0.87,
                            "endurance": 0.91,
                            "descent_control": 0.84,
                            "team_pacing": 0.87,
                            "terrain_adaptation": 0.89
                        })
                    },
                    {
                        "name": "Remco Evenepoel",
                        "number": 12,
                        "team": "Soudal Quick-Step",
                        "nationality": "Belgium",
                        "dci": self.calculate_dci({
                            "climb_percentage": 0.88,
                            "time_gap": 0.85,
                            "heart_rate_stability": 0.83,
                            "cadence": 0.85,
                            "endurance": 0.88,
                            "descent_control": 0.82,
                            "team_pacing": 0.85,
                            "terrain_adaptation": 0.86
                        })
                    }
                ],
                "mock_data": True
            }
        ]
    
    def get_mock_standings(self) -> Dict[str, Any]:
        """Get mock general classification standings"""
        return {
            "race": "Tour de France 2025",
            "classification": "General Classification",
            "standings": [
                {
                    "position": 1,
                    "rider": "Tadej Pogačar",
                    "number": 1,
                    "team": "UAE Team Emirates",
                    "time": "72h 15m 32s",
                    "gap": "Leader",
                    "stage_wins": 4,
                    "dci": self.calculate_dci({
                        "climb_percentage": 0.95,
                        "time_gap": 0.92,
                        "heart_rate_stability": 0.88,
                        "cadence": 0.90,
                        "endurance": 0.93,
                        "descent_control": 0.87,
                        "team_pacing": 0.90,
                        "terrain_adaptation": 0.92
                    })
                },
                {
                    "position": 2,
                    "rider": "Jonas Vingegaard",
                    "number": 2,
                    "team": "Visma-Lease a Bike",
                    "time": "72h 17m 18s",
                    "gap": "+1'46\"",
                    "stage_wins": 2,
                    "dci": self.calculate_dci({
                        "climb_percentage": 0.93,
                        "time_gap": 0.90,
                        "heart_rate_stability": 0.90,
                        "cadence": 0.88,
                        "endurance": 0.92,
                        "descent_control": 0.85,
                        "team_pacing": 0.88,
                        "terrain_adaptation": 0.90
                    })
                }
            ],
            "mock_data": True
        }
