# Reflection — Lab 5: Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest?

The easiest were the Flake8 findings and the mutable default. Each was a one-line change with an obvious correct answer (add a blank line, add spaces around `=`, `extras=None`). Renaming to snake_case was also easy to do but tedious to verify, because every call site had to change together.

The hardest was Bandit's B605. Deleting the `os.system` line would have removed the warning, but it would also have removed the function. I had to decide what the function should do instead: validate the input with `ipaddress.ip_address()` and make the request with `http.client`. The XML finding (B314) needed a judgement call as well, because the fix adds a new dependency (`defusedxml`).

## 2. Did the tools report any false positives?

Not clear-cut ones, but two findings were context-dependent.

- **B314 / B405 (XML):** `METER_XML` is a hardcoded constant in the file, so today nobody can inject anything. The warning matters only if the XML later comes from a file or a network call. I fixed it anyway because it is cheap and the code is clearly meant to read meter data.
- **B105 (hardcoded password):** the value was a demo string and was never used. The detection is correct for the pattern, but nothing could have been exploited. Deleting it was safer than adding a `# nosec` comment.

Pylint's docstring and naming messages are style opinions rather than bugs, and a team could reasonably configure them differently.

## 3. How would you integrate static analysis into a real workflow?

- Run Flake8 and Pylint as a **pre-commit hook** so style and quality problems never reach the repository.
- Run all three tools in **CI** on every pull request, with a Pylint minimum score (for example 9.5) and Bandit set to fail on Medium and above.
- Keep the configuration in the repo (`.pylintrc`, `setup.cfg`/`tox.ini`, `bandit.yaml`) so every developer and the CI see the same rules.
- Use `# nosec` or `# pylint: disable=` only with a written reason in the comment, so suppressions get reviewed rather than hidden.

## 4. What tangible improvements did you see in the code?

- **Security:** the High-severity command injection is gone, XML parsing is hardened, and no secret is stored in source.
- **Correctness:** the shared mutable default can no longer leak state between bills, and the file now writes with an explicit encoding, so the output no longer depends on the machine.
- **Readability and maintainability:** consistent snake_case names, docstrings on every function, and a `__main__` guard so the module can be imported (and tested) without running the demo.
- **Measurable:** Pylint rose from 5.44 to 10.00, and Flake8 and Bandit went from 4 findings each to 0. The program's printed output did not change at all, which I confirmed by diffing it against the original run after every commit.
