---
description: Manuel complet des tests pour le projet Blokus
---

# Testing Manual - Projet Blokus

**Version**: 1.0  
**Last Updated**: 2026-01-02  
**Purpose**: Guide complet pour écrire et maintenir les tests du projet Blokus

---

## 📚 Table des Matières

1. [Philosophie des Tests](#philosophie-des-tests)
2. [Types de Tests](#types-de-tests)
3. [Structure des Tests](#structure-des-tests)
4. [Standards de Qualité](#standards-de-qualité)
5. [Bonnes Pratiques](#bonnes-pratiques)
6. [Exemples Concrets](#exemples-concrets)
7. [Débogage](#débogage)
8. [Maintenance](#maintenance)

---

## Philosophie des Tests

### Objectifs Principaux
- **Prévenir les bugs**: Chaque bug doit avoir un test qui l'aurait attrapé
- **Documenter le code**: Les tests servent de documentation vivante
- **Faciliter le refactoring**: Tests robustes = confiance pour modifier
- **Garantir la qualité**: Maintenir un haut niveau de qualité

### Principes Clés
1. **Test First**: Écrire les tests avant le code quand possible
2. **Test Isolation**: Chaque test doit être indépendant
3. **Test Clarté**: Les tests doivent être faciles à comprendre
4. **Test Couverture**: Couvrir tous les chemins critiques
5. **Test Maintenance**: Les tests doivent évoluer avec le code

---

## Types de Tests

### 1. Unit Tests (Tests Unitaires)
**Objectif**: Tester une fonction/méthode isolée

**Quand écrire**: 
- Pour chaque nouvelle fonction
- Pour chaque nouvelle méthode
- Pour chaque bug fixé

**Exemple**:
```python
# Test unitaire simple
def test_game_manager_initialization():
    manager = GameManager(players=mock_players)
    assert len(manager.players) == 4
    assert manager.current_player_index == 0
```

**Ce qu'on teste**:
- ✅ La fonction fait ce qu'elle doit faire
- ✅ Les paramètres sont validés
- ✅ Les cas limites sont gérés
- ✅ Les erreurs sont gérées

### 2. Logic Tests (Tests de Logique)
**Objectif**: Tester la logique métier et les règles du jeu

**Quand écrire**:
- Pour chaque règle du jeu
- Pour chaque transition d'état
- Pour chaque validation

**Exemple**:
```python
# Test de logique métier
def test_pass_turn_rejects_with_valid_moves():
    game = create_test_game()
    game.has_valid_move = lambda pid: True
    
    result = game.pass_turn(0)
    
    assert result is False
    assert not game.players[0].has_passed
```

**Ce qu'on teste**:
- ✅ Les règles du jeu sont respectées
- ✅ Les validations fonctionnent
- ✅ Les états sont cohérents

### 3. Result Tests (Tests de Résultats)
**Objectif**: Tester que les outputs sont corrects

**Quand écrire**:
- Pour chaque fonction qui retourne quelque chose
- Pour chaque effet secondaire
- Pour chaque mise à jour d'état

**Exemple**:
```python
# Test de résultats
def test_play_move_updates_history():
    game = create_test_game()
    piece = create_test_piece()
    initial_history = len(game.move_history)
    
    game.play_move(piece, 10, 10)
    
    assert len(game.move_history) == initial_history + 1
    assert game.move_history[-1].piece_type == piece.type
```

**Ce qu'on teste**:
- ✅ Les types de retour sont corrects
- ✅ Les effets secondaires sont appliqués
- ✅ L'état est mis à jour

### 4. Integration Tests (Tests d'Intégration)
**Objectif**: Tester l'interaction entre plusieurs modules

**Quand écrire**:
- Pour les workflows importants
- Pour les interactions critiques
- Pour les flux de données

**Exemple**:
```python
# Test d'intégration
def test_ai_controller_complete_turn():
    strategy = MockAIStrategy()
    animator = MockAIAnimator()
    controller = AIController(strategy, animator)
    game_context = create_game_context()
    
    result = controller.execute_turn(game_context)
    
    assert strategy.get_move.called
    assert animator.animate_placement.called
    assert game_context.play_move.called
```

**Ce qu'on teste**:
- ✅ Les modules interagissent correctement
- ✅ Les workflows complets fonctionnent
- ✅ Les données passent correctement

### 5. E2E Tests (Tests End-to-End)
**Objectif**: Tester le jeu complet du début à la fin

**Quand écrire**:
- Pour les scénarios critiques
- Pour les workflows utilisateur
- Pour les vérifications finales

**Exemple**:
```python
# Test E2E (optionnel)
def test_complete_ai_game():
    # Lancer jeu avec 4 IA
    # Jouer jusqu'à la fin
    # Vérifier résultats
    pass
```

**Ce qu'on teste**:
- ✅ L'expérience utilisateur
- ✅ Les performances réelles
- ✅ Les scénarios complets

---

## Structure des Tests

### Organisation des Fichiers
```
tests/
├── unit/                    # Tests unitaires
│   ├── test_game_manager.py
│   ├── test_player.py
│   └── test_board.py
├── integration/             # Tests d'intégration
│   ├── test_ai_controller.py
│   └── test_game_flow.py
├── e2e/                     # Tests E2E (optionnel)
│   └── test_complete_game.py
└── fixtures/                # Données de test
    ├── mock_players.py
    └── test_scenarios.py
```

### Nomination des Tests
- **Unit tests**: `test_<module>_<functionality>`
- **Integration tests**: `test_<workflow>_integration`
- **E2E tests**: `test_<scenario>_e2e`

### Structure d'un Test
```python
def test_descriptive_name():
    """
    Test description explaining what is being tested.
    
    Given: Initial state
    When: Action performed
    Then: Expected result
    """
    # ARRANGE - Préparer les données
    # ACT - Exécuter l'action
    # ASSERT - Vérifier le résultat
```

---

## Standards de Qualité

### Couverture Requise
- **Unit tests**: 85% minimum
- **Logic tests**: 80% minimum
- **Integration tests**: 70% minimum
- **Overall**: 78% minimum

### Qualité des Tests
1. **Clarté**: Le nom du test doit décrire ce qu'il teste
2. **Indépendance**: Chaque test doit pouvoir s'exécuter seul
3. **Rapidité**: Les tests doivent s'exécuter rapidement
4. **Stabilité**: Les tests ne doivent pas être "flaky"
5. **Maintenabilité**: Les tests doivent être faciles à maintenir

### Anti-patterns à Éviter
- ❌ Tests trop complexes
- ❌ Tests qui dépendent de l'ordre d'exécution
- ❌ Tests qui utilisent des données externes
- ❌ Tests sans assertions
- ❌ Tests qui testent trop de choses

---

## Bonnes Pratiques

### Écrire des Tests
1. **AAA Pattern**: Arrange-Act-Assert
2. **Descriptive Names**: Noms qui décrivent le comportement
3. **One Assertion**: Une assertion par test quand possible
4. **Mocking**: Utiliser des mocks pour isoler le test
5. **Fixtures**: Réutiliser les données de test

### Exemples de Bon Tests
```python
# ✅ Bon test
def test_game_manager_sets_starting_player_correctly():
    """Test that GameManager sets starting player correctly."""
    manager = GameManager(mock_players)
    
    manager.set_starting_player(2)
    
    assert manager.current_player_index == 2
    assert manager.current_player.id == 2
```

```python
# ❌ Mauvais test
def test_game_manager():
    manager = GameManager(mock_players)
    manager.set_starting_player(2)
    assert manager.current_player_index == 2
```

### Debugging des Tests
1. **Logs**: Utiliser des logs pour déboguer
2. **Prints**: Utiliser des prints pour les tests complexes
3. **Breakpoints**: Utiliser des breakpoints dans l'IDE
4. **Test Isolation**: Exécuter un test seul pour isoler le problème

---

## Exemples Concrets

### Test d'une Méthode Simple
```python
def test_player_add_piece():
    """Test that player can add a piece."""
    player = Player(id=0, name="Test")
    piece = Piece(type="I2", coords=[[0, 0]])
    
    player.add_piece(piece)
    
    assert len(player.remaining_pieces) == 20
    assert piece not in player.remaining_pieces
```

### Test d'une Classe Complexe
```python
def test_ai_controller_executes_turn():
    """Test that AIController executes a complete turn."""
    strategy = MockAIStrategy()
    animator = MockAIAnimator()
    controller = AIController(strategy, animator)
    game_context = create_game_context()
    player_state = PlayerStateMachine()
    
    controller.execute_turn(game_context, player_state)
    
    assert strategy.get_move.called
    assert animator.showThinkingIndicator.called
    assert animator.hideThinkingIndicator.called
```

### Test d'Intégration
```python
def test_game_flow_with_ai_players():
    """Test complete game flow with AI players."""
    game = Game(num_players=4)
    game.start_game()
    
    # Simulate AI turns
    for _ in range(10):
        if not game.is_game_over:
            current_player = game.current_player
            if current_player.is_ai:
                move = current_player.ai_strategy.get_move(game)
                if move:
                    game.play_move(move.piece, move.row, move.col)
                else:
                    game.pass_turn()
    
    assert game.is_game_over
    assert len(game.get_scores()) == 4
```

---

## Débogage

### Problèmes Communs
1. **Test Flaky**: Test qui passe parfois mais pas toujours
2. **Test Lent**: Test qui prend trop de temps
3. **Test Complexe**: Test qui fait trop de choses
4. **Test Dépendant**: Test qui dépend d'autres tests

### Solutions
1. **Isolation**: Isoler le problème en exécutant un test seul
2. **Logging**: Ajouter des logs pour voir ce qui se passe
3. **Mocking**: Utiliser des mocks pour contrôler les dépendances
4. **Refactoring**: Simplifier le test ou le code testé

### Outils
- **pytest**: Framework de test
- **coverage**: Mesurer la couverture
- **pytest-watch**: Exécuter les tests automatiquement
- **pytest-xdist**: Exécuter les tests en parallèle

---

## Maintenance

### Quand Mettre à Jour les Tests
1. **Nouveau code**: Toujours ajouter des tests
2. **Bug fix**: Ajouter un test qui aurait attrapé le bug
3. **Refactoring**: Mettre à jour les tests existants
4. **Nouvelle fonctionnalité**: Couvrir la nouvelle fonctionnalité

### Révision des Tests
1. **Code Review**: Faire reviewer les tests comme le code
2. **Coverage**: Vérifier la couverture régulièrement
3. **Performance**: Surveiller la performance des tests
4. **Qualité**: Maintenir la qualité des tests

### Documentation
- **README**: Documenter comment exécuter les tests
- **Comments**: Ajouter des commentaires dans les tests complexes
- **Examples**: Garder des exemples de bons tests
- **Guidelines**: Maintenir ce manuel à jour

---

## Références

### Documentation Interne
- [Test Types Guide](../docs/guides/test-types-guide.md)
- [Test Coverage Analysis](../docs/reports/test-types-analysis.md)
- [Test Implementation Summary](../docs/reports/final-test-summary.md)

### Externes
- [pytest documentation](https://docs.pytest.org/)
- [Python testing best practices](https://docs.python.org/3/library/unittest.html)
- [Testing strategies](https://martinfowler.com/articles/mocksArentStubs.html)

---

## Conclusion

Les tests sont un investissement dans la qualité et la maintenabilité du code. En suivant ce manuel, nous pouvons garantir que le projet Blokus reste robuste, maintenable et de haute qualité.

**Rappelez-vous**: Un bug sans test est un bug qui reviendra.
