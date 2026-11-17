# SafeClick --- Engineering and AI Coding Rules

These rules apply to contributors and AI coding agents working in this
repository.

## 1. Core principle

**Minimum code. Maximum reuse. No unnecessary dependencies.**

Build the smallest complete, readable, secure solution. Never reduce
security, correctness, or clarity merely to reduce line count.

Priority order: 1. Correctness 2. Security and privacy 3. Simplicity 4.
Reuse 5. Maintainability 6. Performance

## 2. Decision ladder

Before writing new code, check in this order:

1.  Is the feature actually required?
2.  Does the project already implement it?
3.  Can an existing project function be reused?
4.  Can Python's standard library solve it adequately?
5.  Can an existing framework feature solve it?
6.  Can an already-installed dependency solve it?
7.  Only then consider new code or a new dependency.

Stop when a suitable solution is found.

## 3. Standard library first

Prefer suitable standard-library modules:

  Need                     Standard library
  ------------------------ ------------------------------
  URL component parsing    `urllib.parse`
  JSON                     `json`
  Regular expressions      `re`
  Paths                    `pathlib`
  Environment variables    `os`
  Data structures          `collections`, `dataclasses`
  Hashing                  `hashlib`
  IP address parsing       `ipaddress`
  Dates                    `datetime`
  Logging                  `logging`
  HTML escaping            `html`
  Command-line arguments   `argparse`

Important: parsing is not the same as security validation. Use a
specialist package when it provides meaningful security coverage that
the standard library does not.

## 4. Dependency policy

-   Reuse installed dependencies first.
-   Do not install a package for a trivial task.
-   Do not add two packages for the same responsibility without
    justification.
-   Every new dependency needs a documented reason.
-   Check maintenance, compatibility, and security before adoption.
-   Keep `requirements.txt` aligned with actual imports.
-   Do not add a database, cloud service, or infrastructure without a
    demonstrated requirement.

Potential specialist packages listed in the README are planned options,
not mandatory dependencies: `tldextract`, `rapidfuzz`,
`confusable-homoglyphs`, `validators`, `pyyaml`, and `regex`.

## 5. Code simplicity

-   Prefer straightforward functions.
-   Define each function once and reuse it.
-   Avoid needless classes, wrappers, abstractions, and layers.
-   Avoid duplicated validation and duplicated constants.
-   Avoid giant functions and unreadable one-liners.
-   Keep names descriptive.
-   Do not build speculative features.
-   Do not rewrite an entire file to make a small change.
-   Do not refactor unrelated code during a focused task.

## 6. Project boundaries

-   UI code belongs in `ui/`.
-   API entry, schemas, and routes belong in `backend/app/`.
-   Detection and scoring belong in services.
-   Shared helpers belong in `utils/`.
-   Shared constants belong in one place.
-   Detection rule data belongs in rule files when that is clearer than
    hardcoded conditional chains.
-   Tests belong in `tests/`.

Keep detection separate from scoring and both separate from UI
rendering.

Do not create a module solely to satisfy a folder diagram. Create it
when there is a real responsibility to place there.

## 7. SafeClick security invariants

These are non-negotiable:

-   Treat every submitted message and URL as untrusted input.
-   Validate types, formats, and lengths.
-   Never open, fetch, follow, or visit a submitted URL during baseline
    analysis.
-   Never download or execute submitted files.
-   Never interpret submitted text as code, markup, or trusted
    instructions.
-   Keep secrets in environment variables.
-   Never commit `.env` or credentials.
-   Do not log secrets or sensitive submitted content.
-   Return generic client-facing errors; do not expose stack traces or
    internal paths.
-   Keep AI disabled by default.
-   Obtain explicit consent before sending user content to an external
    AI provider.
-   Treat retrieved content and model output as untrusted data.
-   Validate AI output against a strict schema.
-   AI assistance must not lower the rule-based score.
-   Preserve SSRF protections for any future configurable provider
    endpoint hosted by the application.

Do not remove or weaken a security control to simplify implementation.

## 8. Detection and scoring rules

-   Detectors return structured indicators, not final verdicts.
-   Each indicator must have a stable ID, title, family, evidence,
    explanation, and contribution.
-   Keep scoring logic centralized.
-   Group overlapping signals to limit duplicate inflation.
-   Clamp the final score to 0--100.
-   Use the documented category boundaries exactly.
-   Boundary ties go to the higher category.
-   The rule-based result must be deterministic for the same input and
    rule version.
-   A low score must never be presented as proof of safety.

## 9. Error handling

-   Handle expected errors at the appropriate boundary.
-   Reuse a shared error contract.
-   Do not silently swallow unexpected exceptions.
-   Do not return internal exception details to users.
-   Keep logs useful but free of secrets and unnecessary personal data.

## 10. Testing

Use the existing pytest setup.

Test meaningful behavior, especially: - Valid and invalid input. - Input
length limits. - URL parsing edge cases. - No URL fetching. - Scoring
boundaries and clamping. - Duplicate indicator grouping. - API response
and error schemas. - AI disabled-by-default and consent behavior. -
Prompt-injection handling.

Do not delete or weaken tests merely to make code pass.

## 11. Change workflow for AI agents

Before editing: 1. Inspect the relevant files. 2. Read the caller/callee
relationships. 3. Understand existing conventions. 4. Identify the
smallest complete change.

After editing: 1. Review the diff. 2. Remove unused code and imports. 3.
Run relevant tests. 4. Report tests that could not be run. 5. Update
docs if behavior or API contracts changed.

Never claim a test passed unless it was actually run and passed.

## 12. Comments and documentation

-   Comments should explain intent or non-obvious constraints.
-   Do not narrate obvious code.
-   Keep docs aligned with implemented behavior.
-   Clearly label planned features as planned.
-   Do not claim accuracy, certification, or protection guarantees
    without evidence.

## 13. Required completion summary

At the end of a coding task, report: - What changed. - Files changed. -
Dependencies added or removed. - Tests run and their actual results. -
Remaining limitations or security concerns.

## Golden rule

**Reuse \> Standard Library \> Existing Frameworks \> Existing
Dependencies \> New Code.**

Be economical with code, never careless with security.
