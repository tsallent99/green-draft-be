import pytest


class TestGetTournaments:
    def test_get_all_tournaments(self, client):
        """Test getting all tournaments"""
        response = client.get("/api/tournaments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check first tournament structure
        tournament = data[0]
        assert "id" in tournament
        assert "name" in tournament
        assert "location" in tournament
        assert "start_date" in tournament
        assert "end_date" in tournament
        assert "status" in tournament

    def test_tournaments_contain_masters(self, client):
        """Test that tournaments include Masters"""
        response = client.get("/api/tournaments")
        data = response.json()

        masters = next((t for t in data if "Masters" in t["name"]), None)
        assert masters is not None
        assert "Augusta" in masters["location"]


class TestGetTournamentById:
    def test_get_tournament_success(self, client):
        """Test getting a specific tournament"""
        response = client.get("/api/tournaments/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data
        assert "status" in data

    def test_get_tournament_not_found(self, client):
        """Test getting non-existent tournament"""
        response = client.get("/api/tournaments/99999")
        assert response.status_code == 404
