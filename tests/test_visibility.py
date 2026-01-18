"""Unit tests for fog-of-war visibility calculations."""
import pytest
from app.board import Board
from app.pieces import King, Pawn


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

    def test_multiple_pieces_combine_visibility(self):
        board = Board()
        king = King('white')
        pawn = Pawn('white')
        board.set_piece((7, 4), king)
        board.set_piece((6, 0), pawn)

        visible = board.get_visible_squares('white')

        # King's visibility
        assert (6, 4) in visible
        assert (7, 5) in visible

        # Pawn's visibility
        assert (5, 0) in visible  # Forward
        assert (5, 1) in visible  # Diagonal

    def test_enemy_pieces_not_counted_for_own_visibility(self):
        board = Board()
        king = King('white')
        enemy_king = King('black')
        board.set_piece((7, 4), king)
        board.set_piece((0, 0), enemy_king)

        visible = board.get_visible_squares('white')

        # White can only see what white pieces can reach
        assert (0, 0) not in visible  # Enemy king not in white's range


class TestInitialPositionVisibility:
    def test_initial_white_visibility(self):
        """Test visibility from standard starting position."""
        board = Board()

        # Set up white pieces
        board.set_piece((7, 4), King('white'))
        for col in range(8):
            board.set_piece((6, col), Pawn('white'))

        visible = board.get_visible_squares('white')

        # Own pieces visible
        for col in range(8):
            assert (6, col) in visible  # Pawns
        assert (7, 4) in visible  # King

        # Pawn forward squares visible
        for col in range(8):
            assert (5, col) in visible  # One forward
            assert (4, col) in visible  # Two forward

        # Row 3 and above should mostly be fog
        assert (3, 3) not in visible  # Middle of board in fog
        assert (0, 4) not in visible  # Enemy king's position in fog

    def test_initial_black_visibility(self):
        """Test visibility from black's perspective."""
        board = Board()

        # Set up black pieces
        board.set_piece((0, 4), King('black'))
        for col in range(8):
            board.set_piece((1, col), Pawn('black'))

        visible = board.get_visible_squares('black')

        # Own pieces visible
        for col in range(8):
            assert (1, col) in visible  # Pawns
        assert (0, 4) in visible  # King

        # Pawn forward squares visible
        for col in range(8):
            assert (2, col) in visible  # One forward
            assert (3, col) in visible  # Two forward


class TestVisibilityDuringGame:
    def test_visibility_changes_after_pawn_move(self):
        """Test that visibility updates when pawn advances."""
        board = Board()
        pawn = Pawn('white')
        board.set_piece((6, 4), pawn)

        initial_visible = board.get_visible_squares('white')
        assert (4, 4) in initial_visible  # Two squares forward from start

        # Move pawn forward
        board.set_piece((6, 4), None)
        board.set_piece((5, 4), pawn)

        new_visible = board.get_visible_squares('white')
        # Now only sees one square forward (no longer on starting row)
        assert (4, 4) in new_visible
        assert (3, 4) not in new_visible  # Can't see two forward anymore

    def test_pawn_diagonal_visibility_reveals_enemy(self):
        """Pawn diagonal attack squares reveal enemies."""
        board = Board()
        white_pawn = Pawn('white')
        black_pawn = Pawn('black')
        board.set_piece((5, 4), white_pawn)
        board.set_piece((4, 5), black_pawn)

        visible = board.get_visible_squares('white')

        # White pawn's diagonal attack square is visible
        assert (4, 5) in visible


class TestCombinedVisibility:
    def test_king_and_pawns_combine(self):
        """Test that king and pawns combine visibility."""
        board = Board()
        king = King('white')
        pawn = Pawn('white')

        # King in corner, pawn in center
        board.set_piece((7, 0), king)
        board.set_piece((6, 4), pawn)

        visible = board.get_visible_squares('white')

        # King's adjacent squares
        assert (6, 0) in visible
        assert (6, 1) in visible
        assert (7, 1) in visible

        # Pawn's forward and diagonal squares
        assert (5, 4) in visible
        assert (4, 4) in visible
        assert (5, 3) in visible
        assert (5, 5) in visible

    def test_full_starting_position_visibility(self):
        """Test visibility for a complete starting position."""
        board = Board()

        # White pieces
        board.set_piece((7, 4), King('white'))
        for col in range(8):
            board.set_piece((6, col), Pawn('white'))

        # Black pieces
        board.set_piece((0, 4), King('black'))
        for col in range(8):
            board.set_piece((1, col), Pawn('black'))

        white_visible = board.get_visible_squares('white')
        black_visible = board.get_visible_squares('black')

        # Each side sees their own pieces and forward squares
        # but not the enemy's back rank
        assert (0, 4) not in white_visible  # Black king hidden
        assert (7, 4) not in black_visible  # White king hidden

        # Middle of board (row 4) is visible to both via pawn forward moves
        assert (4, 0) in white_visible
        assert (3, 0) in black_visible
