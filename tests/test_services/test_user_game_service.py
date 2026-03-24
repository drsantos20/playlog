from datetime import date

from app.schemas.user import UserCreate
from app.schemas.user_game import UserGameLogCreate
from app.services.user_game_service import (
    get_user_game_log,
    list_user_game_logs,
    log_user_game,
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

        game_log = await get_user_game_log("paula_service_get", "Inside Service", db_session)

        assert game_log is not None
        assert game_log.game.title == "Inside Service"
        assert game_log.hours_played == 6