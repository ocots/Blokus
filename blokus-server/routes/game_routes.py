from fastapi import APIRouter, Depends, HTTPException
from blokus.pieces import PieceType
from blokus.game import Move
from blokus.player_types import PlayerType
from blokus.rl.registry import get_registry
from blokus.rl.observations import create_observation
from blokus.rl.actions import get_action_mask, decode_action

from api.models import GameState, MoveRequest, MoveResponse, CreateGameRequest
from services.game_service import GameService, get_game_service
from mappers import map_game_to_state

router = APIRouter(prefix="/game", tags=["Game"])

@router.post("/new", response_model=GameState)
def create_game(
    request: CreateGameRequest, 
    service: GameService = Depends(get_game_service)
):
    """Create a new game with configured players."""
    # Determine configuration
    mode = request.two_player_mode.strip().lower() if request.two_player_mode else 'standard'
    board_size = request.board_size if request.board_size else (14 if mode == 'duo' else 20)
    starting_player = request.start_player if request.start_player is not None else 0
    
    # Prepare player configs if provided
    player_configs = None
    if request.players:
        player_configs = []
        for i, p_conf in enumerate(request.players):
            conf = {"id": i, "name": p_conf.name, "type": p_conf.type}
            if p_conf.persona:
                conf["persona"] = p_conf.persona
            player_configs.append(conf)
            
    # Create game via service
    game = service.create_game(
        num_players=len(player_configs) if player_configs else request.num_players,
        players_config=player_configs,
        board_size=board_size,
        starting_player_id=starting_player,
        mode=mode
    )
    
    return map_game_to_state(game)

@router.get("/state", response_model=GameState)
def get_state(service: GameService = Depends(get_game_service)):
    """Get current game state."""
    return map_game_to_state(service.game)

@router.post("/move", response_model=MoveResponse)
def make_move(
    move_req: MoveRequest, 
    service: GameService = Depends(get_game_service)
):
    """Execute a move."""
    game = service.game
    
    try:
        piece_type = PieceType[move_req.piece_type]
        move = Move(
            player_id=move_req.player_id,
            piece_type=piece_type,
            orientation=move_req.orientation,
            row=move_req.row,
            col=move_req.col
        )
        
        rejection = game.get_move_rejection_reason(move)
        if rejection:
            return MoveResponse(success=False, message=rejection)
            
        success = game.play_move(move)
        
        if success:
            return MoveResponse(success=True, game_state=map_game_to_state(game))
        else:
            return MoveResponse(success=False, message="Board placement failed")
            
    except KeyError:
        return MoveResponse(success=False, message=f"Invalid piece type: {move_req.piece_type}")
    except Exception as e:
        return MoveResponse(success=False, message=f"Server error: {str(e)}")

@router.post("/pass", response_model=GameState)
def pass_turn(service: GameService = Depends(get_game_service)):
    """Pass turn for current player."""
    game = service.game
    game.pass_turn()
    return map_game_to_state(game)

@router.post("/reset", response_model=GameState)
def reset_game(service: GameService = Depends(get_game_service)):
    """Reset game keeping same configuration."""
    game = service.reset_game()
    return map_game_to_state(game)

@router.post("/ai/suggest", response_model=MoveResponse)
def suggest_move(service: GameService = Depends(get_game_service)):
    """Get AI move suggestion."""
    game = service.game
    current_player = game.players[game.current_player_idx]
    
    if current_player.type != PlayerType.AI:
        raise HTTPException(status_code=400, detail="Current player is not AI")
        
    try:
        registry = get_registry()
        persona = current_player.persona or "random"
        try:
            agent = registry.load_agent(persona)
        except ValueError:
            agent = registry.load_agent("random")
            
        obs = create_observation(game)
        mask = get_action_mask(game)
        
        if not mask.any():
            game.force_pass()
            return MoveResponse(
                success=True,
                game_state=map_game_to_state(game),
                message="passed"
            )
            
        action = agent.select_action(obs, mask)
        move = decode_action(action, game)
        
        if move is None:
            raise ValueError("Agent selected invalid action")
            
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
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")
