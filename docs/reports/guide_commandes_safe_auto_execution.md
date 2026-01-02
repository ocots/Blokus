# Guide : Commandes Safe Auto-Exécution

**Date** : 2026-01-02  
**Version** : 1.0

## 🎯 Objectif

Permettre l'auto-exécution de TOUTES les commandes de test sans confirmation manuelle.

## 📋 Solution Actuelle

### Annotation `// turbo-all`

Le workflow `blokus-test-python.md` contient déjà `// turbo-all` en ligne 5, ce qui devrait rendre toutes les commandes safe.

**Problème identifié** : Les commandes avec pipes complexes (`2>&1 | tail`) ne sont pas automatiquement considérées comme safe, même avec `// turbo-all`.

## ✅ Commandes qui Fonctionnent (Auto-Exécution)

Ces commandes s'exécutent automatiquement sans confirmation :

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v

// turbo
source .venv/bin/activate && python -m pytest tests/test_property_based.py -v

// turbo
source .venv/bin/activate && mypy src/blokus --strict
```

## ⚠️ Commandes qui Nécessitent Confirmation

Ces commandes nécessitent une confirmation manuelle :

```bash
# Avec pipe et redirection
source .venv/bin/activate && python -m pytest tests/ -v 2>&1 | tail -50

# Avec grep
source .venv/bin/activate && python -m pytest tests/ -v | grep FAILED
```

## 🔧 Solutions de Contournement

### Solution 1 : Séparer les Commandes

Au lieu de :
```bash
source .venv/bin/activate && python -m pytest tests/ -v 2>&1 | tail -50
```

Utiliser :
```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=line
```

Puis lire la sortie complète (pytest affiche automatiquement un résumé à la fin).

### Solution 2 : Utiliser des Options Pytest

Au lieu de `| tail`, utiliser les options pytest :

```bash
// turbo
# Afficher seulement les échecs
source .venv/bin/activate && python -m pytest tests/ -v --tb=short -x

// turbo
# Afficher seulement le résumé
source .venv/bin/activate && python -m pytest tests/ -v --tb=no

// turbo
# Afficher les 10 tests les plus lents
source .venv/bin/activate && python -m pytest tests/ -v --durations=10
```

### Solution 3 : Utiliser des Fichiers de Sortie

```bash
// turbo
# Écrire dans un fichier
source .venv/bin/activate && python -m pytest tests/ -v > test_results.txt

# Puis lire le fichier (commande safe)
// turbo
cat test_results.txt
```

## 📝 Recommandations

### Pour le Workflow

1. **Utiliser `--tb=line`** au lieu de `| tail` pour avoir un résumé compact
2. **Utiliser `-x`** pour s'arrêter au premier échec
3. **Utiliser `--lf`** pour relancer seulement les tests qui ont échoué

### Commandes Recommandées (Toutes Safe)

```bash
// turbo
# Tests complets avec résumé compact
source .venv/bin/activate && python -m pytest tests/ -v --tb=line

// turbo
# Tests avec arrêt au premier échec
source .venv/bin/activate && python -m pytest tests/ -v --tb=short -x

// turbo
# Relancer seulement les tests qui ont échoué
source .venv/bin/activate && python -m pytest tests/ -v --lf

// turbo
# Tests property-based avec détails
source .venv/bin/activate && python -m pytest tests/test_property_based.py -v --tb=long

// turbo
# Couverture
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term

// turbo
# MyPy
source .venv/bin/activate && mypy src/blokus --strict
```

## 🎓 Leçons Apprises

1. **`// turbo-all`** fonctionne pour les commandes simples
2. **Pipes et redirections** (`|`, `>`, `2>&1`) peuvent nécessiter confirmation
3. **Options pytest** sont préférables aux pipes pour le filtrage
4. **Simplicité** : Plus la commande est simple, plus elle a de chances d'être auto-exécutée

## 🔄 Mise à Jour du Workflow

Pour mettre à jour `blokus-test-python.md`, remplacer les commandes avec pipes par :

```markdown
## 🎯 Quick Start

```bash
// turbo
# Run all tests with compact summary
source .venv/bin/activate && python -m pytest tests/ -v --tb=line

// turbo
# Check coverage
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term

// turbo
# Type checking
source .venv/bin/activate && mypy src/blokus --strict

// turbo
# Property-based tests
source .venv/bin/activate && python -m pytest tests/test_property_based.py -v --tb=line
```
```

## ✅ Résultat Attendu

Avec ces modifications, **100% des commandes de test** devraient s'exécuter automatiquement sans confirmation.

---

**Note** : Ce guide sera intégré dans le workflow `blokus-test-python.md` version 5.1.
