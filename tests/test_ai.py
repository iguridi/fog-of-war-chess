"""Unit tests for AI move generation."""
import pytest
from app.board import Board
from app.pieces import King, Queen, Rook, Pawn
from app.ai import AI


class TestAILegalMoves:
    def test_ai_returns_legal_move(self):
        board = Board()
        board.set_piece((0, 4), King('black'))
        board.set_piece((7, 4), King('white'))

        ai = AI(depth=1)
        move = ai.get_move(board, 'black')

        assert move is not None
        from_pos, to_pos, _ = move

        # Verify it's a legal king move
        king_moves = [(0, 3), (0, 5), (1, 3), (1, 4), (1, 5)]
        assert to_pos in king_moves

    def test_ai_captures_visible_material(self):
        board = Board()
        black_queen = Queen('black')
        white_pawn = Pawn('white')
        black_king = King('black')
        white_king = King('white')

        board.set_piece((4, 4), black_queen)
        board.set_piece((4, 7), white_pawn)  # Visible to queen
        board.set_piece((0, 0), black_king)
        board.set_piece((7, 7), white_king)

        ai = AI(depth=2)
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI should prefer capturing the pawn
        assert to_pos == (4, 7)

    def test_ai_captures_king_immediately(self):
        board = Board()
        black_queen = Queen('black')
        white_king = King('white')
        black_king = King('black')

        board.set_piece((4, 4), black_queen)
        board.set_piece((4, 7), white_king)  # King in queen's line of sight
        board.set_piece((0, 0), black_king)

        ai = AI(depth=1)
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI must capture the king
        assert to_pos == (4, 7)

    def test_ai_only_moves_to_visible_squares(self):
        board = Board()
        # Set up a position where AI has limited visibility
        black_king = King('black')
        white_king = King('white')
        white_queen = Queen('white')

        board.set_piece((0, 0), black_king)
        board.set_piece((7, 7), white_king)
        board.set_piece((4, 4), white_queen)

        ai = AI(depth=1)
        move = ai.get_move(board, 'black')

        assert move is not None
        from_pos, to_pos, _ = move

        # Black can only see adjacent squares to king
        visible = board.get_visible_squares('black')
        assert to_pos in visible


class TestAIEvaluation:
    def test_ai_values_material(self):
        ai = AI()

        board1 = Board()
        board1.set_piece((0, 0), King('black'))
        board1.set_piece((7, 7), King('white'))
        board1.set_piece((4, 4), Queen('black'))

        board2 = Board()
        board2.set_piece((0, 0), King('black'))
        board2.set_piece((7, 7), King('white'))
        board2.set_piece((4, 4), Pawn('black'))

        eval1 = ai._evaluate_board(board1, 'black')
        eval2 = ai._evaluate_board(board2, 'black')

        # Board with queen should be valued higher
        assert eval1 > eval2


class TestAISimulation:
    def test_ai_vs_ai_game_completes(self):
        """Test that a full AI vs AI game terminates."""
        board = Board()

        # Simple setup with just kings and pawns
        board.set_piece((0, 4), King('black'))
        board.set_piece((1, 4), Pawn('black'))
        board.set_piece((7, 4), King('white'))
        board.set_piece((6, 4), Pawn('white'))

        ai = AI(depth=2)
        max_moves = 100
        current_color = 'white'
        moves_made = 0

        while moves_made < max_moves:
            move = ai.get_move(board, current_color)
            if move is None:
                break

            from_pos, to_pos, promotion = move
            piece = board.get_piece(from_pos)
            captured = board.get_piece(to_pos)

            # Check for king capture
            if captured and captured.piece_type == 'king':
                break

            board.set_piece(to_pos, piece)
            board.set_piece(from_pos, None)

            # Handle promotion
            if piece.piece_type == 'pawn':
                if (current_color == 'white' and to_pos[0] == 0) or \
                   (current_color == 'black' and to_pos[0] == 7):
                    from app.pieces import Queen
                    board.set_piece(to_pos, Queen(current_color))

            current_color = 'black' if current_color == 'white' else 'white'
            moves_made += 1

        # Game should terminate (either king captured or max moves)
        assert moves_made > 0
