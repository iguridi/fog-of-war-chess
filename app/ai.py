"""Random AI opponent for the 3x3 fog-of-war game."""
import random
from typing import Optional, Tuple, List


class AI:
    """AI that picks a random legal move."""

    def get_move(self, board, color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int], None]]:
        """Get a random legal move for the AI."""
        moves = self._get_all_moves(board, color)
        if not moves:
            return None

        # Check for immediate king capture
        for from_pos, to_pos in moves:
            target = board.get_piece(to_pos)
            if target and target.piece_type == 'king':
                return (from_pos, to_pos, None)

        # Pick a random move
        from_pos, to_pos = random.choice(moves)
        return (from_pos, to_pos, None)

    def _get_all_moves(self, board, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all legal moves for a color."""
        moves = []
        visible = board.get_visible_squares(color)

        for pos, piece in board.get_all_pieces(color):
            piece_moves = piece.get_valid_moves(pos, board)
            for to_pos in piece_moves:
                # AI can only move to squares it can see (fog-of-war)
                if to_pos in visible:
                    moves.append((pos, to_pos))

        return moves
