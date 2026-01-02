---
description: Python testing workflow for Blokus project
---

# Python Testing Workflow

**Version**: 3.0  
**Last Updated**: 2026-01-02  
**Goal**: Run and maintain Python tests for Blokus project

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
# Run all tests
source .venv/bin/activate && python -m pytest tests/ -v --tb=short

# Check coverage
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
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
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
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
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
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

*See testing manual for examples and patterns*

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

## 🔧 Optional Commands

```bash
# Type checking
source .venv/bin/activate && mypy src/

# Linting
source .venv/bin/activate && ruff check src/

# Run specific test
source .venv/bin/activate && python -m pytest tests/test_game_manager.py -v
```

## 📖 References

- **Testing Manual**: `@[.agent/workflows/testing-manual.md]`
- **Test Coverage Analysis**: `../docs/reports/test-types-analysis.md`
- **Test Implementation**: `../docs/reports/final-test-summary.md`

---

**Remember**: Tests are documentation. Keep them clean and meaningful.
