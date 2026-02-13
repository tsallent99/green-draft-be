# Green Draft - Backend

REST API for a Fantasy Golf application that allows users to create leagues, build teams, and compete based on the performance of professional golfers in real tournaments.

## 📋 Description

Green Draft is a fantasy sports platform focused on professional golf. Users can:
- Create and join private leagues for specific tournaments
- Select golfers for their teams based on odds
- Compete against other participants
- Follow real-time leaderboards
- Manage multiple leagues and tournaments

## 🛠️ Technologies

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - ORM for database management
- **SQLite** - Database (development)
- **Pydantic** - Data validation and serialization
- **JWT (python-jose)** - Authentication and authorization
- **Passlib + Bcrypt** - Secure password hashing
- **Pytest** - Testing framework
- **Uvicorn** - ASGI server

## 🏗️ Architecture

The project follows a clean architecture with separation of concerns:

```
app/
├── routers/          # API endpoints (controllers)
│   ├── users.py
│   ├── tournaments.py
│   ├── players.py
│   ├── leagues.py
│   ├── entries.py
│   ├── teams.py
│   └── leaderboard.py
├── models/           # Database models (SQLAlchemy)
│   ├── user.py
│   ├── tournament.py
│   ├── player.py
│   ├── league.py
│   ├── entry.py
│   ├── team.py
│   ├── team_pick.py
│   ├── player_odds.py
│   └── leaderboard.py
├── schemas/          # Pydantic schemas (validation/serialization)
├── auth.py           # JWT authentication system
├── database.py       # Database configuration
└── mock_data.py      # Test data
```

### Domain Model

- **User**: Registered users on the platform
- **Tournament**: Golf tournaments (Masters, PGA Championship, etc.)
- **Player**: Professional golfers
- **PlayerOdds**: Player odds per tournament
- **League**: Private leagues created by users
- **Entry**: User enrollment in a league (with invitation code)
- **Team**: Team formed by a user for a specific league
- **TeamPick**: Selection of golfers for a team
- **Leaderboard**: Team rankings in a league

## 🚀 Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

1. Clone the repository:
```bash
git clone git@github.com:tsallent99/green-draft-be.git
cd green-draft-be
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (optional):
```env
DATABASE_URL=sqlite:///./fantasy_golf.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 💻 Usage

### Run development server:
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### Interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Run tests:
```bash
pytest
```

## 📡 API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login
- `GET /api/users/me` - Get current user profile

### Tournaments
- `GET /api/tournaments` - List tournaments
- `POST /api/tournaments` - Create tournament
- `GET /api/tournaments/{id}` - Get specific tournament

### Players
- `GET /api/players` - List golfers
- `POST /api/players` - Create golfer
- `GET /api/tournaments/{tournament_id}/odds` - Get odds

### Leagues
- `POST /api/leagues` - Create league
- `GET /api/leagues` - List user's leagues
- `POST /api/leagues/join` - Join league with code

### Teams
- `POST /api/teams` - Create team
- `GET /api/teams/{id}` - View team
- `POST /api/teams/{team_id}/picks` - Select golfers

### Leaderboard
- `GET /api/leaderboard/{league_id}` - View league leaderboard

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Protected endpoints require the header:
```
Authorization: Bearer <token>
```

## 🧪 Testing

The project includes unit and integration tests:
- Endpoint tests (routers)
- Model tests
- Authentication tests

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## 📝 Project Status

- ✅ Authentication and authorization
- ✅ User management
- ✅ Tournament and player management
- ✅ League system with invitation codes
- ✅ Team formation
- ✅ Basic leaderboards
- 🚧 Real-time score updates
- 🚧 Advanced scoring system
- 🚧 Professional golf API integration

## 👤 Author

**tsallent99**

## 📄 License

This project is private and for personal use.
