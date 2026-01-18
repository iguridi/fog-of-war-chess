"""Unit tests for chess pieces."""
import pytest
from app.board import Board
from app.pieces import King, Pawn


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

        # Corner king can only move to 3 squares
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

        # King sees all 8 adjacent squares
        assert len(visible) == 8

    def test_corner_visibility(self):
        board = Board()
        king = King('white')
        board.set_piece((0, 0), king)

        visible = king.get_visible_squares((0, 0), board)

        # Corner king sees only 3 squares
        assert len(visible) == 3


class TestPawn:
    def test_white_pawn_moves_forward_one(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((5, 4), pawn)  # Not on starting row

        moves = pawn.get_valid_moves((5, 4), board)

        assert (4, 4) in moves
        assert len(moves) == 1

    def test_white_pawn_moves_forward_two_from_start(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((6, 4), pawn)  # Starting row for white

        moves = pawn.get_valid_moves((6, 4), board)

        assert (5, 4) in moves
        assert (4, 4) in moves
        assert len(moves) == 2

    def test_black_pawn_moves_forward_one(self):
        board = Board()
        pawn = Pawn('black')
        board.set_piece((2, 4), pawn)  # Not on starting row

        moves = pawn.get_valid_moves((2, 4), board)

        assert (3, 4) in moves
        assert len(moves) == 1

    def test_black_pawn_moves_forward_two_from_start(self):
        board = Board()
        pawn = Pawn('black')
        board.set_piece((1, 4), pawn)  # Starting row for black

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

        assert (4, 4) in moves  # Forward
        assert (4, 3) in moves  # Capture left
        assert (4, 5) in moves  # Capture right
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

        # Forward one, forward two, and both diagonals
        assert (5, 4) in visible
        assert (4, 4) in visible
        assert (5, 3) in visible
        assert (5, 5) in visible
        assert len(visible) == 4

    def test_pawn_visibility_after_moving(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((5, 4), pawn)  # Not on starting row

        visible = pawn.get_visible_squares((5, 4), board)

        # Forward one and both diagonals (no two-square move)
        assert (4, 4) in visible
        assert (4, 3) in visible
        assert (4, 5) in visible
        assert len(visible) == 3

    def test_pawn_edge_visibility(self):
        board = Board()
        pawn = Pawn('white')
        board.set_piece((5, 0), pawn)  # Left edge

        visible = pawn.get_visible_squares((5, 0), board)

        # Forward and right diagonal only
        assert (4, 0) in visible
        assert (4, 1) in visible
        assert len(visible) == 2
