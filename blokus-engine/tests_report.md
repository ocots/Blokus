# Rapport de Couverture de Tests - Blokus Engine (Python)

Ce rapport analyse l'état actuel des tests pour le moteur de jeu Blokus (`blokus-engine`) et propose des améliorations pour atteindre une couverture "excellente" et éviter les régressions ("bugs bêtes").

## 1. État des lieux (Existant)

La suite de tests actuelle est bien structurée et couvre les mécaniques principales.

**Points forts :**

* **Mécaniques de Jeu (`test_game.py`)** : Initialisation, validation des coups, tour par tour, scoring, conditions de victoire.
* **Règles de Placement (`test_rules.py`)** : Coups initiaux, adjacence diagonale, interdiction adjacence par les bords.
* **Gestion des Joueurs (`test_player.py`)** : Initialisation, calcul de score (bonus +15/+20), et **sérialisation/désérialisation** (JSON).
* **Environnement RL (`rl/test_environment.py`)** : Forme des observations (Tensor 20x20x47), encodage/décodage des actions.

**Couverture estimée :** ~80% sur le "Happy Path" (cas nominaux).

## 2. Tests Manquants pour l'Excellence ("Bug Prevention")

Pour passer de "fonctionnel" à "robuste" et éviter les erreurs de type `AttributeError` ou appels de fonctions inexistantes, voici les tests à ajouter :

### A. Tests Défensifs & "Dumb Bugs"

Ces tests visent à casser le code avec des entrées invalides ou inattendues.

* **Entrées nulles ou malformées :**
  * Que se passe-t-il si `play_move(None)` est appelé ?
  * Que se passe-t-il si un `Move` a un `piece_type` invalide (ex: entier hors enum) ?
  * **Risque :** Crash runtime (`AttributeError: 'NoneType' has no attribute...`).
* **Désérialisation Robuste (`test_player_factory.py`) :**
  * `Player.from_dict({})` (dictionnaire vide ou incomplet).
  * Injection de types incorrects dans le JSON.
* **Limites du Board (`test_board_boundaries.py`) :**
  * Appels à `get_cell(-1, -1)` ou `get_cell(100, 100)`. `Board.get_cell` retourne `-1` dans ces cas, mais les consommateurs de cette fonction gèrent-ils correctement le `-1` ?

### B. Tests de Logique Profonde (Complex State)

Les tests actuels partent souvent d'un plateau vide ou peu rempli.

* **Vrai Blocage (Endgame) :**
  * Dans `test_rules.py`, le test `test_no_move_when_blocked` conclut actuellement que le coup est... valide. Il manque un test simulant un joueur **réellement** bloqué (aucun coin disponible ou aucun espace pour ses pièces restantes).
  * Vérifier que `get_valid_moves` retourne une liste vide dans ce cas.
* **State Machine Transitions :**
  * Un joueur peut-il passer de `PASSED` à `PLAYING` ? Le système l'empêche-t-il ?
* **Plateau "Plein" :**
  * Simuler un plateau où il ne reste *aucune* place.

### C. Tests de Robustesse API & RL

* **RL Observations :**
  * Le test actuel vérifie la *forme* (shape) du tenseur. Il faut vérifier le *contenu*.
  * **Test :** Placer une pièce I1 en (0,0) pour le joueur 0, et affirmer que `obs[0, 0, channel_player_0] == 1`.
  * **Risque :** Le réseau de neurones apprend sur du bruit si les canaux sont permutés.

## 3. Stratégie Anti-"Fonctions Inexistantes"

Les erreurs de type "fonction inexistante" surviennent souvent lors de refactoring (renommage de méthode) dans les branches non couvertes par les tests.

**Solutions :**

1. **Usage de MyPy (Static Analysis) - CRITIQUE :**
    * Python est dynamique. Seul MyPy peut garantir que vous n'appelez pas une méthode qui n'existe pas *sans* exécuter le code.
    * **Action :** Ajouter une étape `mypy src/` dans le workflow CI/CD.

2. **Tests de Propriétés (Hypothesis) :**
    * Au lieu d'écrire des cas unitaires, utiliser `hypothesis` pour générer des milliers de parties aléatoires et vérifier que le jeu ne crashe jamais (`assert not crashed`).

## 4. Plan d'Action Concret

Voici les fichiers de tests recommandés à créer/enrichir :

| Fichier Cible | Contenu à ajouter | Priorité |
| :--- | :--- | :--- |
| `tests/test_corner_cases.py` | Entrées `None`, types invalides, injections JSON corrompues. | Haute |
| `tests/test_game_logic_deep.py` | Scénarios de fin de partie, blocage total, scores complexes. | Moyenne |
| `tests/rl/test_obs_validity.py` | Vérification pixel-perfect du contenu des tenseurs d'observation. | Haute (pour RL) |
| `github/workflows/ci.yml` | Ajouter `mypy` strict check. | Critique |

## 5. Workflow Suggéré (basé sur @[/blokus-test-python])

1. **Lancer MyPy** : Corriger toutes les erreurs de types statiques.
2. **Créer `tests/test_corner_cases.py`** : Commencer par tenter de faire crasher le jeu avec des inputs horribles.
3. **Refactoriser avec confiance** : Une fois ces filets de sécurité en place, vous pouvez modifier l'architecture interne sans peur.
