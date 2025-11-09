from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
from datetime import datetime, timedelta
from app.schemas.predictions import GameResponse
from app.models.database import db, User, Game
from app.utils.auth import get_current_user
from app.services.thesportsdb import TheSportsDBService
from app.services.balldontlie import BallDontLieService
from app.services.ergast import ErgastService
from app.services.collegefootballdata import CollegeFootballDataService
from app.services.footballdata import FootballDataService

router = APIRouter(prefix="/api/sports", tags=["sports"])

thesportsdb = TheSportsDBService()
balldontlie = BallDontLieService()
ergast = ErgastService()
collegefootball = CollegeFootballDataService()
footballdata = FootballDataService()

@router.get("")
async def get_available_sports(current_user: User = Depends(get_current_user)):
    """Get list of available sports"""
    return {
        "sports": [
            {"id": "nfl", "name": "NFL", "icon": "🏈"},
            {"id": "nba", "name": "NBA", "icon": "🏀"},
            {"id": "mlb", "name": "MLB", "icon": "⚾"},
            {"id": "nhl", "name": "NHL", "icon": "🏒"},
            {"id": "soccer", "name": "Soccer", "icon": "⚽"},
            {"id": "f1", "name": "Formula 1", "icon": "🏎️"},
            {"id": "ncaaf", "name": "College Football", "icon": "🏈"}
        ]
    }

@router.get("/{sport}/schedule", response_model=List[GameResponse])
async def get_sport_schedule(
    sport: str,
    show_all: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get upcoming games for a sport"""
    games = []
    limit = None if show_all else 3
    
    if sport == "nba":
        nba_games = await balldontlie.get_games(season=2024)
        game_limit = len(nba_games) if show_all else min(10, len(nba_games))
        for game_data in nba_games[:game_limit]:
            game_id = str(uuid.uuid4())
            home_team = game_data.get("home_team", {}).get("full_name", "Unknown")
            away_team = game_data.get("visitor_team", {}).get("full_name", "Unknown")
            
            game = Game(
                id=game_id,
                sport="nba",
                league="NBA",
                home_team=home_team,
                away_team=away_team,
                scheduled_time=datetime.utcnow() + timedelta(days=1),
                status=game_data.get("status", "scheduled")
            )
            db.add_game(game)
            games.append(game)
    
    elif sport == "f1":
        f1_races = await ergast.get_current_season_races()
        race_limit = len(f1_races) if show_all else min(5, len(f1_races))
        for race_data in f1_races[:race_limit]:
            game_id = str(uuid.uuid4())
            race_name = race_data.get("raceName", "Unknown Race")
            
            game = Game(
                id=game_id,
                sport="f1",
                league="Formula 1",
                home_team=race_name,
                away_team="Field",
                scheduled_time=datetime.utcnow() + timedelta(days=7),
                status="scheduled"
            )
            db.add_game(game)
            games.append(game)
    
    elif sport == "ncaaf":
        cfb_games = await collegefootball.get_games(year=2024)
        game_limit = len(cfb_games) if show_all else min(10, len(cfb_games))
        for game_data in cfb_games[:game_limit]:
            game_id = str(uuid.uuid4())
            home_team = game_data.get("home_team", "Unknown")
            away_team = game_data.get("away_team", "Unknown")
            
            game = Game(
                id=game_id,
                sport="ncaaf",
                league="NCAA Football",
                home_team=home_team,
                away_team=away_team,
                scheduled_time=datetime.utcnow() + timedelta(days=2),
                status="scheduled"
            )
            db.add_game(game)
            games.append(game)
    
    else:
        mock_teams = {
            "nfl": [("Chiefs", "Bills"), ("49ers", "Cowboys"), ("Eagles", "Packers"), ("Ravens", "Steelers"), ("Bengals", "Browns"), ("Rams", "Cardinals"), ("Seahawks", "49ers"), ("Patriots", "Jets")],
            "mlb": [("Yankees", "Red Sox"), ("Dodgers", "Giants"), ("Astros", "Rangers"), ("Cubs", "White Sox"), ("Mets", "Phillies")],
            "nhl": [("Maple Leafs", "Canadiens"), ("Bruins", "Rangers"), ("Penguins", "Capitals"), ("Oilers", "Flames"), ("Lightning", "Panthers")],
            "soccer": [("Manchester United", "Liverpool"), ("Barcelona", "Real Madrid"), ("Bayern", "Dortmund"), ("PSG", "Marseille"), ("Juventus", "AC Milan")]
        }
        
        if sport in mock_teams:
            teams_to_show = mock_teams[sport] if show_all else mock_teams[sport][:3]
            for i, (home, away) in enumerate(teams_to_show):
                game_id = str(uuid.uuid4())
                game = Game(
                    id=game_id,
                    sport=sport,
                    league=sport.upper(),
                    home_team=home,
                    away_team=away,
                    scheduled_time=datetime.utcnow() + timedelta(days=i+1),
                    status="scheduled"
                )
                db.add_game(game)
                games.append(game)
    
    return [
        GameResponse(
            id=g.id,
            sport=g.sport,
            league=g.league,
            home_team=g.home_team,
            away_team=g.away_team,
            scheduled_time=g.scheduled_time,
            home_score=g.home_score,
            away_score=g.away_score,
            status=g.status
        )
        for g in games
    ]

@router.get("/{sport}/standings")
async def get_sport_standings(
    sport: str,
    current_user: User = Depends(get_current_user)
):
    """Get current standings for a sport"""
    standings = []
    
    if sport == "f1":
        driver_standings = await ergast.get_driver_standings()
        standings = [
            {
                "position": s.get("position"),
                "driver": s.get("Driver", {}).get("givenName", "") + " " + s.get("Driver", {}).get("familyName", ""),
                "points": s.get("points"),
                "wins": s.get("wins")
            }
            for s in driver_standings[:10]
        ]
    else:
        standings = [
            {"position": 1, "team": "Team A", "wins": 10, "losses": 2},
            {"position": 2, "team": "Team B", "wins": 9, "losses": 3},
            {"position": 3, "team": "Team C", "wins": 8, "losses": 4},
        ]
    
    return {"sport": sport, "standings": standings}

@router.get("/{sport}/teams")
async def get_sport_teams(
    sport: str,
    current_user: User = Depends(get_current_user)
):
    """Get teams for a sport"""
    teams = []
    
    if sport == "nba":
        nba_teams = await balldontlie.get_teams()
        teams = [
            {
                "id": t.get("id"),
                "name": t.get("full_name"),
                "abbreviation": t.get("abbreviation"),
                "city": t.get("city")
            }
            for t in nba_teams
        ]
    elif sport == "ncaaf":
        cfb_teams = await collegefootball.get_teams()
        teams = [
            {
                "id": t.get("id"),
                "name": t.get("school"),
                "mascot": t.get("mascot"),
                "conference": t.get("conference")
            }
            for t in cfb_teams[:50]
        ]
    else:
        teams = [
            {"id": 1, "name": "Team 1"},
            {"id": 2, "name": "Team 2"},
            {"id": 3, "name": "Team 3"}
        ]
    
    return {"sport": sport, "teams": teams}
