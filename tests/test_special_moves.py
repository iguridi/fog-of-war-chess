"""Unit tests for special chess moves: castling, en passant, promotion."""
import pytest
from app.board import Board
from app.game import Game
from app.pieces import King, Queen, Rook, Bishop, Knight, Pawn


class TestCastling:
    def test_kingside_castling_available(self):
        """King can castle kingside when conditions are met."""
        board = Board()
        king = King('white')
        rook = Rook('white')
        board.set_piece((7, 4), king)  # e1
        board.set_piece((7, 7), rook)  # h1

        moves = king.get_valid_moves((7, 4), board)

        assert (7, 6) in moves  # g1 - castling destination

    def test_queenside_castling_available(self):
        """King can castle queenside when conditions are met."""
        board = Board()
        king = King('white')
        rook = Rook('white')
        board.set_piece((7, 4), king)  # e1
        board.set_piece((7, 0), rook)  # a1

        moves = king.get_valid_moves((7, 4), board)

        assert (7, 2) in moves  # c1 - castling destination

    def test_cannot_castle_after_king_moved(self):
        """King cannot castle after it has moved."""
        board = Board()
        king = King('white')
        king.has_moved = True
        rook = Rook('white')
        board.set_piece((7, 4), king)
        board.set_piece((7, 7), rook)

        moves = king.get_valid_moves((7, 4), board)

        assert (7, 6) not in moves

    def test_cannot_castle_after_rook_moved(self):
        """King cannot castle after the rook has moved."""
        board = Board()
        king = King('white')
        rook = Rook('white')
        rook.has_moved = True
        board.set_piece((7, 4), king)
        board.set_piece((7, 7), rook)

        moves = king.get_valid_moves((7, 4), board)

        assert (7, 6) not in moves

    def test_cannot_castle_with_pieces_in_way(self):
        """King cannot castle if pieces block the path."""
        board = Board()
        king = King('white')
        rook = Rook('white')
        bishop = Bishop('white')
        board.set_piece((7, 4), king)
        board.set_piece((7, 7), rook)
        board.set_piece((7, 5), bishop)  # Blocking piece

        moves = king.get_valid_moves((7, 4), board)

        assert (7, 6) not in moves

    def test_castling_executes_correctly_kingside(self):
        """Kingside castling moves both king and rook."""
        game = Game()
        game.board = Board()
        king = King('white')
        rook = Rook('white')
        game.board.set_piece((7, 4), king)
        game.board.set_piece((7, 7), rook)
        # Need black king to avoid issues
        game.board.set_piece((0, 4), King('black'))

        game._execute_move((7, 4), (7, 6))

        assert game.board.get_piece((7, 6)).piece_type == 'king'
        assert game.board.get_piece((7, 5)).piece_type == 'rook'
        assert game.board.get_piece((7, 4)) is None
        assert game.board.get_piece((7, 7)) is None

    def test_castling_executes_correctly_queenside(self):
        """Queenside castling moves both king and rook."""
        game = Game()
        game.board = Board()
        king = King('white')
        rook = Rook('white')
        game.board.set_piece((7, 4), king)
        game.board.set_piece((7, 0), rook)
        game.board.set_piece((0, 4), King('black'))

        game._execute_move((7, 4), (7, 2))

        assert game.board.get_piece((7, 2)).piece_type == 'king'
        assert game.board.get_piece((7, 3)).piece_type == 'rook'
        assert game.board.get_piece((7, 4)) is None
        assert game.board.get_piece((7, 0)) is None

    def test_black_can_castle(self):
        """Black can also castle."""
        board = Board()
        king = King('black')
        rook = Rook('black')
        board.set_piece((0, 4), king)  # e8
        board.set_piece((0, 7), rook)  # h8

        moves = king.get_valid_moves((0, 4), board)

        assert (0, 6) in moves


class TestEnPassant:
    def test_en_passant_target_set_on_double_push(self):
        """En passant target is set when pawn double-pushes."""
        game = Game()
        game.board = Board()
        pawn = Pawn('white')
        game.board.set_piece((6, 4), pawn)  # e2
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 4), King('black'))

        game._execute_move((6, 4), (4, 4))  # e2-e4

        assert game.en_passant_target == (5, 4)  # e3

    def test_en_passant_capture_available(self):
        """Pawn can capture en passant when target is set."""
        board = Board()
        white_pawn = Pawn('white')
        white_pawn.has_moved = True
        board.set_piece((3, 4), white_pawn)  # White pawn on e5

        # En passant target is f6 (as if black just pushed f7-f5)
        en_passant_target = (2, 5)

        moves = white_pawn.get_valid_moves((3, 4), board, en_passant_target)

        assert (2, 5) in moves  # Can capture en passant on f6

    def test_en_passant_capture_executes(self):
        """En passant capture removes the enemy pawn."""
        game = Game()
        game.board = Board()
        white_pawn = Pawn('white')
        black_pawn = Pawn('black')
        game.board.set_piece((3, 4), white_pawn)  # White pawn on e5
        game.board.set_piece((3, 5), black_pawn)  # Black pawn on f5
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 4), King('black'))

        # Set en passant target as if black just pushed f7-f5
        game.en_passant_target = (2, 5)

        game._execute_move((3, 4), (2, 5))  # exf6 en passant

        assert game.board.get_piece((2, 5)).piece_type == 'pawn'
        assert game.board.get_piece((2, 5)).color == 'white'
        assert game.board.get_piece((3, 5)) is None  # Black pawn captured
        assert game.board.get_piece((3, 4)) is None  # Original square empty

    def test_en_passant_target_resets_after_move(self):
        """En passant target is reset after any move."""
        game = Game()
        game.board = Board()
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 4), King('black'))
        game.en_passant_target = (2, 5)

        # Make a non-en-passant move
        game._execute_move((7, 4), (7, 3))

        assert game.en_passant_target is None

    def test_en_passant_only_available_immediately(self):
        """En passant is not available if target is not set."""
        board = Board()
        white_pawn = Pawn('white')
        black_pawn = Pawn('black')
        board.set_piece((3, 4), white_pawn)  # White pawn on e5
        board.set_piece((3, 5), black_pawn)  # Black pawn on f5 (but no en passant)

        moves = white_pawn.get_valid_moves((3, 4), board, None)

        assert (2, 5) not in moves  # Cannot capture en passant


class TestPawnPromotion:
    def test_pawn_promotes_to_queen(self):
        """Pawn reaching last rank becomes a queen."""
        game = Game()
        game.board = Board()
        pawn = Pawn('white')
        game.board.set_piece((1, 4), pawn)  # White pawn on e7
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 0), King('black'))

        game._execute_move((1, 4), (0, 4))  # e7-e8

        promoted_piece = game.board.get_piece((0, 4))
        assert promoted_piece.piece_type == 'queen'
        assert promoted_piece.color == 'white'

    def test_pawn_promotes_on_capture(self):
        """Pawn promotes when capturing on last rank."""
        game = Game()
        game.board = Board()
        pawn = Pawn('white')
        enemy_rook = Rook('black')
        game.board.set_piece((1, 4), pawn)
        game.board.set_piece((0, 5), enemy_rook)
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 0), King('black'))

        game._execute_move((1, 4), (0, 5))  # exf8=Q

        promoted_piece = game.board.get_piece((0, 5))
        assert promoted_piece.piece_type == 'queen'
        assert promoted_piece.color == 'white'

    def test_black_pawn_promotes(self):
        """Black pawn also promotes when reaching rank 1."""
        game = Game()
        game.board = Board()
        pawn = Pawn('black')
        game.board.set_piece((6, 4), pawn)  # Black pawn on e2
        game.board.set_piece((0, 4), King('black'))
        game.board.set_piece((7, 0), King('white'))

        game._execute_move((6, 4), (7, 4))  # e2-e1

        promoted_piece = game.board.get_piece((7, 4))
        assert promoted_piece.piece_type == 'queen'
        assert promoted_piece.color == 'black'


class TestHasMovedTracking:
    def test_king_has_moved_updates(self):
        """King's has_moved is set after moving."""
        game = Game()
        game.board = Board()
        king = King('white')
        game.board.set_piece((7, 4), king)
        game.board.set_piece((0, 4), King('black'))

        assert king.has_moved is False
        game._execute_move((7, 4), (7, 5))
        assert king.has_moved is True

    def test_rook_has_moved_updates(self):
        """Rook's has_moved is set after moving."""
        game = Game()
        game.board = Board()
        rook = Rook('white')
        game.board.set_piece((7, 0), rook)
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 4), King('black'))

        assert rook.has_moved is False
        game._execute_move((7, 0), (7, 1))
        assert rook.has_moved is True

    def test_pawn_has_moved_updates(self):
        """Pawn's has_moved is set after moving."""
        game = Game()
        game.board = Board()
        pawn = Pawn('white')
        game.board.set_piece((6, 4), pawn)
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 4), King('black'))

        assert pawn.has_moved is False
        game._execute_move((6, 4), (4, 4))
        assert pawn.has_moved is True

    def test_king_copy_preserves_has_moved(self):
        """Copying a king preserves has_moved state."""
        king = King('white')
        king.has_moved = True

        copy = king.copy()

        assert copy.has_moved is True

    def test_rook_copy_preserves_has_moved(self):
        """Copying a rook preserves has_moved state."""
        rook = Rook('white')
        rook.has_moved = True

        copy = rook.copy()

        assert copy.has_moved is True


class TestSpecialMovesIntegration:
    def test_full_castling_through_game(self):
        """Test castling through the normal game flow."""
        game = Game()
        # Clear pieces between king and rook for white
        game.board.set_piece((7, 5), None)  # Clear bishop
        game.board.set_piece((7, 6), None)  # Clear knight

        # Now white can castle kingside
        result = game.make_player_move((7, 4), (7, 6))

        assert result['success'] is True
        assert game.board.get_piece((7, 6)).piece_type == 'king'
        assert game.board.get_piece((7, 5)).piece_type == 'rook'

    def test_en_passant_through_game(self):
        """Test en passant through the normal game flow."""
        game = Game()
        game.board = Board()

        # Set up position for en passant
        white_pawn = Pawn('white')
        white_pawn.has_moved = True
        black_pawn = Pawn('black')

        game.board.set_piece((3, 4), white_pawn)  # White pawn on e5
        game.board.set_piece((1, 5), black_pawn)  # Black pawn on f7
        game.board.set_piece((7, 4), King('white'))
        game.board.set_piece((0, 4), King('black'))

        # First, black double-pushes (simulate by setting en passant target)
        game.en_passant_target = (2, 5)  # f6
        game.board.set_piece((3, 5), black_pawn)  # Move black pawn to f5
        game.board.set_piece((1, 5), None)

        # White captures en passant
        result = game.make_player_move((3, 4), (2, 5))

        assert result['success'] is True
        assert game.board.get_piece((2, 5)).piece_type == 'pawn'
        assert game.board.get_piece((2, 5)).color == 'white'
        assert game.board.get_piece((3, 5)) is None  # Black pawn captured
