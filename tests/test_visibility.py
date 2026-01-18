"""Unit tests for fog-of-war visibility calculations (Step 1: 3x3 King-only)."""
import pytest
from app.board import Board
from app.pieces import King


class TestBoardVisibility:
    def test_own_piece_square_visible(self):
        board = Board()
        king = King('white')
        board.set_piece((2, 0), king)

        visible = board.get_visible_squares('white')

        assert (2, 0) in visible  # King's position

    def test_king_makes_adjacent_visible(self):
        board = Board()
        king = King('white')
        board.set_piece((1, 1), king)  # Center of 3x3

        visible = board.get_visible_squares('white')

        # King can see all adjacent squares
        expected = [
            (0, 0), (0, 1), (0, 2),
            (1, 0),         (1, 2),
            (2, 0), (2, 1), (2, 2),
        ]
        for pos in expected:
            assert pos in visible

    def test_king_corner_visibility_limited(self):
        board = Board()
        king = King('white')
        board.set_piece((0, 0), king)  # Top-left corner

        visible = board.get_visible_squares('white')

        # Should see only valid adjacent squares
        assert (0, 0) in visible  # Own position
        assert (0, 1) in visible
        assert (1, 0) in visible
        assert (1, 1) in visible
        # Should NOT see off-board positions (handled by is_valid_pos)
        assert len(visible) == 4  # corner + 3 adjacent

    def test_king_edge_visibility(self):
        board = Board()
        king = King('white')
        board.set_piece((1, 0), king)  # Left edge, middle row

        visible = board.get_visible_squares('white')

        expected = [
            (0, 0), (0, 1),
            (1, 0), (1, 1),
            (2, 0), (2, 1),
        ]
        assert len(visible) == 6
        for pos in expected:
            assert pos in visible

    def test_enemy_pieces_not_counted_for_own_visibility(self):
        board = Board()
        white_king = King('white')
        black_king = King('black')
        board.set_piece((2, 0), white_king)
        board.set_piece((0, 2), black_king)

        visible = board.get_visible_squares('white')

        # White can only see what white pieces can reach
        # Black king at (0, 2) is not adjacent to white king at (2, 0)
        assert (0, 2) not in visible

    def test_multiple_pieces_combine_visibility(self):
        """If we had multiple white pieces, their visibility would combine."""
        board = Board()
        king1 = King('white')
        king2 = King('white')  # Hypothetical second king for testing
        board.set_piece((0, 0), king1)
        board.set_piece((2, 2), king2)

        visible = board.get_visible_squares('white')

        # Both kings' positions visible
        assert (0, 0) in visible
        assert (2, 2) in visible
        # Adjacent to first king
        assert (0, 1) in visible
        assert (1, 0) in visible
        # Adjacent to second king
        assert (1, 2) in visible
        assert (2, 1) in visible


class TestInitialPositionVisibility:
    def test_initial_white_visibility(self):
        """Test visibility from standard 3x3 starting position."""
        board = Board()

        # Standard starting position
        board.set_piece((2, 0), King('white'))  # Bottom-left
        board.set_piece((0, 2), King('black'))  # Top-right

        visible = board.get_visible_squares('white')

        # White king's position visible
        assert (2, 0) in visible

        # Adjacent squares visible
        assert (1, 0) in visible
        assert (1, 1) in visible
        assert (2, 1) in visible

        # Black king's corner not visible (too far)
        assert (0, 2) not in visible

    def test_initial_black_visibility(self):
        """Test visibility from black's perspective."""
        board = Board()

        board.set_piece((2, 0), King('white'))
        board.set_piece((0, 2), King('black'))

        visible = board.get_visible_squares('black')

        # Black king's position visible
        assert (0, 2) in visible

        # Adjacent squares visible
        assert (0, 1) in visible
        assert (1, 1) in visible
        assert (1, 2) in visible

        # White king's corner not visible
        assert (2, 0) not in visible

    def test_fog_covers_opposite_corner(self):
        """Verify that the opposite corner is in fog at start."""
        board = Board()

        board.set_piece((2, 0), King('white'))
        board.set_piece((0, 2), King('black'))

        white_visible = board.get_visible_squares('white')
        black_visible = board.get_visible_squares('black')

        # Each side cannot see the other's starting corner
        assert (0, 2) not in white_visible
        assert (2, 0) not in black_visible


class TestVisibilityDuringGame:
    def test_visibility_changes_after_move(self):
        """Test that visibility updates when king moves."""
        board = Board()
        king = King('white')
        board.set_piece((2, 0), king)

        initial_visible = board.get_visible_squares('white')
        assert (0, 0) not in initial_visible  # Top-left corner not visible

        # Move king to center
        board.set_piece((2, 0), None)
        board.set_piece((1, 1), king)

        new_visible = board.get_visible_squares('white')
        # Now can see all squares from center
        assert (0, 0) in new_visible
        assert (0, 2) in new_visible
        assert (2, 0) in new_visible
        assert (2, 2) in new_visible

    def test_kings_can_see_each_other_when_adjacent(self):
        """When kings are adjacent, they can see each other."""
        board = Board()
        white_king = King('white')
        black_king = King('black')

        board.set_piece((1, 0), white_king)
        board.set_piece((1, 1), black_king)

        white_visible = board.get_visible_squares('white')
        black_visible = board.get_visible_squares('black')

        # They can see each other
        assert (1, 1) in white_visible  # White sees black
        assert (1, 0) in black_visible  # Black sees white
