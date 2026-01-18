"""Unit tests for fog-of-war visibility calculations."""
import pytest
from app.board import Board
from app.pieces import King, Queen, Rook, Bishop, Knight, Pawn


class TestBoardVisibility:
    def test_own_piece_squares_visible(self):
        board = Board()
        king = King('white')
        pawn = Pawn('white')
        board.set_piece((7, 4), king)
        board.set_piece((6, 4), pawn)

        visible = board.get_visible_squares('white')

        assert (7, 4) in visible  # King's position
        assert (6, 4) in visible  # Pawn's position

    def test_king_makes_adjacent_visible(self):
        board = Board()
        king = King('white')
        board.set_piece((4, 4), king)

        visible = board.get_visible_squares('white')

        # King can see all adjacent squares
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                assert (4 + dr, 4 + dc) in visible

    def test_pawn_visibility_forward_and_diagonals(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((6, 4), pawn)

        visible = board.get_visible_squares('white')

        assert (5, 4) in visible  # One forward
        assert (4, 4) in visible  # Two forward (from start)
        assert (5, 3) in visible  # Attack diagonal left
        assert (5, 5) in visible  # Attack diagonal right

    def test_sliding_piece_visibility_stops_at_first_piece(self):
        board = Board()
        rook = Rook('white')
        blocker = Pawn('black')
        board.set_piece((4, 0), rook)
        board.set_piece((4, 3), blocker)

        visible = board.get_visible_squares('white')

        assert (4, 1) in visible
        assert (4, 2) in visible
        assert (4, 3) in visible  # Can see the blocker
        assert (4, 4) not in visible  # Cannot see beyond
        assert (4, 5) not in visible

    def test_knight_visibility_all_eight_squares(self):
        board = Board()
        knight = Knight('white')
        board.set_piece((4, 4), knight)

        visible = board.get_visible_squares('white')

        expected_knight_squares = [
            (2, 3), (2, 5), (3, 2), (3, 6),
            (5, 2), (5, 6), (6, 3), (6, 5)
        ]
        for sq in expected_knight_squares:
            assert sq in visible

    def test_multiple_pieces_combine_visibility(self):
        board = Board()
        king = King('white')
        rook = Rook('white')
        board.set_piece((7, 4), king)
        board.set_piece((7, 0), rook)

        visible = board.get_visible_squares('white')

        # King's visibility
        assert (6, 4) in visible
        assert (7, 5) in visible

        # Rook's visibility
        assert (7, 1) in visible
        assert (7, 2) in visible
        assert (0, 0) in visible  # Can see up the file

    def test_enemy_pieces_not_counted_for_own_visibility(self):
        board = Board()
        king = King('white')
        enemy_queen = Queen('black')
        board.set_piece((7, 4), king)
        board.set_piece((0, 0), enemy_queen)

        visible = board.get_visible_squares('white')

        # White can only see what white pieces can reach
        assert (0, 0) not in visible  # Enemy queen not in king's range


class TestInitialPositionVisibility:
    def test_initial_white_visibility(self):
        """Test visibility from standard starting position."""
        board = Board()

        # Set up white pieces
        board.set_piece((7, 0), Rook('white'))
        board.set_piece((7, 1), Knight('white'))
        board.set_piece((7, 2), Bishop('white'))
        board.set_piece((7, 3), Queen('white'))
        board.set_piece((7, 4), King('white'))
        board.set_piece((7, 5), Bishop('white'))
        board.set_piece((7, 6), Knight('white'))
        board.set_piece((7, 7), Rook('white'))
        for col in range(8):
            board.set_piece((6, col), Pawn('white'))

        visible = board.get_visible_squares('white')

        # Own pieces visible
        for col in range(8):
            assert (7, col) in visible
            assert (6, col) in visible

        # Pawn forward squares visible
        for col in range(8):
            assert (5, col) in visible  # One forward
            assert (4, col) in visible  # Two forward

        # Knight destination squares visible
        assert (5, 0) in visible  # b1 knight can reach a3
        assert (5, 2) in visible  # b1 knight can reach c3

        # Row 3 and above should mostly be fog (except knight squares)
        assert (3, 3) not in visible  # Middle of board in fog
