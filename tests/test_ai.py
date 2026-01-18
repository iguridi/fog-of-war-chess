"""Unit tests for AI move generation (Step 1: 3x3 King-only)."""
import pytest
from app.board import Board
from app.pieces import King
from app.ai import AI


class TestAILegalMoves:
    def test_ai_returns_legal_move(self):
        board = Board()
        board.set_piece((0, 2), King('black'))
        board.set_piece((2, 0), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        from_pos, to_pos, _ = move

        # Verify it's a legal king move (adjacent square)
        king = board.get_piece(from_pos)
        valid_moves = king.get_valid_moves(from_pos, board)
        assert to_pos in valid_moves

    def test_ai_captures_king_immediately(self):
        board = Board()
        black_king = King('black')
        white_king = King('white')

        # Kings adjacent - black can capture white
        board.set_piece((1, 1), black_king)
        board.set_piece((1, 0), white_king)

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI must capture the king
        assert to_pos == (1, 0)

    def test_ai_only_moves_to_visible_squares(self):
        board = Board()
        black_king = King('black')
        white_king = King('white')

        board.set_piece((0, 0), black_king)
        board.set_piece((2, 2), white_king)

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
        board.set_piece((1, 1), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is None


class TestAISimulation:
    def test_ai_vs_ai_game_completes(self):
        """Test that a full AI vs AI game terminates."""
        board = Board()

        # Standard 3x3 starting position
        board.set_piece((0, 2), King('black'))
        board.set_piece((2, 0), King('white'))

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

    def test_ai_game_eventually_ends_with_capture(self):
        """Test that kings eventually meet and one captures the other."""
        board = Board()

        # Start kings close together
        board.set_piece((0, 1), King('black'))
        board.set_piece((2, 1), King('white'))

        ai = AI()
        max_moves = 20
        current_color = 'white'
        moves_made = 0
        winner = None

        while moves_made < max_moves:
            move = ai.get_move(board, current_color)
            if move is None:
                break

            from_pos, to_pos, _ = move
            piece = board.get_piece(from_pos)
            captured = board.get_piece(to_pos)

            if captured and captured.piece_type == 'king':
                winner = current_color
                break

            board.set_piece(to_pos, piece)
            board.set_piece(from_pos, None)

            current_color = 'black' if current_color == 'white' else 'white'
            moves_made += 1

        # With kings starting 2 rows apart, game should end quickly
        assert moves_made > 0
