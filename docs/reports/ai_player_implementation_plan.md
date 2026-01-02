# AI Player Implementation Plan

**Date**: 2026-01-02  
**Objective**: Implement automatic AI player moves with visual animations

---

## 🎯 Problem Statement

Currently, when a player is configured as AI, the game does not automatically play their turn. The human player must manually play for the AI, which defeats the purpose of having AI players.

### Current Behavior
- ✅ AI players can be configured in setup (type: 'ai', persona: random/aggressive/defensive/efficient)
- ✅ Player configuration is passed to backend API
- ❌ **Frontend does not detect AI turns and trigger automatic moves**
- ❌ **No visual feedback for AI "thinking" or playing**
- ❌ **AI does not automatically pass when no moves available**

---

## 📋 Requirements

### Functional Requirements
1. **Auto-play AI turns**: When it's an AI player's turn, automatically request and execute a move
2. **Thinking delay**: Add randomized delay (1-3 seconds) to simulate AI thinking
3. **Visual animations**:
   - Show AI "hovering" over board positions
   - Animate piece orientation changes (R/S rotations)
   - Smooth piece placement animation
4. **Auto-pass**: AI should automatically pass if no valid moves available
5. **Turn flow**: Seamlessly transition between human and AI turns

### Non-Functional Requirements
- Smooth UX without blocking the UI
- Clear visual indicators of AI activity
- Configurable animation speed
- Works in both local and API modes

---

## 🔍 Technical Analysis

### Current Architecture

#### Frontend (blokus-web/js/)
```
game.js
├── Game class manages state
├── _nextTurn() advances to next player
├── playMove() executes moves
└── passTurn() handles passing

setup.js
├── Collects player configurations
└── Passes config with type: 'ai' and persona

main.js
└── Launches game with config
```

#### Backend (blokus-server/)
```
main.py
├── /game/new creates game with player configs
├── /game/move executes moves
├── /game/ai/suggest gets AI move suggestion
└── Player.persona determines AI strategy
```

### Missing Components

1. **AI Turn Detection**: No code checks if current player is AI
2. **AI Move Request**: No automatic call to `/game/ai/suggest`
3. **Animation System**: No visual feedback for AI moves
4. **State Management**: No tracking of AI "thinking" state

---

## 🏗️ Implementation Plan

### Phase 1: Core AI Auto-Play ✅ Priority

**Goal**: Make AI players automatically play their turns

#### 1.1 Add AI Detection to Game Class
**File**: `blokus-web/js/game.js`

```javascript
// Add to Game class
_isAIPlayer(playerId) {
    const player = this._players[playerId];
    if (!player) return false;
    
    // Check config for player type
    const playerConfig = this._config.players?.[playerId];
    return playerConfig?.type === 'ai';
}

_getCurrentPlayerConfig() {
    return this._config.players?.[this._currentPlayer];
}
```

#### 1.2 Trigger AI Turn After _nextTurn()
**File**: `blokus-web/js/game.js`

```javascript
_nextTurn() {
    // ... existing code ...
    
    this._updateUI();
    this.save();
    
    // NEW: Check if next player is AI
    if (this._isAIPlayer(this._currentPlayer) && !this._gameOver) {
        this._scheduleAIMove();
    }
}
```

#### 1.3 Implement AI Move Scheduling
**File**: `blokus-web/js/game.js`

```javascript
_scheduleAIMove() {
    // Random delay between 1-3 seconds
    const delay = 1000 + Math.random() * 2000;
    
    setTimeout(() => {
        this._executeAIMove();
    }, delay);
}

async _executeAIMove() {
    if (this._gameOver) return;
    
    const playerId = this._currentPlayer;
    
    // Check if AI has valid moves
    if (!this._hasValidMove(playerId)) {
        console.log(`AI Player ${playerId} has no valid moves, passing...`);
        this.passTurn();
        return;
    }
    
    // Get AI move suggestion
    if (this._useApi) {
        await this._executeAIMoveFromAPI();
    } else {
        await this._executeAIMoveLocal();
    }
}
```

#### 1.4 API Mode: Request AI Move
**File**: `blokus-web/js/game.js`

```javascript
async _executeAIMoveFromAPI() {
    try {
        const response = await this._apiClient.getAISuggestedMove();
        
        if (response.success && response.move) {
            const { piece_type, orientation, row, col } = response.move;
            
            // Get piece object
            const piece = getPiece(piece_type, orientation);
            
            // Execute move
            await this.playMove(piece, row, col);
        } else {
            console.warn('AI returned no move, passing...');
            this.passTurn();
        }
    } catch (err) {
        console.error('AI move failed:', err);
        this.passTurn();
    }
}
```

#### 1.5 Local Mode: Implement Simple AI
**File**: `blokus-web/js/game.js`

```javascript
async _executeAIMoveLocal() {
    const playerId = this._currentPlayer;
    const player = this._players[playerId];
    const isFirst = this.isFirstMove(playerId);
    
    // Simple random AI: try pieces in random order
    const pieces = Array.from(player.remainingPieces);
    
    // Shuffle pieces
    for (let i = pieces.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pieces[i], pieces[j]] = [pieces[j], pieces[i]];
    }
    
    // Try each piece
    for (const type of pieces) {
        for (const piece of PIECES[type]) {
            const corners = this._board.getPlayerCorners(playerId);
            
            // Shuffle corners
            const shuffledCorners = corners.sort(() => Math.random() - 0.5);
            
            for (const [cr, cc] of shuffledCorners) {
                for (const [pr, pc] of piece.coords) {
                    const row = cr - pr;
                    const col = cc - pc;
                    
                    if (this._board.isValidPlacement(piece, row, col, playerId, isFirst)) {
                        // Found valid move!
                        this.playMove(piece, row, col);
                        return;
                    }
                }
            }
        }
    }
    
    // No valid move found
    this.passTurn();
}
```

#### 1.6 Add API Endpoint Call
**File**: `blokus-web/js/api.js`

```javascript
export async function getAISuggestedMove() {
    const response = await fetch(`${BASE_URL}/game/ai/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
        throw new Error(`AI suggestion failed: ${response.statusText}`);
    }
    
    return await response.json();
}
```

---

### Phase 2: Visual Animations 🎨

**Goal**: Add visual feedback for AI moves

#### 2.1 AI Thinking Indicator
**File**: `blokus-web/js/game.js`

```javascript
_scheduleAIMove() {
    // Show thinking indicator
    this._showAIThinking(true);
    
    const delay = 1000 + Math.random() * 2000;
    
    setTimeout(() => {
        this._showAIThinking(false);
        this._executeAIMove();
    }, delay);
}

_showAIThinking(show) {
    const indicator = document.getElementById('ai-thinking-indicator');
    if (indicator) {
        indicator.style.display = show ? 'block' : 'none';
    }
}
```

**File**: `blokus-web/index.html`

```html
<!-- Add to game UI -->
<div id="ai-thinking-indicator" class="ai-thinking" style="display: none;">
    <div class="spinner"></div>
    <span>IA réfléchit...</span>
</div>
```

#### 2.2 Piece Hover Animation
**File**: `blokus-web/js/game.js`

```javascript
async _executeAIMoveWithAnimation(piece, row, col) {
    // 1. Show piece hovering at random positions (2-3 positions)
    await this._animateAIHover(piece, 3);
    
    // 2. Show orientation changes (if needed)
    await this._animateAIOrientation(piece);
    
    // 3. Place piece with animation
    await this._animateAIPlacement(piece, row, col);
    
    // 4. Execute actual move
    this.playMove(piece, row, col);
}

async _animateAIHover(piece, positions) {
    for (let i = 0; i < positions; i++) {
        const randomRow = Math.floor(Math.random() * this._board.size);
        const randomCol = Math.floor(Math.random() * this._board.size);
        
        // Show piece preview at position
        this._board.showPreview(piece, randomRow, randomCol, this._currentPlayer);
        
        // Wait 300-500ms
        await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));
        
        // Clear preview
        this._board.clearPreview();
    }
}

async _animateAIOrientation(piece) {
    // Simulate 1-3 rotations/flips
    const changes = 1 + Math.floor(Math.random() * 3);
    
    for (let i = 0; i < changes; i++) {
        // Visual feedback for R or S key press
        this._showKeyPress(Math.random() > 0.5 ? 'R' : 'S');
        await new Promise(resolve => setTimeout(resolve, 200));
    }
}

async _animateAIPlacement(piece, row, col) {
    // Show piece preview at final position
    this._board.showPreview(piece, row, col, this._currentPlayer);
    
    // Highlight the placement
    this._board.highlightCells(piece, row, col);
    
    // Wait 500ms
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Clear effects
    this._board.clearPreview();
    this._board.clearHighlight();
}
```

#### 2.3 Key Press Visual Feedback
**File**: `blokus-web/css/style.css`

```css
.key-indicator {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 20px 40px;
    border-radius: 10px;
    font-size: 48px;
    font-weight: bold;
    z-index: 1000;
    animation: keyPulse 0.3s ease-out;
}

@keyframes keyPulse {
    0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
    50% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

.ai-thinking {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.9);
    padding: 10px 20px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.spinner {
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

---

### Phase 3: Auto-Pass Logic ✅

**Goal**: AI automatically passes when no moves available

#### 3.1 Enhanced Pass Detection
**File**: `blokus-web/js/game.js`

```javascript
async _executeAIMove() {
    if (this._gameOver) return;
    
    const playerId = this._currentPlayer;
    
    // Check if AI has valid moves
    if (!this._hasValidMove(playerId)) {
        console.log(`🤖 AI Player ${playerId} has no valid moves, passing...`);
        
        // Show pass message
        this._showAIPassMessage();
        
        // Wait a bit before passing
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        this.passTurn();
        return;
    }
    
    // Continue with move...
}

_showAIPassMessage() {
    const player = this._players[this._currentPlayer];
    const message = `${player.name} passe son tour (aucun coup valide)`;
    
    // Show notification
    this._showNotification(message, 'info');
}
```

---

## 🧪 Testing Strategy

### Unit Tests
1. Test `_isAIPlayer()` correctly identifies AI players
2. Test `_scheduleAIMove()` is called after AI turn
3. Test `_executeAIMoveLocal()` finds valid moves
4. Test auto-pass when no moves available

### Integration Tests
1. Test full game with 1 human + 3 AI players
2. Test API mode AI move requests
3. Test local mode AI move generation
4. Test game completion with all AI players

### Manual Tests
1. Create game with different AI personas
2. Verify animations are smooth
3. Verify thinking delay feels natural
4. Verify AI passes correctly
5. Test edge cases (first move, last piece, etc.)

---

## 📊 Success Criteria

- ✅ AI players automatically play their turns
- ✅ Random delay (1-3s) before AI moves
- ✅ Visual "thinking" indicator shown
- ✅ Piece hover animation (2-3 positions)
- ✅ Orientation change animation (R/S keys)
- ✅ Smooth piece placement
- ✅ AI auto-passes when no moves
- ✅ Works in both local and API modes
- ✅ No UI blocking during AI turns
- ✅ Seamless human/AI turn transitions

---

## 🚀 Implementation Order

### Sprint 1: Core Functionality (Day 1)
1. ✅ Add AI detection methods
2. ✅ Implement `_scheduleAIMove()`
3. ✅ Implement `_executeAIMoveLocal()`
4. ✅ Implement `_executeAIMoveFromAPI()`
5. ✅ Add API endpoint call
6. ✅ Test basic auto-play

### Sprint 2: Visual Feedback (Day 1-2)
1. ⏳ Add thinking indicator
2. ⏳ Implement hover animation
3. ⏳ Implement orientation animation
4. ⏳ Implement placement animation
5. ⏳ Add CSS styles
6. ⏳ Test animations

### Sprint 3: Polish & Testing (Day 2)
1. ⏳ Add pass notifications
2. ⏳ Tune animation timings
3. ⏳ Test all AI personas
4. ⏳ Test edge cases
5. ⏳ Performance optimization
6. ⏳ Documentation

---

## 🔧 Configuration Options

### AI Settings (Future Enhancement)
```javascript
{
    aiSpeed: 'normal', // 'fast', 'normal', 'slow'
    showAnimations: true,
    thinkingDelay: { min: 1000, max: 3000 },
    hoverPositions: 3,
    showKeyPresses: true
}
```

---

## 📝 Notes

- Keep animations optional (can be disabled for fast play)
- Ensure AI doesn't block UI thread
- Use async/await for smooth flow
- Consider adding AI difficulty levels later
- May need to adjust delays based on user feedback

---

**Status**: Ready for implementation  
**Estimated Time**: 1-2 days  
**Priority**: High
