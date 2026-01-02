---
description: Python testing workflow for Blokus project
---

# Python Testing Workflow

**Version**: 3.0  
**Last Updated**: 2026-01-02  
**Goal**: Run and maintain Python tests for Blokus project

## 📋 What This Workflow Does

- ✅ Run all Python tests
- ✅ Diagnose and fix test failures
- ✅ Ensure test quality and coverage
- ✅ Maintain SOLID compliance

## 📚 Required Reading

**Before using this workflow, read**: `@[.agent/workflows/testing-manual.md]`

This manual contains:
- Complete testing philosophy
- All test types with examples
- Quality standards
- Best practices
- Debugging techniques

## 🎯 Quick Start

```bash
# Run all tests
source .venv/bin/activate && python -m pytest tests/ -v --tb=short

# Check coverage
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
```

## 🔄 Workflow Steps

### 1) Run Tests

```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

### 2) Analyze Results

- ✅ **All pass**: Great! Continue development
- ❌ **Failures**: Diagnose and fix

### 3) Fix Issues

For each failing test:
1. Read the assertion error
2. Check the testing manual for patterns
3. Fix code or test
4. Re-run tests

### 4) Verify Coverage

```bash
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
```

**Required coverage**:
- Core modules: >95%
- Overall: >90%

## 📁 Test Organization

```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # E2E tests (optional)
└── fixtures/                # Test data
```

## 🎯 Test Types Required

1. **Unit Tests**: Test individual methods
2. **Logic Tests**: Test business logic
3. **Result Tests**: Test outputs
4. **Integration Tests**: Test module interactions

*See testing manual for examples and patterns*

## ⚡ Quality Standards

- **Coverage**: >90% overall
- **Speed**: Tests should be fast
- **Clarity**: Descriptive test names
- **Independence**: No test dependencies

## 🛑️ When to Stop

1. ✅ All tests pass
2. ✅ Coverage meets requirements
3. ✅ No critical failures
4. ✅ Code quality maintained

## 🔧 Optional Commands

```bash
# Type checking
source .venv/bin/activate && mypy src/

# Linting
source .venv/bin/activate && ruff check src/

# Run specific test
source .venv/bin/activate && python -m pytest tests/test_game_manager.py -v
```

## 📖 References

- **Testing Manual**: `@[.agent/workflows/testing-manual.md]`
- **Test Coverage Analysis**: `../docs/reports/test-types-analysis.md`
- **Test Implementation**: `../docs/reports/final-test-summary.md`

---

**Remember**: Tests are documentation. Keep them clean and meaningful.
