"""Unit tests for chess pieces."""
import pytest
from app.board import Board
from app.pieces import King, Queen, Rook, Bishop, Knight, Pawn


class TestKing:
    def test_moves_one_square_all_directions(self):
        board = Board()
        king = King('white')
        board.set_piece((4, 4), king)

        moves = king.get_valid_moves((4, 4), board)

        expected = [(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]
        assert sorted(moves) == sorted(expected)

    def test_cannot_move_off_board(self):
        board = Board()
        king = King('white')
        board.set_piece((0, 0), king)

        moves = king.get_valid_moves((0, 0), board)

        assert len(moves) == 3
        assert (0, 1) in moves
        assert (1, 0) in moves
        assert (1, 1) in moves

    def test_can_capture_enemy(self):
        board = Board()
        white_king = King('white')
        black_pawn = Pawn('black')
        board.set_piece((4, 4), white_king)
        board.set_piece((4, 5), black_pawn)

        moves = white_king.get_valid_moves((4, 4), board)

        assert (4, 5) in moves

    def test_cannot_capture_friendly(self):
        board = Board()
        white_king = King('white')
        white_pawn = Pawn('white')
        board.set_piece((4, 4), white_king)
        board.set_piece((4, 5), white_pawn)

        moves = white_king.get_valid_moves((4, 4), board)

        assert (4, 5) not in moves

    def test_visibility(self):
        board = Board()
        king = King('white')
        board.set_piece((4, 4), king)

        visible = king.get_visible_squares((4, 4), board)

        assert len(visible) == 8

    def test_corner_visibility(self):
        board = Board()
        king = King('white')
        board.set_piece((0, 0), king)

        visible = king.get_visible_squares((0, 0), board)

        assert len(visible) == 3


class TestKnight:
    def test_knight_l_shape_moves(self):
        board = Board()
        knight = Knight('white')
        board.set_piece((4, 4), knight)

        moves = knight.get_valid_moves((4, 4), board)

        expected = [
            (2, 3), (2, 5), (3, 2), (3, 6),
            (5, 2), (5, 6), (6, 3), (6, 5)
        ]
        assert sorted(moves) == sorted(expected)

    def test_knight_corner_moves(self):
        board = Board()
        knight = Knight('white')
        board.set_piece((0, 0), knight)

        moves = knight.get_valid_moves((0, 0), board)

        expected = [(1, 2), (2, 1)]
        assert sorted(moves) == sorted(expected)

    def test_knight_jumps_over_pieces(self):
        board = Board()
        knight = Knight('white')
        board.set_piece((4, 4), knight)
        # Surround with pawns
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr != 0 or dc != 0:
                    board.set_piece((4 + dr, 4 + dc), Pawn('white'))

        moves = knight.get_valid_moves((4, 4), board)

        # Knight can still jump to all L-shape destinations
        assert len(moves) == 8

    def test_knight_can_capture_enemy(self):
        board = Board()
        knight = Knight('white')
        enemy = Pawn('black')
        board.set_piece((4, 4), knight)
        board.set_piece((2, 3), enemy)

        moves = knight.get_valid_moves((4, 4), board)

        assert (2, 3) in moves

    def test_knight_cannot_capture_friendly(self):
        board = Board()
        knight = Knight('white')
        friendly = Pawn('white')
        board.set_piece((4, 4), knight)
        board.set_piece((2, 3), friendly)

        moves = knight.get_valid_moves((4, 4), board)

        assert (2, 3) not in moves

    def test_knight_visibility(self):
        board = Board()
        knight = Knight('white')
        board.set_piece((4, 4), knight)

        visible = knight.get_visible_squares((4, 4), board)

        assert len(visible) == 8


class TestBishop:
    def test_bishop_diagonal_moves(self):
        board = Board()
        bishop = Bishop('white')
        board.set_piece((4, 4), bishop)

        moves = bishop.get_valid_moves((4, 4), board)

        # All diagonals from center
        expected = [
            (0, 0), (1, 1), (2, 2), (3, 3),  # up-left
            (5, 5), (6, 6), (7, 7),          # down-right
            (3, 5), (2, 6), (1, 7),          # up-right
            (5, 3), (6, 2), (7, 1)           # down-left
        ]
        assert sorted(moves) == sorted(expected)

    def test_bishop_blocked_by_own_piece(self):
        board = Board()
        bishop = Bishop('white')
        blocker = Pawn('white')
        board.set_piece((4, 4), bishop)
        board.set_piece((2, 2), blocker)

        moves = bishop.get_valid_moves((4, 4), board)

        # Should not include (2, 2) or beyond
        assert (2, 2) not in moves
        assert (1, 1) not in moves
        assert (0, 0) not in moves
        # But should include (3, 3)
        assert (3, 3) in moves

    def test_bishop_captures_and_stops(self):
        board = Board()
        bishop = Bishop('white')
        enemy = Pawn('black')
        board.set_piece((4, 4), bishop)
        board.set_piece((2, 2), enemy)

        moves = bishop.get_valid_moves((4, 4), board)

        # Can capture but not go beyond
        assert (2, 2) in moves
        assert (1, 1) not in moves
        assert (0, 0) not in moves

    def test_bishop_visibility_stops_at_piece(self):
        board = Board()
        bishop = Bishop('white')
        blocker = Pawn('black')
        board.set_piece((4, 4), bishop)
        board.set_piece((2, 2), blocker)

        visible = bishop.get_visible_squares((4, 4), board)

        # Can see blocker but not beyond
        assert (2, 2) in visible
        assert (1, 1) not in visible


class TestRook:
    def test_rook_straight_moves(self):
        board = Board()
        rook = Rook('white')
        board.set_piece((4, 4), rook)

        moves = rook.get_valid_moves((4, 4), board)

        # All horizontal and vertical from center
        expected = []
        for i in range(8):
            if i != 4:
                expected.append((i, 4))  # Vertical
                expected.append((4, i))  # Horizontal
        assert sorted(moves) == sorted(expected)

    def test_rook_blocked_by_own_piece(self):
        board = Board()
        rook = Rook('white')
        blocker = Pawn('white')
        board.set_piece((4, 4), rook)
        board.set_piece((4, 2), blocker)

        moves = rook.get_valid_moves((4, 4), board)

        # Should not include (4, 2) or beyond
        assert (4, 2) not in moves
        assert (4, 1) not in moves
        assert (4, 0) not in moves
        # But should include (4, 3)
        assert (4, 3) in moves

    def test_rook_captures_and_stops(self):
        board = Board()
        rook = Rook('white')
        enemy = Pawn('black')
        board.set_piece((4, 4), rook)
        board.set_piece((4, 2), enemy)

        moves = rook.get_valid_moves((4, 4), board)

        # Can capture but not go beyond
        assert (4, 2) in moves
        assert (4, 1) not in moves

    def test_rook_visibility_stops_at_piece(self):
        board = Board()
        rook = Rook('white')
        blocker = Pawn('black')
        board.set_piece((4, 4), rook)
        board.set_piece((2, 4), blocker)

        visible = rook.get_visible_squares((4, 4), board)

        # Can see blocker but not beyond
        assert (2, 4) in visible
        assert (1, 4) not in visible
        assert (0, 4) not in visible


class TestQueen:
    def test_queen_combines_rook_and_bishop(self):
        board = Board()
        queen = Queen('white')
        board.set_piece((4, 4), queen)

        moves = queen.get_valid_moves((4, 4), board)

        # Should have both straight and diagonal moves
        # Diagonals
        assert (0, 0) in moves
        assert (7, 7) in moves
        assert (1, 7) in moves
        assert (7, 1) in moves
        # Straights
        assert (0, 4) in moves
        assert (7, 4) in moves
        assert (4, 0) in moves
        assert (4, 7) in moves

    def test_queen_blocked_on_one_ray(self):
        board = Board()
        queen = Queen('white')
        blocker = Pawn('white')
        board.set_piece((4, 4), queen)
        board.set_piece((4, 6), blocker)

        moves = queen.get_valid_moves((4, 4), board)

        # Blocked horizontally right
        assert (4, 6) not in moves
        assert (4, 7) not in moves
        # But other directions still work
        assert (4, 0) in moves
        assert (0, 4) in moves
        assert (0, 0) in moves

    def test_queen_visibility(self):
        board = Board()
        queen = Queen('white')
        board.set_piece((4, 4), queen)

        visible = queen.get_visible_squares((4, 4), board)

        # Should see in all 8 directions
        assert (0, 0) in visible
        assert (0, 4) in visible
        assert (4, 0) in visible
        assert (7, 7) in visible


class TestPawn:
    def test_white_pawn_moves_forward_one(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((5, 4), pawn)

        moves = pawn.get_valid_moves((5, 4), board)

        assert (4, 4) in moves
        assert len(moves) == 1

    def test_white_pawn_moves_forward_two_from_start(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((6, 4), pawn)

        moves = pawn.get_valid_moves((6, 4), board)

        assert (5, 4) in moves
        assert (4, 4) in moves
        assert len(moves) == 2

    def test_black_pawn_moves_forward_one(self):
        board = Board()
        pawn = Pawn('black')
        board.set_piece((2, 4), pawn)

        moves = pawn.get_valid_moves((2, 4), board)

        assert (3, 4) in moves
        assert len(moves) == 1

    def test_black_pawn_moves_forward_two_from_start(self):
        board = Board()
        pawn = Pawn('black')
        board.set_piece((1, 4), pawn)

        moves = pawn.get_valid_moves((1, 4), board)

        assert (2, 4) in moves
        assert (3, 4) in moves
        assert len(moves) == 2

    def test_pawn_cannot_move_forward_if_blocked(self):
        board = Board()
        white_pawn = Pawn('white')
        black_pawn = Pawn('black')
        board.set_piece((6, 4), white_pawn)
        board.set_piece((5, 4), black_pawn)

        moves = white_pawn.get_valid_moves((6, 4), board)

        assert len(moves) == 0

    def test_pawn_captures_diagonally(self):
        board = Board()
        white_pawn = Pawn('white')
        black_pawn1 = Pawn('black')
        black_pawn2 = Pawn('black')
        board.set_piece((5, 4), white_pawn)
        board.set_piece((4, 3), black_pawn1)
        board.set_piece((4, 5), black_pawn2)

        moves = white_pawn.get_valid_moves((5, 4), board)

        assert (4, 4) in moves
        assert (4, 3) in moves
        assert (4, 5) in moves
        assert len(moves) == 3

    def test_pawn_cannot_capture_own_piece(self):
        board = Board()
        white_pawn1 = Pawn('white')
        white_pawn2 = Pawn('white')
        board.set_piece((5, 4), white_pawn1)
        board.set_piece((4, 3), white_pawn2)

        moves = white_pawn1.get_valid_moves((5, 4), board)

        assert (4, 3) not in moves

    def test_pawn_visibility_from_starting_row(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((6, 4), pawn)

        visible = pawn.get_visible_squares((6, 4), board)

        assert (5, 4) in visible
        assert (4, 4) in visible
        assert (5, 3) in visible
        assert (5, 5) in visible
        assert len(visible) == 4

    def test_pawn_visibility_after_moving(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((5, 4), pawn)

        visible = pawn.get_visible_squares((5, 4), board)

        assert (4, 4) in visible
        assert (4, 3) in visible
        assert (4, 5) in visible
        assert len(visible) == 3
