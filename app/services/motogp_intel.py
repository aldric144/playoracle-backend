"""
MotoGP Intelligence Service
Provides DCI scoring and analytics for MotoGP/Superbike races
"""
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MotoGPIntelligence:
    """MotoGP DCI and analytics service"""
    
    DCI_FACTORS = [
        "lap_time_delta",
        "top_speed",
        "braking_efficiency",
        "rider_form",
        "track_adaptation",
        "tire_management",
        "experience",
        "reaction_time"
    ]
    
    def calculate_dci(self, rider_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Dynamic Confidence Index for a MotoGP rider
        
        DCI Factors (8):
        - Lap Time Delta (20%)
        - Top Speed (15%)
        - Braking Efficiency (15%)
        - Rider Form (15%)
        - Track Adaptation (10%)
        - Tire Management (10%)
        - Experience (10%)
        - Reaction Time (5%)
        """
        
        lap_time_delta = rider_stats.get("lap_time_delta", 0.80)  # 0-1
        top_speed = rider_stats.get("top_speed", 0.85)  # 0-1
        braking_efficiency = rider_stats.get("braking_efficiency", 0.75)  # 0-1
        rider_form = rider_stats.get("rider_form", 0.80)  # 0-1
        track_adaptation = rider_stats.get("track_adaptation", 0.70)  # 0-1
        tire_management = rider_stats.get("tire_management", 0.75)  # 0-1
        experience = rider_stats.get("experience", 0.85)  # 0-1
        reaction_time = rider_stats.get("reaction_time", 0.80)  # 0-1
        
        dci_score = (
            lap_time_delta * 0.20 +
            top_speed * 0.15 +
            braking_efficiency * 0.15 +
            rider_form * 0.15 +
            track_adaptation * 0.10 +
            tire_management * 0.10 +
            experience * 0.10 +
            reaction_time * 0.05
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
                "lap_time_delta": round(lap_time_delta * 100, 1),
                "top_speed": round(top_speed * 100, 1),
                "braking_efficiency": round(braking_efficiency * 100, 1),
                "rider_form": round(rider_form * 100, 1),
                "track_adaptation": round(track_adaptation * 100, 1),
                "tire_management": round(tire_management * 100, 1),
                "experience": round(experience * 100, 1),
                "reaction_time": round(reaction_time * 100, 1)
            },
            "breakdown": {
                "lap_time_delta": round(lap_time_delta * 20, 1),
                "top_speed": round(top_speed * 15, 1),
                "braking_efficiency": round(braking_efficiency * 15, 1),
                "rider_form": round(rider_form * 15, 1),
                "track_adaptation": round(track_adaptation * 10, 1),
                "tire_management": round(tire_management * 10, 1),
                "experience": round(experience * 10, 1),
                "reaction_time": round(reaction_time * 5, 1)
            }
        }
    
    def get_mock_races(self) -> List[Dict[str, Any]]:
        """Get mock race data for testing"""
        now = datetime.now()
        
        return [
            {
                "id": "mock-motogp-1",
                "name": "Italian Grand Prix",
                "circuit": "Mugello Circuit",
                "location": "Scarperia, Italy",
                "race_date": "2025-05-30",
                "status": "Upcoming",
                "laps": 23,
                "distance": "120.7 km",
                "class": "MotoGP",
                "top_riders": [
                    {
                        "name": "Francesco Bagnaia",
                        "number": 1,
                        "team": "Ducati Lenovo Team",
                        "bike": "Ducati Desmosedici GP25",
                        "dci": self.calculate_dci({
                            "lap_time_delta": 0.92,
                            "top_speed": 0.90,
                            "braking_efficiency": 0.88,
                            "rider_form": 0.90,
                            "track_adaptation": 0.85,
                            "tire_management": 0.87,
                            "experience": 0.88,
                            "reaction_time": 0.90
                        })
                    },
                    {
                        "name": "Jorge Martin",
                        "number": 89,
                        "team": "Prima Pramac Racing",
                        "bike": "Ducati Desmosedici GP25",
                        "dci": self.calculate_dci({
                            "lap_time_delta": 0.90,
                            "top_speed": 0.88,
                            "braking_efficiency": 0.85,
                            "rider_form": 0.88,
                            "track_adaptation": 0.82,
                            "tire_management": 0.85,
                            "experience": 0.85,
                            "reaction_time": 0.88
                        })
                    },
                    {
                        "name": "Marc Marquez",
                        "number": 93,
                        "team": "Gresini Racing MotoGP",
                        "bike": "Ducati Desmosedici GP24",
                        "dci": self.calculate_dci({
                            "lap_time_delta": 0.88,
                            "top_speed": 0.86,
                            "braking_efficiency": 0.90,
                            "rider_form": 0.85,
                            "track_adaptation": 0.88,
                            "tire_management": 0.83,
                            "experience": 0.95,
                            "reaction_time": 0.92
                        })
                    }
                ],
                "mock_data": True
            },
            {
                "id": "mock-motogp-2",
                "name": "Spanish Grand Prix",
                "circuit": "Circuito de Jerez",
                "location": "Jerez de la Frontera, Spain",
                "race_date": "2025-04-27",
                "status": "Upcoming",
                "laps": 25,
                "distance": "107.0 km",
                "class": "MotoGP",
                "top_riders": [
                    {
                        "name": "Enea Bastianini",
                        "number": 23,
                        "team": "Ducati Lenovo Team",
                        "bike": "Ducati Desmosedici GP25",
                        "dci": self.calculate_dci({
                            "lap_time_delta": 0.87,
                            "top_speed": 0.85,
                            "braking_efficiency": 0.86,
                            "rider_form": 0.84,
                            "track_adaptation": 0.80,
                            "tire_management": 0.84,
                            "experience": 0.83,
                            "reaction_time": 0.85
                        })
                    },
                    {
                        "name": "Brad Binder",
                        "number": 33,
                        "team": "Red Bull KTM Factory Racing",
                        "bike": "KTM RC16",
                        "dci": self.calculate_dci({
                            "lap_time_delta": 0.85,
                            "top_speed": 0.83,
                            "braking_efficiency": 0.84,
                            "rider_form": 0.82,
                            "track_adaptation": 0.78,
                            "tire_management": 0.82,
                            "experience": 0.81,
                            "reaction_time": 0.83
                        })
                    }
                ],
                "mock_data": True
            }
        ]
    
    def get_mock_standings(self) -> Dict[str, Any]:
        """Get mock rider standings"""
        return {
            "season": "2025",
            "class": "MotoGP",
            "standings": [
                {
                    "position": 1,
                    "rider": "Francesco Bagnaia",
                    "number": 1,
                    "team": "Ducati Lenovo Team",
                    "points": 195,
                    "wins": 4,
                    "podiums": 7,
                    "poles": 3,
                    "dci": self.calculate_dci({
                        "lap_time_delta": 0.92,
                        "top_speed": 0.90,
                        "braking_efficiency": 0.88,
                        "rider_form": 0.90,
                        "track_adaptation": 0.85,
                        "tire_management": 0.87,
                        "experience": 0.88,
                        "reaction_time": 0.90
                    })
                },
                {
                    "position": 2,
                    "rider": "Jorge Martin",
                    "number": 89,
                    "team": "Prima Pramac Racing",
                    "points": 182,
                    "wins": 3,
                    "podiums": 6,
                    "poles": 4,
                    "dci": self.calculate_dci({
                        "lap_time_delta": 0.90,
                        "top_speed": 0.88,
                        "braking_efficiency": 0.85,
                        "rider_form": 0.88,
                        "track_adaptation": 0.82,
                        "tire_management": 0.85,
                        "experience": 0.85,
                        "reaction_time": 0.88
                    })
                }
            ],
            "mock_data": True
        }
