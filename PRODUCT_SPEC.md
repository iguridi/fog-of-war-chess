# Fog-of-War Chess - Product Specification

## Product Overview

**Fog-of-War Chess** is a single-player web-based chess variant where the player competes against an AI opponent with limited visibility. Players can only see squares that their pieces can legally move to or attack - all other squares are hidden in "fog," creating a game of strategy under uncertainty.

---

## Game Rules

### Core Concept
Unlike standard chess where both players see the entire board, fog-of-war chess simulates the "fog of war" from military strategy games. You only have intelligence about areas your pieces can reach.

### Visibility Rules
A square is **visible** to you if:
1. One of your pieces occupies it
2. One of your pieces can legally move to it
3. One of your pieces can attack it (important for pawns, which attack diagonally)

All other squares appear as **fog** - you cannot see if they are empty or contain enemy pieces.

### Win Condition
- **The game ends when a king is captured** (not checkmate)
- There is no "check" warning - if your king is under attack and you don't notice, it can be taken
- This makes protecting your king and scouting with your pieces critical

### Standard Chess Rules Apply
- All piece movements follow standard chess rules
- Castling is allowed (kingside and queenside) when legal
- En passant captures are allowed
- Pawn promotion occurs when a pawn reaches the last rank

---

## User Interface

### Main Game Screen

```
┌─────────────────────────────────────────────────────────────┐
│  FOG OF WAR CHESS                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    a   b   c   d   e   f   g   h        Game Info           │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┐     ┌─────────────────┐  │
│ 8│░░░│░░░│░░░│░░░│░░░│░░░│░░░│░░░│     │  White's Turn   │  │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤     └─────────────────┘  │
│ 7│░░░│░░░│░░░│░░░│░░░│░░░│░░░│░░░│                          │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤     [  New Game  ]       │
│ 6│   │   │   │   │   │   │   │   │                          │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤     Difficulty:          │
│ 5│   │   │   │   │   │   │   │   │     [Easy ▼]             │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤                          │
│ 4│   │   │   │   │   │   │   │   │     ─────────────────    │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤     Captured:            │
│ 3│   │   │   │   │   │   │   │   │     You: ♟♟             │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤     AI:  ♙              │
│ 2│ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │ ♙ │                          │
│  ├───┼───┼───┼───┼───┼───┼───┼───┤     ─────────────────    │
│ 1│ ♖ │ ♘ │ ♗ │ ♕ │ ♔ │ ♗ │ ♘ │ ♖ │     Move History:        │
│  └───┴───┴───┴───┴───┴───┴───┴───┘     1. e2-e4  e7-e5      │
│                                         2. Nf3    ...        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Legend:
░░░ = Fog (hidden square)
    = Visible empty square
♙♖♘♗♕♔ = Your pieces (white)
♟♜♞♝♛♚ = Enemy pieces (black, only visible when in sight)
```

### Visual Elements

| Element | Appearance |
|---------|------------|
| Fog squares | Dark pattern with subtle "?" texture |
| Visible empty squares | Standard light/dark chess pattern |
| Your pieces | White pieces with drop shadow |
| Enemy pieces | Black pieces (only shown when visible) |
| Selected piece | Green highlight on square |
| Valid move | Yellow dot in center of square |
| Valid capture | Red border around square |
| Last move | Light green highlight on from/to squares |

### Interactions

1. **Select a piece**: Click on one of your pieces
   - Square highlights green
   - Valid moves appear as yellow dots
   - Valid captures appear with red borders

2. **Make a move**: Click on a valid destination
   - Piece animates to new position
   - Board updates with new visibility
   - AI thinks and responds

3. **Pawn promotion**: When pawn reaches last rank
   - Modal appears with 4 piece choices: ♕ ♖ ♗ ♘
   - Click to select promotion piece

4. **New game**: Click "New Game" button
   - Resets board to starting position

---

## Game Flow

```
┌─────────────┐
│  New Game   │
└──────┬──────┘
       ▼
┌─────────────┐
│ Player Turn │◄─────────────────────┐
└──────┬──────┘                      │
       ▼                             │
┌─────────────┐    ┌─────────────┐   │
│Select Piece │───►│Show Valid   │   │
└──────┬──────┘    │Moves        │   │
       ▼           └─────────────┘   │
┌─────────────┐                      │
│ Make Move   │                      │
└──────┬──────┘                      │
       ▼                             │
┌─────────────┐   Yes  ┌──────────┐  │
│King Captured├───────►│ YOU WIN! │  │
└──────┬──────┘        └──────────┘  │
       │ No                          │
       ▼                             │
┌─────────────┐                      │
│  AI Turn    │                      │
└──────┬──────┘                      │
       ▼                             │
┌─────────────┐                      │
│ AI Thinks   │ (depth-based delay)  │
└──────┬──────┘                      │
       ▼                             │
┌─────────────┐   Yes  ┌──────────┐  │
│King Captured├───────►│ YOU LOSE │  │
└──────┬──────┘        └──────────┘  │
       │ No                          │
       └─────────────────────────────┘
```

---

## AI Behavior

### AI Characteristics
- **Search depth**: 3 (balanced speed and strength)
- **Same fog rules**: AI only sees squares its pieces can reach (fair play)
- **Evaluates under uncertainty**: AI must make decisions with incomplete information
- **Immediate response**: AI moves after brief "thinking" animation
- **Consistent play**: Uses minimax algorithm with alpha-beta pruning
- **Captures visible material**: Prioritizes winning material it can see

---

## Technical Specifications

### Tech Stack
- **Backend**: Python with Flask
- **Package manager**: uv
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **AI**: Minimax with alpha-beta pruning

### Dependencies
**Runtime:**
- `flask` - Web server and API

**Dev:**
- `pytest` - Running tests

No chess libraries - engine built from scratch.

### Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Performance Targets
- Page load: < 2 seconds
- Move response: < 100ms (player)
- AI response: < 3 seconds (depth 4)

### Screen Sizes
- Minimum: 320px width (mobile)
- Optimal: 768px+ (tablet/desktop)
- Board scales responsively

---

## Future Enhancements (Out of Scope)

These features are NOT included in v1 but could be added later:

- [ ] Multiplayer (two humans, both with fog)
- [ ] Move undo/redo
- [ ] Game save/load
- [ ] Opening book for AI
- [ ] Sound effects
- [ ] Move timer
- [ ] Statistics tracking
- [ ] Different fog rules (e.g., see adjacent squares only)

---

## Acceptance Criteria

### Chess Rules
- [ ] Pawns move forward 1 square, or 2 squares from starting position
- [ ] Pawns capture diagonally
- [ ] Pawns promote to Q/R/B/N when reaching the last rank
- [ ] Knights move in L-shape and can jump over pieces
- [ ] Bishops move diagonally any number of squares
- [ ] Rooks move horizontally/vertically any number of squares
- [ ] Queen moves like rook + bishop combined
- [ ] King moves 1 square in any direction
- [ ] Castling works kingside and queenside when:
  - King and rook have not moved
  - Squares between them are empty
  - King does not pass through attacked square (if visible)
- [ ] En passant capture works for one turn after enemy pawn double-moves
- [ ] Game ends when a king is captured

### Fog-of-War Visibility
- [ ] Player sees all squares occupied by their own pieces
- [ ] Player sees all squares their pieces can legally move to
- [ ] Player sees all squares their pieces attack (pawn diagonals even if empty)
- [ ] Sliding pieces (Q/R/B) visibility stops at first piece encountered
- [ ] Knight visibility includes all 8 L-shaped destinations on board
- [ ] Hidden squares display as fog (distinct visual)
- [ ] Enemy pieces only visible when in a visible square
- [ ] Visibility updates immediately after each move

### AI Opponent
- [ ] AI plays under same fog rules as player
- [ ] AI makes only legal moves
- [ ] AI responds within 3 seconds
- [ ] AI provides reasonable challenge
- [ ] AI captures visible material when advantageous

### User Interface
- [ ] Board displays correctly with 8x8 grid
- [ ] Pieces are clearly distinguishable (white vs black)
- [ ] Fog squares are visually distinct from empty squares
- [ ] Clicking own piece highlights valid moves
- [ ] Clicking valid destination executes move
- [ ] Invalid clicks are ignored (no errors)
- [ ] Turn indicator shows whose turn it is
- [ ] Game over state displays winner clearly
- [ ] New Game button resets the board
- [ ] Pawn promotion shows piece selection dialog

### Technical
- [ ] Dependencies install with `uv sync`
- [ ] Server starts with `uv run python run.py`
- [ ] Game loads in browser at localhost:5000
- [ ] No page refresh needed during gameplay
- [ ] Works in Chrome, Firefox, Safari, Edge
- [ ] No console errors during normal gameplay

### Automated Tests
- [ ] Unit tests for each piece's movement generation
- [ ] Unit tests for special moves (castling, en passant, promotion)
- [ ] Unit tests for visibility calculation per piece type
- [ ] Unit tests for game end detection (king capture)
- [ ] Unit tests for AI move generation (returns legal moves only)
- [ ] Integration test: full game simulation (AI vs AI) completes without errors
- [ ] Integration test: API endpoints return valid responses
- [ ] All tests pass with `pytest`

---

## Critical Path

Each step delivers a playable (if minimal) version of the game.

---

### Step 1: Tiny Fog Game (3x3, Web UI)
**Goal:** End-to-end playable game with simplest possible rules

3x3 grid, 1 king each side, fog mechanics, random AI, in browser:
```
? ? ?     (row 3 - enemy side, hidden in fog)
. . .     (row 2 - visible empty squares)
K . .     (row 1 - your king)
```

**Tasks:**
- Flask server + HTML/CSS/JS frontend
- 3x3 board grid
- King piece (moves 1 square any direction)
- Fog: only see squares your king can move to
- Random AI picks legal move
- Click to move, capture enemy king = win

**Success Criteria:**
```bash
uv run python run.py
# Open localhost:5000 in browser
# See 3x3 board with fog on top row
# Click your king → adjacent squares highlight
# Click destination → king moves, AI responds
# Capture enemy king → "You Win!" message
```

**What works after this step:**
- ✅ Web UI (click to move)
- ✅ Fog-of-war mechanics
- ✅ Turn-based play
- ✅ AI opponent (random)
- ✅ Win/lose detection
- ❌ Only kings, 3x3 board

---

### Step 2: Expand to 8x8 with Pawns
**Goal:** Real chess board size, add pawns

**Tasks:**
- Expand grid to 8x8
- Add pawns (move forward 1, capture diagonal)
- Starting position: pawns on rows 2 & 7, kings on row 1 & 8
- Update fog visibility for pawns
- Update frontend to render 8x8

**Success Criteria:**
```bash
uv run python run.py
# Open localhost:5000
# See 8x8 board with fog on enemy rows
# Pawns can move forward, capture diagonally
# King capture still ends game
```

**What works after this step:**
- ✅ 8x8 board in browser
- ✅ Pawns + Kings
- ❌ Missing pieces (knight, bishop, rook, queen)

---

### Step 3: Add All Pieces
**Goal:** Full chess piece set with proper movement

**Tasks:**
- Knight (L-shape, jumps over pieces)
- Bishop (diagonal sliding)
- Rook (horizontal/vertical sliding)
- Queen (bishop + rook combined)
- Update visibility for each piece type

**Success Criteria:**
```bash
uv run python run.py
# Standard chess starting position
# All pieces move correctly
# Visibility includes knight L-shapes, sliding piece rays, etc.
```

**What works after this step:**
- ✅ All 6 piece types
- ✅ Correct visibility per piece
- ❌ AI is still random
- ❌ No special moves

---

### Step 4: Smart AI
**Goal:** AI plays strategically using minimax

**Tasks:**
- Board evaluation function (material + position)
- Minimax with alpha-beta pruning (depth 3)
- AI only evaluates what it can see (fog applies)

**Success Criteria:**
- AI captures undefended pieces
- AI protects its own pieces
- AI responds in < 3 seconds
- Games feel competitive

**What works after this step:**
- ✅ Challenging AI opponent
- ❌ No special moves

---

### Step 5: Special Moves (Optional Polish)
**Goal:** Complete chess rules

**Tasks:**
- Pawn promotion (auto-queen or UI picker)
- Castling (king + rook swap)
- En passant capture
- Pawn double-move from start

**Success Criteria:**
- Pawn reaching last rank becomes queen
- Can castle when legal
- En passant works for one turn after enemy double-push

---

## GOAL COMPLETE

**Final Success Criteria:**
1. Run `uv sync && uv run python run.py`
2. Open `localhost:5000` in browser
3. Play fog-of-war chess against AI
4. Game ends correctly when king is captured
5. Can start new game and play again

---

## Success Criteria

The game is complete when:
1. All deliverables above are completed
2. All acceptance criteria are met
3. A full game can be played from start to finish without bugs
4. The fog-of-war mechanic creates interesting strategic decisions
