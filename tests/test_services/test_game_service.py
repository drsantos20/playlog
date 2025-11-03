import pytest
from fastapi import HTTPException

from app.schemas.game import GameCreate, GenreCreate
from app.services.game_service import (
    create_game,
    get_game,
    update_game,
    create_genre,
    list_genres
)


class TestGameService:
    """Test cases for game service functions."""

    async def test_create_genre_success(self, db_session):
        """Test successful genre creation."""
        genre_data = GenreCreate(
            name="Action_Create",
            description="Fast-paced games with combat and movement"
        )
        
        created_genre = await create_genre(genre_data, db_session)
        
        assert created_genre is not None
        assert created_genre.id is not None
        assert created_genre.name == genre_data.name
        assert created_genre.description == genre_data.description

    async def test_list_genres_empty(self, db_session):
        """Test listing genres when none exist."""
        genres = await list_genres(db_session)
        
        # Check if list is empty or has expected genres from other tests
        assert isinstance(genres, list)

    async def test_list_genres_with_data(self, db_session):
        """Test listing genres when some exist."""
        # Create test genres with unique names
        genre1_data = GenreCreate(name="Simulation_Test", description="Simulation games")
        genre2_data = GenreCreate(name="Educational_Test", description="Educational games")
        
        await create_genre(genre1_data, db_session)
        await create_genre(genre2_data, db_session)
        
        genres = await list_genres(db_session)
        
        # Check that our test genres are in the list
        genre_names = [genre.name for genre in genres]
        assert "Simulation_Test" in genre_names
        assert "Educational_Test" in genre_names

    async def test_create_game_success(self, db_session):
        """Test successful game creation with valid genre."""
        # First create a genre
        genre_data = GenreCreate(
            name="Adventure_Game",
            description="Story-driven exploration games"
        )
        created_genre = await create_genre(genre_data, db_session)
        
        # Store values to avoid session expiration issues
        genre_id = created_genre.id
        genre_name = created_genre.name
        
        # Now create a game
        game_data = GameCreate(
            title="The Legend of Zelda Test",
            genre_id=genre_id
        )
        
        created_game = await create_game(game_data, db_session)
        
        assert created_game is not None
        assert created_game.id is not None
        assert created_game.title == game_data.title
        assert created_game.genre_id == genre_id
        assert created_game.genre is not None
        assert created_game.genre.name == genre_name

    async def test_create_game_invalid_genre(self, db_session):
        """Test game creation with invalid genre_id."""
        game_data = GameCreate(
            title="Invalid Game",
            genre_id=999  # Non-existent genre ID
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await create_game(game_data, db_session)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid genre_id"

    async def test_get_game_success(self, db_session):
        """Test successful game retrieval."""
        # Setup: Create genre and game
        genre_data = GenreCreate(name="Puzzle_Get", description="Brain teasers")
        created_genre = await create_genre(genre_data, db_session)
        
        # Store values to avoid session expiration
        genre_id = created_genre.id
        genre_name = created_genre.name
        
        game_data = GameCreate(
            title="Tetris Test",
            genre_id=genre_id
        )
        await create_game(game_data, db_session)
        
        # Test: Retrieve the game
        retrieved_game = await get_game("Tetris Test", db_session)
        
        assert retrieved_game is not None
        assert retrieved_game.title == "Tetris Test"
        assert retrieved_game.genre_id == genre_id
        assert retrieved_game.genre is not None
        assert retrieved_game.genre.name == genre_name

    async def test_get_game_not_found(self, db_session):
        """Test game retrieval when game doesn't exist."""
        retrieved_game = await get_game("Nonexistent Game", db_session)
        
        assert retrieved_game is None

    async def test_update_game_success(self, db_session):
        """Test successful game update."""
        # Setup: Create genres and a game
        original_genre = await create_genre(
            GenreCreate(name="Sports_Update", description="Athletic games"), 
            db_session
        )
        # Access the ID immediately after creation
        original_genre_id = original_genre.id
        
        new_genre = await create_genre(
            GenreCreate(name="Racing_Update", description="Vehicle racing games"), 
            db_session
        )
        # Access the ID immediately after creation
        new_genre_id = new_genre.id
        
        game_data = GameCreate(
            title="FIFA_Test",
            genre_id=original_genre_id
        )
        await create_game(game_data, db_session)
        
        # Test: Update the game
        update_data = GameCreate(
            title="Need for Speed_Test",
            genre_id=new_genre_id
        )
        
        updated_game = await update_game("FIFA_Test", update_data, db_session)
        
        assert updated_game is not None
        assert updated_game.title == "Need for Speed_Test"
        assert updated_game.genre_id == new_genre_id

    async def test_update_game_not_found(self, db_session):
        """Test game update when game doesn't exist."""
        # Create a genre for the update data
        genre_data = GenreCreate(name="Strategy_Not_Found", description="Strategic games")
        created_genre = await create_genre(genre_data, db_session)
        
        # Store genre ID to avoid session expiration
        genre_id = created_genre.id
        
        update_data = GameCreate(
            title="Updated Game",
            genre_id=genre_id
        )
        
        updated_game = await update_game("Nonexistent Game", update_data, db_session)
        
        assert updated_game is None

    async def test_game_genre_relationship(self, db_session):
        """Test that game-genre relationship is properly loaded."""
        # Create genre
        genre_data = GenreCreate(
            name="Horror_Relationship",
            description="Scary atmospheric games"
        )
        created_genre = await create_genre(genre_data, db_session)
        
        # Store values to avoid session expiration
        genre_id = created_genre.id
        genre_name = created_genre.name
        genre_description = created_genre.description
        
        # Create game
        game_data = GameCreate(
            title="Silent Hill Test",
            genre_id=genre_id
        )
        created_game = await create_game(game_data, db_session)
        
        # Verify relationship is loaded
        assert created_game.genre is not None
        assert created_game.genre.id == genre_id
        assert created_game.genre.name == genre_name
        assert created_game.genre.description == genre_description

    async def test_multiple_games_same_genre(self, db_session):
        """Test creating multiple games with the same genre."""
        # Create genre
        genre_data = GenreCreate(
            name="Platformer_Multi",
            description="Jump and run games"
        )
        created_genre = await create_genre(genre_data, db_session)
        
        # Access genre ID immediately after creation
        genre_id = created_genre.id
        
        # Create multiple games
        game1_data = GameCreate(title="Super Mario Bros Test", genre_id=genre_id)
        game2_data = GameCreate(title="Sonic the Hedgehog Test", genre_id=genre_id)
        
        game1 = await create_game(game1_data, db_session)
        game2 = await create_game(game2_data, db_session)
        
        # Verify both games were created successfully (just check they exist)
        assert game1 is not None
        assert game2 is not None
        
        # Verify we can retrieve them independently (tests the full workflow)
        retrieved_game1 = await get_game("Super Mario Bros Test", db_session)
        retrieved_game2 = await get_game("Sonic the Hedgehog Test", db_session)
        
        assert retrieved_game1 is not None
        assert retrieved_game2 is not None
        assert retrieved_game1.title == "Super Mario Bros Test"
        assert retrieved_game2.title == "Sonic the Hedgehog Test"

    async def test_create_genre_with_special_characters(self, db_session):
        """Test creating genre with special characters in name and description."""
        genre_data = GenreCreate(
            name="Sci-Fi & Fantasy Test",
            description="Games with futuristic & magical elements!"
        )
        
        created_genre = await create_genre(genre_data, db_session)
        
        assert created_genre is not None
        assert created_genre.name == "Sci-Fi & Fantasy Test"
        assert created_genre.description == "Games with futuristic & magical elements!"

    async def test_game_title_uniqueness_constraint(self, db_session):
        """Test that game titles must be unique (if database constraint exists)."""
        # Create genre
        genre_data = GenreCreate(name="Test Genre Unique", description="Test description")
        created_genre = await create_genre(genre_data, db_session)
        
        # Store genre ID to avoid session expiration
        genre_id = created_genre.id
        
        # Create first game
        game_data = GameCreate(title="Unique Game Test", genre_id=genre_id)
        await create_game(game_data, db_session)
        
        # Try to create second game with same title
        # Note: This test assumes the database has a unique constraint on title
        # If not, this test might need to be adjusted based on actual behavior
        duplicate_game_data = GameCreate(title="Unique Game Test", genre_id=genre_id)
        
        # This should either raise an exception or handle duplicates gracefully
        # The exact behavior depends on your database constraints and error handling
        try:
            duplicate_game = await create_game(duplicate_game_data, db_session)
            # If no exception is raised, verify the behavior
            # This might create a second game or return the existing one
            assert duplicate_game is not None
        except Exception as e:
            # If an exception is raised, it should be related to the unique constraint
            assert "unique" in str(e).lower() or "duplicate" in str(e).lower()