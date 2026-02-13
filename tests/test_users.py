import pytest


class TestUserRegistration:
    def test_register_user_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/users/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "full_name": "New User",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/users/register",
            json={
                "email": test_user.email,
                "username": "differentuser",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        response = client.post(
            "/api/users/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()


class TestUserLogin:
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/users/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/users/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401


class TestGetCurrentUser:
    def test_get_current_user_success(self, client, test_user, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/users/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestGetUser:
    def test_get_user_by_id_success(self, client, test_user):
        """Test getting user by ID"""
        response = client.get(f"/api/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    def test_get_user_not_found(self, client):
        """Test getting non-existent user"""
        response = client.get("/api/users/99999")
        assert response.status_code == 404
