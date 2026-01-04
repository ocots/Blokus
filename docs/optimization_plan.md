# Plan d'Optimisation du Moteur de Jeu Blokus

Le profiling a révélé que la validation des coups (`is_valid_placement`) consomme 99% du temps de simulation. Cela est dû au recalcul systématique de l'état global du joueur (cellules occupées, coins disponibles, bords interdits) pour chaque position testée.

## 1. Diagnostic des Goulots d'Étranglement
- **Fonctions critiques** : `get_player_cells`, `get_player_edges`, `get_player_corners`.
- **Volume d'appels** : > 1 000 000 d'appels pour seulement 5 parties.
- **Cause** : Complexité algorithmique de O(N_coups_possibles * N_cases_plateau) au lieu de O(N_coups_possibles).

## 2. Solutions Implémentées

### Phase 1 : Mise en cache de l'état (Mise en Production)

- **Action** : Ajout d'attributs `_cells_cache`, `_corners_cache`, `_edges_cache` dans `Board`.
- **Mécanisme** : Invalidation du cache uniquement lors d'un `place_piece`.
- **Résultat** : Réduction massive du nombre de calculs par tour.

### Phase 2 : Optimisation des Boucles (Mise en Production)

- **Action** : Refactoring de `get_placement_rejection_reason`.
- **Optimisation** :
  - Fusion des boucles "Bounds Check" et "Vacancy Check".
  - Utilisation de `set.isdisjoint()` au lieu d'intersections manuelles.
  - Accès direct à `board.grid` (NumPy array) sans passer par les accesseurs.

## 3. Résultats et Benchmark

Mesures effectuées localement (MacBook M chip) sur 5 parties complètes :

| Version | Temps Total (5 parties) | Temps Moyen / Partie | Speedup | Notes |
|---------|-------------------------|----------------------|---------|-------|
| **Baseline** | ~50.00s | 10.00s | 1x | Lenteur extrême due aux recalculs |
| **Avec Cache** | 6.80s | 1.36s | ~7x | Le cache élimine 90% du travail |
| **Boucles Optimisées** | **1.89s** | **0.38s** | **~26x** | Version finale retenue |
| NumPy Vectorisé | ~6.20s | 1.24s | ~8x | **Échec** : Overhead trop élevé pour petits tableaux |
| Numba JIT | ~7.30s | 1.46s | ~7x | **Échec** : Coût de conversion Python->C trop élevé |

> **Note CI** : Sur GitHub Actions, le temps est passé de ~21s/épisode à **~0.5s/épisode** (45x gain observé).

## 4. Tentatives Infructueuses (Archivées)

### A. Vectorisation NumPy

Nous avons tenté de remplacer les boucles Python par des opérations matricielles :

```python
# Masque binaire pré-calculé pour chaque pièce
mask = get_piece_mask(piece_type, orientation)
# Vérification vectorisée
slice = board.grid[row:row+h, col:col+w]
if np.any(slice[mask]): return False
```

**Pourquoi un échec ?**
Les pièces de Blokus sont petites (1 à 5 cases). Le coût fixe de création des slices NumPy et l'appel à `np.any` en C est supérieur au coût de 5 itérations d'une boucle Python optimisée.

### B. Compilation Numba JIT

Nous avons tenté de compiler les fonctions de validation en code machine avec `@njit`.
**Pourquoi un échec ?**
Le moteur de jeu manipule des `set` de tuples Python `(row, col)`. Pour appeler une fonction Numba efficace, il faut convertir ces sets en `np.array` contigus (`int32`). Cette conversion (`np.array(list(positions))`) effectuée à chaque coup coûte bien plus cher que le gain obtenu par l'exécution du code compilé.

## 5. Prochaines Étapes

- [x] Déployer le cache et les boucles optimisées sur `main`.
- [ ] Lancer un entraînement à grande échelle (10 000 épisodes).
- [ ] (Futur) Parallélisation multi-processus (`SubprocVecEnv`) pour scaler horizontalement.
