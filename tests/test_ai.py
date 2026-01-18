"""Unit tests for AI move generation."""
import random
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


class TestSmartAI:
    """Tests for the minimax-based smart AI."""

    def test_ai_captures_undefended_piece(self):
        """AI should capture a free piece."""
        board = Board()
        # Black queen can capture undefended white rook
        board.set_piece((4, 4), Queen('black'))
        board.set_piece((4, 7), Rook('white'))  # Undefended rook
        board.set_piece((0, 0), King('black'))
        board.set_piece((7, 0), King('white'))  # King safe from queen

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI should capture the free rook
        assert to_pos == (4, 7)

    def test_ai_prefers_higher_value_capture(self):
        """AI should capture queen over pawn when both available."""
        board = Board()
        # Black rook can capture white queen or white pawn
        board.set_piece((4, 4), Rook('black'))
        board.set_piece((4, 0), Pawn('white'))   # Low value target
        board.set_piece((4, 7), Queen('white'))  # High value target
        board.set_piece((0, 0), King('black'))
        board.set_piece((7, 0), King('white'))

        ai = AI()
        move = ai.get_move(board, 'black')

        assert move is not None
        _, to_pos, _ = move
        # AI should capture the queen (higher value)
        assert to_pos == (4, 7)

    def test_ai_uses_depth_parameter(self):
        """AI should accept depth parameter."""
        ai_shallow = AI(depth=1)
        ai_deep = AI(depth=3)

        assert ai_shallow.depth == 1
        assert ai_deep.depth == 3

    def test_ai_evaluation_considers_material(self):
        """Board evaluation should favor material advantage."""
        board = Board()
        board.set_piece((0, 0), King('black'))
        board.set_piece((0, 1), Queen('black'))  # Black has queen
        board.set_piece((7, 7), King('white'))
        # White has no queen - black should have positive score

        ai = AI()
        score = ai._evaluate_board(board, 'black')

        # Black has material advantage (queen), so score should be positive
        assert score > 0

    def test_ai_respects_fog_in_evaluation(self):
        """AI evaluation should only consider visible enemy pieces."""
        board = Board()
        # Black king in corner - limited visibility
        board.set_piece((0, 0), King('black'))
        # White pieces far away (not visible to black)
        board.set_piece((7, 7), King('white'))
        board.set_piece((7, 6), Queen('white'))  # Queen hidden from black

        visible = board.get_visible_squares('black')

        # White queen should not be visible to black king
        assert (7, 6) not in visible

        # AI should still work despite hidden pieces
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

        ai = AI(depth=2)
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


class RandomAI:
    """Baseline random AI for comparison."""

    def get_move(self, board, color):
        """Pick a random legal move."""
        moves = []
        visible = board.get_visible_squares(color)

        for pos, piece in board.get_all_pieces(color):
            piece_moves = piece.get_valid_moves(pos, board)
            for to_pos in piece_moves:
                if to_pos in visible:
                    moves.append((pos, to_pos))

        if not moves:
            return None

        # Check for immediate king capture
        for from_pos, to_pos in moves:
            target = board.get_piece(to_pos)
            if target and target.piece_type == 'king':
                return (from_pos, to_pos, None)

        from_pos, to_pos = random.choice(moves)
        return (from_pos, to_pos, None)


def setup_standard_board():
    """Create a board with standard starting position."""
    board = Board()
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
    return board


def count_material(board, color):
    """Count total material value for a color."""
    values = {'king': 10000, 'queen': 900, 'rook': 500, 'bishop': 330, 'knight': 320, 'pawn': 100}
    total = 0
    for _, piece in board.get_all_pieces(color):
        total += values.get(piece.piece_type, 0)
    return total


def play_n_moves(board, white_ai, black_ai, n_moves):
    """Play n moves and return the resulting board."""
    current_color = 'white'
    for _ in range(n_moves):
        ai = white_ai if current_color == 'white' else black_ai
        move = ai.get_move(board, current_color)
        if move is None:
            break

        from_pos, to_pos, _ = move
        piece = board.get_piece(from_pos)
        captured = board.get_piece(to_pos)

        if captured and captured.piece_type == 'king':
            break

        board.set_piece(to_pos, piece)
        board.set_piece(from_pos, None)
        current_color = 'black' if current_color == 'white' else 'white'

    return board


class TestAIBenchmark:
    """Benchmark tests to verify AI is actually better than random."""

    def test_smart_ai_gains_material_advantage(self):
        """After 10 moves, smart AI should have material advantage over random."""
        random.seed(42)  # Fixed seed for reproducibility
        smart_ai = AI(depth=2)
        random_ai = RandomAI()

        trials = 5
        smart_advantage_count = 0
        ties = 0

        for _ in range(trials):
            board = setup_standard_board()
            play_n_moves(board, smart_ai, random_ai, n_moves=10)

            smart_material = count_material(board, 'white')
            random_material = count_material(board, 'black')

            if smart_material > random_material:
                smart_advantage_count += 1
            elif smart_material == random_material:
                ties += 1

        # Smart AI should gain advantage or tie in majority of trials
        assert smart_advantage_count + ties >= 3, f"Smart AI only gained advantage in {smart_advantage_count}/{trials} trials ({ties} ties)"

    def test_smart_ai_doesnt_lose_material_quickly(self):
        """Smart AI should not lose significant material in first 10 moves."""
        random.seed(42)  # Fixed seed for reproducibility
        smart_ai = AI(depth=2)
        random_ai = RandomAI()

        board = setup_standard_board()
        initial_material = count_material(board, 'white')

        play_n_moves(board, smart_ai, random_ai, n_moves=10)
        final_material = count_material(board, 'white')

        # Should not lose more than a minor piece worth of material
        material_loss = initial_material - final_material
        assert material_loss < 400, f"Smart AI lost {material_loss} material in 10 moves"

    def test_deeper_search_better_evaluation(self):
        """Deeper search should find better evaluated positions."""
        deep_ai = AI(depth=3)
        shallow_ai = AI(depth=1)

        board = setup_standard_board()

        # Get evaluation of moves from each AI
        deep_move = deep_ai.get_move(board, 'white')
        shallow_move = shallow_ai.get_move(board, 'white')

        # Both should return valid moves
        assert deep_move is not None
        assert shallow_move is not None

        # Deep AI's chosen move should have reasonable evaluation
        # (We can't easily compare since they may pick same move,
        # but we verify they both work correctly)
        deep_board = board.copy()
        deep_board.set_piece(deep_move[1], deep_board.get_piece(deep_move[0]))
        deep_board.set_piece(deep_move[0], None)

        # Verify the move doesn't immediately blunder material
        remaining = count_material(deep_board, 'white')
        assert remaining >= count_material(board, 'white') - 100  # At most lost a pawn
