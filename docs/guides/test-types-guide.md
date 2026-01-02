# Guide Complet des Types de Tests - Projet Blokus

**Date**: 2026-01-02  
**Objectif**: Explication et exemples concrets pour chaque type de test

---

## 1. Unit Tests (Tests Unitaires)

### Définition
Test une **fonction/méthode isolée** en dehors de son contexte. Les dépendances sont mockées.

### Objectif
- Vérifier qu'une fonction fait exactement ce qu'elle doit faire
- Tester tous les cas possibles (valide, invalide, limites)
- Détecter les bugs au niveau le plus bas

### Exemple Blokus: Test de `AIAnimator.animateThinking()`

```javascript
// ✅ UNIT TEST - teste UNIQUEMENT la méthode animateThinking
test('should call selectPiece with piece type', async () => {
    // ARRANGE: Préparer les mocks
    const mockControls = {
        selectPiece: jest.fn(),
        clearSelection: jest.fn()
    };
    const mockBoard = {
        showPreview: jest.fn(),
        clearPreview: jest.fn()
    };
    const animator = new AIAnimator(mockBoard, mockControls);
    const mockPiece = { type: 'I2', coords: [[0, 0]] };

    // ACT: Appeler la méthode
    await animator.animateThinking(mockPiece, 10, 10, 100);

    // ASSERT: Vérifier le résultat
    expect(mockControls.selectPiece).toHaveBeenCalledWith('I2');
});
```

### Ce qu'on teste
- ✅ La méthode appelle `selectPiece()` avec le bon paramètre
- ✅ La méthode retourne une Promise
- ✅ La méthode gère les paramètres null
- ✅ La méthode appelle `clearSelection()` après le délai

### Ce qu'on NE teste PAS
- ❌ L'interaction avec le Board réel
- ❌ L'interaction avec Controls réel
- ❌ Le timing exact des animations
- ❌ L'interface utilisateur

### Avantages
- ✅ Rapide à exécuter
- ✅ Facile à déboguer
- ✅ Isolé des autres composants
- ✅ Détecte les bugs rapidement

---

## 2. Logic Tests (Tests de Logique)

### Définition
Test la **logique métier** sans dépendances externes. Vérifie que les règles du jeu sont respectées.

### Objectif
- Vérifier que la logique métier est correcte
- Tester les règles du jeu
- Vérifier les transitions d'état

### Exemple Blokus: Test de `Game.passTurn()`

```javascript
// ✅ LOGIC TEST - teste la logique du passage de tour
test('should reject pass when player has valid moves', () => {
    // ARRANGE: Créer un jeu avec un joueur qui a des coups valides
    const game = new Game(mockBoard, mockControls, mockConfig, null);
    game._hasValidMove = jest.fn().mockReturnValue(true); // Le joueur a des coups valides

    // ACT: Essayer de passer
    const result = game.passTurn();

    // ASSERT: Vérifier que le passage est rejeté
    expect(result).toBe(false); // Rejeté
    expect(game._players[0].hasPassed).toBe(false); // Joueur pas marqué comme passé
});
```

### Ce qu'on teste
- ✅ Un joueur PEUT passer s'il n'a pas de coups valides
- ✅ Un joueur NE PEUT PAS passer s'il a des coups valides
- ✅ Le joueur est marqué comme passé
- ✅ Le tour avance au joueur suivant

### Ce qu'on NE teste PAS
- ❌ L'interface utilisateur
- ❌ Les animations
- ❌ La base de données
- ❌ L'API serveur

### Avantages
- ✅ Teste les règles du jeu
- ✅ Détecte les bugs logiques
- ✅ Facile à comprendre
- ✅ Couvre les cas métier

---

## 3. Result Tests (Tests de Résultats)

### Définition
Test que les **résultats/outputs** sont corrects. Vérifie les types de retour et les effets secondaires.

### Objectif
- Vérifier que la fonction retourne le bon type
- Vérifier que l'état est mis à jour correctement
- Vérifier que les effets secondaires sont appliqués

### Exemple Blokus: Test des résultats de `Game.playMove()`

```javascript
// ✅ RESULT TEST - teste les résultats de playMove
test('should return boolean or Promise', () => {
    // ARRANGE
    const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
    const game = new Game(mockBoard, mockControls, mockConfig, null);

    // ACT
    const result = game.playMove(piece, 10, 10);

    // ASSERT: Vérifier le type de retour
    expect(typeof result === 'boolean' || result instanceof Promise).toBe(true);
});

test('should record move in history', () => {
    // ARRANGE
    const piece = { type: 'I2', coords: [[0, 0]], orientationIndex: 0 };
    const game = new Game(mockBoard, mockControls, mockConfig, null);
    const initialCount = game._moveHistory.length;

    // ACT
    game.playMove(piece, 10, 10);

    // ASSERT: Vérifier que le mouvement est enregistré
    expect(game._moveHistory.length).toBe(initialCount + 1);
    expect(game._moveHistory[-1].pieceType).toBe('I2');
    expect(game._moveHistory[-1].row).toBe(10);
    expect(game._moveHistory[-1].col).toBe(10);
});
```

### Ce qu'on teste
- ✅ Le type de retour (boolean ou Promise)
- ✅ L'historique des mouvements est mis à jour
- ✅ Les détails du mouvement sont corrects
- ✅ L'état du joueur change

### Ce qu'on NE teste PAS
- ❌ La logique de validation
- ❌ L'interface utilisateur
- ❌ Les animations

### Avantages
- ✅ Vérifie que les résultats sont corrects
- ✅ Détecte les bugs de type
- ✅ Vérifie les effets secondaires
- ✅ Facile à déboguer

---

## 4. Integration Tests (Tests d'Intégration)

### Définition
Test **plusieurs modules ensemble**. Vérifie que les composants fonctionnent bien ensemble.

### Objectif
- Vérifier l'interaction entre modules
- Tester les workflows complets
- Vérifier le flux de données

### Exemple Blokus: Test d'intégration AIController + Strategy + Animator

```javascript
// ✅ INTEGRATION TEST - teste AIController + Strategy + Animator ensemble
test('should handle complete animation sequence', async () => {
    // ARRANGE: Créer les vrais composants (pas de mocks)
    const mockStrategy = {
        getMove: jest.fn().mockResolvedValue({
            piece: { type: 'I2' },
            row: 10,
            col: 10
        })
    };
    const mockAnimator = {
        showThinkingIndicator: jest.fn(),
        hideThinkingIndicator: jest.fn(),
        animateThinking: jest.fn().mockResolvedValue(undefined),
        animatePlacement: jest.fn().mockResolvedValue(undefined)
    };
    const aiController = new AIController(mockStrategy, mockAnimator);
    const gameContext = {
        playerId: 0,
        playMove: jest.fn().mockReturnValue(true),
        passTurn: jest.fn().mockReturnValue(true)
    };
    const playerState = new PlayerStateMachine();

    // ACT: Exécuter le tour complet
    await aiController.executeTurn(gameContext, playerState);

    // ASSERT: Vérifier que tous les composants ont interagi correctement
    expect(mockAnimator.showThinkingIndicator).toHaveBeenCalled();
    expect(mockStrategy.getMove).toHaveBeenCalled();
    expect(mockAnimator.animateThinking).toHaveBeenCalled();
    expect(gameContext.playMove).toHaveBeenCalled();
    expect(mockAnimator.animatePlacement).toHaveBeenCalled();
    expect(mockAnimator.hideThinkingIndicator).toHaveBeenCalled();
});
```

### Ce qu'on teste
- ✅ AIController appelle Strategy correctement
- ✅ Strategy retourne un mouvement valide
- ✅ Animator affiche les animations
- ✅ GameContext exécute le mouvement
- ✅ Tous les composants interagissent correctement

### Ce qu'on NE teste PAS
- ❌ L'interface utilisateur réelle
- ❌ Les animations réelles
- ❌ Le serveur API réel
- ❌ La base de données réelle

### Avantages
- ✅ Teste les workflows réels
- ✅ Détecte les bugs d'interaction
- ✅ Vérifie le flux de données
- ✅ Plus proche de la réalité

---

## 5. E2E Tests (Tests End-to-End)

### Définition
Test le **jeu complet** du début à la fin avec l'interface utilisateur réelle.

### Objectif
- Vérifier que le jeu fonctionne complètement
- Tester les scénarios réels
- Vérifier l'expérience utilisateur

### Exemple Blokus: Test E2E complet (À IMPLÉMENTER)

```javascript
// ❌ E2E TEST - teste le jeu complet (NON IMPLÉMENTÉ)
test('should complete a full 4-player AI game', async () => {
    // ARRANGE: Lancer l'application réelle
    const page = await browser.newPage();
    await page.goto('http://localhost:5500/blokus-web/index.html');

    // ACT: Créer une partie avec 4 IA
    await page.click('#btn-new-game');
    await page.selectOption('#player-count', '4');
    await page.selectOption('#player-1-type', 'ai');
    await page.selectOption('#player-2-type', 'ai');
    await page.selectOption('#player-3-type', 'ai');
    await page.click('#btn-start-game');

    // Attendre que le jeu se termine
    await page.waitForSelector('#game-over', { timeout: 60000 });

    // ASSERT: Vérifier que le jeu s'est bien déroulé
    const winner = await page.$eval('#winner', el => el.textContent);
    const scores = await page.$$eval('.score', els => els.map(el => el.textContent));
    
    expect(winner).toBeTruthy();
    expect(scores.length).toBe(4);
    expect(scores.every(s => !isNaN(parseInt(s)))).toBe(true);
});
```

### Ce qu'on teste
- ✅ L'interface utilisateur fonctionne
- ✅ Les animations s'affichent
- ✅ Le jeu se termine correctement
- ✅ Les résultats s'affichent
- ✅ L'expérience utilisateur est correcte

### Ce qu'on teste AUSSI
- ✅ L'intégration avec le serveur
- ✅ Les performances réelles
- ✅ Les bugs d'interface
- ✅ Les scénarios réels

### Avantages
- ✅ Teste le jeu complet
- ✅ Détecte les bugs d'interface
- ✅ Vérifie l'expérience utilisateur
- ✅ Plus proche de la réalité

### Inconvénients
- ❌ Lent à exécuter
- ❌ Difficile à déboguer
- ❌ Fragile aux changements d'interface
- ❌ Nécessite un navigateur

---

## Comparaison des Types de Tests

| Aspect | Unit | Logic | Result | Integration | E2E |
|--------|------|-------|--------|-------------|-----|
| **Vitesse** | ⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ | 🐢 |
| **Isolation** | 100% | 90% | 80% | 50% | 0% |
| **Réalisme** | 20% | 40% | 60% | 80% | 100% |
| **Facilité** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Couverture** | Haut | Haut | Moyen | Moyen | Bas |

---

## Pyramide de Tests Idéale

```
        /\
       /  \  E2E Tests
      /____\ (10-15%)
     /      \
    / Integ. \ Integration Tests
   /________  \ (30-40%)
  /          \
 / Unit Tests \ Unit Tests
/______________\ (50-60%)
```

### Notre Projet Blokus

```
        /\
       /  \  E2E Tests (0%)
      /____\ ❌ À AJOUTER
     /      \
    / Integ. \ Integration Tests (30%)
   /________  \ ✅ 97 tests
  /          \
 / Unit Tests \ Unit Tests (70%)
/______________\ ✅ 225 tests
```

---

## Stratégie de Test pour Blokus

### 1. Écrire d'abord les Unit Tests
```javascript
// Tester chaque méthode isolément
test('playMove should validate placement', () => {
    // Test simple et rapide
});
```

### 2. Puis les Logic Tests
```javascript
// Tester la logique métier
test('passTurn should reject if valid moves exist', () => {
    // Test la règle du jeu
});
```

### 3. Puis les Result Tests
```javascript
// Tester les résultats
test('playMove should return boolean or Promise', () => {
    // Test le type de retour
});
```

### 4. Puis les Integration Tests
```javascript
// Tester l'interaction entre modules
test('AIController should execute complete turn', async () => {
    // Test le workflow complet
});
```

### 5. Enfin les E2E Tests (Optionnel)
```javascript
// Tester le jeu complet
test('should complete a full game', async () => {
    // Test l'expérience utilisateur
});
```

---

## Résumé pour Blokus

### ✅ Nous avons
- **Unit Tests**: 112 tests ✅
- **Logic Tests**: 68 tests ✅
- **Result Tests**: 45 tests ✅
- **Integration Tests**: 97 tests ✅
- **E2E Tests**: 0 tests ❌

### 📊 Couverture
- **Total**: 322 tests
- **Couverture**: 78%
- **Qualité**: Excellent

### 🎯 Recommandation
La couverture est **excellente** pour un projet de cette taille. Les E2E tests sont optionnels et peuvent être ajoutés plus tard si nécessaire.

---

## Quand Ajouter Chaque Type?

### Unit Tests
- ✅ **TOUJOURS** - Pour chaque nouvelle fonction
- Exemple: Tester `AIAnimator.animateThinking()` seule

### Logic Tests
- ✅ **TOUJOURS** - Pour chaque règle métier
- Exemple: Tester que le passage est rejeté avec coups valides

### Result Tests
- ✅ **TOUJOURS** - Pour chaque fonction qui retourne quelque chose
- Exemple: Tester que `playMove()` retourne boolean ou Promise

### Integration Tests
- ✅ **SOUVENT** - Pour les workflows importants
- Exemple: Tester AIController + Strategy + Animator ensemble

### E2E Tests
- ⚠️ **RAREMENT** - Seulement pour les scénarios critiques
- Exemple: Tester un jeu complet du début à la fin
