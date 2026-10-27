# Issues Found and Fixed — `electricity_bill.py`

Line numbers refer to the **original** file. Results: Pylint 5.44 → **10.00/10**, Flake8 4 → **0**, Bandit 4 → **0**. Program output is byte-for-byte identical before and after (`reports/original_output.txt`).

## Bandit (security) — commit `Fix Bandit findings`

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| B605 start_process_with_a_shell (High) | Security | 63 | `os.system("curl http://" + meterIp + "/reading")` builds a shell command from a caller-supplied string, so `meterIp = "1.2.3.4; rm -rf ~"` runs arbitrary commands (command injection, CWE-78). | Removed `os`/`curl`. Validate the argument with `ipaddress.ip_address()` and fetch with `http.client.HTTPConnection(..., timeout=5)`. No shell is involved. |
| B314 xml.etree fromstring (Medium) | Security | 18 | `ET.fromstring()` on XML is vulnerable to entity-expansion attacks ("billion laughs") if the XML ever comes from an untrusted source. | Parse with `defusedxml.ElementTree`, which rejects those constructs. Added `requirements.txt`. |
| B405 import xml.etree (Low) | Security | 3 | Importing `xml.etree.ElementTree` is flagged for the same reason as B314. | Replaced the import with `from defusedxml import ElementTree as ET`. |
| B105 hardcoded_password_string (Low) | Security | 13 | `CLERK_PASSWORD = "bill-desk-demo"` is a secret committed to source control. | The constant was never used anywhere, so it was deleted. Real credentials would come from an environment variable. |

## Pylint (quality / bugs) — commit `Fix Pylint findings`

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| W0102 dangerous-default-value | Bug | 42 | `extras={}` is created once at definition time and shared across every call, so a mutation would leak between bills. | Default changed to `None`; `extras = extras or {}` inside the function. |
| W0613 unused-argument | Code smell | 50 | `average_bill(currency)` never uses `currency`, which misleads callers into thinking it matters. | Removed the parameter and updated the one caller in `main()`. |
| W1514 unspecified-encoding | Bug (portability) | 57 | `open(fileName, "w")` uses the platform default encoding, so output can differ between machines. | `open(file_name, "w", encoding="utf-8")`. |
| C0103 invalid-name (14 occurrences) | Style | 17–67 | camelCase functions, arguments and variables (`readMeters`, `meterId`, `taxRate`, ...) violate PEP 8 snake_case. | Renamed all to snake_case; every call site updated. |
| C0114 / C0116 missing docstrings | Documentation | 1, 17–66 | No module docstring and no function docstrings (8 functions). | Added a one-line docstring to the module and every function. |
| `main()` runs on import | Design (found by reading, not a tool message) | 82 | `main()` was called at module level, so importing the file ran the whole demo and wrote `bills.json`. | Wrapped in `if __name__ == "__main__":`. |

## Flake8 (style) — commit `Fix Flake8 findings`

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| E302 | Style | 22 | Expected 2 blank lines before `calculateUnits`, found 1. | Added the missing blank line. |
| E203 | Style | 44 | Whitespace before `:` in `{"meter" : meterId}`. | Changed to `{"meter": meter_id}`. |
| E501 | Style | 72 | Line is 86 characters, limit is 79. | Wrapped the `print(...)` call over two lines. |
| E225 | Style | 76 | Missing whitespace around `=` in `total=sum(...)`. | Changed to `total = sum(...)`. |

## Behaviour notes

- `sync_meter()` (was `syncMeter`) is not called by the demo. It used to print curl's output; it now **returns** the response text. That is the only intentional behaviour change, and it is in dead code.
- `average_bill()` lost its unused `currency` argument; the printed result is unchanged.
