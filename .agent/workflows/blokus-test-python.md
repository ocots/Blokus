---
description: Python testing workflow for Blokus project
---

// turbo-all

# Python Testing Workflow

**Version**: 5.1  
**Last Updated**: 2026-01-02  
**Goal**: Run and maintain Python tests for Blokus project with type safety and property-based testing

> 🚀 **Auto-Execution Enabled**: All commands run automatically without approval (no pipes/redirections)

## 📋 What This Workflow Does

- ✅ Run all Python tests
- ✅ Diagnose and fix test failures
- ✅ Ensure test quality and coverage
- ✅ Maintain SOLID compliance

## 📚 Required Reading

**Before using this workflow, read**:
1. `@[.agent/workflows/testing-manual.md]` - Guide complet des tests
2. `@[.agent/workflows/testing-methodology.md]` - Méthodologie TDD

These manuals contain:
- Complete testing philosophy
- TDD methodology (RED-GREEN-REFACTOR)
- All test types with examples
- Quality standards and best practices
- Debugging techniques
- Diagnostic process

## 🎯 Quick Start

```bash
// turbo
# Run all tests with compact summary
source .venv/bin/activate && python -m pytest tests/ -v --tb=line

// turbo
# Check coverage
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term

// turbo
# Type checking (critical for preventing bugs)
source .venv/bin/activate && mypy src/blokus --strict

// turbo
# Run specific test suites - Defensive tests
source .venv/bin/activate && python -m pytest tests/test_corner_cases.py -v

// turbo
# RL content validation
source .venv/bin/activate && python -m pytest tests/rl/test_obs_validity.py -v

// turbo
# Property-based tests
source .venv/bin/activate && python -m pytest tests/test_property_based.py -v --tb=line
```

## ⚡ Command Aliases

Pour faciliter l'utilisation, voici des alias pratiques à ajouter dans votre `~/.zshrc` :

```bash
# Blokus Testing Aliases
alias blokus-cd='cd /Users/ocots/Documents/Jeux/Blokus'
alias blokus-venv='source .venv/bin/activate'
alias blokus-test='source .venv/bin/activate && python -m pytest tests/ -v --tb=line'
alias blokus-test-x='source .venv/bin/activate && python -m pytest tests/ -v -x'
alias blokus-test-lf='source .venv/bin/activate && python -m pytest tests/ -v --lf'
alias blokus-test-cov='source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term'
alias blokus-mypy='source .venv/bin/activate && mypy src/blokus --strict'
alias blokus-property='source .venv/bin/activate && python -m pytest tests/test_property_based.py -v --tb=line'

# Blokus Engine specific
alias blokus-engine-cd='cd /Users/ocots/Documents/Jeux/Blokus/blokus-engine'
alias blokus-engine-test='cd /Users/ocots/Documents/Jeux/Blokus/blokus-engine && source .venv/bin/activate && python -m pytest tests/ -v'
```

**Installation rapide** :

```bash
# Ajouter les alias à votre .zshrc
cat >> ~/.zshrc << 'EOF'

# Blokus Testing Aliases (added 2026-01-02)
alias blokus-cd='cd /Users/ocots/Documents/Jeux/Blokus'
alias blokus-venv='source .venv/bin/activate'
alias blokus-test='source .venv/bin/activate && python -m pytest tests/ -v --tb=line'
alias blokus-test-x='source .venv/bin/activate && python -m pytest tests/ -v -x'
alias blokus-test-lf='source .venv/bin/activate && python -m pytest tests/ -v --lf'
alias blokus-test-cov='source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term'
alias blokus-mypy='source .venv/bin/activate && mypy src/blokus --strict'
alias blokus-property='source .venv/bin/activate && python -m pytest tests/test_property_based.py -v --tb=line'
alias blokus-engine-cd='cd /Users/ocots/Documents/Jeux/Blokus/blokus-engine'
alias blokus-engine-test='cd /Users/ocots/Documents/Jeux/Blokus/blokus-engine && source .venv/bin/activate && python -m pytest tests/ -v'
EOF

# Recharger votre configuration
source ~/.zshrc
```

**Utilisation** :

```bash
# Tests complets avec résumé compact
blokus-test

# Arrêt au premier échec
blokus-test-x

# Relancer seulement les tests qui ont échoué
blokus-test-lf

# Tests property-based
blokus-property
```

## 🔄 Méthodologie TDD

### Principe Fondamental
**NE JAMAIS modifier un test pour le faire passer**  
Un test qui échoue est une information précieuse sur le code.

### Processus TDD (RED-GREEN-REFACTOR)

#### 🔴 RED - Écrire le test en premier
```python
# Toujours écrire le test AVANT le code
def test_game_manager_sets_starting_player():
    manager = GameManager(mock_players)
    manager.set_starting_player(2)
    assert manager.current_player_index == 2
```

#### 🟢 GREEN - Implémenter CORRECTEMENT
```python
# Implémentation minimale mais CORRECTE
def set_starting_player(self, player_id: int) -> None:
    for player in self.players:
        if player.id == player_id:
            self.current_player_index = self.players.index(player)
            return
    raise ValueError(f"Player with ID {player_id} not found")
```

#### 🔄 REFACTOR - Améliorer le code
```python
# Améliorer la structure SANS changer le comportement
def set_starting_player(self, player_id: int) -> None:
    player = self._find_player_by_id(player_id)
    if player is None:
        raise ValueError(f"Player with ID {player_id} not found")
    self.current_player_index = self.players.index(player)
```

## 🔄 Workflow Steps

### 1) Run Tests

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=line
```

### 2) Analyser les Échecs

Pour chaque test qui échoue:
1. **Lire l'erreur**: Que dit l'assertion ?
2. **Poser les bonnes questions**:
   - Le test est-il correct ?
   - Le comportement attendu est-il correct ?
   - Le code implémente-t-il correctement ?

3. **Décider l'action**:
   - Test incorrect → 📝 Modifier le test
   - Spécification incorrecte → 🤔 Revoir la spécification
   - Code incorrect → 🔧 Corriger le code
   - Code manquant → ➕ Implémenter le code

### 3) Appliquer TDD

**Pour nouvelle fonctionnalité**:
1. Écrire test principal (RED)
2. Implémenter minimum (GREEN)
3. Ajouter tests cas limites (RED)
4. Implémenter validation (GREEN)
5. Ajouter tests intégration (RED)
6. Implémenter intégration (GREEN)
7. Refactoriser (REFACTOR)

**Pour bug fix**:
1. Reproduire avec test (RED)
2. Confirmer l'échec
3. Corriger le bug (GREEN)
4. Ajouter tests régression (PLUS DE RED)
5. Implémenter si nécessaire (GREEN)

### 4) Vérifier la Couverture

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term
```

**Required coverage**:
- Core modules: >95%
- Overall: >90%

### 5) Répéter le Cycle

Continuer jusqu'à:
- ✅ Tous les tests passent
- ✅ Couverture atteinte
- ✅ Code propre et maintenable

## 📁 Test Organization

```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # E2E tests (optional)
└── fixtures/                # Test data
```

## 🎯 Test Types Required

1. **Unit Tests**: Test individual methods
2. **Logic Tests**: Test business logic
3. **Result Tests**: Test outputs
4. **Integration Tests**: Test module interactions
5. **Defensive Tests** (`test_corner_cases.py`): Test invalid inputs, edge cases
6. **RL Content Tests** (`rl/test_obs_validity.py`): Verify observation tensor content
7. **Property-Based Tests** (`test_property_based.py`): Test invariants with Hypothesis

*See testing manual for examples and patterns*

## 🛡️ New Test Categories (v4.0)

### Defensive Tests

**File**: `tests/test_corner_cases.py`  
**Purpose**: Prevent crashes from invalid inputs

- Invalid/None inputs
- Out-of-bounds coordinates
- Configuration mismatches
- Corrupted JSON deserialization
- Complex game states (full board, all passed)

### RL Content Validation

**File**: `tests/rl/test_obs_validity.py`  
**Purpose**: Ensure RL observations contain correct data

- Channel content verification (not just shape)
- Piece placement accuracy
- Available pieces flags
- First move flags
- No NaN/Inf values

### Property-Based Tests

**File**: `tests/test_property_based.py`  
**Purpose**: Test invariants under random scenarios

- Game never crashes with valid inputs
- Scores stay in valid range [-89, 20]
- Pieces count decreases monotonically
- Board cells never overlap
- Game copy is independent

## ⚡ Quality Standards

- **Coverage**: >90% overall
- **Speed**: Tests should be fast
- **Clarity**: Descriptive test names
- **Independence**: No test dependencies

## 🛑️ When to Stop

1. ✅ All tests pass
2. ✅ Coverage meets requirements
3. ✅ No critical failures
4. ✅ Code quality maintained

## 🔧 Useful Pytest Options

```bash
// turbo
# Stop at first failure
source .venv/bin/activate && python -m pytest tests/ -v -x

// turbo
# Rerun only failed tests
source .venv/bin/activate && python -m pytest tests/ -v --lf

// turbo
# Show 10 slowest tests
source .venv/bin/activate && python -m pytest tests/ -v --durations=10

// turbo
# Verbose output with full tracebacks
source .venv/bin/activate && python -m pytest tests/ -v --tb=long

// turbo
# No traceback, summary only
source .venv/bin/activate && python -m pytest tests/ -v --tb=no
```

## 📖 References

- **Testing Manual**: `@[.agent/workflows/testing-manual.md]`
- **Test Coverage Analysis**: `../docs/reports/test-types-analysis.md`
- **Test Implementation**: `../docs/reports/final-test-summary.md`
- **Safe Commands Guide**: `../docs/reports/guide_commandes_safe_auto_execution.md`

---

**Remember**: Tests are documentation. Keep them clean and meaningful.

## 🆕 Version 5.1 Changes

- ✅ Removed all pipes and redirections for auto-execution
- ✅ Added `--tb=line` for compact summaries
- ✅ Added useful pytest options section
- ✅ Updated aliases to use simplified commands
- ✅ All commands now run automatically without confirmation
