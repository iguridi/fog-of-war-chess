"""Smart AI opponent using minimax with alpha-beta pruning."""
import random
from typing import Optional, Tuple, List


# Piece values for material evaluation
PIECE_VALUES = {
    'king': 10000,    # Must be very high - losing king loses the game
    'queen': 900,
    'rook': 500,
    'bishop': 330,
    'knight': 320,
    'pawn': 100,
}

# Position bonuses - encourage pieces to control the center
# Values are for white (flip for black)
POSITION_BONUS = {
    'pawn': [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0],
    ],
    'knight': [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50],
    ],
    'bishop': [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20],
    ],
    'rook': [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0],
    ],
    'queen': [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20],
    ],
    'king': [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20],
    ],
}


class AI:
    """AI that uses minimax with alpha-beta pruning."""

    def __init__(self, depth: int = 3):
        """Initialize AI with search depth."""
        self.depth = depth

    def get_move(self, board, color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int], None]]:
        """Get the best move for the AI using minimax."""
        moves = self._get_all_moves(board, color)
        if not moves:
            return None

        # Check for immediate king capture - always take it
        for from_pos, to_pos in moves:
            target = board.get_piece(to_pos)
            if target and target.piece_type == 'king':
                return (from_pos, to_pos, None)

        # Use minimax to find best move
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # Shuffle moves for variety when scores are equal
        random.shuffle(moves)

        for from_pos, to_pos in moves:
            # Simulate the move
            new_board = self._make_move(board, from_pos, to_pos)

            # Evaluate with minimax (opponent's turn next, so minimize)
            score = self._minimax(new_board, self.depth - 1, alpha, beta, False, color)

            if score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)

            alpha = max(alpha, score)

        if best_move:
            return (best_move[0], best_move[1], None)

        # Fallback to random move if minimax fails
        from_pos, to_pos = random.choice(moves)
        return (from_pos, to_pos, None)

    def _minimax(self, board, depth: int, alpha: float, beta: float,
                 is_maximizing: bool, ai_color: str) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        opponent_color = 'white' if ai_color == 'black' else 'black'
        current_color = ai_color if is_maximizing else opponent_color

        # Check for game over conditions
        ai_king_pos = board.find_king(ai_color)
        opponent_king_pos = board.find_king(opponent_color)

        if ai_king_pos is None:
            return float('-inf')  # AI lost
        if opponent_king_pos is None:
            return float('inf')   # AI won

        # Base case: depth reached
        if depth == 0:
            return self._evaluate_board(board, ai_color)

        moves = self._get_all_moves(board, current_color)

        if not moves:
            # No moves available - evaluate current position
            return self._evaluate_board(board, ai_color)

        if is_maximizing:
            max_eval = float('-inf')
            for from_pos, to_pos in moves:
                new_board = self._make_move(board, from_pos, to_pos)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, False, ai_color)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for from_pos, to_pos in moves:
                new_board = self._make_move(board, from_pos, to_pos)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, True, ai_color)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def _evaluate_board(self, board, ai_color: str) -> float:
        """
        Evaluate the board from AI's perspective.
        Only considers pieces the AI can see (fog-of-war applies).
        """
        opponent_color = 'white' if ai_color == 'black' else 'black'
        visible = board.get_visible_squares(ai_color)

        score = 0.0

        # Evaluate AI's own pieces (always visible)
        for pos, piece in board.get_all_pieces(ai_color):
            score += self._get_piece_value(piece, pos, ai_color)

        # Evaluate opponent pieces that are visible
        for pos, piece in board.get_all_pieces(opponent_color):
            if pos in visible:
                score -= self._get_piece_value(piece, pos, opponent_color)
            else:
                # Unknown pieces - assume average piece value to be cautious
                score -= 300  # Roughly average minor piece value

        # Bonus for controlling more visible squares
        ai_visible = len(board.get_visible_squares(ai_color))
        opponent_visible = len(board.get_visible_squares(opponent_color))
        score += (ai_visible - opponent_visible) * 2  # Small bonus per visible square

        return score

    def _get_piece_value(self, piece, pos: Tuple[int, int], color: str) -> float:
        """Get the value of a piece including position bonus."""
        base_value = PIECE_VALUES.get(piece.piece_type, 0)

        # Get position bonus
        row, col = pos
        position_table = POSITION_BONUS.get(piece.piece_type)

        if position_table:
            # Flip the table for black (black views board from opposite side)
            if color == 'black':
                row = 7 - row
            position_bonus = position_table[row][col]
        else:
            position_bonus = 0

        return base_value + position_bonus

    def _make_move(self, board, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """Make a move and return the new board state."""
        new_board = board.copy()
        piece = new_board.get_piece(from_pos)
        new_board.set_piece(to_pos, piece)
        new_board.set_piece(from_pos, None)
        return new_board

    def _get_all_moves(self, board, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all legal moves for a color (respecting fog-of-war)."""
        moves = []
        visible = board.get_visible_squares(color)

        for pos, piece in board.get_all_pieces(color):
            piece_moves = piece.get_valid_moves(pos, board)
            for to_pos in piece_moves:
                # AI can only move to squares it can see (fog-of-war)
                if to_pos in visible:
                    moves.append((pos, to_pos))

        return moves
