# Guide d'Installation des Alias Blokus

## 🎯 Objectif

Ce guide vous aide à installer des alias shell pour simplifier vos commandes de test Blokus fréquentes.

## ⚡ Installation Rapide

### Option 1 : Installation Automatique (Recommandé)

Copiez-collez cette commande dans votre terminal :

```bash
cat >> ~/.zshrc << 'EOF'

# ========================================
# Blokus Testing Aliases (added 2026-01-02)
# ========================================

# Navigation
alias blokus-cd='cd /Users/ocots/Documents/Jeux/Blokus'
alias blokus-engine-cd='cd /Users/ocots/Documents/Jeux/Blokus/blokus-engine'

# Virtual Environment
alias blokus-venv='source .venv/bin/activate'

# Tests généraux
alias blokus-test='source .venv/bin/activate && python -m pytest tests/ -v --tb=short'
alias blokus-test-tail='source .venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -50'
alias blokus-test-cov='source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing'

# Type checking
alias blokus-mypy='source .venv/bin/activate && mypy src/blokus --strict'

# Tests spécifiques
alias blokus-engine-test='cd /Users/ocots/Documents/Jeux/Blokus && source venv/bin/activate && python -m pytest blokus-engine/tests/ -v'
alias blokus-test-copy='cd /Users/ocots/Documents/Jeux/Blokus && source venv/bin/activate && python -m pytest blokus-engine/tests/test_ai_system.py::TestGameCopy::test_game_copy_independent_pieces -v'

EOF
```

Puis rechargez votre configuration :

```bash
source ~/.zshrc
```

### Option 2 : Installation Manuelle

1. Ouvrez votre fichier `~/.zshrc` :
   ```bash
   nano ~/.zshrc
   ```

2. Ajoutez les alias à la fin du fichier (voir le contenu ci-dessus)

3. Sauvegardez et rechargez :
   ```bash
   source ~/.zshrc
   ```

## 📖 Utilisation des Alias

### Avant (commandes longues)

```bash
# Test spécifique
cd /Users/ocots/Documents/Jeux/Blokus && source venv/bin/activate && python -m pytest blokus-engine/tests/test_ai_system.py::TestGameCopy::test_game_copy_independent_pieces -v

# Tous les tests avec tail
source .venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -50
```

### Après (avec alias)

```bash
# Test spécifique
blokus-test-copy

# Tous les tests avec tail
blokus-test-tail

# Couverture de code
blokus-test-cov

# Type checking
blokus-mypy
```

## 🚀 Workflow Antigravity

Le workflow `/blokus-test-python` a été amélioré avec :

1. **Auto-exécution activée** : L'annotation `// turbo-all` permet à toutes les commandes du workflow de s'exécuter automatiquement sans demander d'approbation

2. **Alias intégrés** : Documentation complète des alias disponibles

3. **Commandes fréquentes** : Vos commandes les plus utilisées sont maintenant des alias courts

## ✅ Vérification

Pour vérifier que les alias sont installés :

```bash
# Lister tous les alias Blokus
alias | grep blokus
```

Vous devriez voir tous les alias listés.

## 🔧 Personnalisation

Vous pouvez ajouter vos propres alias en suivant le même pattern :

```bash
alias blokus-mon-test='cd /Users/ocots/Documents/Jeux/Blokus && source venv/bin/activate && python -m pytest tests/mon_test.py -v'
```

## 📚 Ressources

- Workflow complet : `.agent/workflows/blokus-test-python.md`
- Manuel de tests : `.agent/workflows/testing-manual.md`
- Méthodologie TDD : `.agent/workflows/testing-methodology.md`

---

**Note** : Ces alias sont spécifiques à votre machine. Si vous travaillez sur plusieurs machines, vous devrez adapter les chemins.
