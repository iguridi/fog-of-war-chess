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

        assert (7, 4) in visible
        assert (6, 4) in visible

    def test_sliding_piece_visibility(self):
        board = Board()
        rook = Rook('white')
        board.set_piece((4, 4), rook)

        visible = board.get_visible_squares('white')

        # Rook sees entire row and column
        for i in range(8):
            if i != 4:
                assert (i, 4) in visible
                assert (4, i) in visible

    def test_knight_visibility(self):
        board = Board()
        knight = Knight('white')
        board.set_piece((4, 4), knight)

        visible = board.get_visible_squares('white')

        # Knight sees all L-shape squares
        expected = [
            (2, 3), (2, 5), (3, 2), (3, 6),
            (5, 2), (5, 6), (6, 3), (6, 5)
        ]
        for pos in expected:
            assert pos in visible

    def test_multiple_pieces_combine_visibility(self):
        board = Board()
        king = King('white')
        rook = Rook('white')
        board.set_piece((7, 4), king)
        board.set_piece((7, 0), rook)

        visible = board.get_visible_squares('white')

        # King's adjacent squares
        assert (6, 4) in visible
        assert (7, 5) in visible

        # Rook's visibility (vertical ray, blocked by own pieces horizontally)
        assert (0, 0) in visible
        assert (6, 0) in visible

    def test_enemy_pieces_not_counted_for_own_visibility(self):
        board = Board()
        king = King('white')
        enemy_queen = Queen('black')
        board.set_piece((7, 4), king)
        board.set_piece((0, 0), enemy_queen)

        visible = board.get_visible_squares('white')

        # White can only see what white pieces can reach
        assert (0, 0) not in visible


class TestSlidingPieceVisibility:
    def test_rook_visibility_stops_at_piece(self):
        board = Board()
        rook = Rook('white')
        blocker = Pawn('black')
        board.set_piece((4, 4), rook)
        board.set_piece((4, 6), blocker)

        visible = board.get_visible_squares('white')

        # Can see blocker
        assert (4, 6) in visible
        # Cannot see beyond
        assert (4, 7) not in visible

    def test_bishop_visibility_stops_at_piece(self):
        board = Board()
        bishop = Bishop('white')
        blocker = Pawn('black')
        board.set_piece((4, 4), bishop)
        board.set_piece((2, 2), blocker)

        visible = board.get_visible_squares('white')

        assert (2, 2) in visible
        assert (1, 1) not in visible
        assert (0, 0) not in visible

    def test_queen_visibility_all_directions(self):
        board = Board()
        queen = Queen('white')
        board.set_piece((4, 4), queen)

        visible = board.get_visible_squares('white')

        # Diagonals
        assert (0, 0) in visible
        assert (7, 7) in visible
        assert (1, 7) in visible
        assert (7, 1) in visible

        # Straights
        assert (0, 4) in visible
        assert (7, 4) in visible
        assert (4, 0) in visible
        assert (4, 7) in visible


class TestInitialPositionVisibility:
    def test_initial_white_visibility(self):
        """Test visibility from standard starting position."""
        board = Board()

        # Set up white pieces (back rank + pawns)
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
            assert (6, col) in visible
            assert (7, col) in visible

        # Pawn forward squares visible
        for col in range(8):
            assert (5, col) in visible
            assert (4, col) in visible

        # Knight jump squares visible
        assert (5, 0) in visible  # b1 knight to a3
        assert (5, 2) in visible  # b1 knight to c3

        # Deep enemy territory in fog
        assert (0, 4) not in visible

    def test_knight_extends_visibility(self):
        """Knights can see squares other pieces can't reach at start."""
        board = Board()

        # Just knights and pawns
        board.set_piece((7, 1), Knight('white'))
        board.set_piece((7, 6), Knight('white'))
        for col in range(8):
            board.set_piece((6, col), Pawn('white'))

        visible = board.get_visible_squares('white')

        # Knights can see L-shape squares
        assert (5, 0) in visible  # a3
        assert (5, 2) in visible  # c3
        assert (5, 5) in visible  # f3
        assert (5, 7) in visible  # h3


class TestVisibilityDuringGame:
    def test_visibility_changes_after_piece_move(self):
        """Test that visibility updates when pieces move."""
        board = Board()
        rook = Rook('white')
        board.set_piece((7, 0), rook)

        initial_visible = board.get_visible_squares('white')
        # Rook can see up the a-file
        assert (0, 0) in initial_visible

        # Add a blocking piece (use a King so it doesn't add forward visibility)
        board.set_piece((4, 0), King('white'))

        new_visible = board.get_visible_squares('white')
        # Rook is now blocked at (4, 0)
        assert (4, 0) in new_visible
        # Rook can't see beyond the king, but king can see (3, 0) adjacent
        # So let's check (2, 0) which neither can reach
        assert (2, 0) not in new_visible
        assert (0, 0) not in new_visible

    def test_capturing_reveals_new_squares(self):
        """When a blocking piece is captured, visibility extends."""
        board = Board()
        bishop = Bishop('white')
        blocker = Pawn('black')
        board.set_piece((4, 4), bishop)
        board.set_piece((2, 2), blocker)

        visible = board.get_visible_squares('white')
        assert (2, 2) in visible
        assert (0, 0) not in visible

        # Simulate capture
        board.set_piece((2, 2), None)

        new_visible = board.get_visible_squares('white')
        # Now can see further
        assert (2, 2) in new_visible
        assert (1, 1) in new_visible
        assert (0, 0) in new_visible


class TestCombinedVisibility:
    def test_full_starting_position_visibility(self):
        """Test visibility for a complete starting position."""
        board = Board()

        # White pieces
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

        # Black pieces
        board.set_piece((0, 0), Rook('black'))
        board.set_piece((0, 1), Knight('black'))
        board.set_piece((0, 2), Bishop('black'))
        board.set_piece((0, 3), Queen('black'))
        board.set_piece((0, 4), King('black'))
        board.set_piece((0, 5), Bishop('black'))
        board.set_piece((0, 6), Knight('black'))
        board.set_piece((0, 7), Rook('black'))
        for col in range(8):
            board.set_piece((1, col), Pawn('black'))

        white_visible = board.get_visible_squares('white')
        black_visible = board.get_visible_squares('black')

        # Each side can't see the other's back rank (blocked by pawns)
        assert (0, 4) not in white_visible  # Black king hidden
        assert (7, 4) not in black_visible  # White king hidden

        # Middle rows visible to both
        assert (4, 4) in white_visible
        assert (3, 4) in black_visible
