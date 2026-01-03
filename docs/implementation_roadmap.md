# Plan d'Implémentation - Blokus RL

Roadmap détaillé pour le développement du projet.

---

## Phase 1 : Moteur de Jeu (Python) 🎮 - **TERMINÉ**

**Objectif** : Créer le cœur logique du jeu Blokus.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 1.1 | Créer la structure du projet | `blokus-engine/` |
| 1.2 | Implémenter les 21 pièces avec rotations/symétries | `pieces.py` |
| 1.3 | Implémenter le plateau 20×20 | `board.py` |
| 1.4 | Implémenter les règles de placement | `rules.py` |
| 1.5 | Créer le gestionnaire de partie | `game.py` |
| 1.6 | Tests unitaires du moteur | `tests/` |

---

## Phase 2 : Interface Web (HTML/JS) 💻 - **TERMINÉ**

**Objectif** : Interface jouable pour les parties en famille.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 2.1 | Refactoring Architecture JS (ES6 + DIP) | `js/` |
| 2.2 | Rendu complet (Layout, Netteté) | `style.css` |
| 2.3 | Interactions (Sélection, Rotation R/S, Placement) | `controls.js` |
| 2.4 | Système de tests JS complet | `tests/` |

---

## Phase 3 : Refactoring & Serveur API 🌐 - **TERMINÉ**

**Objectif** : Robuster le code Python et connecter l'interface.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 3.1 | **Refactoring Python** : Appliquer DIP (injection dépendances) | `blokus-engine/` |
| 3.2 | **Refactoring** : Couverture tests 100% sur cœur | `tests/` |
| 3.3 | Créer le serveur **FastAPI** | `api/main.py` |
| 3.4 | Endpoints : `GET /state`, `POST /move`, `POST /reset` | `api/routes.py` |
| 3.5 | Connecter l'interface web au serveur (Client API) | `js/api.js` |

---

## Phase 3.5 : Menu & Polish UI 🎨 - **TERMINÉ**

**Objectif** : Améliorer l'expérience utilisateur et permettre la configuration de partie.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 3.5.1 | **Menu Modal** : HTML/CSS pour configuration partie | `index.html` |
| 3.5.2 | **Logique Menu** : Gestion formulaire (Joueurs, Noms, Couleurs) | `js/setup.js` |
| 3.5.3 | **Score Panel** : Redesign vertical (Nom + Score) | `style.css` |
| 3.5.4 | **Communication API** : Envoyer config partie au serveur | `js/api.js` |


---

## Phase 3.75 : Refactoring & Robustesse 🛡️ - **TERMINÉ**

**Objectif** : Améliorer l'architecture, la qualité du code et l'accessibilité.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 3.75.1 | **Tests JS** : Unit testing avec Jest | `tests/setup.test.js`, `tests/game.test.js` |
| 3.75.2 | **State Machine** : Gestion des états UI/Jeu | `state.js`, `main.js` |
| 3.75.3 | **API Evolution** : `PlayerConfig` dans `CreateGameRequest` | `models.py` |
| 3.75.4 | **Accessibilité** : Mode Daltonien (Motifs) | `board.js` |

## Phase 3.8 : Persistence & UX 💾 - **TERMINÉ**

**Objectif** : Améliorer l'expérience utilisateur avec sauvegarde et refonte visuelle.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 3.8.1 | **Persistence** : Sauvegarde localStorage & Reprise | `game.js`, `main.js` |
| 3.8.2 | **UX** : Bouton Quitter & Gestion Fin de Partie | `index.html`, `style.css` |
| 3.8.3 | **Refonte Menu** : Layout Horizontal | `index.html`, `style.css` |

## Phase 4 : Environnement RL 🧠 - **TERMINÉ**

**Objectif** : Wrapper le jeu pour l'apprentissage par renforcement.

**Nouveau module** : `blokus-engine/src/blokus/rl/`

| Étape | Description | Fichier | Dépendances |
|-------|-------------|---------|-------------|
| 4.1 | Structure module `rl/` | `rl/__init__.py` | ✅ |
| 4.2 | Observations (47 canaux) | `rl/observations.py` | ✅ |
| 4.3 | Espace d'actions + masquage (~6000 actions) | `rl/actions.py` | ✅ |
| 4.4 | Reward shaping (potential-based) | `rl/rewards.py` | ✅ |
| 4.5 | Environnement Gym (`BlokusEnv`) | `rl/environment.py` | ✅ |
| 4.6 | Tests unitaires RL | `tests/rl/` | ✅ |
| 4.7 | Validation (100 random rollouts) | `scripts/validate_env.py` | ✅ |

**Détail tenseur d'observation (47 canaux)** :

- 0-3 : Occupation par joueur
- 4-7 : Coins valides par joueur
- 8-15 : Historique T-1, T-2
- 16 : Numéro de tour (normalisé)
- 17-37 : Pièces restantes (21 canaux)
- 38-46 : Métadonnées (autres joueurs, flags)

---

## Phase 5 : Entraînement 🏋️ - **EN COURS**

**Objectif** : Entraîner un agent via self-play.

| Étape | Description | Fichier | État |
|-------|-------------|---------|------|
| 5.1 | Infrastructure (Config, Checkpoints, Metrics, Tests) | `rl/training/` | ✅ |
| 5.2 | Dashboard de suivi (Streamlit) | `rl/visualization/dashboard.py` | ✅ |
| 5.3 | Architecture réseau CNN (PyTorch) | `rl/networks.py` | ✅ |
| 5.4 | Agent DQN + Dueling + PER | `rl/agents/dqn_agent.py` | ✅ |
| 5.5 | Script entraînement 2P self-play | `scripts/train.py` | 🚧 |
| 5.6 | Transfer learning → 4P | `scripts/train_4p.py` | 📅 |
| 5.7 | Registre modèles par profil | `blokus/rl/registry.py` | ✅ |

**Curriculum Learning** :

1. Phase 1 : 2P self-play (apprendre règles + patterns)
2. Phase 2 : 4P vs random (adaptation multi-joueurs)
3. Phase 3 : 4P self-play (stratégies compétitives)
4. Phase 4 : vs best checkpoints (polish)

---

## Phase 6 : Intégration IA 🤖

**Objectif** : Connecter les modèles entraînés à l'interface web.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 6.1 | Chargement modèle par persona | `api/ai_service.py` |
| 6.2 | Endpoint `/ai/move` | `main.py` |
| 6.3 | Client API IA côté JS | `js/ai.js` |
| 6.4 | Joueur IA automatique | `js/game.js` |
| 6.5 | Option "Suggestion" (highlight coup) | `js/board.js` |

**Profils IA prévus** (déjà en UI) :

- **Random** : Agent aléatoire (baseline)
- **Agressif** : Favorise contact + blocage adversaires
- **Défensif** : Consolidation territoire
- **Efficace** : Minimise pièces restantes

---

## Ordre d'Exécution

```text
Phase 1 ──┬──→ Phase 3.x ──→ Phase 4 ──→ Phase 5 ──→ Phase 6
Phase 2 ──┘
```

---

## Estimation

| Phase | Durée estimée | Status |
|-------|---------------|--------|
| Phase 1 | 2-3 jours | ✅ TERMINÉ |
| Phase 2 | 3-4 jours | ✅ TERMINÉ |
| Phase 3-3.8 | 3 jours | ✅ TERMINÉ |
| Phase 4 | 2 jours | ✅ TERMINÉ |
| Phase 5 | 5 jours (implémentation + tests) | ✅ TERMINÉ (Socle) |
| Phase 6 | 1 jour | 🚧 À faire |
