import pytest


class TestGetMyEntries:
    def test_get_my_entries_success(self, client, test_entry, auth_headers):
        """Test getting current user's entries"""
        response = client.get("/api/entries/my-entries", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_entry.id

    def test_get_my_entries_empty(self, client, auth_headers):
        """Test getting entries when user has none"""
        response = client.get("/api/entries/my-entries", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_my_entries_no_auth(self, client):
        """Test getting entries without authentication"""
        response = client.get("/api/entries/my-entries")
        assert response.status_code == 403


class TestGetEntry:
    def test_get_entry_success(self, client, test_entry, auth_headers):
        """Test getting a specific entry"""
        response = client.get(f"/api/entries/{test_entry.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_entry.id
        assert data["user_id"] == test_entry.user_id
        assert data["league_id"] == test_entry.league_id

    def test_get_entry_not_owner(self, client, test_entry, test_user2):
        """Test getting entry by non-owner"""
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

        response = client.get(f"/api/entries/{test_entry.id}", headers=headers)
        assert response.status_code == 403

    def test_get_entry_not_found(self, client, auth_headers):
        """Test getting non-existent entry"""
        response = client.get("/api/entries/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateEntry:
    def test_update_payment_status(self, client, test_entry, auth_headers):
        """Test updating entry payment status"""
        response = client.patch(
            f"/api/entries/{test_entry.id}",
            json={"payment_status": "paid"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_status"] == "paid"

    def test_update_total_score(self, client, test_entry, auth_headers):
        """Test updating entry total score"""
        response = client.patch(
            f"/api/entries/{test_entry.id}",
            json={"total_score": 150.5},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_score"] == 150.5

    def test_update_entry_not_owner(self, client, test_entry, test_user2):
        """Test updating entry by non-owner"""
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

        response = client.patch(
            f"/api/entries/{test_entry.id}",
            json={"payment_status": "paid"},
            headers=headers
        )
        assert response.status_code == 403

    def test_update_entry_not_found(self, client, auth_headers):
        """Test updating non-existent entry"""
        response = client.patch(
            "/api/entries/99999",
            json={"payment_status": "paid"},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestDeleteEntry:
    def test_delete_entry_success(self, client, test_entry, auth_headers):
        """Test deleting an entry (leaving league)"""
        response = client.delete(
            f"/api/entries/{test_entry.id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/entries/{test_entry.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_entry_after_payment(self, client, test_entry, auth_headers, db_session):
        """Test deleting entry after payment is made"""
        # Update payment status to paid
        test_entry.payment_status = "paid"
        db_session.commit()

        response = client.delete(
            f"/api/entries/{test_entry.id}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "after payment" in response.json()["detail"].lower()

    def test_delete_entry_not_owner(self, client, test_entry, test_user2):
        """Test deleting entry by non-owner"""
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
            f"/api/entries/{test_entry.id}",
            headers=headers
        )
        assert response.status_code == 403

    def test_delete_entry_not_found(self, client, auth_headers):
        """Test deleting non-existent entry"""
        response = client.delete("/api/entries/99999", headers=auth_headers)
        assert response.status_code == 404
