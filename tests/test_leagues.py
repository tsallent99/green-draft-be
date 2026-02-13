import pytest


class TestCreateLeague:
    def test_create_league_success(self, client, auth_headers):
        """Test creating a league successfully"""
        response = client.post(
            "/api/leagues",
            json={
                "name": "My Fantasy League",
                "tournament_id": 1,
                "entry_fee": 50.0,
                "max_participants": 20
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Fantasy League"
        assert data["tournament_id"] == 1
        assert data["entry_fee"] == 50.0
        assert data["max_participants"] == 20
        assert "invitation_code" in data
        assert len(data["invitation_code"]) == 8
        assert data["status"] == "open"

    def test_create_league_invalid_tournament(self, client, auth_headers):
        """Test creating league with invalid tournament"""
        response = client.post(
            "/api/leagues",
            json={
                "name": "Invalid League",
                "tournament_id": 99999,
                "entry_fee": 50.0,
                "max_participants": 20
            },
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_create_league_no_auth(self, client):
        """Test creating league without authentication"""
        response = client.post(
            "/api/leagues",
            json={
                "name": "My League",
                "tournament_id": 1,
                "entry_fee": 50.0
            }
        )
        assert response.status_code == 403


class TestGetLeagues:
    def test_get_user_leagues(self, client, test_league, auth_headers):
        """Test getting leagues for current user"""
        response = client.get("/api/leagues", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["id"] == test_league.id

    def test_get_leagues_empty(self, client, auth_headers):
        """Test getting leagues when user has none"""
        response = client.get("/api/leagues", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_leagues_no_auth(self, client):
        """Test getting leagues without authentication"""
        response = client.get("/api/leagues")
        assert response.status_code == 403


class TestGetLeagueById:
    def test_get_league_success(self, client, test_league):
        """Test getting a specific league"""
        response = client.get(f"/api/leagues/{test_league.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_league.id
        assert data["name"] == test_league.name

    def test_get_league_not_found(self, client):
        """Test getting non-existent league"""
        response = client.get("/api/leagues/99999")
        assert response.status_code == 404


class TestJoinLeague:
    def test_join_league_success(self, client, test_league, test_user2):
        """Test joining a league with invitation code"""
        # Login as second user
        login_response = client.post(
            "/api/users/login",
            json={
                "email": test_user2.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/leagues/join",
            json={"invitation_code": test_league.invitation_code},
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user2.id
        assert data["league_id"] == test_league.id
        assert data["payment_status"] == "pending"

    def test_join_league_invalid_code(self, client, auth_headers):
        """Test joining league with invalid code"""
        response = client.post(
            "/api/leagues/join",
            json={"invitation_code": "INVALID"},
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_join_league_already_joined(self, client, test_league, test_entry, auth_headers):
        """Test joining a league already joined"""
        response = client.post(
            "/api/leagues/join",
            json={"invitation_code": test_league.invitation_code},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already joined" in response.json()["detail"].lower()

    def test_join_league_no_auth(self, client, test_league):
        """Test joining league without authentication"""
        response = client.post(
            "/api/leagues/join",
            json={"invitation_code": test_league.invitation_code}
        )
        assert response.status_code == 403


class TestGetLeagueEntries:
    def test_get_league_entries(self, client, test_league, test_entry):
        """Test getting all entries for a league"""
        response = client.get(f"/api/leagues/{test_league.id}/entries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_entry.id

    def test_get_league_entries_not_found(self, client):
        """Test getting entries for non-existent league"""
        response = client.get("/api/leagues/99999/entries")
        assert response.status_code == 404


class TestDeleteLeague:
    def test_delete_league_success(self, client, test_league, auth_headers):
        """Test deleting a league as creator"""
        response = client.delete(
            f"/api/leagues/{test_league.id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/leagues/{test_league.id}")
        assert get_response.status_code == 404

    def test_delete_league_not_creator(self, client, test_league, test_user2):
        """Test deleting league by non-creator"""
        # Login as second user
        login_response = client.post(
            "/api/users/login",
            json={
                "email": test_user2.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(
            f"/api/leagues/{test_league.id}",
            headers=headers
        )
        assert response.status_code == 403

    def test_delete_league_not_found(self, client, auth_headers):
        """Test deleting non-existent league"""
        response = client.delete("/api/leagues/99999", headers=auth_headers)
        assert response.status_code == 404
