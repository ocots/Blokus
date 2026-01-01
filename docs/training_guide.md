# Guide d'Apprentissage par Renforcement - Blokus

Ce guide explique comment utiliser l'infrastructure d'apprentissage par renforcement (RL) mise en place pour le projet Blokus.

---

## 1. Vue d'ensemble de l'Architecture

Le système d'apprentissage repose sur 3 composants principaux :

1.  **Environnement (`blokus.rl.environment`)** : Simulation du jeu compatible Gym/Gymnasium.
2.  **Infrastructure (`blokus.rl.training`)** : Gestion des sauvegardes, métriques et configuration.
3.  **Agents (`blokus.rl.agents`)** : Implémentation des algorithmes (ex: DQN).

L'entraînement se fait "Offline" par rapport à l'interface web. Les modèles sont sauvegardés sur le disque et peuvent être chargés ultérieurement par l'API pour jouer contre des humains.

---

## 2. Validation de l'Environnement

Avant de lancer un entraînement long, il est recommandé de valider que l'environnement fonctionne correctement (règles, observations, récompenses).

**Commande :**
```bash
python blokus-engine/scripts/validate_env.py
```

Cela va :
- Lancer 100 épisodes "random vs random".
- Vérifier qu'il n'y a pas de crashs.
- Afficher les statistiques de base (durée des parties, scores).

---

## 3. Lancer l'Entraînement (Phase 5)

> **Note :** Le script d'entraînement est en cours de développement (Phase 5).

La commande standard pour lancer l'entraînement d'un agent DQN en self-play sera :

**Commande prévue :**
```bash
python blokus-engine/scripts/train_2p.py --experiment "mon_experience_dqn" --device "mps"
```

### Arguments Principaux (Prévus) :
- `--experiment` : Nom de l'expérience (créera un dossier dans `models/experiments/`).
- `--board_size` : 14 (Duo) ou 20 (Standard). Défaut : 14.
- `--total_timesteps` : Nombre de pas de temps total (ex: 1000000).
- `--device` : `cpu`, `cuda`, ou `mps` (Mac).

---

## 4. Reprise de l'Entraînement

Le système de checkointing est conçu pour permettre l'arrêt et la reprise à tout moment.

Pour reprendre un entraînement interrompu :
1. Relancez simplement la **même commande** avec le **même nom d'expérience**.
2. Le script détectera le dossier existant (`models/experiments/mon_experience_dqn`).
3. Il chargera le dernier checkpoint (`checkpoint_latest.pt`) et le fichier de métadonnées.
4. L'entraînement reprendra exactement là où il s'était arrêté (numéro d'épisode, buffer de replay, état de l'optimiseur).

---

## 5. Suivi des Performances (Dashboard)

Un dashboard interactif basé sur Streamlit permet de suivre l'évolution de l'apprentissage en temps réel.

**Lancer le dashboard :**
```bash
streamlit run blokus-engine/src/blokus/rl/visualization/dashboard.py
```

Une fois lancé (port 8501 par défaut) :
1. Sélectionnez votre expérience dans la barre latérale.
2. Activez "Auto-refresh" pour voir les courbes se mettre à jour.
3. Observez :
    - **Win Rate** : Taux de victoire contre l'agent aléatoire (doit augmenter).
    - **Loss** : Convergence du réseau de neurones.
    - **Episode Length** : Durée des parties.

---

## 6. Structure des Dossiers

Les résultats de l'entraînement sont stockés dans `models/experiments/` :

```text
models/experiments/mon_experience/
├── checkpoints/
│   ├── checkpoint_latest.pt   # Dernier état complet
│   ├── checkpoint_best.pt     # Meilleur modèle (win rate)
│   └── checkpoint_1000.pt     # Sauvegarde périodique
├── metrics.csv                # Historique complet (pour Dashboard)
├── metadata.json              # État global (steps, episodes)
└── config.json                # Hyperparamètres utilisés
```
