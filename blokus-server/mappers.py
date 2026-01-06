from api.models import GameState, PlayerState
from blokus.game import Game

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
