"""
Authentication Unit and Integration Tests
Tests registration, login, JWT issuance, profile retrieval, password update, and logout.
"""
def test_register_success(client):
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "SecurePassword123!"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Doe"


def test_register_duplicate_email(client, test_user):
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Duplicate User",
            "email": test_user.email,
            "password": "Password999!"
        }
    )
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_login_success(client, test_user):
    res = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "Password123!"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["id"] == str(test_user.id)


def test_login_invalid_password(client, test_user):
    res = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "WrongPassword!"
        }
    )
    assert res.status_code == 401


def test_get_me_authenticated(client, test_user, test_user_token):
    res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert res.status_code == 200
    assert res.json()["email"] == test_user.email


def test_get_me_unauthorized(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_change_password(client, test_user, test_user_token):
    res = client.post(
        "/api/auth/change-password",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "current_password": "Password123!",
            "new_password": "BrandNewPassword789!"
        }
    )
    assert res.status_code == 200
    assert "successfully updated" in res.json()["message"]

    # Verify login with new password
    login_res = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "BrandNewPassword789!"}
    )
    assert login_res.status_code == 200


def test_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert "Successfully logged out" in res.json()["message"]
