# SafeClick --- Development Phases

> Status: The phase sequence follows the README roadmap. The detailed
> tasks and completion checks below expand that roadmap into an
> actionable plan. A phase is complete only when its acceptance checks
> pass.

## Working principles

-   Build the smallest working increment.
-   Keep the rule engine usable without AI or external services.
-   Do not claim a feature is complete until implemented and tested.
-   Avoid adding dependencies without a clear need.
-   Keep the README, API contract, and tests synchronized.

## Phase 1 --- Repository setup and project contract

**README roadmap focus:** Repo setup, README, API contract agreed.

Tasks: - Confirm repository structure. - Add `.gitignore` and
`.env.example`. - Establish Python 3.11+ environment. - Confirm
dependencies and remove unused packages. - Agree request/response and
error contracts. - Add project documentation.

Acceptance checks: - Fresh environment can install dependencies. - No
secrets are committed. - API contract is documented. - Project structure
matches the actual implementation.

## Phase 2 --- Streamlit UI skeleton

**README roadmap focus:** UI skeleton with mock data.

Tasks: - Create analyzer home page. - Add message and URL inputs. - Add
input validation feedback. - Add loading, success, and error states. -
Build reusable score and indicator components. - Create Learn page
structure. - Use mock results only until API integration is ready.

Acceptance checks: - UI launches locally. - User can enter text, URL, or
both. - Mock result states render correctly. - Empty and oversized input
are handled clearly. - No secrets are embedded in UI code.

## Phase 3 --- FastAPI skeleton, schemas, validation, and errors

**README roadmap focus:** API skeleton, schemas, validation, errors.

Tasks: - Create FastAPI application entry point. - Define Pydantic
request and response models. - Implement `POST /api/analyze`. - Enforce
input limits and required-field rules. - Implement consistent error
responses. - Configure allowed origins safely. - Add API tests.

Acceptance checks: - Valid request returns the agreed response
structure. - Missing or malformed input returns 422. - Oversized input
returns 413. - Wrong content type returns 415 where applicable. - Wrong
method returns 405. - Unexpected errors return a generic 500 response
without leaking internals.

## Phase 4 --- Detection rules and risk scoring

**README roadmap focus:** Text, URL, and app-lure rules plus scoring.

Tasks: - Implement text normalization utilities. - Implement phishing
indicators. - Implement digital-arrest indicators. - Implement malicious
app-lure indicators. - Implement URL parsing and indicators. - Store
maintainable rule definitions in data files where appropriate. - Return
structured evidence for each indicator. - Implement grouped
contributions and score clamping. - Implement category assignment and
recommendations.

Acceptance checks: - Same input and rule version produce the same
rule-based result. - Score always stays within 0--100. - Category
boundaries match the specification. - Duplicate/overlapping signals
cannot inflate the score without limit. - Every score contribution maps
to a named indicator. - Submitted URLs are never opened or fetched. -
Legitimate examples and obvious scam examples are included in tests.

## Phase 5 --- UI and API integration

**README roadmap focus:** UI and API integration.

Tasks: - Replace mock analysis with API calls. - Add request timeout and
user-friendly connection errors. - Render score, category, indicators,
recommendations, and metadata. - Handle API validation errors. - Ensure
the UI does not independently calculate risk scores.

Acceptance checks: - A user can submit input from the UI and see the API
result. - UI output matches the API response. - API outages do not crash
the UI. - No backend logic is duplicated in the frontend.

## Phase 6 --- Tests, security review, and optional AI

**README roadmap focus:** Tests, security review, optional AI assist.

Tasks: - Expand unit and API test coverage. - Review input validation
and size limits. - Review URL non-fetching guarantee. - Review logging
and secret handling. - Review prompt-injection boundaries. - Implement
optional AI only if the baseline system is stable. - Keep AI disabled by
default. - Add explicit consent before external processing. - Validate
model output and constrain its effect.

Acceptance checks: - Security-critical tests pass. - No secrets appear
in repository or logs. - AI cannot silently activate. - AI output cannot
lower the rule-based score. - AI failure does not break baseline
analysis. - No unsupported accuracy claims are made.

## Phase 7 --- Learn section, polish, and demo

**README roadmap focus:** Learn section, polish, demo.

Tasks: - Complete awareness guides and checklists. - Improve empty,
error, and result states. - Check keyboard accessibility and
readability. - Prepare representative demo inputs. - Document
limitations and setup. - Verify the project from a clean clone.

Acceptance checks: - Learn section is accessible from the UI. - Demo
covers legitimate content and representative threat families. - Demo
does not imply that the system guarantees safety. - Setup instructions
work from a clean environment. - Known limitations are documented.

## Optional future work --- only after core completion

These are future possibilities from the README, not committed baseline
requirements: - Optional threat-intelligence lookups. - Wider language
coverage. - Trained classifiers after labelled data exists. - Browser
extension or share-sheet integration.

Each addition requires a separate scope, privacy review, security
review, and acceptance criteria.

## Definition of Done

A task is done when: 1. The requested behavior is implemented. 2.
Relevant tests pass. 3. Existing behavior is not unintentionally broken.
4. Security and privacy constraints remain intact. 5. Documentation is
updated when contracts or behavior change. 6. No unnecessary
dependencies or unrelated refactors were introduced.
