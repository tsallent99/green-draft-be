import pytest
from app.models import Entry, User


class TestGetLeaderboard:
    def test_get_leaderboard_success(self, client, test_league, test_entry, db_session):
        """Test getting leaderboard for a league"""
        response = client.get(f"/api/leaderboard/{test_league.id}")
        assert response.status_code == 200
        data = response.json()

        assert data["league_id"] == test_league.id
        assert data["league_name"] == test_league.name
        assert "tournament_name" in data
        assert "prize_pool" in data
        assert "first_place_prize" in data
        assert "second_place_prize" in data
        assert "third_place_prize" in data
        assert "rankings" in data
        assert isinstance(data["rankings"], list)

    def test_get_leaderboard_with_multiple_entries(self, client, test_league, test_entry, test_user2, db_session):
        """Test leaderboard with multiple entries"""
        # Create second entry with different score
        entry2 = Entry(
            user_id=test_user2.id,
            league_id=test_league.id,
            total_score=150.0
        )
        db_session.add(entry2)

        # Update first entry score
        test_entry.total_score = 200.0
        db_session.commit()

        response = client.get(f"/api/leaderboard/{test_league.id}")
        assert response.status_code == 200
        data = response.json()

        rankings = data["rankings"]
        assert len(rankings) == 2

        # Check ranking order (descending by score)
        assert rankings[0]["position"] == 1
        assert rankings[0]["score"] == 200.0
        assert rankings[1]["position"] == 2
        assert rankings[1]["score"] == 150.0

    def test_get_leaderboard_prize_distribution(self, client, test_league, test_entry, test_user2, db_session):
        """Test prize distribution in leaderboard"""
        # Create additional entries
        entry2 = Entry(
            user_id=test_user2.id,
            league_id=test_league.id,
            total_score=150.0
        )
        db_session.add(entry2)

        # Create third user and entry
        user3 = User(
            email="test3@example.com",
            username="testuser3",
            hashed_password="hash"
        )
        db_session.add(user3)
        db_session.flush()

        entry3 = Entry(
            user_id=user3.id,
            league_id=test_league.id,
            total_score=100.0
        )
        db_session.add(entry3)

        # Set scores
        test_entry.total_score = 200.0
        db_session.commit()

        response = client.get(f"/api/leaderboard/{test_league.id}")
        assert response.status_code == 200
        data = response.json()

        # Check prize pool calculation (3 entries * 100.0 entry fee)
        assert data["prize_pool"] == 300.0
        assert data["first_place_prize"] == 180.0  # 60%
        assert data["second_place_prize"] == 90.0   # 30%
        assert data["third_place_prize"] == 30.0    # 10%

        # Check prizes in rankings
        rankings = data["rankings"]
        assert rankings[0]["prize"] == 180.0
        assert rankings[1]["prize"] == 90.0
        assert rankings[2]["prize"] == 30.0

    def test_get_leaderboard_league_not_found(self, client):
        """Test getting leaderboard for non-existent league"""
        response = client.get("/api/leaderboard/99999")
        assert response.status_code == 404

    def test_get_leaderboard_empty_league(self, client, test_league):
        """Test getting leaderboard for league with no entries"""
        response = client.get(f"/api/leaderboard/{test_league.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["prize_pool"] == 0.0


class TestRefreshLeaderboard:
    def test_refresh_leaderboard_success(self, client, test_league, test_entry):
        """Test refreshing leaderboard"""
        response = client.post(f"/api/leaderboard/{test_league.id}/refresh")
        assert response.status_code == 200
        data = response.json()

        assert data["league_id"] == test_league.id
        assert "rankings" in data
        assert "prize_pool" in data

    def test_refresh_leaderboard_updates_rankings(self, client, test_league, test_entry, test_user2, db_session):
        """Test that refresh updates rankings correctly"""
        # Create second entry
        entry2 = Entry(
            user_id=test_user2.id,
            league_id=test_league.id,
            total_score=100.0
        )
        db_session.add(entry2)
        test_entry.total_score = 50.0
        db_session.commit()

        # Get initial leaderboard
        response1 = client.get(f"/api/leaderboard/{test_league.id}")
        data1 = response1.json()
        assert data1["rankings"][0]["score"] == 100.0

        # Update scores
        test_entry.total_score = 200.0
        entry2.total_score = 80.0
        db_session.commit()

        # Refresh leaderboard
        response2 = client.post(f"/api/leaderboard/{test_league.id}/refresh")
        data2 = response2.json()

        # Check new rankings
        rankings = data2["rankings"]
        assert rankings[0]["score"] == 200.0
        assert rankings[0]["position"] == 1
        assert rankings[1]["score"] == 80.0
        assert rankings[1]["position"] == 2

    def test_refresh_leaderboard_not_found(self, client):
        """Test refreshing leaderboard for non-existent league"""
        response = client.post("/api/leaderboard/99999/refresh")
        assert response.status_code == 404

    def test_refresh_leaderboard_recalculates_prizes(self, client, test_league, test_entry, test_user2, db_session):
        """Test that refresh recalculates prizes"""
        # Create additional entry
        entry2 = Entry(
            user_id=test_user2.id,
            league_id=test_league.id,
            total_score=100.0
        )
        db_session.add(entry2)
        test_entry.total_score = 150.0
        db_session.commit()

        # Refresh leaderboard
        response = client.post(f"/api/leaderboard/{test_league.id}/refresh")
        assert response.status_code == 200
        data = response.json()

        # Check prize calculation (2 entries * 100.0 entry fee)
        assert data["prize_pool"] == 200.0
        assert data["first_place_prize"] == 120.0  # 60%
        assert data["second_place_prize"] == 60.0  # 30%
        assert data["third_place_prize"] == 20.0   # 10%
