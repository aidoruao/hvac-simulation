# Contributing to HVAC Simulation

**Status:** LOCKED — read [KIMI_ONBOARDING.md](KIMI_ONBOARDING.md) before any mutation.

---

## How to Add a Requirement

1. **Draft in SRS:** Add to `docs/HVAC_SRS.md` Section 2 with ID, description, tests, verification
2. **Write tests:** `test_<feature>.py` in repo root or `tests/<suite>/`
3. **Implement:** Source file in repo root
4. **Cite formulas:** Add to `docs/FORMULA_CITATIONS.md` with primary source
5. **Verify:** Run full suite — 207/207 must PASS
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

## AI Agent Workflow

This project is co-developed with AI agents. Agent capabilities and rules vary:

### CLI Agents (Direct Filesystem Access)

**Kimi CLI** and **Codewhale** run inside WSL2 with direct filesystem access. Use them for:
- File writes, edits, and refactors
- Test runs and debugging
- Git operations
- Full development workflow

### Web Agents (No Filesystem Access)

**Kimi Web**, **DeepSeek Web**, and other browser-based agents have no direct access to the WSL2 filesystem. Use them for:
- Architecture review and design discussion
- Code review and refactoring suggestions
- Orchestration and workflow planning
- Generating code blocks for manual paste

### Base64 Encoding Rule (Web Agents)

When a web agent must transmit a multi-line file, encode to Base64:
```bash
echo '<base64>' | base64 -d > target_file
```

### Heredoc Ban

`<< EOF` is banned for multi-line scripts. Bash interpolates `$`, `\n`, and `#` before file write, and long heredoc blocks corrupt mid-sentence. See [KIMI_ONBOARDING.md](KIMI_ONBOARDING.md) for the full war history (7 consecutive failures in Campaign 5a).

### Hardware-Accelerated Headless Rendering

For Godot visual regression on RTX 4050:
```bash
--rendering-driver d3d12
```

### Path Mapping

When the Windows Godot executable accesses WSL2 files:
```bash
wslpath -w /home/idor/hvac-simulation
```

---

## Running Tests

```bash
# Activate virtual environment
source ~/hvac-simulation/venv/bin/activate

# Python tests (195 tests, 0 xfailed expected)
cd ~/hvac-simulation && PYTHONPATH=. ./venv/bin/pytest -v

# Godot regression (12 tests)
cd ~/hvac-simulation && python3 test_godot_regression.py
```

**Gate:** All 207 tests must pass before push.

---

## Commit Discipline

| Rule | Detail |
|------|--------|
| **Commit locally** | After each working chunk — provides rollback safety and traceability |
| **Push gate** | Only after SRS update + full test pass (207/207) + docs updated |
| **Conventional commits** | `feat()`, `fix()`, `docs()`, `test()`, `chore()` |
| **Requirement IDs** | Reference SRS requirement IDs in commit messages (e.g., `FR-MA-001`) |

### Example commit messages

```
feat(math_model): FR-MA-001 derived thermodynamic properties and Jacobian stability
fix(math_model): Aly-Lee 1999 ideal-gas c_v^0 for R410A, removes 9 xfails
docs: SRS v1.6, CHANGELOG, FORMULA_CITATIONS for FR-MA-001
```

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

---

## AI Patch Rejection Protocol (FR-SV-005)

At any integration boundary (SIT/POST), AI agents face a structural choice:
**repair the data contract** or **patch the consumer**. This protocol enforces
the correct choice.

| Rule | Action |
|:---|:---|
| **Rule 1** | If AI proposes changing a consumer (UI/parser) to accept broken data, **reject immediately**. |
| **Rule 2** | If AI proposes changing the data generator to output correct data, **verify and approve**. |
| **Rule 3** | If AI claims both options are equivalent, **reject** — they are never equivalent. |
| **Rule 4** | The human operator has **veto power** over all AI patch proposals at SIT/POST. |

**Rationale:** The data contract is load-bearing. The UI is cosmetic.
Repairs must target load-bearing elements. See `docs/AI_BEHAVIORAL_ARCHETYPES.md`
for documented instances of this pattern.
