def test_log_game_for_user_creates_missing_game_and_genre(client):
    client.post(
        "/api/v1/users/create",
        json={
            "username": "daniel_integration_log",
            "email": "daniel_integration_log@example.com",
            "password": "secret",
        },
    )

    response = client.post(
        "/api/v1/users/daniel_integration_log/games/log",
        json={
            "title": "Expedition 33 Integration",
            "hours_played": 70,
            "finished_at": "2026-03-24",
            "genre": {
                "name": "JRPG Integration",
                "description": "Japanese role-playing game",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["hours_played"] == 70
    assert payload["finished_at"] == "2026-03-24"
    assert payload["game"]["title"] == "Expedition 33 Integration"
    assert payload["game"]["genre"]["name"] == "JRPG Integration"


def test_log_game_for_user_updates_existing_entry(client):
    client.post(
        "/api/v1/users/create",
        json={
            "username": "alice_integration_update",
            "email": "alice_integration_update@example.com",
            "password": "secret",
        },
    )

    client.post(
        "/api/v1/users/alice_integration_update/games/log",
        json={
            "title": "Returnal Integration",
            "hours_played": 25,
        },
    )

    response = client.post(
        "/api/v1/users/alice_integration_update/games/log",
        json={
            "title": "Returnal Integration",
            "hours_played": 32,
            "finished_at": "2026-03-20",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["hours_played"] == 32
    assert payload["finished_at"] == "2026-03-20"


def test_list_logged_games_for_user(client):
    client.post(
        "/api/v1/users/create",
        json={
            "username": "maria_integration_list",
            "email": "maria_integration_list@example.com",
            "password": "secret",
        },
    )

    client.post("/api/v1/users/maria_integration_list/games/log", json={"title": "Celeste Integration", "hours_played": 15})
    client.post("/api/v1/users/maria_integration_list/games/log", json={"title": "Hades Integration", "hours_played": 40})

    response = client.get("/api/v1/users/maria_integration_list/games")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert [item["game"]["title"] for item in payload] == ["Celeste Integration", "Hades Integration"]


def test_get_logged_game_for_user(client):
    client.post(
        "/api/v1/users/create",
        json={
            "username": "joao_integration_get",
            "email": "joao_integration_get@example.com",
            "password": "secret",
        },
    )

    client.post(
        "/api/v1/users/joao_integration_get/games/log",
        json={
            "title": "Metaphor ReFantazio Integration",
            "hours_played": 55,
            "finished_at": "2026-03-18",
        },
    )

    response = client.get("/api/v1/users/joao_integration_get/games/Metaphor ReFantazio Integration")

    assert response.status_code == 200
    payload = response.json()
    assert payload["game"]["title"] == "Metaphor ReFantazio Integration"
    assert payload["hours_played"] == 55
    assert payload["finished_at"] == "2026-03-18"


def test_log_game_for_unknown_user_returns_not_found(client):
    response = client.post(
        "/api/v1/users/ghost/games/log",
        json={
            "title": "Unknown Game",
            "hours_played": 10,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}