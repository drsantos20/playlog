

from app.core.security import verify_password
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user


def test_create_user(client):
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/users/create", json=user_data)
    assert response.status_code == 200

    response_data = response.json()
    
    assert "id" in response_data
    assert response_data["username"] == user_data["username"]
    assert response_data["email"] == user_data["email"]
    assert response_data["is_active"] == True


async def test_get_user(client, db_session):
    user_data = UserCreate(
        username="createuser",
        email="createuser@example.com",
        password="testpassword"
    )

    await create_user(user_data, db_session)
    response = client.get(f"/api/v1/users/user/{user_data.username}")
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    response_data = response.json()

    assert "id" in response_data
    assert response_data["username"] == user_data.username
    assert response_data["email"] == user_data.email
    assert response_data["is_active"] is True


async def test_not_found_user(client):
    response = client.get("/api/v1/users/user/nonexistent")

    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


async def test_update_user(client, db_session):
    user = UserCreate(
        username="usertoupdate",
        email="usertoupdate@example.com",
        password="testpassword"
    )

    await create_user(user, db_session)

    # Login to get token
    login_response = client.post(
        "/api/v1/users/login",
        json={"username": user.username, "password": "testpassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    user_data = {
        "password": "updatepassword"
    }

    # Update with bearer token
    response = client.put(
        f"/api/v1/users/update/{user.username}",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    
    updated_user = await get_user(user.username, db_session)

    assert updated_user.hashed_password != user.password
    assert updated_user.hashed_password != user_data["password"]
    assert verify_password(user_data["password"], updated_user.hashed_password)


async def test_login_success(client, db_session):
    user = UserCreate(
        username="loginuser",
        email="loginuser@example.com",
        password="testpassword"
    )

    await create_user(user, db_session)

    response = client.post(
        "/api/v1/users/login",
        json={"username": "loginuser", "password": "testpassword"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert "user" in response_data
    assert response_data["user"]["username"] == "loginuser"


async def test_login_invalid_password(client, db_session):
    user = UserCreate(
        username="loginuser2",
        email="loginuser2@example.com",
        password="testpassword"
    )

    await create_user(user, db_session)

    response = client.post(
        "/api/v1/users/login",
        json={"username": "loginuser2", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


async def test_login_user_not_found(client):
    response = client.post(
        "/api/v1/users/login",
        json={"username": "nonexistent", "password": "password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


async def test_get_current_user(client, db_session):
    user = UserCreate(
        username="meuser",
        email="meuser@example.com",
        password="testpassword"
    )

    await create_user(user, db_session)

    # Login to get token
    login_response = client.post(
        "/api/v1/users/login",
        json={"username": "meuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["username"] == "meuser"
    assert response_data["email"] == "meuser@example.com"


async def test_get_current_user_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 403
