"""
Table Tennis Intelligence Service
Provides DCI scoring and analytics for table tennis matches
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TableTennisIntelligence:
    """Table Tennis DCI and analytics service"""
    
    DCI_FACTORS = [
        "aces",
        "errors",
        "rally_efficiency",
        "set_win_percentage",
        "reflex",
        "momentum"
    ]
    
    def calculate_dci(self, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Dynamic Confidence Index for a table tennis player
        
        DCI Factors (6):
        - Aces (20%)
        - Errors (20%)
        - Rally Efficiency (20%)
        - Set Win % (15%)
        - Reflex (15%)
        - Momentum (10%)
        """
        
        aces = player_stats.get("aces_per_game", 5.0)  # 0-15
        errors = player_stats.get("errors_per_game", 3.0)  # 0-10 (lower is better)
        rally_efficiency = player_stats.get("rally_efficiency", 0.70)  # 0-1
        set_win_pct = player_stats.get("set_win_percentage", 0.65)  # 0-1
        reflex = player_stats.get("reflex_score", 0.75)  # 0-1
        momentum = player_stats.get("momentum", 0.70)  # 0-1
        
        aces_normalized = min(aces / 15, 1.0)
        
        errors_normalized = 1.0 - min(errors / 10, 1.0)
        
        dci_score = (
            aces_normalized * 0.20 +
            errors_normalized * 0.20 +
            rally_efficiency * 0.20 +
            set_win_pct * 0.15 +
            reflex * 0.15 +
            momentum * 0.10
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
                "aces": round(aces, 1),
                "errors": round(errors, 1),
                "rally_efficiency": round(rally_efficiency * 100, 1),
                "set_win_percentage": round(set_win_pct * 100, 1),
                "reflex": round(reflex * 100, 1),
                "momentum": round(momentum * 100, 1)
            },
            "breakdown": {
                "aces": round(aces_normalized * 20, 1),
                "errors": round(errors_normalized * 20, 1),
                "rally_efficiency": round(rally_efficiency * 20, 1),
                "set_win_percentage": round(set_win_pct * 15, 1),
                "reflex": round(reflex * 15, 1),
                "momentum": round(momentum * 10, 1)
            }
        }
    
    def get_mock_matches(self) -> List[Dict[str, Any]]:
        """Get mock match data for testing"""
        now = datetime.now()
        
        return [
            {
                "id": "mock-tt-1",
                "tournament": "World Table Tennis Championships",
                "player1": {
                    "name": "Fan Zhendong",
                    "country": "China",
                    "rank": 1,
                    "dci": self.calculate_dci({
                        "aces_per_game": 8.5,
                        "errors_per_game": 2.0,
                        "rally_efficiency": 0.85,
                        "set_win_percentage": 0.78,
                        "reflex_score": 0.90,
                        "momentum": 0.85
                    })
                },
                "player2": {
                    "name": "Ma Long",
                    "country": "China",
                    "rank": 2,
                    "dci": self.calculate_dci({
                        "aces_per_game": 7.8,
                        "errors_per_game": 2.5,
                        "rally_efficiency": 0.82,
                        "set_win_percentage": 0.75,
                        "reflex_score": 0.88,
                        "momentum": 0.80
                    })
                },
                "start_time": (now + timedelta(days=1)).isoformat(),
                "venue": "Singapore Indoor Stadium",
                "status": "Scheduled",
                "round": "Semifinals",
                "best_of": 7,
                "mock_data": True
            },
            {
                "id": "mock-tt-2",
                "tournament": "ITTF World Cup",
                "player1": {
                    "name": "Wang Chuqin",
                    "country": "China",
                    "rank": 3,
                    "dci": self.calculate_dci({
                        "aces_per_game": 7.5,
                        "errors_per_game": 2.8,
                        "rally_efficiency": 0.80,
                        "set_win_percentage": 0.72,
                        "reflex_score": 0.85,
                        "momentum": 0.78
                    })
                },
                "player2": {
                    "name": "Hugo Calderano",
                    "country": "Brazil",
                    "rank": 5,
                    "dci": self.calculate_dci({
                        "aces_per_game": 6.8,
                        "errors_per_game": 3.2,
                        "rally_efficiency": 0.75,
                        "set_win_percentage": 0.68,
                        "reflex_score": 0.82,
                        "momentum": 0.75
                    })
                },
                "start_time": (now + timedelta(days=2)).isoformat(),
                "venue": "Tokyo Metropolitan Gymnasium",
                "status": "Scheduled",
                "round": "Quarterfinals",
                "best_of": 7,
                "mock_data": True
            }
        ]
    
    def get_mock_history(self) -> List[Dict[str, Any]]:
        """Get mock historical match data"""
        now = datetime.now()
        
        return [
            {
                "id": "mock-tt-hist-1",
                "tournament": "World Table Tennis Championships",
                "player1": "Fan Zhendong",
                "player2": "Truls Moregard",
                "score": "4-2",
                "sets": [11-9, 11-7, 9-11, 11-8, 8-11, 11-6],
                "date": (now - timedelta(days=7)).isoformat(),
                "winner": "Fan Zhendong",
                "duration_minutes": 52,
                "mock_data": True
            },
            {
                "id": "mock-tt-hist-2",
                "tournament": "ITTF World Cup",
                "player1": "Ma Long",
                "player2": "Lin Yun-Ju",
                "score": "4-1",
                "sets": [11-8, 11-9, 9-11, 11-7, 11-5],
                "date": (now - timedelta(days=14)).isoformat(),
                "winner": "Ma Long",
                "duration_minutes": 45,
                "mock_data": True
            }
        ]
