import sys
import os
from typing import List, Optional

# Add engine to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../blokus-engine/src")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from blokus.game import Game, Move
from blokus.pieces import PieceType

from api.models import (
    GameState, PlayerState, MoveRequest, MoveResponse, CreateGameRequest
)

app = FastAPI(title="Blokus API", description="API for Blokus Game Engine")

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
    scores = game.get_scores()
    
    players_states = []
    for i, p in enumerate(game.players):
        # Convert set of PieceType to list of strings
        pieces = sorted([pt.name for pt in p.remaining_pieces])
        players_states.append(PlayerState(
            id=p.id,
            pieces_remaining=pieces,
            score=scores[i],
            has_passed=p.has_passed
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
    return {"message": "Welcome to Blokus API"}

@app.post("/game/new", response_model=GameState)
def create_game(request: CreateGameRequest):
    global game_instance
    game_instance = Game(num_players=request.num_players)
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
        
        success = game.play_move(move)
        
        if success:
            return MoveResponse(
                success=True, 
                game_state=map_game_to_state(game)
            )
        else:
            return MoveResponse(
                success=False, 
                message="Invalid move according to Blokus rules"
            )
            
    except KeyError:
        return MoveResponse(success=False, message=f"Invalid piece type: {move_req.piece_type}")
    except Exception as e:
        return MoveResponse(success=False, message=f"Server error: {str(e)}")

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
