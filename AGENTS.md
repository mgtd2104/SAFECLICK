# SafeClick — Minimal Code Engineering Rules

## Core Philosophy

Act like a lazy but highly competent senior Python developer.

**The best code is the code you never had to write.**

Build the smallest, simplest, safest implementation that completely solves the requested task.

Priorities:
1. Correctness
2. Security
3. Simplicity
4. Reusability
5. Maintainability
6. Performance

Never sacrifice correctness or security just to reduce lines of code.

## 1. The Decision Ladder

Before writing ANY code, follow this order. Stop at the first option that fully solves the problem.

1. Does this feature actually need to exist? If not, don't build it (YAGNI).
2. Does the functionality already exist in the project? Reuse it.
3. Can Python's standard library handle it? Prefer it.
4. Can an existing framework or native platform feature handle it?
5. Can an already-installed dependency handle it?
6. Can the solution be simplified into fewer lines?
7. Only then write new code.

Never introduce unnecessary implementations.

## 2. Python Standard Library First

Prefer Python's built-in modules whenever suitable.

Examples:

| Requirement | Prefer |
|---|---|
| URL parsing | urllib.parse |
| JSON handling | json |
| Regular expressions | re |
| File operations | pathlib |
| Environment variables | os |
| Data structures | collections |
| Data validation basics | Built-in checks |
| Hashing | hashlib |
| Dates and times | datetime |
| Logging | logging |
| IP address checks | ipaddress |
| HTML escaping | html |
| Command-line arguments | argparse |
| Testing simple logic | unittest / assert |

Do not install a third-party package for functionality Python already provides.

Important: Standard-library URL parsing is not equivalent to security validation. Use specialist libraries when their additional protection is genuinely necessary.

## 3. Dependency Rules

- Reuse installed dependencies before considering new ones.
- Never install a package for a trivial operation.
- Never add duplicate libraries that solve the same problem.
- Every new dependency must have a clear technical justification.
- Prefer lightweight and maintained packages.
- Ask before introducing a new dependency.
- Keep requirements.txt clean and remove unused packages.

Existing project stack:
- Streamlit: UI
- FastAPI: API
- Pydantic: schemas and validation
- pytest: existing test framework
- OpenAI-compatible client: optional AI integration

Planned specialist libraries such as tldextract, rapidfuzz and confusable-homoglyphs should only be added when their specific capabilities are needed.

## 4. Minimum Code Rules

- Write the fewest lines that remain readable.
- Avoid unnecessary classes.
- Avoid unnecessary functions.
- Avoid excessive helper files.
- Avoid duplicate validation.
- Avoid unnecessary wrappers.
- Avoid unnecessary configuration options.
- Avoid overengineering.
- Avoid creating features for hypothetical future requirements.
- Delete redundant code instead of adding another workaround.

Do not compress code into unreadable one-liners.

Readable and maintainable code is more important than winning a line-count competition.

## 5. Reuse and Architecture

Follow the existing SafeClick architecture.

- Define each function once.
- Reuse existing functions wherever possible.
- Keep shared helpers in utils/.
- Keep constants centralized.
- Keep detection rules in YAML/JSON data files rather than lengthy if-else chains.
- Keep detection separate from risk scoring.
- Keep business logic separate from the UI.
- Do not duplicate existing functionality in another module.

Do not create a new architectural layer unless it solves an actual problem.

## 6. Security Is Non-Negotiable

This is a cybersecurity awareness project. Never remove security protections to make code shorter.

Always preserve:

- Input validation and length limits.
- Safe error handling.
- URL parsing without visiting submitted URLs.
- Protection against malicious input.
- Prompt injection protections.
- Secret and API key protection.
- SSRF protections.
- Consent before sending user content to external AI services.
- Safe handling of untrusted data.
- No execution or downloading of submitted files.
- No sensitive information in logs.

Never trust AI-generated security decisions.

The rule engine remains the source of truth. AI assistance may only raise the score after schema validation.

## 7. Error Handling

- Handle errors where they actually occur.
- Reuse shared error-handling functions.
- Do not create multiple handlers for the same error.
- Never expose stack traces, internal paths, secrets or sensitive configuration.
- Preserve the existing API error contract.
- Do not silently ignore unexpected errors.

## 8. Testing Rules

Do not build unnecessary testing infrastructure.

For every new non-trivial piece of logic, add the smallest useful test using the existing pytest framework.

Prioritize:
- Input validation
- URL edge cases
- Scoring boundaries
- Duplicate indicator handling
- Malicious input
- API response structure
- Security regressions

Simple one-line changes do not need elaborate tests.

Never remove an existing test just to make an implementation pass.

## 9. Modification Rules

Before changing existing code:

1. Read the relevant file.
2. Understand how the function is used.
3. Check its callers and dependencies.
4. Identify potential regressions.
5. Fix the root cause instead of adding repeated workarounds.
6. Make the smallest complete change.
7. Run relevant tests.

Do not rewrite entire files when a small modification is sufficient.

Do not modify unrelated files.

## 10. Comments and Documentation

- Write comments only when the reason is not obvious from the code.
- Avoid comments that simply repeat the code.
- Avoid excessive documentation.
- Update documentation when actual functionality or API behaviour changes.
- Mark deliberate shortcuts with:

`shortcut: <known limitation>, <when to upgrade>`

## 11. Final Response

After completing a coding task, briefly report:

1. What changed.
2. Which files were modified.
3. Whether dependencies were added.
4. Whether tests passed.
5. Any limitations or security concerns.

Mention what you deliberately did not build when it helps explain the scope.

## Golden Rule

**Reuse > Standard Library > Native Features > Existing Dependencies > New Code.**

Be lazy about the solution, never careless about correctness.

The smallest complete and secure implementation wins.