"""Unit tests for game logic."""
import pytest
from app.game import Game
from app.board import Board
from app.pieces import King, Pawn


class TestGameEndDetection:
    def test_white_wins_by_capturing_black_king(self):
        game = Game()
        game.board = Board()

        white_king = King('white')
        black_king = King('black')
        game.board.set_piece((4, 4), white_king)
        game.board.set_piece((4, 5), black_king)

        game._execute_move((4, 4), (4, 5))

        assert game.game_over is True
        assert game.winner == 'white'

    def test_black_wins_by_capturing_white_king(self):
        game = Game()
        game.board = Board()

        white_king = King('white')
        black_king = King('black')
        game.board.set_piece((4, 4), white_king)
        game.board.set_piece((4, 5), black_king)

        game.current_turn = 'black'
        game._execute_move((4, 5), (4, 4))

        assert game.game_over is True
        assert game.winner == 'black'

    def test_pawn_capturing_king_ends_game(self):
        game = Game()
        game.board = Board()

        white_pawn = Pawn('white')
        black_king = King('black')
        game.board.set_piece((5, 4), white_pawn)
        game.board.set_piece((4, 5), black_king)

        game._execute_move((5, 4), (4, 5))

        assert game.game_over is True
        assert game.winner == 'white'


class TestVisibleState:
    def test_initial_state_has_fog(self):
        game = Game()
        state = game.get_visible_state()

        # Enemy rows should be fog
        has_fog = any(
            cell == 'fog'
            for row in state['board']
            for cell in row
        )
        assert has_fog

    def test_own_pieces_visible(self):
        game = Game()
        state = game.get_visible_state()

        # White king at (7, 4) should be visible
        king_cell = state['board'][7][4]
        assert king_cell is not None
        assert king_cell != 'fog'
        assert king_cell['color'] == 'white'
        assert king_cell['type'] == 'king'

        # White pawns on row 6 should be visible
        for col in range(8):
            pawn_cell = state['board'][6][col]
            assert pawn_cell is not None
            assert pawn_cell != 'fog'
            assert pawn_cell['color'] == 'white'
            assert pawn_cell['type'] == 'pawn'

    def test_board_size_in_state(self):
        game = Game()
        state = game.get_visible_state()

        assert state['boardSize'] == 8
        assert len(state['board']) == 8
        assert len(state['board'][0]) == 8

    def test_enemy_king_not_visible_at_start(self):
        game = Game()
        state = game.get_visible_state()

        # Black king at (0, 4) should be in fog
        black_king_cell = state['board'][0][4]
        assert black_king_cell == 'fog'


class TestInitialPosition:
    def test_initial_position_has_correct_pieces(self):
        game = Game()

        # White king on e1 (row 7, col 4)
        white_king = game.board.get_piece((7, 4))
        assert white_king is not None
        assert white_king.piece_type == 'king'
        assert white_king.color == 'white'

        # Black king on e8 (row 0, col 4)
        black_king = game.board.get_piece((0, 4))
        assert black_king is not None
        assert black_king.piece_type == 'king'
        assert black_king.color == 'black'

        # White pawns on row 6
        for col in range(8):
            pawn = game.board.get_piece((6, col))
            assert pawn is not None
            assert pawn.piece_type == 'pawn'
            assert pawn.color == 'white'

        # Black pawns on row 1
        for col in range(8):
            pawn = game.board.get_piece((1, col))
            assert pawn is not None
            assert pawn.piece_type == 'pawn'
            assert pawn.color == 'black'


class TestPlayerMoves:
    def test_pawn_can_move_forward(self):
        game = Game()

        # Move e2 pawn to e4
        result = game.make_player_move((6, 4), (4, 4))

        assert result['success'] is True
        assert game.board.get_piece((4, 4)) is not None
        assert game.board.get_piece((6, 4)) is None

    def test_invalid_move_rejected(self):
        game = Game()

        # Try to move pawn backwards
        result = game.make_player_move((6, 4), (7, 4))

        assert result['success'] is False
