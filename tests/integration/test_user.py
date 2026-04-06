

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

    user_data = {
        "password": "updatepassword"
    }

    response = client.put(f"/api/v1/users/update/{user.username}", json=user_data)

    assert response.status_code == 200
    
    updated_user = await get_user(user.username, db_session)

    assert updated_user.hashed_password != user.password
    assert updated_user.hashed_password != user_data["password"]
    assert verify_password(user_data["password"], updated_user.hashed_password)
