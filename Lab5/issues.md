# Lab 5 – Issues Found (scholarship_disbursement.py)

Line numbers refer to the **original** file. Ordered by severity (security and bugs first).
Baseline: Pylint **5.00/10**, Bandit **1 Medium + 3 Low**, Flake8 **6 messages**.
Final: Pylint **10.00/10**, Bandit **0 issues**, Flake8 **0 messages**.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SQL injection via string formatting (Bandit B608, Pylint C0209) | Security (Medium) | 10 | `grant()` builds the INSERT with `%` formatting, so student/scheme text is pasted straight into the SQL. A name like `O'Brien` crashes it with a syntax error, and a crafted name can inject SQL. | Used a parameterised query (`VALUES (?, ?, ?, 0)` with a tuple), the same way `disburse()` and `by_scheme_count()` already do. |
| Mutable default argument (Pylint W0102) | Bug | 9 | `audit=[]` is created once and shared by every call, so audit entries leak between unrelated calls (second call returned `['Ishaan','Divya',...]`). | Default changed to `None`; a new list is created inside the function when `audit is None`. |
| Inconsistent return / missing-award path (Pylint R1710) | Bug | 15-21 | `disburse()` returns an amount when the award exists but falls off the end (implicit `None`) when it does not. Easy to miss, as `disburse(9)` printed `None`. | Inverted into a guard clause: `if row is None: return None`, with the behaviour documented in the docstring. |
| `os.system` starts a shell (Bandit B605, B607) | Security (Low) | 26 | Shell process started with a partial path (`echo`). Safe today as the string is constant, but it is a command-injection risk if it ever takes input, and it is needless for printing a message. | Removed the shell call and print the message directly. (A real archiver should use `subprocess.run([...], shell=False)` with an absolute path.) |
| Silent broad exception (Bandit B110, Pylint W0718) | Quality / Security (Low) | 27-28 | `except Exception: pass` swallows every error, so failures in `archive()` would vanish unnoticed. | Removed the try/except; nothing in the body needs it and errors now surface instead of being hidden. |
| `global` mutable state (Pylint W0603, C0103) | Design | 6, 16 | `disbursed_total` is a module-level variable edited through `global`, so it can drift out of sync with the database, and its name breaks the constant naming style. | Removed the global. Added `get_disbursed_total()` which computes `SUM(amount)` of disbursed awards from the database, a single source of truth. |
| Comparison to None with `==` (Pylint C0121, Flake8 E711) | Style | 32 | `scheme == None` should use identity. | Changed to `scheme is None`. One fix clears both tools' messages. |
| Function name not snake_case (Pylint C0103) | Style | 31 | `bySchemeCount` is camelCase. | Renamed to `by_scheme_count` and updated the call in `main()`. |
| Missing docstrings (Pylint C0114, C0116) | Documentation | 1, 9, 15, 24, 31, 37 | The module and all 5 functions had no docstrings. | Added a module docstring and a short docstring on every function. |
| Lines too long (Pylint C0301 >100, Flake8 E501 >79) | Style | 5, 10, 17, 19, 34 | Five lines exceed 79 characters (two also exceed Pylint's 100). | Wrapped long strings and calls across lines (commit 2 handled the >100 ones, commit 3 the rest). |
| Demo runs on import (not flagged by any tool) | Design | 45 | `main()` is called at module level, so merely importing the file runs the demo. | Wrapped in `if __name__ == "__main__":`. Found by reading, not by the tools. |

## Commits
1. `Fix Bandit findings` – B608, B605, B607, B110
2. `Fix Pylint findings` – docstrings, mutable default, global, return, naming, `is None` (5.00 → 10.00)
3. `Fix Flake8 findings` – remaining E501 line wrapping (E711 was already fixed with Pylint's C0121)

Reports are in `reports/before/` and `reports/after/`.
