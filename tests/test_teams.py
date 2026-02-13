import pytest


class TestCreateTeam:
    def test_create_team_success(self, client, test_entry, auth_headers):
        """Test creating a valid team"""
        response = client.post(
            "/api/teams",
            json={
                "entry_id": test_entry.id,
                "picks": [
                    {"player_id": 1, "player_category": 1},  # Scheffler
                    {"player_id": 2, "player_category": 1},  # Rory
                    {"player_id": 9, "player_category": 2},  # Hatton
                    {"player_id": 16, "player_category": 4}, # Oosthuizen
                    {"player_id": 17, "player_category": 5}, # Theegala
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["entry_id"] == test_entry.id
        assert data["is_valid"] is True
        assert data["total_category_points"] == 13
        assert len(data["picks"]) == 5

    def test_create_team_invalid_sum(self, client, test_entry, auth_headers):
        """Test creating team with invalid category sum"""
        response = client.post(
            "/api/teams",
            json={
                "entry_id": test_entry.id,
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 5, "player_category": 2},
                    {"player_id": 6, "player_category": 2},
                    {"player_id": 7, "player_category": 2},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error
        assert "at least 13" in str(response.json()).lower()

    def test_create_team_duplicate_player(self, client, test_entry, auth_headers):
        """Test creating team with duplicate player"""
        response = client.post(
            "/api/teams",
            json={
                "entry_id": test_entry.id,
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 1, "player_category": 1},  # Duplicate
                    {"player_id": 9, "player_category": 2},
                    {"player_id": 16, "player_category": 4},
                    {"player_id": 17, "player_category": 5},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 422
        assert "same player" in str(response.json()).lower()

    def test_create_team_wrong_number_of_picks(self, client, test_entry, auth_headers):
        """Test creating team with wrong number of players"""
        response = client.post(
            "/api/teams",
            json={
                "entry_id": test_entry.id,
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 9, "player_category": 2},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 422
        response_text = str(response.json()).lower()
        assert ("at least 5" in response_text or "5 items" in response_text)

    def test_create_team_already_exists(self, client, test_team, auth_headers):
        """Test creating team when one already exists"""
        response = client.post(
            "/api/teams",
            json={
                "entry_id": test_team.entry_id,
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 9, "player_category": 2},
                    {"player_id": 16, "player_category": 4},
                    {"player_id": 17, "player_category": 5},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_team_invalid_entry(self, client, auth_headers):
        """Test creating team for non-existent entry"""
        response = client.post(
            "/api/teams",
            json={
                "entry_id": 99999,
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 9, "player_category": 2},
                    {"player_id": 16, "player_category": 4},
                    {"player_id": 17, "player_category": 5},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_create_team_not_entry_owner(self, client, test_entry, test_user2):
        """Test creating team for someone else's entry"""
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
            "/api/teams",
            json={
                "entry_id": test_entry.id,
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 9, "player_category": 2},
                    {"player_id": 16, "player_category": 4},
                    {"player_id": 17, "player_category": 5},
                ]
            },
            headers=headers
        )
        assert response.status_code == 403


class TestGetTeam:
    def test_get_team_by_entry(self, client, test_team, auth_headers):
        """Test getting team by entry ID"""
        response = client.get(
            f"/api/teams/entry/{test_team.entry_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_team.id
        assert len(data["picks"]) == 5

    def test_get_team_by_id(self, client, test_team):
        """Test getting team by team ID"""
        response = client.get(f"/api/teams/{test_team.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_team.id

    def test_get_team_not_found(self, client, auth_headers):
        """Test getting non-existent team"""
        response = client.get(
            "/api/teams/entry/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestUpdateTeam:
    def test_update_team_success(self, client, test_team, auth_headers):
        """Test updating team picks"""
        response = client.put(
            f"/api/teams/{test_team.id}",
            json={
                "picks": [
                    {"player_id": 3, "player_category": 1},  # Different picks
                    {"player_id": 4, "player_category": 1},
                    {"player_id": 10, "player_category": 3},
                    {"player_id": 16, "player_category": 4},
                    {"player_id": 17, "player_category": 5},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_category_points"] == 14
        assert data["is_valid"] is True

    def test_update_team_invalid_sum(self, client, test_team, auth_headers):
        """Test updating team with invalid category sum"""
        response = client.put(
            f"/api/teams/{test_team.id}",
            json={
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 5, "player_category": 2},
                    {"player_id": 6, "player_category": 2},
                    {"player_id": 7, "player_category": 2},
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_update_team_not_owner(self, client, test_team, test_user2):
        """Test updating team by non-owner"""
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

        response = client.put(
            f"/api/teams/{test_team.id}",
            json={
                "picks": [
                    {"player_id": 1, "player_category": 1},
                    {"player_id": 2, "player_category": 1},
                    {"player_id": 9, "player_category": 2},
                    {"player_id": 16, "player_category": 4},
                    {"player_id": 17, "player_category": 5},
                ]
            },
            headers=headers
        )
        assert response.status_code == 403


class TestDeleteTeam:
    def test_delete_team_success(self, client, test_team, auth_headers):
        """Test deleting a team"""
        response = client.delete(
            f"/api/teams/{test_team.id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/teams/{test_team.id}")
        assert get_response.status_code == 404

    def test_delete_team_not_owner(self, client, test_team, test_user2):
        """Test deleting team by non-owner"""
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
            f"/api/teams/{test_team.id}",
            headers=headers
        )
        assert response.status_code == 403

    def test_delete_team_not_found(self, client, auth_headers):
        """Test deleting non-existent team"""
        response = client.delete("/api/teams/99999", headers=auth_headers)
        assert response.status_code == 404
