"""Chess pieces for the fog-of-war game."""
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


class Pawn:
    """Pawn piece - moves forward 1 (or 2 from start), captures diagonally."""

    def __init__(self, color: str):
        self.color = color
        self.has_moved = False

    @property
    def piece_type(self) -> str:
        return 'pawn'

    @property
    def symbol(self) -> str:
        return '\u2659' if self.color == 'white' else '\u265f'

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for the pawn."""
        moves = []
        row, col = pos

        # Direction depends on color: white moves up (decreasing row), black moves down
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Move forward one square
        new_row = row + direction
        if 0 <= new_row < board.SIZE:
            if board.is_empty((new_row, col)):
                moves.append((new_row, col))

                # Move forward two squares from starting position
                if row == start_row:
                    two_forward = row + (2 * direction)
                    if 0 <= two_forward < board.SIZE and board.is_empty((two_forward, col)):
                        moves.append((two_forward, col))

        # Capture diagonally
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_row < board.SIZE and 0 <= new_col < board.SIZE:
                target = board.get_piece((new_row, new_col))
                if target and target.color != self.color:
                    moves.append((new_row, new_col))

        return moves

    def get_visible_squares(self, pos: Tuple[int, int], board) -> Set[Tuple[int, int]]:
        """Get all squares visible to the pawn (forward squares and diagonal attack squares)."""
        visible = set()
        row, col = pos

        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Forward squares (one and potentially two)
        new_row = row + direction
        if 0 <= new_row < board.SIZE:
            visible.add((new_row, col))

            # Two squares forward from start
            if row == start_row:
                two_forward = row + (2 * direction)
                if 0 <= two_forward < board.SIZE:
                    visible.add((two_forward, col))

        # Diagonal attack squares (always visible, even if empty)
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_row < board.SIZE and 0 <= new_col < board.SIZE:
                visible.add((new_row, new_col))

        return visible

    def copy(self) -> 'Pawn':
        """Create a copy of this piece."""
        new_pawn = Pawn(self.color)
        new_pawn.has_moved = self.has_moved
        return new_pawn
