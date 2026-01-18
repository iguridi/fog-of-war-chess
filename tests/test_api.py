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
        assert data['boardSize'] == 3
        assert len(data['board']) == 3

    def test_new_game_resets_state(self, client):
        response = client.post('/api/new-game')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['turn'] == 'white'
        assert data['gameOver'] is False

    def test_valid_move_succeeds(self, client):
        client.post('/api/new-game')

        # Move white king from (2,0) to (1,0)
        response = client.post('/api/move', json={
            'from': [2, 0],
            'to': [1, 0]
        })
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert 'state' in data
