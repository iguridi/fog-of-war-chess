"""Unit tests for king piece movement."""
import pytest
from app.board import Board
from app.pieces import King


class TestKing:
    def test_moves_one_square_all_directions(self):
        board = Board()
        king = King('white')
        board.set_piece((1, 1), king)  # Center of 3x3

        moves = king.get_valid_moves((1, 1), board)

        # King in center should have 8 moves
        expected = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
        assert sorted(moves) == sorted(expected)

    def test_cannot_move_off_board(self):
        board = Board()
        king = King('white')
        board.set_piece((0, 0), king)

        moves = king.get_valid_moves((0, 0), board)

        expected = [(0, 1), (1, 0), (1, 1)]
        assert sorted(moves) == sorted(expected)

    def test_can_capture_enemy(self):
        board = Board()
        white_king = King('white')
        black_king = King('black')
        board.set_piece((1, 1), white_king)
        board.set_piece((1, 2), black_king)

        moves = white_king.get_valid_moves((1, 1), board)

        assert (1, 2) in moves

    def test_cannot_capture_friendly(self):
        board = Board()
        king1 = King('white')
        king2 = King('white')
        board.set_piece((1, 1), king1)
        board.set_piece((1, 2), king2)

        moves = king1.get_valid_moves((1, 1), board)

        assert (1, 2) not in moves

    def test_visibility(self):
        board = Board()
        king = King('white')
        board.set_piece((1, 1), king)

        visible = king.get_visible_squares((1, 1), board)

        expected = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)}
        assert visible == expected

    def test_corner_visibility(self):
        board = Board()
        king = King('white')
        board.set_piece((0, 0), king)

        visible = king.get_visible_squares((0, 0), board)

        expected = {(0, 1), (1, 0), (1, 1)}
        assert visible == expected
