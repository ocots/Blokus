import sys
import os
from typing import List, Optional

# Add engine to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../blokus-engine/src")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from blokus.game import Game, Move
from blokus.board import Board
from blokus.pieces import PieceType
from blokus.game_manager_factory import GameManagerFactory

from api.models import (
    GameState, PlayerState, MoveRequest, MoveResponse, CreateGameRequest, AIModelInfo
)
from blokus.rl.registry import get_registry
from blokus.rl.observations import create_observation
from blokus.rl.actions import get_action_mask, decode_action
import os
from datetime import datetime
from blokus.player_types import PlayerType
from version import BACKEND_VERSION

# Runtime Identification
PID = os.getpid()
START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"🚀 Blokus Backend {BACKEND_VERSION} Starting...")
print(f"🆔 Process ID: {PID}")
print(f"⏰ Started at: {START_TIME}")

app = FastAPI(title="Blokus API", description="API for Blokus Game Engine", version=BACKEND_VERSION)

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game instance (simple in-memory storage)
game_instance: Optional[Game] = None

def get_game_or_404() -> Game:
    if game_instance is None:
        raise HTTPException(status_code=404, detail="Game not initialized")
    return game_instance

def map_game_to_state(game: Game) -> GameState:
    """Map Game instance to API GameState model."""
    # Calculate scores for all players
    scores = game.get_scores()
    
    players_states = []
    for i, p in enumerate(game.players):
        # Convert set of PieceType to list of strings
        pieces = sorted([pt.name for pt in p.remaining_pieces])
        
        players_states.append(PlayerState(
            id=p.id,
            name=p.name,
            color=p.color,
            type=p.type.value,
            persona=p.persona,
            pieces_remaining=pieces,
            pieces_count=p.pieces_count,
            squares_remaining=p.squares_remaining,
            score=scores[i],
            has_passed=p.has_passed,
            status=p.status.value,
            display_name=p.display_name,
            turn_order=p.turn_order
        ))
    
    return GameState(
        board=game.board.grid.tolist(),
        players=players_states,
        current_player_id=game.current_player_idx,
        status=game.status.value,
        turn_number=game.turn_number
    )

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to Blokus API {BACKEND_VERSION}", 
        "version": BACKEND_VERSION,
        "pid": PID,
        "started_at": START_TIME
    }

@app.get("/ai/models", response_model=list[AIModelInfo])
def list_ai_models():
    """List all available AI models/personas."""
    registry = get_registry()
    return registry.list_for_api(only_enabled=True)

@app.post("/game/new", response_model=GameState)
def create_game(request: CreateGameRequest):
    """
    Create a new game with configured players.
    
    Uses GameManagerFactory to create players with proper configuration.
    """
    global game_instance
    
    # Use start_player if provided, otherwise default to 0
    starting_player = request.start_player if request.start_player is not None else 0
    
    print(f"📥 New Game Request: Mode={request.two_player_mode}, Size={request.board_size}, Players={len(request.players) if request.players else request.num_players}")
    try:
        print(f"📦 REQUEST DUMP: {request.model_dump_json()}")
    except:
        print(f"📦 REQUEST DUMP: {request}")
    
    # Determine board size
    board_size = 20
    
    mode = request.two_player_mode.strip().lower() if request.two_player_mode else None
    
    if request.board_size is not None:
        board_size = request.board_size
    elif mode == 'duo':
        board_size = 14
        
    board = Board(size=board_size)
    
    if request.players:
        # Create game from player configurations
        player_configs = []
        for i, player_config in enumerate(request.players):
            config = {
                "id": i,
                "name": player_config.name,
                "type": player_config.type,
            }
            if player_config.persona:
                config["persona"] = player_config.persona
            player_configs.append(config)
        
        # Use GameManagerFactory to create GameManager with configured players
        if mode == 'standard' and len(player_configs) == 2:
            game_manager = GameManagerFactory.create_standard_2p_game(
                player_configs,
                starting_player_id=starting_player
            )
        else:
            game_manager = GameManagerFactory.create_from_config(
                player_configs, 
                starting_player_id=starting_player
            )
        game_instance = Game(game_manager=game_manager, board=board)
    else:
        # Create standard game with default players
        game_manager = GameManagerFactory.create_standard_game(
            num_players=request.num_players,
            starting_player_id=starting_player
        )
        # Note: Standard game usually implies standard board, but we allow override
        game_instance = Game(game_manager=game_manager, board=board)
    
    return map_game_to_state(game_instance)

@app.get("/game/state", response_model=GameState)
def get_state():
    game = get_game_or_404()
    return map_game_to_state(game)

@app.post("/game/move", response_model=MoveResponse)
def make_move(move_req: MoveRequest):
    game = get_game_or_404()
    
    try:
        # Convert string piece type to Enum
        piece_type = PieceType[move_req.piece_type]
        
        move = Move(
            player_id=move_req.player_id,
            piece_type=piece_type,
            orientation=move_req.orientation,
            row=move_req.row,
            col=move_req.col
        )
        
        # Check validity first to get reason if invalid
        rejection_reason = game.get_move_rejection_reason(move)
        if rejection_reason:
            print(f"XXX API REJECT: {rejection_reason}")
            return MoveResponse(
                success=False, 
                message=rejection_reason
            )
            
        success = game.play_move(move)
        
        if success:
            return MoveResponse(
                success=True, 
                game_state=map_game_to_state(game)
            )
        else:
            return MoveResponse(
                success=False, 
                message="Board placement failed (unknown error)"
            )
            
    except KeyError:
        return MoveResponse(success=False, message=f"Invalid piece type: {move_req.piece_type}")
    except Exception as e:
        return MoveResponse(success=False, message=f"Server error: {str(e)}")

@app.post("/game/ai/suggest", response_model=MoveResponse)
def suggest_move():
    """
    Request the AI to suggest (and implicitly prepare) a move.
    Actually, the frontend expects this to MAKE the move if it's an AI turn.
    """
    game = get_game_or_404()
    
    # 1. Validate current player is AI
    current_player = game.players[game.current_player_idx]
    if current_player.type != PlayerType.AI:
        raise HTTPException(status_code=400, detail="Current player is not AI")
    
    try:
        # 2. Load agent
        registry = get_registry()
        # Default to 'random' if no persona or unknown
        persona = current_player.persona or "random"
        try:
            agent = registry.load_agent(persona)
        except ValueError:
            # Fallback to random if agent not found
            agent = registry.load_agent("random")
        
        # 3. Create observation and mask
        obs = create_observation(game)
        mask = get_action_mask(game)
        
        # 4. Select action
        # If mask is empty, select_action might fail or return 0 depending on agent impl.
        # But get_action_mask handles it (all false).
        # Our modified agents return 0 if mask is empty.
        
        # Check if pass is forced (no valid moves)
        if not mask.any():
            # Force pass
            game.force_pass()
            return MoveResponse(
                success=True,
                game_state=map_game_to_state(game),
                message="passed"
            )
            
        action = agent.select_action(obs, mask)
        
        # 5. Decode move
        move = decode_action(action, game)
        if move is None:
            # Should not happen if agent respects mask
             raise ValueError("Agent selected invalid action")
             
        # DO NOT PLAY MOVE. Just return suggestion.
        # Frontend will animate and then call /game/move
        
        return MoveResponse(
            success=True, 
            game_state=map_game_to_state(game),
            message=f"suggested {move.piece_type.name}",
            move=MoveRequest(
                player_id=move.player_id,
                piece_type=move.piece_type.name,
                orientation=move.orientation,
                row=move.row,
                col=move.col
            )
        )
            
    except Exception as e:
        print(f"AI Error: {e}")
        # Return success=False but with message so frontend handles it gracefully?
        # No, raise 500 is better for debugging, but let's be safe
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

@app.post("/game/pass", response_model=GameState)
def pass_turn():
    game = get_game_or_404()
    game.pass_turn()
    return map_game_to_state(game)

@app.post("/game/reset", response_model=GameState)
def reset_game():
    global game_instance
    if game_instance:
        game_instance = Game(num_players=game_instance.num_players)
    else:
        game_instance = Game()
    return map_game_to_state(game_instance)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
