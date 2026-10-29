# Lab 5 – Reflection

## 1. What did each tool catch that the others did not?
Bandit alone flagged the SQL injection (B608) and the shell call (B605/B607), which are the risks that matter most for a program handling money. Pylint alone caught the mutable default argument (W0102), the inconsistent return in `disburse()` (R1710) and the `global` statement (W0603), all of which are logic and design problems. Flake8 was the only one to check PEP 8 line length at 79 characters, and it overlapped with Pylint on `== None` (E711 / C0121). Together they cover security, correctness and style, and no single tool does all three.

## 2. Which issue was the most serious, and why?
The SQL injection in `grant()`. The input is spliced into the query string, so a student name with an apostrophe crashes it (I confirmed `O'Brien` raised an error in the original), and a crafted name could alter the SQL. In a scholarship system that stores financial amounts this is the one that could cause real harm. The mutable default `audit=[]` was a close second because it fails silently and leaks data between calls.

## 3. Were there false positives or findings you chose not to act on the same way?
Bandit's B605/B607 on `os.system("echo archiving awards")` are Low severity and technically safe, because the string is a constant. I still removed the call because it adds risk for no benefit. Pylint's R1710 (inconsistent returns) was a judgement call: I kept returning `None` for a missing award to preserve existing behaviour and documented it, though returning 0 or raising an error would also be defensible. The tools flag patterns, not intent, so a human has to decide.

## 4. How does static analysis contribute to code quality and maintainability?
It finds whole classes of problems without running the code, and it does so consistently, which a tired reviewer will not. The score also gives an objective target: Pylint went from 5.00 to 10.00 and Bandit and Flake8 went to zero, while the program's output stayed identical. It has limits: none of the tools flagged that `main()` ran on import, I only noticed that by reading the code, so static analysis supports code review but does not replace it or testing. In a team I would run all three in CI so new issues are blocked before merge.
