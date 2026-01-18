"""Core game logic for Fog-of-War chess game."""
from app.board import Board
from app.pieces import King, Queen, Rook, Bishop, Knight, Pawn
from app.ai import AI


class Game:
    """Manages the fog-of-war chess game state."""

    def __init__(self):
        """Initialize a new game."""
        self.board = Board()
        self.current_turn = 'white'
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.ai = AI()
        self._setup_initial_position()

    def _setup_initial_position(self):
        """Set up the standard chess starting position."""
        # White pieces (bottom, row 7 = rank 1)
        self.board.set_piece((7, 0), Rook('white'))    # a1
        self.board.set_piece((7, 1), Knight('white'))  # b1
        self.board.set_piece((7, 2), Bishop('white'))  # c1
        self.board.set_piece((7, 3), Queen('white'))   # d1
        self.board.set_piece((7, 4), King('white'))    # e1
        self.board.set_piece((7, 5), Bishop('white'))  # f1
        self.board.set_piece((7, 6), Knight('white'))  # g1
        self.board.set_piece((7, 7), Rook('white'))    # h1
        for col in range(8):
            self.board.set_piece((6, col), Pawn('white'))  # Pawns on rank 2

        # Black pieces (top, row 0 = rank 8)
        self.board.set_piece((0, 0), Rook('black'))    # a8
        self.board.set_piece((0, 1), Knight('black'))  # b8
        self.board.set_piece((0, 2), Bishop('black'))  # c8
        self.board.set_piece((0, 3), Queen('black'))   # d8
        self.board.set_piece((0, 4), King('black'))    # e8
        self.board.set_piece((0, 5), Bishop('black'))  # f8
        self.board.set_piece((0, 6), Knight('black'))  # g8
        self.board.set_piece((0, 7), Rook('black'))    # h8
        for col in range(8):
            self.board.set_piece((1, col), Pawn('black'))  # Pawns on rank 7

    def get_visible_state(self):
        """Get the game state with fog-of-war applied for white player."""
        visible_squares = self.board.get_visible_squares('white')

        board_state = []
        for row in range(Board.SIZE):
            row_state = []
            for col in range(Board.SIZE):
                pos = (row, col)
                if pos in visible_squares:
                    piece = self.board.get_piece(pos)
                    if piece:
                        row_state.append({
                            'type': piece.piece_type,
                            'color': piece.color,
                            'symbol': piece.symbol
                        })
                    else:
                        row_state.append(None)
                else:
                    row_state.append('fog')
            board_state.append(row_state)

        return {
            'board': board_state,
            'turn': self.current_turn,
            'gameOver': self.game_over,
            'winner': self.winner,
            'lastMove': self.last_move,
            'boardSize': Board.SIZE,
        }

    def make_player_move(self, from_pos: tuple, to_pos: tuple, promotion=None) -> dict:
        """Make a player move and return the result."""
        if self.game_over:
            return {'success': False, 'error': 'Game is over'}

        if self.current_turn != 'white':
            return {'success': False, 'error': 'Not your turn'}

        piece = self.board.get_piece(from_pos)
        if not piece or piece.color != 'white':
            return {'success': False, 'error': 'No valid piece at that position'}

        valid_moves = piece.get_valid_moves(from_pos, self.board)
        if to_pos not in valid_moves:
            return {'success': False, 'error': 'Invalid move'}

        # Execute the move
        self._execute_move(from_pos, to_pos)

        if self.game_over:
            return {
                'success': True,
                'state': self.get_visible_state()
            }

        # AI's turn
        self.current_turn = 'black'
        ai_move = self.ai.get_move(self.board, 'black')

        if ai_move:
            ai_from, ai_to, _ = ai_move
            self._execute_move(ai_from, ai_to)

        if not self.game_over:
            self.current_turn = 'white'

        return {
            'success': True,
            'state': self.get_visible_state(),
            'aiMove': ai_move[:2] if ai_move else None
        }

    def _execute_move(self, from_pos: tuple, to_pos: tuple):
        """Execute a move on the board."""
        piece = self.board.get_piece(from_pos)
        captured = self.board.get_piece(to_pos)

        # Check for king capture
        if captured and captured.piece_type == 'king':
            self.game_over = True
            self.winner = piece.color

        # Move the piece
        self.board.set_piece(to_pos, piece)
        self.board.set_piece(from_pos, None)

        self.last_move = {'from': from_pos, 'to': to_pos}
