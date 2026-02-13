import pytest


class TestGetPlayers:
    def test_get_all_players(self, client):
        """Test getting all players"""
        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check first player structure
        player = data[0]
        assert "id" in player
        assert "name" in player
        assert "country" in player
        assert "world_ranking" in player

    def test_players_contain_scheffler(self, client):
        """Test that players include Scottie Scheffler"""
        response = client.get("/api/players")
        data = response.json()

        scheffler = next((p for p in data if "Scheffler" in p["name"]), None)
        assert scheffler is not None
        assert scheffler["country"] == "USA"


class TestGetPlayerById:
    def test_get_player_success(self, client):
        """Test getting a specific player"""
        response = client.get("/api/players/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data
        assert "country" in data

    def test_get_player_not_found(self, client):
        """Test getting non-existent player"""
        response = client.get("/api/players/99999")
        assert response.status_code == 404


class TestGetPlayersWithOdds:
    def test_get_players_with_odds_all_categories(self, client):
        """Test getting all players with odds for a tournament"""
        response = client.get("/api/players/odds/1")  # Masters Tournament
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure
        player_odds = data[0]
        assert "player_id" in player_odds
        assert "player_name" in player_odds
        assert "category" in player_odds
        assert "odds" in player_odds
        assert "country" in player_odds
        assert "world_ranking" in player_odds

    def test_get_players_with_odds_category_1(self, client):
        """Test getting category 1 players"""
        response = client.get("/api/players/odds/1?category=1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # All should be category 1
        for player in data:
            assert player["category"] == 1

    def test_get_players_with_odds_category_5(self, client):
        """Test getting category 5 players"""
        response = client.get("/api/players/odds/1?category=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # All should be category 5
        for player in data:
            assert player["category"] == 5

    def test_get_players_with_odds_invalid_tournament(self, client):
        """Test getting odds for non-existent tournament"""
        response = client.get("/api/players/odds/99999")
        assert response.status_code == 404

    def test_category_ordering(self, client):
        """Test that categories are properly assigned"""
        response = client.get("/api/players/odds/1")
        data = response.json()

        # Get players from different categories
        cat1_players = [p for p in data if p["category"] == 1]
        cat5_players = [p for p in data if p["category"] == 5]

        assert len(cat1_players) > 0
        assert len(cat5_players) > 0

        # Category 1 should have better odds (lower numbers)
        if cat1_players and cat5_players:
            assert cat1_players[0]["odds"] < cat5_players[0]["odds"]
