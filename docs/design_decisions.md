# Décisions de Conception - Blokus RL

Historique des choix techniques et leur justification.

---

## 2026-01-01 : Choix Fondamentaux

### Langage de Programmation

| Aspect          | Choix               | Alternatives considérées |
|-----------------|---------------------|--------------------------|
| **RL / Backend**| Python              | Julia                    |
| **Interface**   | HTML/CSS/JavaScript | Electron, PyQt           |


**Justification** :

- Python : écosystème RL mature (PyTorch, Stable Baselines3)
- HTML/JS : portable, pas de dépendances, fonctionne en local

---

### Architecture RL

| Aspect                | Choix                    | Justification                     |
|-----------------------|--------------------------|-----------------------------------|
| **Représentation état** | Multi-canal 47 channels  | Complétude, style AlphaZero prouvé|
| **Espace d'actions**  | Flat + Masquage (~6000)  | Simplicité, efficacité            |
| **Récompenses**       | Potential-Based Shaping  | Optimalité + convergence rapide   |
| **Algorithme initial**| DQN + Dueling + PER      | Validation rapide, baseline solide|


---

### Priorités

1. Mode **4 joueurs** (objectif final)
2. Via **2 joueurs** (transfer learning)
3. Usage **local** uniquement

---

## 2026-01-01 : Phase 3 et 3.5 (API & UI)

### Gestion de l'État (State Management)

| Décision                  | Description                                                                              | Justification                                                 |
|---------------------------|------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| **API Stateless (Setup)** | Le backend ignore les noms/couleurs/personas.                                            | Simplifie le modèle de données Python pour l'instant (focus sur RL). |
| **Sync Hybride**          | Le frontend fusionne l'état Serveur (plateau, scores) avec l'état Local (noms, config).  | Permet une UI riche sans alourdir le backend prématurément.   |
| **SetupManager**          | Classe dédiée pour le workflow d'initialisation.                                         | Sépare clairement la configuration du cycle de vie du jeu (`Game`). |


---

## 2026-01-01 : Phase 3.75 - Refactoring

### Architecture Logicielle : Machines à États (FSM)

| Domaine         | Utilité | Verdict | Justification                                                                                             |
|-----------------|---------|---------|-----------------------------------------------------------------------------------------------------------|
| **UI / Menus**  | Haute   | ✅ **OUI** | Gère proprement les transitions (`Intro` → `Setup` → `Jeu` → `Fin`) et évite les bugs d'états incohérents. |
| **Logique Jeu** | Haute   | ✅ **OUI** | Sécurise la boucle de jeu (`Attente Input` → `Validation` → `Sync API` → `Tour Suivant`).                 |
| **Joueurs**     | Faible  | ❌ **NON** | Les joueurs sont des *Acteurs*. Le **Strategy Pattern** (Interface `makeMove`) est plus flexible.         |


---

| **Streamlit** | Dashboard interactif (`dashboard.py`). | UX supérieure à TB pour trier/comparer les expériences (custom KPIs). |

---

## 2026-01-01 : Stratégie de Test & Qualité

| Décision | Description | Justification |
|----------|-------------|---------------|
| **Tests en 3 Phases** | Phase 1 (Core RL), Phase 2 (Infrastructure), Phase 3 (Intégration). | Approche progressive pour isoler les bugs (du bas vers le haut). |
| **Objectif > 85%** | Couverture stricte sur les modules de décision (Agent, Réseaux, Jeu). | Sécurise les futurs refactorings et les entraînements longs. |
| **Mocking local** | Utilisation de fichiers temporaires et de mocks pour les dépendances externes (FS, API). | Tests reproductibles et rapides sans effets de bord. |


---

## Décisions à Venir

- [ ] Taille exacte du réseau (64 vs 128 filtres)
- [ ] Durée d'entraînement Phase 1
- [ ] Métriques de validation

---

## 2026-01-03 : Modes de Jeu & Affinement

### Modes 2 Joueurs Distincts

| Mode | Configuration | Justification |
|------|---------------|---------------|
| **Blokus Duo** | 14x14, 1 couleur/joueur, départ centre | Règles officielles Duo, parties plus rapides/tendues. |
| **Blokus Standard (2P)** | 20x20, 2 couleurs/joueur, départ coins | Respect des règles officielles classiques 2P. Plus stratégique. |

### Suppression du Mode 3 Joueurs

| Décision | Justification |
|----------|---------------|
| **Suppression Complète** | Le mode 3 joueurs nécessite des règles ad-hoc (couleur neutre ou asymétrie) qui complexifient l'implémentation et l'apprentissage RL sans apporter de valeur significative par rapport aux modes 2 et 4 joueurs. |

### Persistence & Replay

- **Persistence** : Utilisation du `LocalStorage` avec Observer Pattern pour sauvegarder les préférences utilisateur (noms, couleurs, mode rapide) sans couplage fort.
- **Replay** : Système de replay deterministic basé sur l'historique des coups, permettant de rejouer des parties complètes (utile pour débug et analyse).
