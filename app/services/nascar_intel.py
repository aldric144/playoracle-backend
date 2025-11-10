"""
NASCAR Intelligence Service
Provides DCI scoring and analytics for NASCAR/IndyCar races
"""
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NASCARIntelligence:
    """NASCAR DCI and analytics service"""
    
    DCI_FACTORS = [
        "laps_completed",
        "pit_stops",
        "average_speed",
        "consistency",
        "overtakes",
        "tire_wear",
        "team_coordination",
        "weather_impact"
    ]
    
    def calculate_dci(self, driver_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Dynamic Confidence Index for a NASCAR driver
        
        DCI Factors (8):
        - Laps Completed (15%)
        - Pit Stops (10%)
        - Average Speed (20%)
        - Consistency (15%)
        - Overtakes (10%)
        - Tire Wear (10%)
        - Team Coordination (15%)
        - Weather Impact (5%)
        """
        
        laps_completed = driver_stats.get("laps_completed", 0.85)  # 0-1
        pit_stops = driver_stats.get("pit_stops", 0.75)  # 0-1 (efficiency)
        average_speed = driver_stats.get("average_speed", 0.80)  # 0-1
        consistency = driver_stats.get("consistency", 0.70)  # 0-1
        overtakes = driver_stats.get("overtakes", 0.65)  # 0-1
        tire_wear = driver_stats.get("tire_wear", 0.75)  # 0-1 (management)
        team_coordination = driver_stats.get("team_coordination", 0.80)  # 0-1
        weather_impact = driver_stats.get("weather_impact", 0.70)  # 0-1
        
        dci_score = (
            laps_completed * 0.15 +
            pit_stops * 0.10 +
            average_speed * 0.20 +
            consistency * 0.15 +
            overtakes * 0.10 +
            tire_wear * 0.10 +
            team_coordination * 0.15 +
            weather_impact * 0.05
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
                "laps_completed": round(laps_completed * 100, 1),
                "pit_stops": round(pit_stops * 100, 1),
                "average_speed": round(average_speed * 100, 1),
                "consistency": round(consistency * 100, 1),
                "overtakes": round(overtakes * 100, 1),
                "tire_wear": round(tire_wear * 100, 1),
                "team_coordination": round(team_coordination * 100, 1),
                "weather_impact": round(weather_impact * 100, 1)
            },
            "breakdown": {
                "laps_completed": round(laps_completed * 15, 1),
                "pit_stops": round(pit_stops * 10, 1),
                "average_speed": round(average_speed * 20, 1),
                "consistency": round(consistency * 15, 1),
                "overtakes": round(overtakes * 10, 1),
                "tire_wear": round(tire_wear * 10, 1),
                "team_coordination": round(team_coordination * 15, 1),
                "weather_impact": round(weather_impact * 5, 1)
            }
        }
    
    def get_mock_races(self) -> List[Dict[str, Any]]:
        """Get mock race data for testing"""
        now = datetime.now()
        
        return [
            {
                "id": "mock-nascar-1",
                "name": "Daytona 500",
                "track": "Daytona International Speedway",
                "location": "Daytona Beach, FL",
                "race_date": "2025-02-16",
                "status": "Upcoming",
                "laps": 200,
                "distance": "500 miles",
                "purse": "$23,600,000",
                "top_drivers": [
                    {
                        "name": "Kyle Larson",
                        "number": 5,
                        "team": "Hendrick Motorsports",
                        "dci": self.calculate_dci({
                            "laps_completed": 0.92,
                            "pit_stops": 0.85,
                            "average_speed": 0.88,
                            "consistency": 0.90,
                            "overtakes": 0.82,
                            "tire_wear": 0.87,
                            "team_coordination": 0.92,
                            "weather_impact": 0.85
                        })
                    },
                    {
                        "name": "Chase Elliott",
                        "number": 9,
                        "team": "Hendrick Motorsports",
                        "dci": self.calculate_dci({
                            "laps_completed": 0.90,
                            "pit_stops": 0.82,
                            "average_speed": 0.85,
                            "consistency": 0.88,
                            "overtakes": 0.80,
                            "tire_wear": 0.85,
                            "team_coordination": 0.90,
                            "weather_impact": 0.82
                        })
                    },
                    {
                        "name": "Denny Hamlin",
                        "number": 11,
                        "team": "Joe Gibbs Racing",
                        "dci": self.calculate_dci({
                            "laps_completed": 0.88,
                            "pit_stops": 0.80,
                            "average_speed": 0.83,
                            "consistency": 0.85,
                            "overtakes": 0.78,
                            "tire_wear": 0.82,
                            "team_coordination": 0.88,
                            "weather_impact": 0.80
                        })
                    }
                ],
                "mock_data": True
            },
            {
                "id": "mock-nascar-2",
                "name": "Coca-Cola 600",
                "track": "Charlotte Motor Speedway",
                "location": "Concord, NC",
                "race_date": "2025-05-25",
                "status": "Upcoming",
                "laps": 400,
                "distance": "600 miles",
                "purse": "$13,000,000",
                "top_drivers": [
                    {
                        "name": "Kyle Busch",
                        "number": 8,
                        "team": "Richard Childress Racing",
                        "dci": self.calculate_dci({
                            "laps_completed": 0.89,
                            "pit_stops": 0.83,
                            "average_speed": 0.86,
                            "consistency": 0.87,
                            "overtakes": 0.81,
                            "tire_wear": 0.84,
                            "team_coordination": 0.89,
                            "weather_impact": 0.83
                        })
                    },
                    {
                        "name": "Martin Truex Jr.",
                        "number": 19,
                        "team": "Joe Gibbs Racing",
                        "dci": self.calculate_dci({
                            "laps_completed": 0.87,
                            "pit_stops": 0.81,
                            "average_speed": 0.84,
                            "consistency": 0.86,
                            "overtakes": 0.79,
                            "tire_wear": 0.83,
                            "team_coordination": 0.87,
                            "weather_impact": 0.81
                        })
                    }
                ],
                "mock_data": True
            }
        ]
    
    def get_mock_standings(self) -> Dict[str, Any]:
        """Get mock driver standings"""
        return {
            "season": "2025",
            "standings": [
                {
                    "position": 1,
                    "driver": "Kyle Larson",
                    "number": 5,
                    "team": "Hendrick Motorsports",
                    "points": 485,
                    "wins": 3,
                    "top_5": 8,
                    "top_10": 12,
                    "dci": self.calculate_dci({
                        "laps_completed": 0.92,
                        "pit_stops": 0.85,
                        "average_speed": 0.88,
                        "consistency": 0.90,
                        "overtakes": 0.82,
                        "tire_wear": 0.87,
                        "team_coordination": 0.92,
                        "weather_impact": 0.85
                    })
                },
                {
                    "position": 2,
                    "driver": "Chase Elliott",
                    "number": 9,
                    "team": "Hendrick Motorsports",
                    "points": 472,
                    "wins": 2,
                    "top_5": 7,
                    "top_10": 11,
                    "dci": self.calculate_dci({
                        "laps_completed": 0.90,
                        "pit_stops": 0.82,
                        "average_speed": 0.85,
                        "consistency": 0.88,
                        "overtakes": 0.80,
                        "tire_wear": 0.85,
                        "team_coordination": 0.90,
                        "weather_impact": 0.82
                    })
                }
            ],
            "mock_data": True
        }
