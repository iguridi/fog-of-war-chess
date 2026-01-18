"""Unit tests for AI move generation."""
import pytest
from app.board import Board
from app.pieces import King, Queen, Rook, Bishop, Knight, Pawn
from app.ai import AI


class TestAILegalMoves:
    def test_ai_returns_legal_move(self):
        board = Board()
        # Set up standard black position
        board.set_piece((0, 4), King('black'))
        board.set_piece((0, 1), Knight('black'))
        for col in range(8):
            board.set_piece((1, col), Pawn('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        from_pos, to_pos, _ = move

        # Verify it's a legal move
        piece = board.get_piece(from_pos)
        valid_moves = piece.get_valid_moves(from_pos, board)
        assert to_pos in valid_moves

    def test_ai_captures_king_immediately(self):
        board = Board()
        black_queen = Queen('black')
        white_king = King('white')

        # Queen can capture king
        board.set_piece((4, 4), black_queen)
        board.set_piece((4, 7), white_king)
        board.set_piece((0, 0), King('black'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI must capture the king
        assert to_pos == (4, 7)

    def test_ai_rook_captures_king(self):
        board = Board()
        black_rook = Rook('black')
        white_king = King('white')

        # Rook can capture king on same file
        board.set_piece((0, 4), black_rook)
        board.set_piece((7, 4), white_king)
        board.set_piece((0, 0), King('black'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        assert to_pos == (7, 4)

    def test_ai_only_moves_to_visible_squares(self):
        board = Board()
        black_king = King('black')
        white_king = King('white')

        board.set_piece((0, 0), black_king)
        board.set_piece((7, 7), white_king)

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        from_pos, to_pos, _ = move

        # Black can only see adjacent squares to king
        visible = board.get_visible_squares('black')
        assert to_pos in visible

    def test_ai_returns_none_when_no_moves(self):
        """Test AI handles case with no legal moves gracefully."""
        board = Board()
        # Only white king, no black pieces
        board.set_piece((4, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is None


class TestAIWithAllPieces:
    def test_ai_can_move_knight(self):
        board = Board()
        board.set_piece((0, 1), Knight('black'))
        board.set_piece((0, 4), King('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None

    def test_ai_can_move_bishop(self):
        board = Board()
        board.set_piece((0, 2), Bishop('black'))
        board.set_piece((0, 4), King('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None

    def test_ai_can_move_rook(self):
        board = Board()
        board.set_piece((0, 0), Rook('black'))
        board.set_piece((0, 4), King('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None

    def test_ai_can_move_queen(self):
        board = Board()
        board.set_piece((0, 3), Queen('black'))
        board.set_piece((0, 4), King('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None


class TestAISimulation:
    def test_ai_vs_ai_game_completes(self):
        """Test that a full AI vs AI game terminates."""
        board = Board()

        # Standard starting position
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

        ai = AI()
        max_moves = 50
        current_color = 'white'
        moves_made = 0
        game_over = False

        while moves_made < max_moves and not game_over:
            move = ai.get_move(board, current_color)
            if move is None:
                break

            from_pos, to_pos, _ = move
            piece = board.get_piece(from_pos)
            captured = board.get_piece(to_pos)

            # Check for king capture
            if captured and captured.piece_type == 'king':
                game_over = True
                break

            board.set_piece(to_pos, piece)
            board.set_piece(from_pos, None)

            current_color = 'black' if current_color == 'white' else 'white'
            moves_made += 1

        # Game should have made at least one move
        assert moves_made > 0
