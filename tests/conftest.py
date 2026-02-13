import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User, League, Entry, Team, Leaderboard
from app.auth import get_password_hash, create_access_token
from main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session):
    """Create a second test user"""
    user = User(
        email="test2@example.com",
        username="testuser2",
        full_name="Test User 2",
        hashed_password=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Create an authentication token for test user"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_league(db_session, test_user):
    """Create a test league"""
    league = League(
        name="Test League",
        creator_id=test_user.id,
        tournament_id=1,  # Masters Tournament from mock data
        entry_fee=100.0,
        invitation_code="TEST1234",
        max_participants=10
    )
    db_session.add(league)
    db_session.commit()
    db_session.refresh(league)

    # Create leaderboard for league
    leaderboard = Leaderboard(league_id=league.id)
    db_session.add(leaderboard)
    db_session.commit()

    return league


@pytest.fixture
def test_entry(db_session, test_user, test_league):
    """Create a test entry"""
    entry = Entry(
        user_id=test_user.id,
        league_id=test_league.id
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


@pytest.fixture
def test_team(db_session, test_entry):
    """Create a test team with valid picks"""
    team = Team(entry_id=test_entry.id)
    db_session.add(team)
    db_session.flush()

    # Add 5 picks with valid categories (sum = 13)
    from app.models import TeamPick
    picks_data = [
        {"player_id": 1, "category": 1},  # Scheffler
        {"player_id": 2, "category": 1},  # Rory
        {"player_id": 9, "category": 2},  # Hatton
        {"player_id": 16, "category": 4}, # Oosthuizen
        {"player_id": 17, "category": 5}, # Theegala
    ]

    for pick_data in picks_data:
        pick = TeamPick(
            team_id=team.id,
            player_id=pick_data["player_id"],
            player_category=pick_data["category"]
        )
        db_session.add(pick)

    db_session.flush()
    db_session.refresh(team)
    team.calculate_validity()
    db_session.commit()
    db_session.refresh(team)

    return team
