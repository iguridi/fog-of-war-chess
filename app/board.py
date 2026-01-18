"""Board representation for 8x8 fog-of-war chess game."""
from typing import Optional, Set, Tuple


class Board:
    """Represents an 8x8 board for the fog-of-war chess game."""

    SIZE = 8

    def __init__(self):
        """Initialize an empty 8x8 board."""
        self.grid = [[None for _ in range(self.SIZE)] for _ in range(self.SIZE)]

    def get_piece(self, pos: Tuple[int, int]):
        """Get the piece at the given position."""
        row, col = pos
        if 0 <= row < self.SIZE and 0 <= col < self.SIZE:
            return self.grid[row][col]
        return None

    def set_piece(self, pos: Tuple[int, int], piece):
        """Set a piece at the given position."""
        row, col = pos
        if 0 <= row < self.SIZE and 0 <= col < self.SIZE:
            self.grid[row][col] = piece

    def is_valid_pos(self, pos: Tuple[int, int]) -> bool:
        """Check if a position is within the board."""
        row, col = pos
        return 0 <= row < self.SIZE and 0 <= col < self.SIZE

    def is_empty(self, pos: Tuple[int, int]) -> bool:
        """Check if a position is empty."""
        return self.get_piece(pos) is None

    def get_all_pieces(self, color: str) -> list:
        """Get all pieces of a given color with their positions."""
        pieces = []
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    pieces.append(((row, col), piece))
        return pieces

    def get_visible_squares(self, color: str) -> Set[Tuple[int, int]]:
        """Get all squares visible to a player based on their pieces."""
        visible = set()

        for pos, piece in self.get_all_pieces(color):
            # The square the piece is on is always visible
            visible.add(pos)

            # Add squares the piece can move to or attack
            visible_from_piece = piece.get_visible_squares(pos, self)
            visible.update(visible_from_piece)

        return visible

    def find_king(self, color: str) -> Optional[Tuple[int, int]]:
        """Find the position of a king of the given color."""
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                piece = self.grid[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    return (row, col)
        return None

    def copy(self) -> 'Board':
        """Create a copy of the board for simulation."""
        new_board = Board()
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                piece = self.grid[row][col]
                if piece:
                    new_board.grid[row][col] = piece.copy()
        return new_board
