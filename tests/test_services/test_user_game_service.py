from datetime import date

from app.schemas.user import UserCreate
from app.schemas.user_game import UserGameLogCreate, UserGameLogUpdate
from app.services.user_game_service import (
    delete_user_game_log,
    get_user_game_log,
    get_user_top_games,
    get_user_total_hours,
    list_user_game_logs,
    log_user_game,
    update_user_game_log,
)
from app.services.user_service import create_user


class TestUserGameService:
    async def test_log_user_game_creates_game_and_genre(self, db_session):
        await create_user(
            UserCreate(
                username="daniel_service_log",
                email="daniel_service_log@example.com",
                password="secret",
            ),
            db_session,
        )

        payload = UserGameLogCreate(
            title="Expedition 33",
            hours_played=70,
            finished_at=date(2026, 3, 24),
            genre={
                "name": "JRPG",
                "description": "Japanese role-playing game",
            },
        )

        game_log = await log_user_game("daniel_service_log", payload, db_session)

        assert game_log is not None
        assert game_log.hours_played == 70
        assert game_log.finished_at == date(2026, 3, 24)
        assert game_log.game.title == "Expedition 33"
        assert game_log.game.genre is not None
        assert game_log.game.genre.name == "JRPG"

    async def test_log_user_game_updates_existing_log(self, db_session):
        await create_user(
            UserCreate(
                username="sam_service_update",
                email="sam_service_update@example.com",
                password="secret",
            ),
            db_session,
        )

        first_payload = UserGameLogCreate(title="Balatro", hours_played=12)
        second_payload = UserGameLogCreate(
            title="Balatro",
            hours_played=20,
            finished_at=date(2026, 3, 10),
        )

        first_log = await log_user_game("sam_service_update", first_payload, db_session)
        second_log = await log_user_game("sam_service_update", second_payload, db_session)

        assert first_log is not None
        assert second_log is not None
        assert first_log.id == second_log.id
        assert second_log.hours_played == 20
        assert second_log.finished_at == date(2026, 3, 10)

    async def test_list_user_game_logs(self, db_session):
        await create_user(
            UserCreate(
                username="maria_service_list",
                email="maria_service_list@example.com",
                password="secret",
            ),
            db_session,
        )

        await log_user_game("maria_service_list", UserGameLogCreate(title="Celeste Service", hours_played=15), db_session)
        await log_user_game("maria_service_list", UserGameLogCreate(title="Hades Service", hours_played=40), db_session)

        game_logs = await list_user_game_logs("maria_service_list", db_session)

        assert game_logs is not None
        assert len(game_logs) == 2
        assert [game_log.game.title for game_log in game_logs] == ["Celeste Service", "Hades Service"]

    async def test_get_user_game_log(self, db_session):
        await create_user(
            UserCreate(
                username="paula_service_get",
                email="paula_service_get@example.com",
                password="secret",
            ),
            db_session,
        )

        await log_user_game("paula_service_get", UserGameLogCreate(title="Inside Service", hours_played=6), db_session)

        user_exists, game_log = await get_user_game_log("paula_service_get", "Inside Service", db_session)

        assert user_exists
        assert game_log is not None
        assert game_log.game.title == "Inside Service"
        assert game_log.hours_played == 6

    async def test_get_user_game_log_returns_none_for_unknown_user(self, db_session):
        user_exists, game_log = await get_user_game_log("nonexistent_user", "Some Game", db_session)
        assert not user_exists
        assert game_log is None

    async def test_get_user_game_log_returns_none_when_game_not_logged(self, db_session):
        await create_user(
            UserCreate(
                username="user_without_log",
                email="user_without_log@example.com",
                password="secret",
            ),
            db_session,
        )

        user_exists, game_log = await get_user_game_log("user_without_log", "Unlogged Game", db_session)
        assert user_exists
        assert game_log is None

    async def test_list_user_game_logs_returns_none_for_unknown_user(self, db_session):
        game_logs = await list_user_game_logs("nonexistent_user", db_session)
        assert game_logs is None

    async def test_list_user_game_logs_returns_empty_for_user_with_no_games(self, db_session):
        await create_user(
            UserCreate(
                username="user_no_games",
                email="user_no_games@example.com",
                password="secret",
            ),
            db_session,
        )

        game_logs = await list_user_game_logs("user_no_games", db_session)
        assert game_logs is not None
        assert len(game_logs) == 0

    async def test_update_user_game_log(self, db_session):
        await create_user(
            UserCreate(
                username="user_update_log",
                email="user_update_log@example.com",
                password="secret",
            ),
            db_session,
        )
        await log_user_game(
            "user_update_log",
            UserGameLogCreate(title="Sea of Stars Update", hours_played=18),
            db_session,
        )

        user_exists, updated_log = await update_user_game_log(
            "user_update_log",
            "Sea of Stars Update",
            UserGameLogUpdate(hours_played=42, finished_at=date(2026, 3, 24)),
            db_session,
        )

        assert user_exists
        assert updated_log is not None
        assert updated_log.hours_played == 42
        assert updated_log.finished_at == date(2026, 3, 24)

    async def test_update_user_game_log_not_found_cases(self, db_session):
        user_exists, updated_log = await update_user_game_log(
            "missing_user",
            "Any Game",
            UserGameLogUpdate(hours_played=10),
            db_session,
        )
        assert not user_exists
        assert updated_log is None

        await create_user(
            UserCreate(
                username="user_update_not_found",
                email="user_update_not_found@example.com",
                password="secret",
            ),
            db_session,
        )
        user_exists, updated_log = await update_user_game_log(
            "user_update_not_found",
            "Missing Game",
            UserGameLogUpdate(hours_played=10),
            db_session,
        )
        assert user_exists
        assert updated_log is None

    async def test_delete_user_game_log(self, db_session):
        await create_user(
            UserCreate(
                username="user_delete_log",
                email="user_delete_log@example.com",
                password="secret",
            ),
            db_session,
        )
        await log_user_game(
            "user_delete_log",
            UserGameLogCreate(title="Delete Me", hours_played=11),
            db_session,
        )

        user_exists, deleted = await delete_user_game_log("user_delete_log", "Delete Me", db_session)
        assert user_exists
        assert deleted

        user_exists, game_log = await get_user_game_log("user_delete_log", "Delete Me", db_session)
        assert user_exists
        assert game_log is None

    async def test_delete_user_game_log_not_found_cases(self, db_session):
        user_exists, deleted = await delete_user_game_log("missing_user", "Any Game", db_session)
        assert not user_exists
        assert not deleted

        await create_user(
            UserCreate(
                username="user_delete_not_found",
                email="user_delete_not_found@example.com",
                password="secret",
            ),
            db_session,
        )
        user_exists, deleted = await delete_user_game_log("user_delete_not_found", "Missing Game", db_session)
        assert user_exists
        assert not deleted

    async def test_get_user_total_hours(self, db_session):
        await create_user(
            UserCreate(
                username="user_total_hours",
                email="user_total_hours@example.com",
                password="secret",
            ),
            db_session,
        )
        await log_user_game(
            "user_total_hours",
            UserGameLogCreate(title="Game One Total", hours_played=15),
            db_session,
        )
        await log_user_game(
            "user_total_hours",
            UserGameLogCreate(title="Game Two Total", hours_played=30),
            db_session,
        )

        user_exists, total_hours = await get_user_total_hours("user_total_hours", db_session)

        assert user_exists
        assert total_hours == 45

    async def test_get_user_total_hours_for_empty_and_unknown_user(self, db_session):
        await create_user(
            UserCreate(
                username="user_zero_hours",
                email="user_zero_hours@example.com",
                password="secret",
            ),
            db_session,
        )

        user_exists, total_hours = await get_user_total_hours("user_zero_hours", db_session)
        assert user_exists
        assert total_hours == 0

        user_exists, total_hours = await get_user_total_hours("missing_user", db_session)
        assert not user_exists
        assert total_hours is None

    async def test_get_user_top_games(self, db_session):
        await create_user(
            UserCreate(
                username="user_top_games",
                email="user_top_games@example.com",
                password="secret",
            ),
            db_session,
        )
        await log_user_game(
            "user_top_games",
            UserGameLogCreate(title="Third Place", hours_played=10),
            db_session,
        )
        await log_user_game(
            "user_top_games",
            UserGameLogCreate(title="First Place", hours_played=80, finished_at=date(2026, 3, 21)),
            db_session,
        )
        await log_user_game(
            "user_top_games",
            UserGameLogCreate(title="Second Place", hours_played=40),
            db_session,
        )

        user_exists, top_games = await get_user_top_games("user_top_games", db_session, limit=2)

        assert user_exists
        assert top_games is not None
        assert len(top_games) == 2
        assert [game_log.game.title for game_log in top_games] == ["First Place", "Second Place"]

    async def test_get_user_top_games_for_empty_and_unknown_user(self, db_session):
        await create_user(
            UserCreate(
                username="user_no_top_games",
                email="user_no_top_games@example.com",
                password="secret",
            ),
            db_session,
        )

        user_exists, top_games = await get_user_top_games("user_no_top_games", db_session)
        assert user_exists
        assert top_games == []

        user_exists, top_games = await get_user_top_games("missing_user", db_session)
        assert not user_exists
        assert top_games is None
