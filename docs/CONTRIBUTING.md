# Contributing to HVAC Simulation

**Status:** LOCKED — read [KIMI_ONBOARDING.md](KIMI_ONBOARDING.md) before any mutation.

---

## How to Add a Requirement

1. **Draft in SRS:** Add to `docs/HVAC_SRS.md` Section 2 with ID, description, tests, verification
2. **Write tests:** `test_<feature>.py` in repo root or `tests/<suite>/`
3. **Implement:** Source file in repo root
4. **Cite formulas:** Add to `docs/FORMULA_CITATIONS.md` with primary source
5. **Verify:** Run full suite — 188/188 must PASS
6. **Update INDEX:** Bump commit hash in `docs/INDEX.md`
7. **Commit:** Message must include requirement ID and test count

---

## How to Add a Formula Citation

| Field | Required |
|-------|----------|
| Formula | Exact equation |
| Source | Primary source (not secondary) |
| Citation | Full bibliographic entry |
| Implementation | Code location (file:line) |
| Verification | Test file that validates it |

See [FORMULA_CITATIONS.md](FORMULA_CITATIONS.md) for examples.

---

## How to Update AI Onboarding

1. Edit `docs/KIMI_ONBOARDING.md`
2. Bump **Last Updated** date
3. Update **Current Commit** hash
4. Update **Test Count**
5. Add new invariants to Environment table
6. Commit with `docs:` prefix

---

## Shell Escaping Rule (MANDATORY)

- **NEVER** use heredoc (`<< EOF`) for GDScript or any file with `$`, `\n`, `#`
- **ALWAYS** use `echo <base64> | base64 -d > file` or Python intermediate file
- **Rationale:** 7 consecutive failures in Campaign 5a (Heredoc War)

---

## Commit Message Format

```
<type>(<scope>): <requirement-id> <description>

- <detail 1>
- <detail 2>

Ground truth: <commit-hash>
```

| Type | Use For |
|------|---------|
| `feat` | New requirement implementation |
| `test` | New or updated tests |
| `docs` | Documentation updates |
| `fix` | Bug fixes |
| `chore` | Maintenance, cleanup |

---

*Glass box enforced. Every mutation is traceable.*
