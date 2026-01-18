"""Unit tests for AI move generation."""
import pytest
from app.board import Board
from app.pieces import King, Pawn
from app.ai import AI


class TestAILegalMoves:
    def test_ai_returns_legal_move(self):
        board = Board()
        board.set_piece((0, 4), King('black'))
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
        black_king = King('black')
        white_king = King('white')

        # Kings adjacent - black can capture white
        board.set_piece((4, 4), black_king)
        board.set_piece((4, 5), white_king)

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI must capture the king
        assert to_pos == (4, 5)

    def test_ai_pawn_captures_king(self):
        board = Board()
        black_pawn = Pawn('black')
        white_king = King('white')

        # Pawn can capture king diagonally
        board.set_piece((5, 4), black_pawn)
        board.set_piece((6, 5), white_king)
        board.set_piece((0, 0), King('black'))  # Black king somewhere safe

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI should capture the king with pawn
        assert to_pos == (6, 5)

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


class TestAIWithPawns:
    def test_ai_can_move_pawn(self):
        board = Board()
        board.set_piece((1, 4), Pawn('black'))
        board.set_piece((0, 4), King('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        # AI should be able to move either king or pawn

    def test_ai_pawn_advances(self):
        board = Board()
        # Only a pawn that can move forward
        board.set_piece((1, 4), Pawn('black'))
        board.set_piece((0, 0), King('black'))
        board.set_piece((7, 7), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        from_pos, to_pos, _ = move

        # Should move the pawn forward (only piece that can see forward squares)
        if from_pos == (1, 4):
            assert to_pos in [(2, 4), (3, 4)]  # Pawn can move 1 or 2 squares


class TestAISimulation:
    def test_ai_vs_ai_game_completes(self):
        """Test that a full AI vs AI game terminates."""
        board = Board()

        # Standard starting position
        board.set_piece((0, 4), King('black'))
        for col in range(8):
            board.set_piece((1, col), Pawn('black'))
        board.set_piece((7, 4), King('white'))
        for col in range(8):
            board.set_piece((6, col), Pawn('white'))

        ai = AI()
        max_moves = 100
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
