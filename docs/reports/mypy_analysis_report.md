# Rapport MyPy - Analyse Statique des Types

**Date :** 2026-01-02  
**Commande :** `mypy src/blokus --strict`  
**Résultat :** 73 erreurs détectées dans 17 fichiers (sur 29 analysés)

## Résumé Exécutif

L'analyse statique révèle des problèmes de typage qui peuvent causer des bugs runtime :
- **Priorité Critique** : Arguments `Optional` non déclarés (risque de `None` inattendu)
- **Priorité Haute** : Fonctions sans annotations de retour (impossible de vérifier les appels)
- **Priorité Moyenne** : Types génériques incomplets (`dict`, `list` sans paramètres)

## Erreurs par Catégorie

### 1. Arguments Optional Implicites (Critique)

**Problème :** PEP 484 interdit les `Optional` implicites. Un argument avec `default=None` doit être typé `str | None`.

**Fichiers affectés :**
- `player_factory.py` (lignes 35, 58, 89) : Argument `color: str = None`
- `game_manager.py` (ligne 33) : Argument `players: list[Player] = None`
- `game_manager_factory.py` (ligne 117) : Argument `ai_personas: list[str] = None`

**Exemple d'erreur :**
```python
# ❌ AVANT (Erreur MyPy)
def create_human_player(id: int, name: str, color: str = None) -> Player:
    ...

# ✅ APRÈS (Correct)
def create_human_player(id: int, name: str, color: str | None = None) -> Player:
    ...
```

**Impact :** Si un appelant passe `None` sans vérification, crash runtime garanti.

---

### 2. Fonctions Sans Annotations de Retour (Haute)

**Problème :** MyPy ne peut pas vérifier que les appelants gèrent correctement les valeurs de retour.

**Fichiers affectés :**
- `game_manager.py` (lignes 160, 185, 205, 247, 349)
- `rl/visualization/dashboard.py` (ligne 144)
- `rl/training/evaluator.py` (ligne 52)
- `rl/observations.py` (ligne 143)
- `rl/environment.py` (ligne 312)

**Exemple :**
```python
# ❌ AVANT
def reset_game(self):
    self.game = Game(...)

# ✅ APRÈS
def reset_game(self) -> None:
    self.game = Game(...)
```

---

### 3. Types Génériques Incomplets (Moyenne)

**Problème :** `dict` et `list` sans paramètres de type sont ambigus.

**Fichiers affectés :**
- `rl/training/checkpoint.py` (lignes 142, 143, 185, 211)
- `rl/registry.py` (lignes 36, 120)
- `rl/agents/dqn_agent.py` (lignes 192, 286, 297)
- `player_factory.py` (ligne 125)

**Exemple :**
```python
# ❌ AVANT
def to_dict(self) -> dict:
    return {"key": "value"}

# ✅ APRÈS
def to_dict(self) -> dict[str, Any]:
    return {"key": "value"}
```

---

### 4. Erreurs Spécifiques RL/Gymnasium (Moyenne)

**Problème :** Incompatibilités avec les types Gymnasium et dépendances manquantes.

**Fichiers affectés :**
- `rl/environment.py` : 
  - Ligne 221 : `Move | None` passé à une fonction attendant `Move`
  - Ligne 285 : Type de retour `render()` incompatible avec Gymnasium
- `rl/visualization/dashboard.py` : Stubs manquants pour `streamlit`, `plotly`, `pandas`

**Action recommandée :** Installer les stubs de types :
```bash
pip install pandas-stubs types-plotly
```

---

## Plan d'Action Prioritaire

| Priorité | Action | Fichiers | Effort |
|----------|--------|----------|--------|
| 🔴 **P0** | Corriger les `Optional` implicites | `player_factory.py`, `game_manager.py`, `game_manager_factory.py` | 15 min |
| 🟠 **P1** | Ajouter annotations de retour manquantes | `game_manager.py`, `rl/training/evaluator.py` | 30 min |
| 🟡 **P2** | Typer les `dict` et `list` génériques | `rl/training/checkpoint.py`, `rl/registry.py` | 20 min |
| 🟢 **P3** | Installer stubs de types pour dépendances | `requirements.txt` | 5 min |
| 🔵 **P4** | Corriger incompatibilités Gymnasium | `rl/environment.py` | 45 min |

**Temps total estimé :** ~2 heures

---

## Commandes de Vérification

### Vérification complète (strict)
```bash
source .venv/bin/activate && mypy src/blokus --strict
```

### Vérification rapide (sans strict)
```bash
source .venv/bin/activate && mypy src/blokus
```

### Installation des stubs manquants
```bash
source .venv/bin/activate && pip install pandas-stubs types-plotly
```

---

## Bénéfices Attendus

Une fois ces erreurs corrigées :
1. ✅ **Zéro crash** dû à des appels de fonctions inexistantes
2. ✅ **Détection précoce** des erreurs de types avant l'exécution
3. ✅ **Meilleure documentation** (les types servent de documentation)
4. ✅ **Refactoring sûr** (MyPy détecte les impacts des changements)

---

## Recommandation Finale

**Ajouter MyPy au CI/CD** pour bloquer les PRs avec des erreurs de types :

```yaml
# .github/workflows/ci.yml
- name: Type Check
  run: |
    source .venv/bin/activate
    mypy src/blokus --strict
```

Cela garantira que le code reste typé correctement au fil du temps.
