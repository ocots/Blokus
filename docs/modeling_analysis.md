# Analyse de Modélisation pour Blokus RL

Comparaison des approches de représentation d'état, d'espace d'actions, et d'algorithmes pour un apprentissage par renforcement efficace.

---

## 1. Représentation de l'État (Observation)

### Option A : Tenseur Multi-Canal Basique

**Structure** : `(20, 20, C)` où C = nombre de canaux

| Canal | Description |
|-------|-------------|
| 0-3 | Occupation par joueur (1 si occupé, 0 sinon) |
| 4 | Cases vides |
| 5 | Indicateur joueur courant (tout à 1 ou encodage one-hot) |

**Avantages** :

- Simple à implémenter
- Compatible avec tout CNN standard
- Faible empreinte mémoire (~1.6 KB par état)

**Inconvénients** :

- Pas d'information sur les pièces restantes
- Pas d'historique des coups
- Le réseau doit réapprendre les contraintes de placement

**Score robustesse** : ⭐⭐☆☆☆

---

### Option B : Tenseur Enrichi Style AlphaZero ✅ CHOISI

**Structure** : `(20, 20, C)` avec C ≈ 47 canaux

| Canaux | Description |
|--------|-------------|
| 0-3 | Occupation par joueur |
| 4-7 | Coins valides par joueur (où chaque joueur peut jouer) |
| 8-11 | Historique T-1 (position précédente) |
| 12-15 | Historique T-2 |
| 16 | Numéro de tour (normalisé 0-1) |
| 17-37 | Pièces restantes joueur courant (1 canal par type, filled si disponible) |

**Avantages** :

- Information complète pour la prise de décision
- L'historique aide à détecter les patterns de jeu
- **Prouvé efficace** par AlphaZero/AlphaGo

**Inconvénients** :

- Plus coûteux en mémoire (~8 KB par état)
- Complexité d'implémentation accrue

**Score robustesse** : ⭐⭐⭐⭐⭐

---

## 2. Espace d'Actions

### Défi Principal

Blokus a un espace d'actions gigantesque :

- 21 pièces × 8 orientations × 400 positions = **67,200 actions** théoriques
- En pratique : ~500-2000 actions valides par tour

### Option Choisie : Flat + Masquage ✅

```python
def get_action(state):
    q_values = network(state)           # (67200,)
    mask = get_valid_actions_mask(state) # (67200,) binaire
    q_values[~mask] = -inf
    return argmax(q_values)
```

Avec réduction via symétries : **~6000 actions uniques**

---

## 3. Fonction de Récompense

### Option Choisie : Potential-Based Shaping ✅

```python
def potential(state, player_id):
    placed = sum(piece.size for piece in state.placed_pieces[player_id])
    corners = len(state.valid_corners[player_id])
    big_pieces_left = sum(1 for p in state.remaining[player_id] if p.size >= 4)
    
    return (
        0.5 * placed / 89 +
        0.3 * corners / 50 +
        -0.2 * big_pieces_left / 12
    )

def shaped_reward(state, action, next_state):
    gamma = 0.99
    base = sparse_reward(state, action, next_state)
    shaping = gamma * potential(next_state) - potential(state)
    return base + shaping
```

**Garantit l'optimalité** tout en accélérant la convergence.

---

## 4. Comparaison des Algorithmes

| Critère | DQN | PPO | AlphaZero |
|---------|-----|-----|-----------|
| **Sample Efficiency** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Compute requis** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Multi-joueurs** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Implémentation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

**Stratégie** : DQN → PPO → AlphaZero (progression)

---

## 5. Architecture Réseau

```
Input: (20, 20, 47)
    │
Conv2D(64, 3×3) + BN + ReLU
    │
ResidualBlock(64) × 8
    │
    ├── Value Head → V(s)
    └── Policy Head → π(a|s)
```

~2M paramètres

---

## 6. Curriculum Learning

| Phase | Config | Objectif |
|-------|--------|----------|
| 1 | 2P self-play | Apprendre règles et patterns |
| 2 | 4P vs random | Adaptation multi-joueurs |
| 3 | 4P self-play | Stratégies compétitives |
| 4 | vs best checkpoints | Polish final |

---

## 7. Gestion des Modèles (Phase 4)

### Structure du Registre

Pour gérer les différentes configurations (nombre de joueurs, style de jeu), les modèles sont organisés hiérarchiquement :

```bash
models/
  ├── 2_players/
  │   ├── aggressive_v1.zip   # Reward: contact + territories
  │   └── defensive_v1.zip    # Reward: coverage + blockades
  ├── 4_players/
  │   ├── standard_v1.zip     # Mixed reward
  │   └── filler_ai.zip       # Lightweight model for 3p mode
  └── registry.json           # Mapping personas -> files
```

### Profils d'IA (Personas)

- **Agressif** : Favorise le contact avec les pièces adverses.
- **Défensif** : Favorise la consolidation de territoire.
- **Efficace** : Minimise les pièces restantes à tout prix.
