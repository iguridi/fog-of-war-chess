"""Chess pieces for the fog-of-war game."""
from typing import List, Set, Tuple


class King:
    """King piece - moves one square in any direction."""

    def __init__(self, color: str):
        self.color = color
        self.has_moved = False

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

        # Castling
        if not self.has_moved:
            back_row = 7 if self.color == 'white' else 0
            if row == back_row and col == 4:
                # Kingside castling (O-O)
                kingside_rook = board.get_piece((back_row, 7))
                if (kingside_rook and kingside_rook.piece_type == 'rook' and
                    not kingside_rook.has_moved and
                    board.is_empty((back_row, 5)) and
                    board.is_empty((back_row, 6))):
                    moves.append((back_row, 6))

                # Queenside castling (O-O-O)
                queenside_rook = board.get_piece((back_row, 0))
                if (queenside_rook and queenside_rook.piece_type == 'rook' and
                    not queenside_rook.has_moved and
                    board.is_empty((back_row, 1)) and
                    board.is_empty((back_row, 2)) and
                    board.is_empty((back_row, 3))):
                    moves.append((back_row, 2))

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
        new_king = King(self.color)
        new_king.has_moved = self.has_moved
        return new_king


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

    def get_valid_moves(self, pos: Tuple[int, int], board, en_passant_target=None) -> List[Tuple[int, int]]:
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
                # En passant capture
                elif en_passant_target and (new_row, new_col) == en_passant_target:
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


class Knight:
    """Knight piece - moves in L-shape, can jump over pieces."""

    def __init__(self, color: str):
        self.color = color

    @property
    def piece_type(self) -> str:
        return 'knight'

    @property
    def symbol(self) -> str:
        return '\u2658' if self.color == 'white' else '\u265e'

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for the knight."""
        moves = []
        row, col = pos
        # L-shape moves: 2 squares in one direction, 1 in perpendicular
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in offsets:
            new_pos = (row + dr, col + dc)
            if board.is_valid_pos(new_pos):
                target = board.get_piece(new_pos)
                if target is None or target.color != self.color:
                    moves.append(new_pos)

        return moves

    def get_visible_squares(self, pos: Tuple[int, int], board) -> Set[Tuple[int, int]]:
        """Get all squares visible to the knight (all L-shape destinations)."""
        visible = set()
        row, col = pos
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in offsets:
            new_pos = (row + dr, col + dc)
            if board.is_valid_pos(new_pos):
                visible.add(new_pos)

        return visible

    def copy(self) -> 'Knight':
        """Create a copy of this piece."""
        return Knight(self.color)


class Bishop:
    """Bishop piece - moves diagonally any number of squares."""

    def __init__(self, color: str):
        self.color = color

    @property
    def piece_type(self) -> str:
        return 'bishop'

    @property
    def symbol(self) -> str:
        return '\u2657' if self.color == 'white' else '\u265d'

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for the bishop."""
        return self._get_sliding_moves(pos, board, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def get_visible_squares(self, pos: Tuple[int, int], board) -> Set[Tuple[int, int]]:
        """Get all squares visible to the bishop (diagonal rays until blocked)."""
        return self._get_sliding_visibility(pos, board, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def _get_sliding_moves(self, pos: Tuple[int, int], board, directions) -> List[Tuple[int, int]]:
        """Get moves along sliding directions (stops at pieces)."""
        moves = []
        row, col = pos

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_valid_pos((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break  # Can capture but not go further
                else:
                    break  # Blocked by own piece
                r, c = r + dr, c + dc

        return moves

    def _get_sliding_visibility(self, pos: Tuple[int, int], board, directions) -> Set[Tuple[int, int]]:
        """Get visible squares along sliding directions (stops at first piece)."""
        visible = set()
        row, col = pos

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_valid_pos((r, c)):
                visible.add((r, c))
                if board.get_piece((r, c)) is not None:
                    break  # Can see the piece but not beyond
                r, c = r + dr, c + dc

        return visible

    def copy(self) -> 'Bishop':
        """Create a copy of this piece."""
        return Bishop(self.color)


class Rook:
    """Rook piece - moves horizontally or vertically any number of squares."""

    def __init__(self, color: str):
        self.color = color
        self.has_moved = False

    @property
    def piece_type(self) -> str:
        return 'rook'

    @property
    def symbol(self) -> str:
        return '\u2656' if self.color == 'white' else '\u265c'

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for the rook."""
        return self._get_sliding_moves(pos, board, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def get_visible_squares(self, pos: Tuple[int, int], board) -> Set[Tuple[int, int]]:
        """Get all squares visible to the rook (straight rays until blocked)."""
        return self._get_sliding_visibility(pos, board, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _get_sliding_moves(self, pos: Tuple[int, int], board, directions) -> List[Tuple[int, int]]:
        """Get moves along sliding directions (stops at pieces)."""
        moves = []
        row, col = pos

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_valid_pos((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

        return moves

    def _get_sliding_visibility(self, pos: Tuple[int, int], board, directions) -> Set[Tuple[int, int]]:
        """Get visible squares along sliding directions (stops at first piece)."""
        visible = set()
        row, col = pos

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_valid_pos((r, c)):
                visible.add((r, c))
                if board.get_piece((r, c)) is not None:
                    break
                r, c = r + dr, c + dc

        return visible

    def copy(self) -> 'Rook':
        """Create a copy of this piece."""
        new_rook = Rook(self.color)
        new_rook.has_moved = self.has_moved
        return new_rook


class Queen:
    """Queen piece - moves like bishop + rook combined."""

    def __init__(self, color: str):
        self.color = color

    @property
    def piece_type(self) -> str:
        return 'queen'

    @property
    def symbol(self) -> str:
        return '\u2655' if self.color == 'white' else '\u265b'

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """Get all valid moves for the queen."""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        return self._get_sliding_moves(pos, board, directions)

    def get_visible_squares(self, pos: Tuple[int, int], board) -> Set[Tuple[int, int]]:
        """Get all squares visible to the queen (all rays until blocked)."""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        return self._get_sliding_visibility(pos, board, directions)

    def _get_sliding_moves(self, pos: Tuple[int, int], board, directions) -> List[Tuple[int, int]]:
        """Get moves along sliding directions (stops at pieces)."""
        moves = []
        row, col = pos

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_valid_pos((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

        return moves

    def _get_sliding_visibility(self, pos: Tuple[int, int], board, directions) -> Set[Tuple[int, int]]:
        """Get visible squares along sliding directions (stops at first piece)."""
        visible = set()
        row, col = pos

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_valid_pos((r, c)):
                visible.add((r, c))
                if board.get_piece((r, c)) is not None:
                    break
                r, c = r + dr, c + dc

        return visible

    def copy(self) -> 'Queen':
        """Create a copy of this piece."""
        return Queen(self.color)
