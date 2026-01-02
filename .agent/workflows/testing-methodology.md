---
description: Méthodologie complète de développement guidé par les tests
---

# Méthodologie de Développement Guidé par les Tests

**Version**: 1.0  
**Last Updated**: 2026-01-02  
**Purpose**: Guide méthodologique pour le développement TDD et l'écriture de tests

---

## 🎯 Philosophie Fondamentale

### Le Principe d'Or
**NE JAMAIS modifier un test pour le faire passer**  
Un test qui échoue est une **information précieuse**, pas un problème à éliminer.

### Mentalité Correcte
- ❌ **Mauvaise**: "Comment faire passer ce test ?"
- ✅ **Bonne**: "Que m'indique ce test sur mon code ?"

### Le Test est Spécification
Un test n'est pas un obstacle, c'est la **définition du comportement attendu**.

---

## 🔄 Méthodologie TDD (Test-Driven Development)

### Les 3 Cycles du TDD

#### 1. 🔴 RED - Écrire un test qui échoue
```python
# Écrire le test AVANT le code
def test_game_manager_sets_starting_player():
    """Test that GameManager sets starting player correctly."""
    manager = GameManager(mock_players)
    
    manager.set_starting_player(2)
    
    assert manager.current_player_index == 2
    assert manager.current_player.id == 2
```

**Pourquoi il doit échouer**:
- ✅ Confirme que le test fonctionne
- ✅ Définit clairement le besoin
- ✅ Évite les faux positifs

#### 2. 🟢 GREEN - Faire passer le test (MAIS correctement)
```python
# Implémentation MINIMALE mais CORRECTE
def set_starting_player(self, player_id: int) -> None:
    """Set starting player by ID."""
    for player in self.players:
        if player.id == player_id:
            self.current_player_index = self.players.index(player)
            return
    raise ValueError(f"Player with ID {player_id} not found")
```

**Principes**:
- ✅ **Code minimal**: Juste assez pour faire passer le test
- ✅ **Code correct**: Respecte les règles métier
- ✅ **Pas de tricherie**: Ne pas modifier le test

#### 3. 🔄 REFACTOR - Améliorer le code
```python
# Améliorer la structure sans changer le comportement
def set_starting_player(self, player_id: int) -> None:
    """Set starting player by ID."""
    player = self._find_player_by_id(player_id)
    if player is None:
        raise ValueError(f"Player with ID {player_id} not found")
    self.current_player_index = self.players.index(player)

def _find_player_by_id(self, player_id: int) -> Optional[Player]:
    """Find player by ID - helper method for reuse."""
    for player in self.players:
        if player.id == player_id:
            return player
    return None
```

**Principes**:
- ✅ **Comportement inchangé**: Les tests passent toujours
- ✅ **Code plus propre**: Meilleure structure
- ✅ **Réutilisabilité**: Extraire les helpers

---

## 📊 Ordre d'Écriture des Tests

### Progression Recommandée

#### Phase 1: Tests Unitaires (Base)
```python
# 1. Tester les méthodes simples
def test_player_initialization():
    player = Player(id=0, name="Alice")
    assert player.id == 0
    assert player.name == "Alice"

# 2. Tester les cas limites
def test_player_with_negative_id():
    with pytest.raises(ValueError):
        Player(id=-1, name="Invalid")

# 3. Tester les états
def test_player_initial_pieces():
    player = Player(id=0, name="Alice")
    assert len(player.remaining_pieces) == 21
```

#### Phase 2: Tests de Logique (Règles)
```python
# 4. Tester les règles métier
def test_player_cannot_pass_with_valid_moves():
    player = create_test_player()
    game = create_test_game_with_valid_moves(player)
    
    result = player.try_pass_turn(game)
    
    assert result is False
    assert player.status != PlayerStatus.PASSED

# 5. Tester les transitions d'état
def test_player_status_transitions():
    player = Player(id=0, name="Alice")
    
    player.start_turn()
    assert player.status == PlayerStatus.ACTIVE
    
    player.pass_turn()
    assert player.status == PlayerStatus.PASSED
```

#### Phase 3: Tests de Résultats (Outputs)
```python
# 6. Tester les retours
def test_game_manager_returns_correct_scores():
    game = create_test_game()
    scores = game.get_scores()
    
    assert isinstance(scores, list)
    assert len(scores) == 4
    assert all(isinstance(score, int) for score in scores)

# 7. Tester les effets secondaires
def test_play_move_updates_history():
    game = create_test_game()
    initial_count = len(game.move_history)
    
    game.play_move(test_piece, 10, 10)
    
    assert len(game.move_history) == initial_count + 1
```

#### Phase 4: Tests d'Intégration (Interactions)
```python
# 8. Tester les interactions
def test_ai_controller_with_strategy():
    strategy = MockAIStrategy()
    controller = AIController(strategy)
    game = create_test_game()
    
    controller.execute_turn(game)
    
    assert strategy.get_move.called
    assert game.move_history[-1].player_id == 0

# 9. Tester les workflows
def test_complete_turn_flow():
    game = create_test_game()
    player = game.current_player
    
    player.start_turn()
    move = player.ai_strategy.get_move(game)
    game.play_move(move.piece, move.row, move.col)
    player.end_turn()
    
    assert player.status == PlayerStatus.WAITING
    assert len(game.move_history) > 0
```

#### Phase 5: Tests E2E (Optionnel)
```python
# 10. Tester les scénarios complets
def test_complete_game_with_4_players():
    game = Game(num_players=4)
    game.start_game()
    
    while not game.is_game_over:
        current_player = game.current_player
        if current_player.is_ai:
            move = current_player.ai_strategy.get_move(game)
            if move:
                game.play_move(move.piece, move.row, move.col)
            else:
                game.pass_turn()
    
    assert game.is_game_over
    assert len(game.get_winner()) == 1
```

---

## 🚨 Processus de Diagnostic des Échecs

### Étape 1: Analyser l'Échec
```python
# Échec typique
FAILED test_game_manager_sets_starting_player.py::test_set_starting_player
AssertionError: assert 0 == 2
Expected: 2
Actual: 0
```

### Étape 2: Poser les Bonnes Questions
1. **Le test est-il correct ?**
   - L'assertion reflète-t-elle le besoin réel ?
   - Les données de test sont-elles valides ?

2. **Le comportement attendu est-il correct ?**
   - Est-ce que le code DEVRAIT faire ça ?
   - Est-ce que la spécification est bonne ?

3. **Le code implémente-t-il correctement le comportement ?**
   - Est-ce un bug d'implémentation ?
   - Est-ce un bug de conception ?

### Étape 3: Décider de l'Action

| Scénario | Action | Raison |
|----------|--------|--------|
| Test incorrect | 📝 **Modifier le test** | Le test ne reflète pas le besoin |
| Spécification incorrecte | 🤔 **Revoir la spécification** | Le besoin est mal défini |
| Code incorrect | 🔧 **Corriger le code** | L'implémentation est fausse |
| Code manquant | ➕ **Implémenter le code** | Fonctionnalité non implémentée |

---

## 🔄 Alternance Code-Tests

### Stratégie Recommandée

#### Développement d'une Nouvelle Fonctionnalité
```python
# 1. Écrire le test principal
def test_new_feature_basic_functionality():
    feature = NewFeature()
    result = feature.do_something()
    assert result == expected_value

# 2. Implémenter le minimum
class NewFeature:
    def do_something(self):
        return expected_value

# 3. Ajouter les tests de cas limites
def test_new_feature_edge_cases():
    feature = NewFeature()
    
    with pytest.raises(ValueError):
        feature.do_something(None)
    
    with pytest.raises(ValueError):
        feature.do_something("invalid")

# 4. Implémenter la validation
class NewFeature:
    def do_something(self, input_data):
        if input_data is None or input_data == "invalid":
            raise ValueError("Invalid input")
        return expected_value

# 5. Ajouter les tests d'intégration
def test_new_feature_integration():
    feature = NewFeature()
    system = System(feature)
    
    result = system.process_data(test_data)
    assert result.success is True

# 6. Implémenter l'intégration
# ... et continuer le cycle
```

### Règles d'Alternance
1. **Toujours écrire le test en premier**
2. **Implémenter juste assez pour faire passer**
3. **Ajouter des tests avant d'ajouter du code**
4. **Refactoriser après chaque test qui passe**
5. **Ne jamais modifier un test pour le faire passer**

---

## 🎯 Bonnes Pratiques de Diagnostic

### Checklist de Diagnostic
- [ ] Le test est-il lisible et compréhensible ?
- [ ] L'assertion est-elle précise ?
- [ ] Les données de test sont-elles valides ?
- [ ] Le comportement attendu est-il documenté ?
- [ ] Le message d'erreur est-il clair ?

### Anti-patterns à Éviter
```python
# ❌ ANTI-PATTERN: Modifier le test pour le faire passer
def test_something():
    # Le test échoue
    assert some_function() == 42
    
    # On modifie le test pour qu'il passe
    # assert some_function() == get_actual_value()  # MAUVAIS !

# ✅ BONNE PRATIQUE: Comprendre pourquoi ça échoue
def test_something():
    # Le test échoue -> analyser pourquoi
    assert some_function() == 42  # Garder l'assertion originale
    # Corriger le code pour qu'il retourne 42
```

---

## 📈 Métriques de Qualité

### Indicateurs de Bonne Méthodologie
- ✅ **Temps de cycle**: < 5 minutes par cycle RED-GREEN-REFACTOR
- ✅ **Taille des implémentations**: < 10 lignes par GREEN
- ✅ **Couverture**: Augmente progressivement
- ✅ **Tests flaky**: 0%

### Signes d'Alerte
- ❌ Tests modifiés après écriture
- ❌ Implémentations complexes avant les tests
- ❌ Tests qui ne testent rien
- ❌ Couverture qui baisse

---

## 🔄 Workflow Complet

### Pour une Nouvelle Fonctionnalité
1. **Comprendre le besoin** (documentation, discussion)
2. **Écrire le test principal** (RED)
3. **Implémenter le minimum** (GREEN)
4. **Ajouter les tests de cas limites** (RED)
5. **Implémenter la validation** (GREEN)
6. **Ajouter les tests d'intégration** (RED)
7. **Implémenter l'intégration** (GREEN)
8. **Refactoriser** (REFACTOR)
9. **Répéter** jusqu'à couverture complète

### Pour un Bug Fix
1. **Reproduire le bug avec un test** (RED)
2. **Vérifier que le test échoue** (CONFIRMATION)
3. **Corriger le bug** (GREEN)
4. **Ajouter des tests de régression** (PLUS DE RED)
5. **Implémenter si nécessaire** (GREEN)
6. **Refactoriser** (REFACTOR)

---

## 🎯 Conclusion

La méthodologie TDD n'est pas seulement une technique, c'est une **philosophie de développement**. Le test n'est pas l'ennemi, il est ton **guide**.

**Rappelez-vous**:
- Un test qui échoue est une **opportunité d'apprendre**
- La qualité vient de la **discipline**, pas des raccourcis
- Le code est **maintenable** grâce aux tests, pas malgré eux

**Le test passe quand le code est correct, pas l'inverse.**
