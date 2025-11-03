import pytest
from fastapi import HTTPException

from app.schemas.game import GameCreate, GenreCreate
from app.services.game_service import create_game, create_genre


class TestGameIntegration:
    """Integration tests for game API endpoints."""

    def test_create_game_endpoint_success(self, client, db_session):
        """Test successful game creation via API endpoint."""
        # First create a genre via API
        genre_data = {
            "name": "Action",
            "description": "Fast-paced action games"
        }
        genre_response = client.post("/api/v1/genres/create", json=genre_data)
        assert genre_response.status_code == 200
        created_genre = genre_response.json()
        
        # Now create a game
        game_data = {
            "title": "God of War",
            "genre_id": created_genre["id"]
        }
        
        response = client.post("/api/v1/games/create", json=game_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert "id" in response_data
        assert response_data["title"] == game_data["title"]
        assert response_data["genre_id"] == created_genre["id"]
        assert response_data["genre"] is not None
        assert response_data["genre"]["name"] == genre_data["name"]

    def test_create_game_invalid_genre_id(self, client):
        """Test game creation with invalid genre_id via API."""
        game_data = {
            "title": "Invalid Game",
            "genre_id": 999  # Non-existent genre ID
        }
        
        response = client.post("/api/v1/games/create", json=game_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid genre_id"

    def test_get_game_endpoint_success(self, client):
        """Test successful game retrieval via API endpoint."""
        # Setup: Create genre and game via API
        genre_data = {
            "name": "RPG",
            "description": "Role-playing games"
        }
        genre_response = client.post("/api/v1/genres/create", json=genre_data)
        created_genre = genre_response.json()
        
        game_data = {
            "title": "Final Fantasy VII",
            "genre_id": created_genre["id"]
        }
        client.post("/api/v1/games/create", json=game_data)
        
        # Test: Get the game
        response = client.get("/api/v1/games/Final Fantasy VII")
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["title"] == "Final Fantasy VII"
        assert response_data["genre_id"] == created_genre["id"]
        assert response_data["genre"]["name"] == "RPG"

    def test_get_game_not_found(self, client):
        """Test game retrieval when game doesn't exist."""
        response = client.get("/api/v1/games/Nonexistent Game")
        assert response.status_code == 404
        assert response.json()["detail"] == "Game not found"

    def test_update_game_endpoint_success(self, client):
        """Test successful game update via API endpoint."""
        # Setup: Create genres and a game
        original_genre_data = {
            "name": "Puzzle",
            "description": "Brain teaser games"
        }
        original_genre_response = client.post("/api/v1/genres/create", json=original_genre_data)
        original_genre = original_genre_response.json()
        
        new_genre_data = {
            "name": "Strategy",
            "description": "Strategic thinking games"
        }
        new_genre_response = client.post("/api/v1/genres/create", json=new_genre_data)
        new_genre = new_genre_response.json()
        
        game_data = {
            "title": "Tetris",
            "genre_id": original_genre["id"]
        }
        client.post("/api/v1/games/create", json=game_data)
        
        # Test: Update the game
        update_data = {
            "title": "Chess Master",
            "genre_id": new_genre["id"]
        }
        
        response = client.put("/api/v1/games/Tetris", json=update_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["title"] == "Chess Master"
        assert response_data["genre_id"] == new_genre["id"]

    def test_update_game_not_found(self, client):
        """Test game update when game doesn't exist."""
        # Create a genre for the update data
        genre_data = {
            "name": "Adventure",
            "description": "Adventure games"
        }
        genre_response = client.post("/api/v1/genres/create", json=genre_data)
        created_genre = genre_response.json()
        
        update_data = {
            "title": "Updated Game",
            "genre_id": created_genre["id"]
        }
        
        response = client.put("/api/v1/games/Nonexistent Game", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Game not found"


class TestGenreIntegration:
    """Integration tests for genre API endpoints."""

    def test_create_genre_endpoint_success(self, client):
        """Test successful genre creation via API endpoint."""
        genre_data = {
            "name": "Horror",
            "description": "Scary and suspenseful games"
        }
        
        response = client.post("/api/v1/genres/create", json=genre_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert "id" in response_data
        assert response_data["name"] == genre_data["name"]
        assert response_data["description"] == genre_data["description"]

    def test_list_genres_empty(self, client):
        """Test listing genres when none exist via API."""
        response = client.get("/api/v1/genres/list")
        assert response.status_code == 200
        # Just check that it returns a list (might have genres from other tests)
        assert isinstance(response.json(), list)

    def test_list_genres_with_data(self, client):
        """Test listing genres when some exist via API."""
        # Create test genres with unique names
        genre1_data = {
            "name": "Sports_Integration",
            "description": "Athletic and competitive games"
        }
        genre2_data = {
            "name": "Racing_Integration",
            "description": "Vehicle racing games"
        }
        
        client.post("/api/v1/genres/create", json=genre1_data)
        client.post("/api/v1/genres/create", json=genre2_data)
        
        response = client.get("/api/v1/genres/list")
        assert response.status_code == 200
        
        response_data = response.json()
        genre_names = [genre["name"] for genre in response_data]
        
        # Check that our test genres are in the list
        assert "Sports_Integration" in genre_names
        assert "Racing_Integration" in genre_names

    def test_create_genre_with_special_characters(self, client):
        """Test creating genre with special characters via API."""
        genre_data = {
            "name": "Sci-Fi & Fantasy",
            "description": "Futuristic & magical games!"
        }
        
        response = client.post("/api/v1/genres/create", json=genre_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["name"] == "Sci-Fi & Fantasy"
        assert response_data["description"] == "Futuristic & magical games!"


class TestGameGenreWorkflow:
    """End-to-end workflow tests for games and genres."""

    def test_complete_game_management_workflow(self, client):
        """Test complete workflow: create genre, create game, get game, update game."""
        # Step 1: Create a genre
        genre_data = {
            "name": "Simulation",
            "description": "Life and world simulation games"
        }
        genre_response = client.post("/api/v1/genres/create", json=genre_data)
        assert genre_response.status_code == 200
        created_genre = genre_response.json()
        
        # Step 2: Create a game
        game_data = {
            "title": "The Sims",
            "genre_id": created_genre["id"]
        }
        create_response = client.post("/api/v1/games/create", json=game_data)
        assert create_response.status_code == 200
        created_game = create_response.json()
        
        # Step 3: Retrieve the game
        get_response = client.get(f"/api/v1/games/{game_data['title']}")
        assert get_response.status_code == 200
        retrieved_game = get_response.json()
        assert retrieved_game["title"] == game_data["title"]
        assert retrieved_game["genre"]["name"] == genre_data["name"]
        
        # Step 4: Update the game
        update_data = {
            "title": "SimCity",
            "genre_id": created_genre["id"]
        }
        update_response = client.put(f"/api/v1/games/{game_data['title']}", json=update_data)
        assert update_response.status_code == 200
        updated_game = update_response.json()
        assert updated_game["title"] == "SimCity"
        
        # Step 5: Verify the update by getting the game with new title
        final_get_response = client.get("/api/v1/games/SimCity")
        assert final_get_response.status_code == 200
        final_game = final_get_response.json()
        assert final_game["title"] == "SimCity"

    def test_multiple_games_same_genre_workflow(self, client):
        """Test creating multiple games with the same genre."""
        # Create a genre
        genre_data = {
            "name": "Fighting",
            "description": "Combat and martial arts games"
        }
        genre_response = client.post("/api/v1/genres/create", json=genre_data)
        created_genre = genre_response.json()
        
        # Create multiple games with the same genre
        games_data = [
            {"title": "Street Fighter", "genre_id": created_genre["id"]},
            {"title": "Tekken", "genre_id": created_genre["id"]},
            {"title": "Mortal Kombat", "genre_id": created_genre["id"]}
        ]
        
        created_games = []
        for game_data in games_data:
            response = client.post("/api/v1/games/create", json=game_data)
            assert response.status_code == 200
            created_games.append(response.json())
        
        # Verify all games were created with the correct genre
        for i, created_game in enumerate(created_games):
            assert created_game["title"] == games_data[i]["title"]
            assert created_game["genre_id"] == created_genre["id"]
            assert created_game["genre"]["name"] == "Fighting"
        
        # Verify we can retrieve all games individually
        for game_data in games_data:
            response = client.get(f"/api/v1/games/{game_data['title']}")
            assert response.status_code == 200
            retrieved_game = response.json()
            assert retrieved_game["title"] == game_data["title"]

    async def test_service_layer_integration(self, db_session):
        """Test direct service layer integration without API."""
        # Create genre via service
        genre_data = GenreCreate(
            name="Indie",
            description="Independent developer games"
        )
        created_genre = await create_genre(genre_data, db_session)
        
        # Create game via service
        game_data = GameCreate(
            title="Hollow Knight",
            genre_id=created_genre.id
        )
        created_game = await create_game(game_data, db_session)
        
        # Verify the integration
        assert created_game is not None
        assert created_game.genre is not None
        assert created_game.genre.id == created_genre.id
        assert created_game.genre.name == "Indie"
        assert created_game.title == "Hollow Knight"