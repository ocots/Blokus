# Guide d'Apprentissage par Renforcement - Blokus

Ce guide explique comment utiliser l'infrastructure d'apprentissage par renforcement (RL) mise en place pour le projet Blokus.

---

## 1. Vue d'ensemble de l'Architecture

Le système d'apprentissage repose sur 3 composants principaux :

1. **Environnement (`blokus.rl.environment`)** : Simulation du jeu compatible Gym/Gymnasium.
2. **Infrastructure (`blokus.rl.training`)** : Gestion des sauvegardes, métriques et configuration.
3. **Agents (`blokus.rl.agents`)** : Implémentation des algorithmes (ex: DQN).

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

## 3. Lancer l'Entraînement (Local)

La commande pour lancer l'entraînement d'un agent DQN :

**Commande :**

```bash
python blokus-engine/scripts/train.py --new --name "mon_experience" --board-size 14
```

### Arguments Principaux

- `--new` : Créer une nouvelle expérience.
- `--resume [NAME]` : Reprendre une expérience existante.
- `--name` : Nom de l'expérience (obligatoire pour `--new`).
- `--board-size` : 14 (Duo) ou 20 (Standard).
- `--episodes` : Nombre total d'épisodes d'entraînement.
- `--eval-freq` : Fréquence des évaluations (ex: 1000).

---

## 4. Entraînement via GitHub Actions (Cloud)

Une plateforme d'entraînement automatisée est disponible dans GitHub Actions. Elle tente d'utiliser le runner **occidata** (avec GPU si possible) et se replie sur un runner GitHub standard si besoin.

### Méthode A : Lancement Manuel (Dispatch)

1. Allez sur GitHub → **Actions** → **RL Training**.
2. Cliquez sur **"Run workflow"**.
3. Remplissez le formulaire (Nom, Taille, Épisodes, etc.).
4. Cochez **"Resume"** si vous voulez continuer une session passée.

### Méthode B : Lancement par "Queue" (Push)

Vous pouvez déclencher un entraînement en modifiant le fichier `blokus-engine/training_queue.json` sur `main` :

```json
{
  "queue": [
    {
      "experiment_name": "duo_master_v1",
      "board_size": 14,
      "episodes": 100000,
      "resume": false
    }
  ]
}
```

Un simple `git push` de ce fichier lancera l'entraînement.

### Résultat : Une Pull Request Automatique

Une fois l'entraînement fini, le workflow :

1. Sauvegarde le modèle (`.pt`) et les métadonnées.
2. Enregistre automatiquement l'IA dans `blokus-engine/models/registry.json`.
3. **Crée une Pull Request** avec les résultats. Une fois fusionnée, l'IA devient disponible dans le jeu !

---

## 5. Reprise de l'Entraînement

Le système de checkpointing est conçu pour permettre l'arrêt et la reprise à tout moment.

**En Local :**

```bash
python blokus-engine/scripts/train.py --resume mon_experience
```

**Sur GitHub :**
Cochez la case **"Resume"** lors du lancement, ou mettez `"resume": true` dans le JSON. Le script récupérera `checkpoint_latest.pt` et continuera.

---

## 6. Suivi des Performances (Dashboard)

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
