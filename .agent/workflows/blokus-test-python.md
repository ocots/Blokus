---
description: Interactive Python testing workflow with feedback loop
---

# Python Unit Test Workflow

**Version**: 2.0  
**Last Updated**: 2026-01-02  
**Goal**: Run tests, diagnose failures, fix issues in a feedback loop until all tests pass.

**Updates v2.0**:
- Ajout tests pour factories (PlayerFactory, GameManagerFactory)
- Tests pour machines à états (PlayerStatus, GameStatus)
- Tests d'intégration API
- Patterns de test pour SOLID compliance

## Hard Rules

1. **Always run tests from the virtual environment**
   ```bash
   source .venv/bin/activate && python -m pytest tests/ -v
   ```

2. **One test file per module** (when it makes sense)
   - `src/blokus/pieces.py` → `tests/test_pieces.py`
   - `src/blokus/player.py` → `tests/test_player.py`
   - `src/blokus/player_factory.py` → `tests/test_player_factory.py`
   - `src/blokus/game_manager.py` → `tests/test_game_manager.py`

3. **Clear test organization**
   - Use `class TestFeatureName:` to group related tests
   - Descriptive test names: `test_<what>_<condition>_<expected>`
   - Test SOLID principles (especially SRP and OCP)

## Workflow Steps

### 1) Run all tests

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

### 2) If tests fail, diagnose

For each failing test:
1. Read the assertion error
2. Read the relevant source code
3. Determine if it's a test bug or code bug

### 3) Fix the issue

- If **test bug**: Update the test expectation
- If **code bug**: Fix the source code

### 4) Re-run tests

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

### 5) Repeat until all pass

Continue the diagnose → fix → test loop until:
- ✅ All tests pass
- 📊 Coverage is acceptable (>80% recommended)

### 6) Optional: Check coverage

```bash
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
```

### 7) Optional: Type checking

```bash
source .venv/bin/activate && mypy src/
```

### 8) Optional: Linting

```bash
source .venv/bin/activate && ruff check src/
```

## Stop Points

1. After initial test run (report status)
2. If >5 tests fail (ask for guidance)
3. Before making major code changes
4. When all tests pass (report success)

## Testing Patterns for SOLID Architecture

### Testing Factories (OCP)

```python
# tests/test_player_factory.py
from blokus.player_factory import PlayerFactory
from blokus.player_types import PlayerType

class TestPlayerFactory:
    def test_create_human_player(self):
        player = PlayerFactory.create_human(0, "Alice")
        assert player.type == PlayerType.HUMAN
        assert player.name == "Alice"
    
    def test_create_ai_player_with_persona(self):
        player = PlayerFactory.create_ai(1, "random")
        assert player.type == PlayerType.AI
        assert player.persona == "random"
    
    def test_factory_creates_valid_players(self):
        # Test that factory respects contracts
        player = PlayerFactory.create_human(0, "Test")
        assert hasattr(player, 'id')
        assert hasattr(player, 'remaining_pieces')
```

### Testing State Machines

```python
# tests/test_player_state_machine.py
from blokus.player_types import PlayerStatus

class TestPlayerStateMachine:
    def test_valid_state_transitions(self):
        player = create_test_player()
        
        # Valid transition
        player.status = PlayerStatus.ACTIVE
        assert player.status == PlayerStatus.ACTIVE
    
    def test_invalid_state_transitions_raise_error(self):
        player = create_test_player()
        player.status = PlayerStatus.PASSED
        
        # Cannot go from PASSED to ACTIVE
        with pytest.raises(ValueError):
            player.status = PlayerStatus.ACTIVE
```

### Testing Strategy Pattern (AI)

```python
# tests/test_ai_strategies.py
class TestAIStrategies:
    def test_random_strategy_returns_valid_move(self):
        strategy = RandomAIStrategy()
        game = create_test_game()
        
        move = strategy.get_move(game)
        
        assert move is not None
        assert game.is_valid_move(move)
    
    def test_strategy_returns_none_when_no_moves(self):
        strategy = RandomAIStrategy()
        game = create_game_with_no_valid_moves()
        
        move = strategy.get_move(game)
        
        assert move is None
```

### Testing Dependency Injection (DIP)

```python
# tests/test_game_with_mocks.py
class TestGameWithDependencyInjection:
    def test_game_with_mock_api_client(self):
        mock_api = Mock()
        mock_api.get_ai_suggestion.return_value = {"move": test_move}
        
        game = Game(board, controls, config, apiClient=mock_api)
        
        # Test that game uses injected dependency
        game.execute_ai_move()
        mock_api.get_ai_suggestion.assert_called_once()
```

### Integration Tests

```python
# tests/test_api_integration.py
from fastapi.testclient import TestClient
from blokus_server.main import app

class TestAPIIntegration:
    def test_create_game_with_ai_players(self):
        client = TestClient(app)
        
        response = client.post("/game/new", json={
            "num_players": 2,
            "players": [
                {"name": "Human", "type": "human"},
                {"name": "AI", "type": "ai", "persona": "random"}
            ]
        })
        
        assert response.status_code == 200
        assert len(response.json()["players"]) == 2
```

## Coverage Goals

- **Core modules**: > 95% (pieces, board, rules, game)
- **Factories**: > 90% (player_factory, game_manager_factory)
- **State machines**: 100% (all transitions tested)
- **API**: > 85% (all endpoints + error cases)
- **Overall**: > 90%

## Philosophy

Test first • Clear assertions • Minimal fixtures • Fast feedback • SOLID compliance
