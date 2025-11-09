import random
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

class PredictionEngine:
    """
    AI Prediction Engine for sports analytics
    Uses historical data patterns to generate predictions
    """
    
    def __init__(self):
        self.model_cache = {}
    
    def calculate_dci(
        self,
        historical_accuracy: float,
        momentum_stability: float,
        health_factor: float,
        volatility_penalty: float
    ) -> float:
        """
        Calculate Dynamic Confidence Index (DCI)
        DCI = (HistoricalAccuracy * 0.4) + (MomentumStability * 0.3) + 
              (HealthFactor * 0.2) + (VolatilityPenalty * 0.1)
        
        Returns: DCI score normalized to 0-100
        """
        dci = (
            historical_accuracy * 0.4 +
            momentum_stability * 0.3 +
            health_factor * 0.2 -
            volatility_penalty * 0.1
        )
        return max(0, min(100, dci))
    
    def analyze_team_momentum(self, team_data: Dict) -> float:
        """
        Analyze team momentum based on recent performance
        Returns: Momentum score 0-100
        """
        recent_wins = team_data.get("recent_wins", 0)
        recent_games = team_data.get("recent_games", 1)
        win_rate = recent_wins / max(recent_games, 1)
        
        avg_points = team_data.get("avg_points_scored", 0)
        avg_allowed = team_data.get("avg_points_allowed", 0)
        point_differential = avg_points - avg_allowed
        
        momentum = (win_rate * 60) + (min(point_differential / 10, 1) * 40)
        return max(0, min(100, momentum))
    
    def analyze_health_factor(self, team_data: Dict) -> float:
        """
        Analyze team health (injuries, rest days, etc.)
        Returns: Health score 0-100
        """
        injured_key_players = team_data.get("injured_key_players", 0)
        days_rest = team_data.get("days_rest", 3)
        travel_distance = team_data.get("travel_distance", 0)
        
        health = 100
        health -= injured_key_players * 15
        health -= max(0, (3 - days_rest)) * 10
        health -= min(travel_distance / 1000, 20)
        
        return max(0, min(100, health))
    
    def calculate_volatility(self, team_data: Dict) -> float:
        """
        Calculate team performance volatility
        Returns: Volatility penalty 0-100
        """
        performance_variance = team_data.get("performance_variance", 0.5)
        consistency_score = team_data.get("consistency_score", 0.7)
        
        volatility = (performance_variance * 50) + ((1 - consistency_score) * 50)
        return max(0, min(100, volatility))
    
    def predict_game(
        self,
        game_id: str,
        home_team: str,
        away_team: str,
        sport: str,
        home_team_data: Optional[Dict] = None,
        away_team_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate AI prediction for a game
        Returns: Prediction dict with winner, confidence, DCI, and analysis
        """
        if not home_team_data:
            home_team_data = self._generate_mock_team_data(home_team)
        if not away_team_data:
            away_team_data = self._generate_mock_team_data(away_team)
        
        home_momentum = self.analyze_team_momentum(home_team_data)
        away_momentum = self.analyze_team_momentum(away_team_data)
        
        home_health = self.analyze_health_factor(home_team_data)
        away_health = self.analyze_health_factor(away_team_data)
        
        home_volatility = self.calculate_volatility(home_team_data)
        away_volatility = self.calculate_volatility(away_team_data)
        
        home_advantage = 5
        
        home_score = home_momentum + home_health - home_volatility + home_advantage
        away_score = away_momentum + away_health - away_volatility
        
        if home_score > away_score:
            predicted_winner = home_team
            confidence = min(95, 50 + (home_score - away_score) / 2)
            winner_data = home_team_data
        else:
            predicted_winner = away_team
            confidence = min(95, 50 + (away_score - home_score) / 2)
            winner_data = away_team_data
        
        historical_accuracy = 75 + random.uniform(-10, 10)
        momentum_stability = self.analyze_team_momentum(winner_data)
        health_factor = self.analyze_health_factor(winner_data)
        volatility_penalty = self.calculate_volatility(winner_data)
        
        dci_score = self.calculate_dci(
            historical_accuracy,
            momentum_stability,
            health_factor,
            volatility_penalty
        )
        
        analysis = self._generate_analysis(
            predicted_winner,
            home_team,
            away_team,
            confidence,
            dci_score,
            home_momentum,
            away_momentum,
            home_health,
            away_health
        )
        
        return {
            "game_id": game_id,
            "predicted_winner": predicted_winner,
            "confidence": round(confidence, 2),
            "dci_score": round(dci_score, 2),
            "analysis": analysis,
            "factors": {
                "home_momentum": round(home_momentum, 2),
                "away_momentum": round(away_momentum, 2),
                "home_health": round(home_health, 2),
                "away_health": round(away_health, 2),
                "home_volatility": round(home_volatility, 2),
                "away_volatility": round(away_volatility, 2),
                "home_advantage": home_advantage
            }
        }
    
    def _generate_mock_team_data(self, team_name: str) -> Dict:
        """Generate mock team data for demonstration"""
        random.seed(hash(team_name) % 10000)
        return {
            "recent_wins": random.randint(3, 8),
            "recent_games": 10,
            "avg_points_scored": random.uniform(20, 35),
            "avg_points_allowed": random.uniform(18, 32),
            "injured_key_players": random.randint(0, 3),
            "days_rest": random.randint(1, 7),
            "travel_distance": random.uniform(0, 2000),
            "performance_variance": random.uniform(0.2, 0.8),
            "consistency_score": random.uniform(0.5, 0.9)
        }
    
    def _generate_analysis(
        self,
        predicted_winner: str,
        home_team: str,
        away_team: str,
        confidence: float,
        dci_score: float,
        home_momentum: float,
        away_momentum: float,
        home_health: float,
        away_health: float
    ) -> str:
        """Generate textual analysis of the prediction"""
        is_home_winner = predicted_winner == home_team
        
        analysis = f"AI predicts {predicted_winner} to win with {confidence:.1f}% confidence (DCI: {dci_score:.1f}). "
        
        if is_home_winner:
            if home_momentum > away_momentum + 15:
                analysis += f"{home_team} shows strong momentum advantage with recent performance trends. "
            if home_health > 85:
                analysis += f"{home_team} is at full strength with minimal injuries. "
            analysis += "Home field advantage provides additional edge. "
        else:
            if away_momentum > home_momentum + 15:
                analysis += f"{away_team} demonstrates superior momentum despite playing away. "
            if away_health > 85:
                analysis += f"{away_team} roster is healthy and well-rested. "
        
        if dci_score > 80:
            analysis += "High confidence in this prediction based on strong data patterns."
        elif dci_score > 60:
            analysis += "Moderate confidence - some volatility factors present."
        else:
            analysis += "Lower confidence - high volatility or limited data quality."
        
        return analysis
    
    def personalize_prediction(self, user_history: List[Dict]) -> Dict:
        """
        Analyze user's prediction patterns and provide insights
        """
        if not user_history:
            return {
                "bias_detected": None,
                "accuracy_trend": "insufficient_data",
                "recommendation": "Make more predictions to unlock personalized insights"
            }
        
        total = len(user_history)
        correct = sum(1 for p in user_history if p.get("was_correct"))
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        home_predictions = sum(1 for p in user_history if "home" in p.get("predicted_winner", "").lower())
        home_bias = (home_predictions / total) * 100 if total > 0 else 50
        
        insights = {
            "accuracy": round(accuracy, 2),
            "total_predictions": total,
            "correct_predictions": correct
        }
        
        if home_bias > 65:
            insights["bias_detected"] = f"You tend to favor home teams ({home_bias:.1f}% of predictions)"
            insights["recommendation"] = "Consider away team momentum more carefully"
        elif home_bias < 35:
            insights["bias_detected"] = f"You tend to favor away teams ({100-home_bias:.1f}% of predictions)"
            insights["recommendation"] = "Don't underestimate home field advantage"
        else:
            insights["bias_detected"] = None
            insights["recommendation"] = "Your predictions show balanced analysis"
        
        return insights

prediction_engine = PredictionEngine()
