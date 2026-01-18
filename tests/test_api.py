"""Integration tests for API endpoints."""
import pytest
import json
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    def test_index_returns_html(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'FOG OF WAR CHESS' in response.data

    def test_get_state_returns_valid_json(self, client):
        response = client.get('/api/state')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'board' in data
        assert 'turn' in data
        assert 'gameOver' in data
        assert 'boardSize' in data
        assert data['boardSize'] == 8
        assert len(data['board']) == 8

    def test_new_game_resets_state(self, client):
        response = client.post('/api/new-game')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['turn'] == 'white'
        assert data['gameOver'] is False

    def test_valid_move_succeeds(self, client):
        client.post('/api/new-game')

        # Move white pawn from e2 (6,4) to e4 (4,4)
        response = client.post('/api/move', json={
            'from': [6, 4],
            'to': [4, 4]
        })
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert 'state' in data

    def test_invalid_move_fails(self, client):
        client.post('/api/new-game')

        # Try to move pawn backwards (invalid)
        response = client.post('/api/move', json={
            'from': [6, 4],
            'to': [7, 4]
        })
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is False

    def test_state_contains_pieces(self, client):
        client.post('/api/new-game')
        response = client.get('/api/state')
        data = json.loads(response.data)

        # White king should be at e1 (7, 4)
        king = data['board'][7][4]
        assert king is not None
        assert king['type'] == 'king'
        assert king['color'] == 'white'

        # White pawns should be on row 6
        for col in range(8):
            pawn = data['board'][6][col]
            assert pawn is not None
            assert pawn['type'] == 'pawn'
            assert pawn['color'] == 'white'
