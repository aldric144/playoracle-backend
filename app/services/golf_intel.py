"""
Golf Intelligence Service
Provides DCI scoring and analytics for golf tournaments
"""
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GolfIntelligence:
    """Golf DCI and analytics service"""
    
    DCI_FACTORS = [
        "driving_accuracy",
        "strokes_gained",
        "birdie_conversion",
        "sand_saves",
        "consistency",
        "stamina",
        "weather_impact",
        "form"
    ]
    
    def calculate_dci(self, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Dynamic Confidence Index for a golfer
        
        DCI Factors (8):
        - Driving Accuracy (15%)
        - Strokes Gained (20%)
        - Birdie Conversion (15%)
        - Sand Saves (10%)
        - Consistency (15%)
        - Stamina (10%)
        - Weather Impact (10%)
        - Form (5%)
        """
        
        driving_accuracy = player_stats.get("driving_accuracy", 0.65)  # 0-1
        strokes_gained = player_stats.get("strokes_gained", 0.0)  # -5 to +5
        birdie_conversion = player_stats.get("birdie_conversion", 0.20)  # 0-1
        sand_saves = player_stats.get("sand_saves", 0.50)  # 0-1
        consistency = player_stats.get("consistency", 0.70)  # 0-1
        stamina = player_stats.get("stamina", 0.75)  # 0-1
        weather_impact = player_stats.get("weather_impact", 0.70)  # 0-1
        form = player_stats.get("recent_form", 0.70)  # 0-1
        
        strokes_gained_normalized = (strokes_gained + 5) / 10
        
        dci_score = (
            driving_accuracy * 0.15 +
            strokes_gained_normalized * 0.20 +
            birdie_conversion * 0.15 +
            sand_saves * 0.10 +
            consistency * 0.15 +
            stamina * 0.10 +
            weather_impact * 0.10 +
            form * 0.05
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
                "driving_accuracy": round(driving_accuracy * 100, 1),
                "strokes_gained": round(strokes_gained, 2),
                "birdie_conversion": round(birdie_conversion * 100, 1),
                "sand_saves": round(sand_saves * 100, 1),
                "consistency": round(consistency * 100, 1),
                "stamina": round(stamina * 100, 1),
                "weather_impact": round(weather_impact * 100, 1),
                "form": round(form * 100, 1)
            },
            "breakdown": {
                "driving_accuracy": round(driving_accuracy * 15, 1),
                "strokes_gained": round(strokes_gained_normalized * 20, 1),
                "birdie_conversion": round(birdie_conversion * 15, 1),
                "sand_saves": round(sand_saves * 10, 1),
                "consistency": round(consistency * 15, 1),
                "stamina": round(stamina * 10, 1),
                "weather_impact": round(weather_impact * 10, 1),
                "form": round(form * 5, 1)
            }
        }
    
    def get_mock_tournaments(self) -> List[Dict[str, Any]]:
        """Get mock tournament data for testing"""
        now = datetime.now()
        
        return [
            {
                "id": "mock-golf-1",
                "name": "The Masters Tournament",
                "venue": "Augusta National Golf Club",
                "location": "Augusta, GA",
                "start_date": "2025-04-10",
                "end_date": "2025-04-13",
                "status": "Upcoming",
                "purse": "$18,000,000",
                "field_size": 90,
                "top_players": [
                    {
                        "name": "Scottie Scheffler",
                        "rank": 1,
                        "dci": self.calculate_dci({
                            "driving_accuracy": 0.72,
                            "strokes_gained": 2.5,
                            "birdie_conversion": 0.28,
                            "sand_saves": 0.65,
                            "consistency": 0.85,
                            "stamina": 0.90,
                            "weather_impact": 0.80,
                            "recent_form": 0.85
                        })
                    },
                    {
                        "name": "Rory McIlroy",
                        "rank": 2,
                        "dci": self.calculate_dci({
                            "driving_accuracy": 0.68,
                            "strokes_gained": 2.2,
                            "birdie_conversion": 0.26,
                            "sand_saves": 0.60,
                            "consistency": 0.80,
                            "stamina": 0.85,
                            "weather_impact": 0.75,
                            "recent_form": 0.80
                        })
                    }
                ],
                "mock_data": True
            },
            {
                "id": "mock-golf-2",
                "name": "PGA Championship",
                "venue": "Quail Hollow Club",
                "location": "Charlotte, NC",
                "start_date": "2025-05-15",
                "end_date": "2025-05-18",
                "status": "Upcoming",
                "purse": "$17,500,000",
                "field_size": 156,
                "top_players": [
                    {
                        "name": "Jon Rahm",
                        "rank": 3,
                        "dci": self.calculate_dci({
                            "driving_accuracy": 0.70,
                            "strokes_gained": 2.0,
                            "birdie_conversion": 0.25,
                            "sand_saves": 0.62,
                            "consistency": 0.82,
                            "stamina": 0.88,
                            "weather_impact": 0.78,
                            "recent_form": 0.82
                        })
                    }
                ],
                "mock_data": True
            }
        ]
    
    def get_mock_leaderboard(self, tournament_id: str) -> Dict[str, Any]:
        """Get mock leaderboard for a tournament"""
        return {
            "tournament_id": tournament_id,
            "tournament_name": "The Masters Tournament",
            "round": 2,
            "leaderboard": [
                {
                    "position": 1,
                    "player": "Scottie Scheffler",
                    "score": -8,
                    "thru": 18,
                    "today": -4,
                    "dci": self.calculate_dci({
                        "driving_accuracy": 0.72,
                        "strokes_gained": 2.5,
                        "birdie_conversion": 0.28,
                        "sand_saves": 0.65,
                        "consistency": 0.85,
                        "stamina": 0.90,
                        "weather_impact": 0.80,
                        "recent_form": 0.85
                    })
                },
                {
                    "position": 2,
                    "player": "Rory McIlroy",
                    "score": -7,
                    "thru": 18,
                    "today": -3,
                    "dci": self.calculate_dci({
                        "driving_accuracy": 0.68,
                        "strokes_gained": 2.2,
                        "birdie_conversion": 0.26,
                        "sand_saves": 0.60,
                        "consistency": 0.80,
                        "stamina": 0.85,
                        "weather_impact": 0.75,
                        "recent_form": 0.80
                    })
                }
            ],
            "mock_data": True
        }
