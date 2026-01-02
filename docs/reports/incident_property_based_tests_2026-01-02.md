# Test Incident Report - Property-Based Tests

**Date**: 2026-01-02 14:08  
**Severity**: 🔴 High (All property-based tests failing)  
**Reported by**: Test Architect (Personne A)  
**Assigned to**: Test Developer (Personne B)

---

## 🐛 Issue Summary

**All property-based tests in `test_property_based.py` are failing** due to a KeyError.

---

## 🔍 Root Cause Analysis

### Error Details

```
KeyError: 'starting_player'
File: tests/test_property_based.py
Line: 39
```

### The Problem

The `valid_game_config()` strategy generates:
```python
{'num_players': 2, 'starting_player_idx': 0}
```

But the test code tries to access:
```python
starting_player_idx=config["starting_player"]  # ❌ Wrong key!
```

Should be:
```python
starting_player_idx=config["starting_player_idx"]  # ✅ Correct
```

---

## 📝 Affected Tests

All tests in `TestGameInvariants` class:
1. ❌ `test_game_initialization_never_crashes`
2. ❌ `test_random_valid_moves_never_crash`
3. ❌ `test_force_pass_maintains_invariants`
4. ❌ `test_score_calculation_never_negative_beyond_limit`
5. ❌ `test_game_copy_is_independent`

And likely others in the file.

---

## 🔧 Fix Required (for Personne B)

### File: `tests/test_property_based.py`

**Search and replace**:
- Find: `config["starting_player"]`
- Replace: `config["starting_player_idx"]`

### Specific Lines to Fix

Line 39:
```python
# Before
starting_player_idx=config["starting_player"]

# After
starting_player_idx=config["starting_player_idx"]
```

**Estimated occurrences**: 5-10 (check all uses of `config` dict)

---

## ✅ Verification Steps

After fix, run:

```bash
# Test one specific test
pytest tests/test_property_based.py::TestGameInvariants::test_game_initialization_never_crashes -v

# Test all property-based tests
pytest tests/test_property_based.py -v

# Full test suite
pytest tests/ -v
```

Expected result: All property-based tests should PASS.

---

## 📊 Impact Assessment

**Current state**:
- ~15 tests failing (all property-based)
- Test suite completion rate: ~95% → ~100% after fix

**Priority**: 🔴 High  
**Effort**: 🟢 Low (5-10 minutes)  
**Risk**: 🟢 Low (simple find/replace)

---

## 🎓 Lessons Learned

1. **Always run new tests immediately after creation** to catch simple errors
2. **Hypothesis provides excellent error messages** ("Falsifying example")
3. **Property-based tests are sensitive to strategy/test mismatches**

---

## 👥 Action Items

**For Personne B (Test Developer)**:
- [ ] Fix the KeyError in `test_property_based.py`
- [ ] Run all property-based tests to verify
- [ ] Create PR with fix
- [ ] Add this to regression tests checklist

**For Personne A (Test Architect)**:
- [x] Identify root cause
- [x] Document incident
- [ ] Review PR from Personne B
- [ ] Update test creation guidelines

---

## 🕐 Timeline

- **14:00** - Tests launched, failures detected
- **14:08** - Root cause identified by Personne A
- **14:10** - Incident report created
- **14:15** - ETA for fix by Personne B
- **14:20** - ETA for verification

---

**Status**: 🟡 Waiting for fix from Personne B  
**Next sync**: 14:30 (Daily standup)
