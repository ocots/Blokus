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
| 3.75.5 | **3 Joueurs** : Logique de rotation Couleur Partagée | `game.js` |

## Phase 4 : Environnement RL 🧠

**Objectif** : Wrapper le jeu pour l'apprentissage par renforcement.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 4.1 | Environnement Gym-compatible | `environment.py` |
| 4.2 | Représentation d'état (47 canaux) | `environment.py` |
| 4.3 | Masquage d'actions invalides | `environment.py` |
| 4.4 | Fonction de récompense potential-based | `rewards.py` |

---

## Phase 5 : Entraînement 🏋️

**Objectif** : Entraîner un agent qui joue bien.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 5.1 | Architecture réseau CNN (PyTorch) | `networks.py` |
| 5.2 | Entraînement DQN 2 joueurs | `agents/dqn.py` |
| 5.3 | Transfer learning → 4 joueurs | `scripts/train.py` |
| 5.4 | Sauvegarde et évaluation des modèles | `models/` |

---

## Phase 6 : Intégration IA 🤖

**Objectif** : Utiliser l'IA entraînée pour aider les joueurs.

| Étape | Description | Fichier |
|-------|-------------|---------|
| 6.1 | Endpoint suggestion de coup | `main.py` |
| 6.2 | Toggle aide IA dans l'interface | `ai.js` |
| 6.3 | Affichage des suggestions sur le plateau | `board.js` |

---

## Ordre d'Exécution

```text
Phase 1 ──┬──→ Phase 3 ──→ Phase 4 ──→ Phase 5 ──→ Phase 6
Phase 2 ──┘
```

Les phases 1 et 2 peuvent être développées en parallèle.
La phase 3 les connecte, puis les phases 4-6 ajoutent l'IA.

---

## Estimation

| Phase | Durée estimée |
|-------|---------------|
| Phase 1 | 2-3 jours |
| Phase 2 | 3-4 jours |
| Phase 3 | 1 jour |
| Phase 4 | 2 jours |
| Phase 5 | Variable (entraînement) |
| Phase 6 | 1 jour |
