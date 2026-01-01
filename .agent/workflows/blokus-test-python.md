---
description: Interactive Python testing workflow with feedback loop
---

# Python Unit Test Workflow

**Goal**: Run tests, diagnose failures, fix issues in a feedback loop until all tests pass.

## Hard Rules

1. **Always run tests from the virtual environment**
   ```bash
   source .venv/bin/activate && python -m pytest tests/ -v
   ```

2. **One test file per module** (when it makes sense)
   - `src/blokus/pieces.py` → `tests/test_pieces.py`

3. **Clear test organization**
   - Use `class TestFeatureName:` to group related tests
   - Descriptive test names: `test_<what>_<condition>_<expected>`

## Workflow Steps

### 1) Run all tests

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

### 2) If tests fail, diagnose

For each failing test:
1. Read the assertion error
2. Read the relevant source code
3. Determine if it's a test bug or code bug

### 3) Fix the issue

- If **test bug**: Update the test expectation
- If **code bug**: Fix the source code

### 4) Re-run tests

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

### 5) Repeat until all pass

Continue the diagnose → fix → test loop until:
- ✅ All tests pass
- 📊 Coverage is acceptable (>80% recommended)

### 6) Optional: Check coverage

```bash
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
```

### 7) Optional: Type checking

```bash
source .venv/bin/activate && mypy src/
```

### 8) Optional: Linting

```bash
source .venv/bin/activate && ruff check src/
```

## Stop Points

1. After initial test run (report status)
2. If >5 tests fail (ask for guidance)
3. Before making major code changes
4. When all tests pass (report success)

## Philosophy

Test first • Clear assertions • Minimal fixtures • Fast feedback
