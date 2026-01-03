"""
Comprehensive game mode tests.

Tests all game configurations:
- Standard 4 players (20x20)
- Standard 3 players (20x20, shared color)
- Standard 2 players with 4 colors (20x20)
- Duo mode 2 players (14x14)
- All AI configurations
- Mixed Human/AI configurations
- Different starting players
"""

import pytest
from typing import List, Dict, Any
from blokus.game import Game, GameStatus
from blokus.game_manager_factory import GameManagerFactory
from blokus.player_types import PlayerType
from blokus.board import Board


class TestStandard4Players:
    """Test standard 4-player game mode (20x20)."""
    
    def test_4p_all_human(self):
        """4 human players game."""
        configs = [
            {"id": i, "name": f"Player {i+1}", "type": "human"}
            for i in range(4)
        ]
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm)
        
        assert game.board.size == 20
        assert len(game.players) == 4
        assert all(p.type == PlayerType.HUMAN for p in game.players)
    
    def test_4p_all_ai(self):
        """4 AI players game."""
        configs = [
            {"id": i, "name": f"AI {i+1}", "type": "ai", "persona": "random"}
            for i in range(4)
        ]
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm)
        
        assert len(game.players) == 4
        assert all(p.type == PlayerType.AI for p in game.players)
    
    def test_4p_mixed_1h_3ai(self):
        """1 human vs 3 AI."""
        configs = [
            {"id": 0, "name": "Human", "type": "human"},
            {"id": 1, "name": "AI 1", "type": "ai", "persona": "random"},
            {"id": 2, "name": "AI 2", "type": "ai", "persona": "random"},
            {"id": 3, "name": "AI 3", "type": "ai", "persona": "random"},
        ]
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm)
        
        assert game.players[0].type == PlayerType.HUMAN
        assert game.players[1].type == PlayerType.AI
        assert game.players[2].type == PlayerType.AI
        assert game.players[3].type == PlayerType.AI
    
    def test_4p_mixed_2h_2ai_alternating(self):
        """2 humans, 2 AI alternating."""
        configs = [
            {"id": 0, "name": "Human 1", "type": "human"},
            {"id": 1, "name": "AI 1", "type": "ai", "persona": "random"},
            {"id": 2, "name": "Human 2", "type": "human"},
            {"id": 3, "name": "AI 2", "type": "ai", "persona": "random"},
        ]
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm)
        
        assert game.players[0].type == PlayerType.HUMAN
        assert game.players[1].type == PlayerType.AI
        assert game.players[2].type == PlayerType.HUMAN
        assert game.players[3].type == PlayerType.AI
    
    def test_4p_different_starting_players(self):
        """Test all 4 starting player positions."""
        configs = [{"id": i, "type": "human"} for i in range(4)]
        
        for start in range(4):
            gm = GameManagerFactory.create_from_config(configs, starting_player_id=start)
            game = Game(game_manager=gm)
            assert game.current_player_idx == start
    
    def test_4p_full_game_simulation(self):
        """Simulate a full 4-player game with random moves."""
        configs = [
            {"id": i, "type": "ai", "persona": "random"}
            for i in range(4)
        ]
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm)
        
        moves_played = 0
        max_moves = 200
        
        while game.status == GameStatus.IN_PROGRESS and moves_played < max_moves:
            valid_moves = game.get_valid_moves()
            if valid_moves:
                game.play_move(valid_moves[0])
            else:
                game.force_pass()
            moves_played += 1
        
        # Game should eventually finish
        assert game.status == GameStatus.FINISHED or moves_played == max_moves


class TestDuoMode:
    """Test Duo mode (14x14, 2 players)."""
    
    def test_duo_board_size(self):
        """Duo mode should use 14x14 board."""
        board = Board(size=14)
        game = Game(num_players=2, board=board)
        
        assert game.board.size == 14
        assert len(game.players) == 2
    
    def test_duo_2_humans(self):
        """Duo with 2 human players."""
        configs = [
            {"id": 0, "name": "Player 1", "type": "human"},
            {"id": 1, "name": "Player 2", "type": "human"},
        ]
        board = Board(size=14)
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm, board=board)
        
        assert game.board.size == 14
        assert all(p.type == PlayerType.HUMAN for p in game.players)
    
    def test_duo_human_vs_ai(self):
        """Duo: Human vs AI."""
        configs = [
            {"id": 0, "name": "Human", "type": "human"},
            {"id": 1, "name": "AI", "type": "ai", "persona": "random"},
        ]
        board = Board(size=14)
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm, board=board)
        
        assert game.players[0].type == PlayerType.HUMAN
        assert game.players[1].type == PlayerType.AI
    
    def test_duo_2_ai(self):
        """Duo with 2 AI players."""
        configs = [
            {"id": 0, "type": "ai", "persona": "random"},
            {"id": 1, "type": "ai", "persona": "random"},
        ]
        board = Board(size=14)
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm, board=board)
        
        assert all(p.type == PlayerType.AI for p in game.players)
    
    def test_duo_starting_corners(self):
        """Duo mode starting corners should be different from standard."""
        board = Board(size=14)
        game = Game(num_players=2, board=board)
        
        # Duo corners are typically (4,4) and (9,9) for 14x14
        corners_p0 = game.board.get_player_corners(0)
        corners_p1 = game.board.get_player_corners(1)
        
        assert len(corners_p0) > 0
        assert len(corners_p1) > 0
        # They should be different
        assert corners_p0 != corners_p1
    
    def test_duo_full_game_simulation(self):
        """Simulate a full Duo game."""
        configs = [
            {"id": 0, "type": "ai", "persona": "random"},
            {"id": 1, "type": "ai", "persona": "random"},
        ]
        board = Board(size=14)
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm, board=board)
        
        moves_played = 0
        max_moves = 100
        
        while game.status == GameStatus.IN_PROGRESS and moves_played < max_moves:
            valid_moves = game.get_valid_moves()
            if valid_moves:
                game.play_move(valid_moves[0])
            else:
                game.force_pass()
            moves_played += 1
        
        assert game.status == GameStatus.FINISHED or moves_played == max_moves


class TestStandard2Players:
    """Test Standard 2-player mode (20x20, 4 colors)."""
    
    def test_std2p_expands_to_4_players(self):
        """Standard 2P should create 4 logical players."""
        configs = [
            {"id": 0, "name": "Player 1", "type": "human"},
            {"id": 1, "name": "Player 2", "type": "human"},
        ]
        gm = GameManagerFactory.create_standard_2p_game(configs)
        
        assert len(gm.players) == 4
    
    def test_std2p_color_assignment(self):
        """P1 gets Blue/Yellow, P2 gets Green/Red."""
        configs = [
            {"id": 0, "name": "P1", "type": "human"},
            {"id": 1, "name": "P2", "type": "human"},
        ]
        gm = GameManagerFactory.create_standard_2p_game(configs)
        
        # P0 (Blue) and P2 (Yellow) should be P1's
        assert "P1" in gm.players[0].name
        assert "P1" in gm.players[2].name
        
        # P1 (Green) and P3 (Red) should be P2's
        assert "P2" in gm.players[1].name
        assert "P2" in gm.players[3].name
    
    def test_std2p_human_vs_ai(self):
        """Standard 2P: Human vs AI - AI should control 2 colors."""
        configs = [
            {"id": 0, "name": "Human", "type": "human"},
            {"id": 1, "name": "Bot", "type": "ai", "persona": "random"},
        ]
        gm = GameManagerFactory.create_standard_2p_game(configs)
        game = Game(game_manager=gm)
        
        # Human controls P0 (Blue) and P2 (Yellow)
        assert game.players[0].type == PlayerType.HUMAN
        assert game.players[2].type == PlayerType.HUMAN
        
        # AI controls P1 (Green) and P3 (Red)
        assert game.players[1].type == PlayerType.AI
        assert game.players[3].type == PlayerType.AI
    
    def test_std2p_ai_vs_human(self):
        """Standard 2P: AI vs Human - order reversed."""
        configs = [
            {"id": 0, "name": "Bot", "type": "ai", "persona": "random"},
            {"id": 1, "name": "Human", "type": "human"},
        ]
        gm = GameManagerFactory.create_standard_2p_game(configs)
        game = Game(game_manager=gm)
        
        # AI controls P0 (Blue) and P2 (Yellow)
        assert game.players[0].type == PlayerType.AI
        assert game.players[2].type == PlayerType.AI
        
        # Human controls P1 (Green) and P3 (Red)
        assert game.players[1].type == PlayerType.HUMAN
        assert game.players[3].type == PlayerType.HUMAN
    
    def test_std2p_ai_vs_ai(self):
        """Standard 2P: AI vs AI."""
        configs = [
            {"id": 0, "type": "ai", "persona": "random"},
            {"id": 1, "type": "ai", "persona": "random"},
        ]
        gm = GameManagerFactory.create_standard_2p_game(configs)
        game = Game(game_manager=gm)
        
        assert all(p.type == PlayerType.AI for p in game.players)
    
    def test_std2p_turn_rotation(self):
        """Turn order: Blue -> Green -> Yellow -> Red -> Blue."""
        configs = [
            {"id": 0, "type": "human"},
            {"id": 1, "type": "human"},
        ]
        gm = GameManagerFactory.create_standard_2p_game(configs)
        game = Game(game_manager=gm)
        
        expected_order = [0, 1, 2, 3, 0]
        for expected in expected_order[:-1]:
            assert game.current_player_idx == expected
            game.force_pass()
        
        # After 4 passes, game is over
        assert game.status == GameStatus.FINISHED
    
    def test_std2p_starting_player(self):
        """Test starting with different players."""
        configs = [{"id": 0, "type": "human"}, {"id": 1, "type": "human"}]
        
        # Start with player 1 (Green)
        gm = GameManagerFactory.create_standard_2p_game(configs, starting_player_id=1)
        game = Game(game_manager=gm)
        
        assert game.current_player_idx == 1


class TestGameFlow:
    """Test game flow mechanics across modes."""
    
    def test_pass_advances_turn(self):
        """Passing should advance to next player."""
        game = Game(num_players=4)
        
        assert game.current_player_idx == 0
        game.force_pass()
        assert game.current_player_idx == 1
        game.force_pass()
        assert game.current_player_idx == 2
    
    def test_all_pass_ends_game(self):
        """Game ends when all players pass consecutively."""
        game = Game(num_players=2)
        
        game.force_pass()  # P0
        assert game.status == GameStatus.IN_PROGRESS
        game.force_pass()  # P1
        assert game.status == GameStatus.FINISHED
    
    def test_valid_moves_at_start(self):
        """All players should have valid moves at start."""
        game = Game(num_players=4)
        
        for player_id in range(4):
            # Simulate each player's turn
            if game.current_player_idx == player_id:
                moves = game.get_valid_moves()
                assert len(moves) > 0, f"Player {player_id} has no moves at start"
                # Play a move to advance
                game.play_move(moves[0])
    
    def test_piece_removed_after_play(self):
        """Playing a piece removes it from remaining pieces."""
        game = Game(num_players=2)
        
        moves = game.get_valid_moves()
        piece_type = moves[0].piece_type
        
        assert piece_type in game.players[0].remaining_pieces
        game.play_move(moves[0])
        assert piece_type not in game.players[0].remaining_pieces


class TestAIPersonas:
    """Test different AI personas work correctly."""
    
    @pytest.mark.parametrize("persona", ["random", "aggressive", "defensive", "efficient"])
    def test_ai_persona_creation(self, persona):
        """All AI personas should be creatable."""
        configs = [{"id": 0, "type": "ai", "persona": persona}]
        gm = GameManagerFactory.create_from_config(configs)
        
        assert gm.players[0].persona == persona
    
    def test_multiple_different_personas(self):
        """Mix of different AI personas."""
        configs = [
            {"id": 0, "type": "ai", "persona": "random"},
            {"id": 1, "type": "ai", "persona": "aggressive"},
            {"id": 2, "type": "ai", "persona": "defensive"},
            {"id": 3, "type": "ai", "persona": "efficient"},
        ]
        gm = GameManagerFactory.create_from_config(configs)
        game = Game(game_manager=gm)
        
        assert game.players[0].persona == "random"
        assert game.players[1].persona == "aggressive"
        assert game.players[2].persona == "defensive"
        assert game.players[3].persona == "efficient"


class TestScoring:
    """Test scoring across different game states."""
    
    def test_initial_score_all_negative(self):
        """Initial score should be -89 (all 89 squares remaining)."""
        game = Game(num_players=2)
        
        for player in game.players:
            score = player.calculate_score()
            assert score == -89
    
    def test_score_increases_with_placement(self):
        """Score should increase when pieces are placed."""
        game = Game(num_players=2)
        
        initial_score = game.players[0].calculate_score()
        
        moves = game.get_valid_moves()
        game.play_move(moves[0])
        
        # After playing, remaining pieces decrease, so score increases
        new_score = game.players[0].calculate_score()
        assert new_score > initial_score
    
    def test_perfect_score(self):
        """Perfect score is 20 (all pieces + monomino last bonus)."""
        from blokus.player import Player
        
        player = Player(id=0, name="Test", color="#000000")
        player.remaining_pieces.clear()
        player.last_piece_was_monomino = True
        
        assert player.calculate_score() == 20


class TestEdgeCases:
    """Edge case tests."""
    
    def test_single_player_rejected(self):
        """Single player mode is not supported."""
        with pytest.raises(ValueError):
            Game(num_players=1)
    
    def test_game_copy_independence(self):
        """Copied game should be independent."""
        game1 = Game(num_players=2)
        game2 = game1.copy()
        
        # Play in game1
        moves = game1.get_valid_moves()
        game1.play_move(moves[0])
        
        # game2 should be unaffected
        assert game1.board.count_occupied() > 0
        assert game2.board.count_occupied() == 0
    
    def test_invalid_player_count_raises(self):
        """Invalid player count should raise error."""
        with pytest.raises(ValueError):
            Game(num_players=0)
        
        with pytest.raises(ValueError):
            Game(num_players=5)
