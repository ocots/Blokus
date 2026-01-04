# Plan d'Optimisation du Moteur de Jeu Blokus

Le profiling a révélé que la validation des coups (`is_valid_placement`) consomme 99% du temps de simulation. Cela est dû au recalcul systématique de l'état global du joueur (cellules occupées, coins disponibles, bords interdits) pour chaque position testée.

## 1. Diagnostic des Goulots d'Étranglement
- **Fonctions critiques** : `get_player_cells`, `get_player_edges`, `get_player_corners`.
- **Volume d'appels** : > 1 000 000 d'appels pour seulement 5 parties.
- **Cause** : Complexité algorithmique de O(N_coups_possibles * N_cases_plateau) au lieu de O(N_coups_possibles).

## 2. Stratégie d'Optimisation

### Phase 1 : Mise en cache de l'état (Quick Win)
- **Objectif** : Ne calculer les coins et bords d'un joueur qu'une seule fois par tour.
- **Action** : Ajouter des attributs de cache dans `Board` ou `Game` pour stocker les `set` de coordonnées des coins et bords.
- **Gain attendu** : Facteur 10x à 50x.

### Phase 2 : Approche par Masques Binaires (Vectorisation)
- **Objectif** : Transformer les vérifications de collision en opérations logiques matricielles.
- **Action** : 
  - Maintenir un masque 2D (NumPy) pour chaque couleur.
  - Créer un masque "Bords Interdits" (dilatation du masque de couleur).
  - Créer un masque "Coins Valides" (coins des pièces posées).
  - Valider un placement par un simple `np.any(piece_mask & valid_corners_mask)` et `!np.any(piece_mask & forbidden_mask)`.
- **Gain attendu** : Facteur 100x+.

### Phase 3 : Parallélisation (Scaling)
- **Objectif** : Utiliser tous les coeurs du CPU.
- **Action** : Passer à un runner multi-environnements (`SubprocVecEnv`).

## 3. Étapes d'Exécution
1. [ ] Modifier `Board` pour supporter le cache des métadonnées (cellules, coins, bords).
2. [ ] Refactoriser `rules.py` pour utiliser ce cache.
3. [ ] Mesurer le nouveau temps de simulation avec `profile_env.py`.
4. [ ] (Optionnel) Implémenter la version vectorisée si le gain de la Phase 1 est insuffisant.
