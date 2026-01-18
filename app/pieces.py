"""King piece for the 3x3 fog-of-war game."""
from typing import List, Set, Tuple


class King:
    """King piece - moves one square in any direction."""

    def __init__(self, color: str):
        self.color = color

    @property
    def piece_type(self) -> str:
        return 'king'

    @property
    def symbol(self) -> str:
        return '\u2654' if self.color == 'white' else '\u265a'

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for the king."""
        moves = []
        row, col = pos
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            new_pos = (row + dr, col + dc)
            if board.is_valid_pos(new_pos):
                target = board.get_piece(new_pos)
                if target is None or target.color != self.color:
                    moves.append(new_pos)

        return moves

    def get_visible_squares(self, pos: Tuple[int, int], board) -> Set[Tuple[int, int]]:
        """Get all squares visible to the king (adjacent squares)."""
        row, col = pos
        visible = set()
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            new_pos = (row + dr, col + dc)
            if board.is_valid_pos(new_pos):
                visible.add(new_pos)

        return visible

    def copy(self) -> 'King':
        """Create a copy of this piece."""
        return King(self.color)
