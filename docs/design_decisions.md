# Décisions de Conception - Blokus RL

Historique des choix techniques et leur justification.

---

## 2026-01-01 : Choix Fondamentaux

### Langage de Programmation

| Aspect | Choix | Alternatives considérées |
|--------|-------|--------------------------|
| **RL / Backend** | Python | Julia |
| **Interface** | HTML/CSS/JavaScript | Electron, PyQt |

**Justification** :

- Python : écosystème RL mature (PyTorch, Stable Baselines3)
- HTML/JS : portable, pas de dépendances, fonctionne en local

---

### Architecture RL

| Aspect | Choix | Justification |
|--------|-------|---------------|
| **Représentation état** | Multi-canal 47 channels | Complétude, style AlphaZero prouvé |
| **Espace d'actions** | Flat + Masquage (~6000) | Simplicité, efficacité |
| **Récompenses** | Potential-Based Shaping | Optimalité + convergence rapide |
| **Algorithme initial** | DQN + Dueling + PER | Validation rapide, baseline solide |

---

### Priorités

1. Mode **4 joueurs** (objectif final)
2. Via **2 joueurs** (transfer learning)
3. Usage **local** uniquement

---

## 2026-01-01 : Phase 3 et 3.5 (API & UI)

### Gestion de l'État (State Management)

| Décision | Description | Justification |
|----------|-------------|---------------|
| **API Stateless (Setup)** | Le backend ignore les noms/couleurs/personas. | Simplifie le modèle de données Python pour l'instant (focus sur RL). |
| **Sync Hybride** | Le frontend fusionne l'état Serveur (plateau, scores) avec l'état Local (noms, config). | Permet une UI riche sans alourdir le backend prématurément. |
| **SetupManager** | Classe dédiée pour le workflow d'initialisation. | Sépare clairement la configuration du cycle de vie du jeu (`Game`). |

---

## 2026-01-01 : Phase 3.75 - Refactoring

### Architecture Logicielle : Machines à États (FSM)

| Domaine | Utilité | Verdict | Justification |
|---------|---------|---------|---------------|
| **UI / Menus** | Haute | ✅ **OUI** | Gère proprement les transitions (`Intro` → `Setup` → `Jeu` → `Fin`) et évite les bugs d'états incohérents. Indispensable pour le flux "Rejouer". |
| **Logique Jeu** | Haute | ✅ **OUI** | Sécurise la boucle de jeu (`Attente Input` → `Validation` → `Sync API` → `Tour Suivant`). Clarifie le code async (IA/Réseau). |
| **Joueurs** | Faible | ❌ **NON** | Les joueurs sont des *Acteurs*. Le **Strategy Pattern** (Interface `makeMove`) est plus flexible qu'une FSM interne. |

---

## Décisions à Venir

- [ ] Taille exacte du réseau (64 vs 128 filtres)
- [ ] Durée d'entraînement Phase 1
- [ ] Métriques de validation
