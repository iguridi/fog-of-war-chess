"""Unit tests for game logic."""
import pytest
from app.game import Game
from app.board import Board
from app.pieces import King, Queen, Rook, Bishop, Knight, Pawn


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

    def test_queen_capturing_king_ends_game(self):
        game = Game()
        game.board = Board()

        white_queen = Queen('white')
        black_king = King('black')
        game.board.set_piece((4, 4), white_queen)
        game.board.set_piece((4, 7), black_king)

        game._execute_move((4, 4), (4, 7))

        assert game.game_over is True
        assert game.winner == 'white'


class TestVisibleState:
    def test_initial_state_has_fog(self):
        game = Game()
        state = game.get_visible_state()

        has_fog = any(
            cell == 'fog'
            for row in state['board']
            for cell in row
        )
        assert has_fog

    def test_own_pieces_visible(self):
        game = Game()
        state = game.get_visible_state()

        # White king at e1 (7, 4) should be visible
        king_cell = state['board'][7][4]
        assert king_cell is not None
        assert king_cell != 'fog'
        assert king_cell['color'] == 'white'
        assert king_cell['type'] == 'king'

        # White queen at d1 (7, 3) should be visible
        queen_cell = state['board'][7][3]
        assert queen_cell['type'] == 'queen'

    def test_board_size_in_state(self):
        game = Game()
        state = game.get_visible_state()

        assert state['boardSize'] == 8
        assert len(state['board']) == 8
        assert len(state['board'][0]) == 8

    def test_enemy_king_not_visible_at_start(self):
        game = Game()
        state = game.get_visible_state()

        # Black king at e8 (0, 4) should be in fog
        black_king_cell = state['board'][0][4]
        assert black_king_cell == 'fog'


class TestInitialPosition:
    def test_initial_position_has_correct_pieces(self):
        game = Game()

        # White back rank
        assert game.board.get_piece((7, 0)).piece_type == 'rook'
        assert game.board.get_piece((7, 1)).piece_type == 'knight'
        assert game.board.get_piece((7, 2)).piece_type == 'bishop'
        assert game.board.get_piece((7, 3)).piece_type == 'queen'
        assert game.board.get_piece((7, 4)).piece_type == 'king'
        assert game.board.get_piece((7, 5)).piece_type == 'bishop'
        assert game.board.get_piece((7, 6)).piece_type == 'knight'
        assert game.board.get_piece((7, 7)).piece_type == 'rook'

        # White pawns
        for col in range(8):
            pawn = game.board.get_piece((6, col))
            assert pawn.piece_type == 'pawn'
            assert pawn.color == 'white'

        # Black back rank
        assert game.board.get_piece((0, 0)).piece_type == 'rook'
        assert game.board.get_piece((0, 1)).piece_type == 'knight'
        assert game.board.get_piece((0, 2)).piece_type == 'bishop'
        assert game.board.get_piece((0, 3)).piece_type == 'queen'
        assert game.board.get_piece((0, 4)).piece_type == 'king'
        assert game.board.get_piece((0, 5)).piece_type == 'bishop'
        assert game.board.get_piece((0, 6)).piece_type == 'knight'
        assert game.board.get_piece((0, 7)).piece_type == 'rook'

        # Black pawns
        for col in range(8):
            pawn = game.board.get_piece((1, col))
            assert pawn.piece_type == 'pawn'
            assert pawn.color == 'black'

    def test_middle_rows_empty(self):
        game = Game()

        for row in range(2, 6):
            for col in range(8):
                assert game.board.get_piece((row, col)) is None


class TestPlayerMoves:
    def test_pawn_can_move_forward(self):
        game = Game()

        result = game.make_player_move((6, 4), (4, 4))

        assert result['success'] is True
        assert game.board.get_piece((4, 4)) is not None
        assert game.board.get_piece((6, 4)) is None

    def test_knight_can_move(self):
        game = Game()

        # Move knight from g1 to f3
        result = game.make_player_move((7, 6), (5, 5))

        assert result['success'] is True
        knight = game.board.get_piece((5, 5))
        assert knight is not None
        assert knight.piece_type == 'knight'

    def test_invalid_move_rejected(self):
        game = Game()

        # Try to move pawn backwards
        result = game.make_player_move((6, 4), (7, 4))

        assert result['success'] is False

    def test_cannot_move_through_pieces(self):
        game = Game()

        # Try to move rook through pawn
        result = game.make_player_move((7, 0), (5, 0))

        assert result['success'] is False
