"""Unit tests for game logic."""
import pytest
from app.game import Game
from app.board import Board
from app.pieces import King


class TestGameEndDetection:
    def test_white_wins_by_capturing_black_king(self):
        game = Game()
        game.board = Board()

        white_king = King('white')
        black_king = King('black')
        game.board.set_piece((1, 1), white_king)
        game.board.set_piece((1, 2), black_king)

        game._execute_move((1, 1), (1, 2))

        assert game.game_over is True
        assert game.winner == 'white'

    def test_black_wins_by_capturing_white_king(self):
        game = Game()
        game.board = Board()

        white_king = King('white')
        black_king = King('black')
        game.board.set_piece((1, 1), white_king)
        game.board.set_piece((1, 2), black_king)

        game.current_turn = 'black'
        game._execute_move((1, 2), (1, 1))

        assert game.game_over is True
        assert game.winner == 'black'


class TestVisibleState:
    def test_initial_state_has_fog(self):
        game = Game()
        state = game.get_visible_state()

        # Top-right corner should be fog (black king is there but not visible)
        has_fog = any(
            cell == 'fog'
            for row in state['board']
            for cell in row
        )
        assert has_fog

    def test_own_piece_visible(self):
        game = Game()
        state = game.get_visible_state()

        # White king at (2, 0) should be visible
        piece = state['board'][2][0]
        assert piece is not None
        assert piece != 'fog'
        assert piece['color'] == 'white'
        assert piece['type'] == 'king'

    def test_board_size_in_state(self):
        game = Game()
        state = game.get_visible_state()

        assert state['boardSize'] == 3
        assert len(state['board']) == 3
        assert len(state['board'][0]) == 3
