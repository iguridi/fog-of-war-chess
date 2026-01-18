/**
 * Fog of War Chess
 */

class ChessGame {
    constructor() {
        this.boardEl = document.getElementById('board');
        this.turnIndicator = document.getElementById('turn-indicator');
        this.lastMoveEl = document.getElementById('last-move');
        this.gameOverModal = document.getElementById('game-over-modal');
        this.gameOverMessage = document.getElementById('game-over-message');

        this.boardSize = 8;
        this.selectedSquare = null;
        this.validMoves = [];
        this.gameState = null;

        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.fetchState();
    }

    createBoard() {
        this.boardEl.innerHTML = '';
        this.boardEl.style.setProperty('--grid-size', this.boardSize);

        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                const square = document.createElement('div');
                square.className = 'square';
                square.dataset.row = row;
                square.dataset.col = col;

                const isLight = (row + col) % 2 === 0;
                square.classList.add(isLight ? 'light' : 'dark');

                this.boardEl.appendChild(square);
            }
        }

        this.createLabels();
    }

    createLabels() {
        const files = 'abcdefgh'.slice(0, this.boardSize).split('');
        const ranks = Array.from({ length: this.boardSize }, (_, i) => this.boardSize - i);

        // Top and bottom labels (files: a-h)
        ['top-labels', 'bottom-labels'].forEach(id => {
            const container = document.getElementById(id);
            container.innerHTML = files.map(f => `<span>${f}</span>`).join('');
        });

        // Left and right labels (ranks: 8-1)
        ['left-labels', 'right-labels'].forEach(id => {
            const container = document.getElementById(id);
            container.innerHTML = ranks.map(r => `<span>${r}</span>`).join('');
        });
    }

    setupEventListeners() {
        this.boardEl.addEventListener('click', (e) => this.handleSquareClick(e));
        document.getElementById('new-game-btn').addEventListener('click', () => this.newGame());
        document.getElementById('play-again-btn').addEventListener('click', () => this.newGame());
    }

    async fetchState() {
        try {
            const response = await fetch('/api/state');
            this.gameState = await response.json();
            this.boardSize = this.gameState.boardSize || 8;
            this.createBoard();
            this.render();
        } catch (error) {
            console.error('Failed to fetch game state:', error);
        }
    }

    render() {
        if (!this.gameState) return;

        const squares = this.boardEl.querySelectorAll('.square');

        squares.forEach(square => {
            const row = parseInt(square.dataset.row);
            const col = parseInt(square.dataset.col);
            const cellData = this.gameState.board[row][col];

            // Reset classes
            square.className = 'square';
            const isLight = (row + col) % 2 === 0;
            square.classList.add(isLight ? 'light' : 'dark');
            square.innerHTML = '';

            // Apply fog
            if (cellData === 'fog') {
                square.classList.add('fog');
                return;
            }

            // Render piece
            if (cellData) {
                const pieceEl = document.createElement('span');
                pieceEl.className = `piece ${cellData.color}`;
                pieceEl.textContent = cellData.symbol;
                square.appendChild(pieceEl);
            }
        });

        // Highlight last move
        if (this.gameState.lastMove) {
            const { from, to } = this.gameState.lastMove;
            this.getSquareEl(from[0], from[1])?.classList.add('last-move');
            this.getSquareEl(to[0], to[1])?.classList.add('last-move');
        }

        // Highlight selected square and valid moves
        if (this.selectedSquare) {
            const [row, col] = this.selectedSquare;
            this.getSquareEl(row, col)?.classList.add('selected');

            this.validMoves.forEach(([r, c]) => {
                const sq = this.getSquareEl(r, c);
                if (sq) {
                    const cellData = this.gameState.board[r][c];
                    if (cellData && cellData !== 'fog') {
                        sq.classList.add('valid-capture');
                    } else {
                        sq.classList.add('valid-move');
                    }
                }
            });
        }

        // Update turn indicator
        this.updateTurnIndicator();

        // Update last move text
        if (this.gameState.lastMove) {
            const from = this.posToNotation(this.gameState.lastMove.from);
            const to = this.posToNotation(this.gameState.lastMove.to);
            this.lastMoveEl.textContent = `Last move: ${from} → ${to}`;
        } else {
            this.lastMoveEl.textContent = '';
        }

        // Check for game over
        if (this.gameState.gameOver) {
            this.showGameOver();
        }
    }

    updateTurnIndicator() {
        if (this.gameState.gameOver) {
            if (this.gameState.winner === 'white') {
                this.turnIndicator.textContent = 'You Win!';
                this.turnIndicator.className = 'turn-indicator you-win';
            } else {
                this.turnIndicator.textContent = 'You Lose!';
                this.turnIndicator.className = 'turn-indicator game-over';
            }
        } else {
            const isWhiteTurn = this.gameState.turn === 'white';
            this.turnIndicator.textContent = isWhiteTurn ? "Your Turn" : "AI Thinking...";
            this.turnIndicator.className = `turn-indicator ${isWhiteTurn ? 'white-turn' : 'black-turn'}`;
        }
    }

    getSquareEl(row, col) {
        return this.boardEl.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    }

    posToNotation([row, col]) {
        const file = String.fromCharCode(97 + col); // a-h
        const rank = this.boardSize - row; // 8-1
        return `${file}${rank}`;
    }

    async handleSquareClick(e) {
        const square = e.target.closest('.square');
        if (!square || this.gameState.gameOver || this.gameState.turn !== 'white') return;

        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        const cellData = this.gameState.board[row][col];

        // If a square is already selected
        if (this.selectedSquare) {
            const [selRow, selCol] = this.selectedSquare;

            // Check if clicking on a valid move
            const isValidMove = this.validMoves.some(([r, c]) => r === row && c === col);

            if (isValidMove) {
                await this.makeMove([selRow, selCol], [row, col]);
            } else {
                // Deselect or select new piece
                this.selectedSquare = null;
                this.validMoves = [];

                if (cellData && cellData !== 'fog' && cellData.color === 'white') {
                    this.selectPiece(row, col);
                }
            }
        } else {
            // Select a piece
            if (cellData && cellData !== 'fog' && cellData.color === 'white') {
                this.selectPiece(row, col);
            }
        }

        this.render();
    }

    selectPiece(row, col) {
        this.selectedSquare = [row, col];
        this.validMoves = this.calculateValidMoves(row, col);
    }

    calculateValidMoves(row, col) {
        const board = this.gameState.board;
        const piece = board[row][col];

        if (!piece || piece === 'fog') return [];

        if (piece.type === 'king') {
            return this.calculateKingMoves(row, col);
        } else if (piece.type === 'pawn') {
            return this.calculatePawnMoves(row, col, piece.color);
        }

        return [];
    }

    calculateKingMoves(row, col) {
        const moves = [];
        const board = this.gameState.board;
        const directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];

        for (const [dr, dc] of directions) {
            const r = row + dr;
            const c = col + dc;

            if (r < 0 || r >= this.boardSize || c < 0 || c >= this.boardSize) continue;

            const target = board[r][c];
            if (target === 'fog') continue;
            if (target === null || target.color !== 'white') {
                moves.push([r, c]);
            }
        }

        return moves;
    }

    calculatePawnMoves(row, col, color) {
        const moves = [];
        const board = this.gameState.board;
        const direction = color === 'white' ? -1 : 1;
        const startRow = color === 'white' ? 6 : 1;

        // Move forward one square
        const oneForward = row + direction;
        if (oneForward >= 0 && oneForward < this.boardSize) {
            const target = board[oneForward][col];
            if (target !== 'fog' && target === null) {
                moves.push([oneForward, col]);

                // Move forward two squares from starting position
                if (row === startRow) {
                    const twoForward = row + (2 * direction);
                    if (twoForward >= 0 && twoForward < this.boardSize) {
                        const target2 = board[twoForward][col];
                        if (target2 !== 'fog' && target2 === null) {
                            moves.push([twoForward, col]);
                        }
                    }
                }
            }

            // Capture diagonally
            for (const dc of [-1, 1]) {
                const newCol = col + dc;
                if (newCol >= 0 && newCol < this.boardSize) {
                    const target = board[oneForward][newCol];
                    if (target !== 'fog' && target !== null && target.color !== color) {
                        moves.push([oneForward, newCol]);
                    }
                }
            }
        }

        return moves;
    }

    async makeMove(from, to) {
        try {
            this.turnIndicator.textContent = 'AI Thinking...';
            this.turnIndicator.className = 'turn-indicator black-turn';

            const response = await fetch('/api/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from, to })
            });

            const result = await response.json();

            if (result.success) {
                this.gameState = result.state;
            } else {
                console.error('Move failed:', result.error);
            }
        } catch (error) {
            console.error('Failed to make move:', error);
        }

        this.selectedSquare = null;
        this.validMoves = [];
        this.render();
    }

    showGameOver() {
        const message = this.gameState.winner === 'white'
            ? 'Victory! You captured the enemy king!'
            : 'Defeat! The AI captured your king!';
        this.gameOverMessage.textContent = message;
        this.gameOverModal.classList.remove('hidden');
    }

    async newGame() {
        try {
            const response = await fetch('/api/new-game', { method: 'POST' });
            this.gameState = await response.json();
            this.boardSize = this.gameState.boardSize || 8;
            this.selectedSquare = null;
            this.validMoves = [];
            this.gameOverModal.classList.add('hidden');
            this.createBoard();
            this.render();
        } catch (error) {
            console.error('Failed to start new game:', error);
        }
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChessGame();
});
