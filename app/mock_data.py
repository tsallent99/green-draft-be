from datetime import datetime, timedelta
from app.models.tournament import TournamentStatus

# Mock Tournaments
MOCK_TOURNAMENTS = [
    {
        "id": 1,
        "name": "Masters Tournament",
        "location": "Augusta National Golf Club, Georgia",
        "start_date": datetime(2026, 4, 9),
        "end_date": datetime(2026, 4, 12),
        "status": TournamentStatus.UPCOMING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 2,
        "name": "PGA Championship",
        "location": "Quail Hollow Club, North Carolina",
        "start_date": datetime(2026, 5, 14),
        "end_date": datetime(2026, 5, 17),
        "status": TournamentStatus.UPCOMING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 3,
        "name": "U.S. Open",
        "location": "Oakmont Country Club, Pennsylvania",
        "start_date": datetime(2026, 6, 18),
        "end_date": datetime(2026, 6, 21),
        "status": TournamentStatus.UPCOMING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": 4,
        "name": "The Open Championship",
        "location": "Royal Birkdale, England",
        "start_date": datetime(2026, 7, 16),
        "end_date": datetime(2026, 7, 19),
        "status": TournamentStatus.UPCOMING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

# Mock Players
MOCK_PLAYERS = [
    {"id": 1, "name": "Scottie Scheffler", "country": "USA", "world_ranking": 1},
    {"id": 2, "name": "Rory McIlroy", "country": "Northern Ireland", "world_ranking": 2},
    {"id": 3, "name": "Jon Rahm", "country": "Spain", "world_ranking": 3},
    {"id": 4, "name": "Viktor Hovland", "country": "Norway", "world_ranking": 4},
    {"id": 5, "name": "Xander Schauffele", "country": "USA", "world_ranking": 5},
    {"id": 6, "name": "Patrick Cantlay", "country": "USA", "world_ranking": 6},
    {"id": 7, "name": "Collin Morikawa", "country": "USA", "world_ranking": 7},
    {"id": 8, "name": "Ludvig Åberg", "country": "Sweden", "world_ranking": 8},
    {"id": 9, "name": "Tyrrell Hatton", "country": "England", "world_ranking": 9},
    {"id": 10, "name": "Tommy Fleetwood", "country": "England", "world_ranking": 10},
    {"id": 11, "name": "Brooks Koepka", "country": "USA", "world_ranking": 11},
    {"id": 12, "name": "Max Homa", "country": "USA", "world_ranking": 12},
    {"id": 13, "name": "Wyndham Clark", "country": "USA", "world_ranking": 13},
    {"id": 14, "name": "Matt Fitzpatrick", "country": "England", "world_ranking": 14},
    {"id": 15, "name": "Brian Harman", "country": "USA", "world_ranking": 15},
    {"id": 16, "name": "Louis Oosthuizen", "country": "South Africa", "world_ranking": 35},
    {"id": 17, "name": "Sahith Theegala", "country": "USA", "world_ranking": 40},
    {"id": 18, "name": "Tom Kim", "country": "South Korea", "world_ranking": 22},
    {"id": 19, "name": "Cameron Young", "country": "USA", "world_ranking": 18},
    {"id": 20, "name": "Russell Henley", "country": "USA", "world_ranking": 25},
    {"id": 21, "name": "Tony Finau", "country": "USA", "world_ranking": 16},
    {"id": 22, "name": "Justin Thomas", "country": "USA", "world_ranking": 17},
    {"id": 23, "name": "Sam Burns", "country": "USA", "world_ranking": 19},
    {"id": 24, "name": "Jason Day", "country": "Australia", "world_ranking": 20},
    {"id": 25, "name": "Rickie Fowler", "country": "USA", "world_ranking": 28},
]

# Mock Player Odds for Masters Tournament (tournament_id = 1)
# Category 1: Top favorites (odds 1-10)
# Category 2: Strong contenders (odds 11-25)
# Category 3: Good chances (odds 26-50)
# Category 4: Dark horses (odds 51-100)
# Category 5: Long shots (odds 100+)
MOCK_PLAYER_ODDS = [
    # Category 1 players
    {"id": 1, "player_id": 1, "tournament_id": 1, "category": 1, "odds": 5.5},
    {"id": 2, "player_id": 2, "tournament_id": 1, "category": 1, "odds": 8.0},
    {"id": 3, "player_id": 3, "tournament_id": 1, "category": 1, "odds": 9.0},
    {"id": 4, "player_id": 4, "tournament_id": 1, "category": 1, "odds": 10.0},

    # Category 2 players
    {"id": 5, "player_id": 5, "tournament_id": 1, "category": 2, "odds": 12.0},
    {"id": 6, "player_id": 6, "tournament_id": 1, "category": 2, "odds": 14.0},
    {"id": 7, "player_id": 7, "tournament_id": 1, "category": 2, "odds": 16.0},
    {"id": 8, "player_id": 8, "tournament_id": 1, "category": 2, "odds": 18.0},
    {"id": 9, "player_id": 9, "tournament_id": 1, "category": 2, "odds": 20.0},
    {"id": 10, "player_id": 21, "tournament_id": 1, "category": 2, "odds": 22.0},
    {"id": 11, "player_id": 22, "tournament_id": 1, "category": 2, "odds": 24.0},

    # Category 3 players
    {"id": 12, "player_id": 10, "tournament_id": 1, "category": 3, "odds": 30.0},
    {"id": 13, "player_id": 11, "tournament_id": 1, "category": 3, "odds": 33.0},
    {"id": 14, "player_id": 12, "tournament_id": 1, "category": 3, "odds": 35.0},
    {"id": 15, "player_id": 13, "tournament_id": 1, "category": 3, "odds": 40.0},
    {"id": 16, "player_id": 14, "tournament_id": 1, "category": 3, "odds": 45.0},
    {"id": 17, "player_id": 23, "tournament_id": 1, "category": 3, "odds": 48.0},

    # Category 4 players
    {"id": 18, "player_id": 15, "tournament_id": 1, "category": 4, "odds": 55.0},
    {"id": 19, "player_id": 16, "tournament_id": 1, "category": 4, "odds": 65.0},
    {"id": 20, "player_id": 18, "tournament_id": 1, "category": 4, "odds": 70.0},
    {"id": 21, "player_id": 19, "tournament_id": 1, "category": 4, "odds": 80.0},
    {"id": 22, "player_id": 24, "tournament_id": 1, "category": 4, "odds": 90.0},

    # Category 5 players
    {"id": 23, "player_id": 17, "tournament_id": 1, "category": 5, "odds": 110.0},
    {"id": 24, "player_id": 20, "tournament_id": 1, "category": 5, "odds": 125.0},
    {"id": 25, "player_id": 25, "tournament_id": 1, "category": 5, "odds": 150.0},
]


def get_mock_tournaments():
    """Get all mock tournaments"""
    return MOCK_TOURNAMENTS


def get_mock_future_tournaments():
    """Get tournaments that haven't started yet (start_date > now)"""
    now = datetime.utcnow()
    return [t for t in MOCK_TOURNAMENTS if t["start_date"] > now]


def get_mock_tournament(tournament_id: int):
    """Get a specific mock tournament"""
    for tournament in MOCK_TOURNAMENTS:
        if tournament["id"] == tournament_id:
            return tournament
    return None


def get_mock_players():
    """Get all mock players"""
    return MOCK_PLAYERS


def get_mock_player(player_id: int):
    """Get a specific mock player"""
    for player in MOCK_PLAYERS:
        if player["id"] == player_id:
            return player
    return None


def get_mock_player_odds(tournament_id: int):
    """Get all player odds for a specific tournament"""
    return [odds for odds in MOCK_PLAYER_ODDS if odds["tournament_id"] == tournament_id]


def get_mock_player_odds_by_category(tournament_id: int, category: int):
    """Get player odds for a specific tournament and category"""
    return [
        odds for odds in MOCK_PLAYER_ODDS
        if odds["tournament_id"] == tournament_id and odds["category"] == category
    ]
