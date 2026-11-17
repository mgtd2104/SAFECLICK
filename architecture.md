# SafeClick --- Architecture

> Status: Proposed implementation architecture based on the project
> README. Features remain planned until implemented and verified.

## 1. Purpose

SafeClick is a cybersecurity-awareness platform that accepts a
suspicious message, URL, or both and returns an explainable risk score
(0--100), named indicators, and practical next steps.

The architecture prioritizes: - Explainable, deterministic rule-based
analysis. - Separation of detection, scoring, API, and UI. - Safe
handling of untrusted input. - No automatic visiting, fetching,
following, downloading, or executing of submitted URLs or files. -
Optional AI assistance, disabled by default.

## 2. System overview

``` text
User
  |
  v
Streamlit UI
  |
  | POST /api/analyze
  v
FastAPI application
  |
  +--> Request validation (Pydantic)
  |
  +--> Text analyzer
  |
  +--> URL analyzer
  |
  +--> Risk scorer
  |
  +--> Recommendations
  |
  +--> Optional AI assistance (explicit consent only)
  |
  v
Structured response
  |
  v
Streamlit results UI
```

Optional reputation checks may be added later, only with explicit
consent and a reviewed privacy/security design. They are not required
for the baseline rule engine.

## 3. Technology choices

  -----------------------------------------------------------------------
  Layer                   Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  UI                      Streamlit               Input, loading/error
                                                  states, results,
                                                  learning content

  API                     FastAPI                 HTTP interface and
                                                  request lifecycle

  Schemas                 Pydantic                Request/response
                                                  validation

  Core                    Python 3.11+            Detection, scoring,
                                                  recommendations

  Tests                   pytest                  Unit and API tests

  Optional AI             Python standard library AI assistance through
                          (urllib)                compatible endpoints,
                                                  only when enabled and
                                                  consented

  Rules                   YAML/JSON or Python     Maintainable detection
                          data structures         rules
  -----------------------------------------------------------------------

Use the Python standard library where it is sufficient. Add specialist
dependencies only when their specific capability is needed.

## 4. Suggested repository structure

``` text
SafeClick/
├── README.md
├── AGENTS.md
├── .gitignore
├── .env.example
├── requirements.txt
├── ui/
│   ├── streamlit_app.py
│   ├── api_client.py
│   ├── components.py
│   ├── theme.py
│   └── pages/
│       └── Learn.py
├── backend/
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       ├── routes/
│       │   └── analyze.py
│       ├── services/
│       │   ├── text_analyzer.py
│       │   ├── url_analyzer.py
│       │   ├── risk_scorer.py
│       │   ├── recommendations.py
│       │   └── llm_client.py
│       ├── rules/
│       │   ├── text_rules.yaml
│       │   └── url_rules.yaml
│       └── utils/
│           ├── config.py
│           ├── constants.py
│           ├── errors.py
│           └── text_utils.py
├── tests/
│   ├── test_text_analyzer.py
│   ├── test_url_analyzer.py
│   ├── test_scorer.py
│   └── test_api.py
└── docs/
    ├── architecture.md
    ├── design.md
    ├── phases.md
    ├── rules.md
    └── PRD.md
```

Keep the structure proportional to the implementation. Do not create
empty modules or layers before they are needed. The README's original
structure is the baseline; the recommendations module and `AGENTS.md`
are proposed additions.

## 5. Request lifecycle

1.  The UI accepts text, URL, or both.
2.  The UI sends JSON to `POST /api/analyze`.
3.  FastAPI validates the request using Pydantic.
4.  The text analyzer and/or URL analyzer inspect the supplied values
    locally.
5.  Each detector returns structured indicators with evidence and rule
    metadata.
6.  The scorer groups overlapping signals, calculates contributions,
    clamps the score to 0--100, and assigns a category.
7.  The recommendation layer selects plain-language next steps based on
    the category and indicators.
8.  If AI is enabled and the user has explicitly consented, optional AI
    assistance may run. Its output must be schema-validated and must not
    lower the rule-based score.
9.  The API returns a consistent response.
10. The UI renders the score, category, indicators, recommendations, and
    metadata.

## 6. Core contracts

### Request

`POST /api/analyze`

``` json
{
  "text": "optional suspicious message",
  "url": "optional suspicious URL",
  "options": {
    "use_ai": false
  }
}
```

At least one of `text` or `url` must be supplied. `options` is optional.
The exact supported option names should be finalized in the
implementation.

### Response

``` json
{
  "score": 0,
  "category": "low",
  "indicators": [],
  "recommendations": [],
  "metadata": {
    "detector_version": "string",
    "external_check_used": false
  }
}
```

Each indicator should include stable identity, title, family, evidence,
explanation, and score contribution. The exact schema belongs in
`backend/app/schemas.py`.

### Error contract

Use one consistent error response shape for: - `405` wrong method -
`413` input too large - `415` wrong content type - `422` missing or
malformed input - `500` generic server error

Do not expose stack traces, filesystem paths, secrets, or internal
configuration in client-facing errors.

## 7. Detection families

  -----------------------------------------------------------------------
  Family                              Example signals
  ----------------------------------- -----------------------------------
  Phishing                            Urgency, authority impersonation,
                                      credential/KYC requests, unusual
                                      payment channels, generic
                                      greetings, prize bait, obfuscated
                                      spelling

  Digital arrest                      FIR/case claims, secrecy pressure,
                                      stay-on-call pressure,
                                      verification-fee demands,
                                      video-call impersonation, arrest
                                      threats

  Malicious app lures                 Direct APK/EXE links, sideloading
                                      instructions, risky permission
                                      requests, fake update prompts

  URL indicators                      Lookalike domains, shorteners,
                                      punycode/homoglyphs, misleading
                                      subdomains, plain HTTP, embedded
                                      credentials, suspicious query
                                      parameters
  -----------------------------------------------------------------------

These are intended detection categories, not a claim that every example
is already implemented.

## 8. Scoring architecture

-   Detection produces indicators; it does not decide the final
    category.
-   The scorer consumes structured indicators and applies configured
    contributions.
-   Overlapping indicators are grouped so repeated matches cannot
    inflate the score without limit.
-   The final score is clamped to 0--100.
-   Boundary ties go to the higher category.
-   The same input and same rule version must produce the same
    rule-based result.

  Category       Score
  ---------- ---------
  Low            0--24
  Medium        25--49
  High          50--74
  Critical     75--100

A low score is not proof that content is safe.

## 9. Security and privacy boundaries

-   Treat all submitted text and URLs as untrusted data.
-   Never open, fetch, follow, resolve through a browser, or download a
    submitted URL as part of baseline analysis.
-   Never execute or install submitted files.
-   Validate and length-limit inputs.
-   Do not interpret submitted content as code, HTML, templates, or
    instructions.
-   Keep secrets in environment variables; never commit them.
-   Do not log submitted content, API keys, or sensitive values by
    default.
-   AI is off by default. Obtain explicit consent before sending user
    content to an external provider.
-   Treat model output as untrusted; validate its schema and constrain
    its influence.
-   Block private-network destinations for any future server-side
    user-configurable provider URL feature.
-   Keep external reputation lookups optional and separately consented.

## 10. Configuration

Expected environment variables from the README:

  Variable            Purpose
  ------------------- ---------------------------------------
  `ENABLE_LLM`        Enables optional AI; false by default
  `LLM_BASE_URL`      OpenAI-compatible endpoint
  `LLM_API_KEY`       Provider credential; secret
  `LLM_MODEL`         Provider model identifier
  `LLM_ALLOW_PRIVATE_NETWORK`  Opt-in to allow a local/private endpoint (SSRF off by default)
  `ALLOWED_ORIGINS`   Allowed CORS origins

Never hardcode credentials. Validate configuration at startup and fail
safely when required settings are missing.

## 11. Testing strategy

-   Unit-test text detection, URL detection, scoring, and recommendation
    selection.
-   Test category boundaries: 24/25, 49/50, 74/75.
-   Test score clamping and duplicate/overlapping indicators.
-   Test empty, whitespace-only, malformed, and oversized input.
-   Test that submitted URLs are not fetched.
-   Test API error shapes and response schema.
-   Test AI-disabled behavior and consent enforcement.
-   Include legitimate examples and representative scam examples.
-   Do not claim accuracy or benchmark performance without a documented
    evaluation dataset and reproducible method.

## 12. Architecture decision rules

1.  Prefer standard-library functionality when it is sufficient.
2.  Reuse existing project functions and dependencies.
3.  Introduce a new package only for a clear capability gap.
4.  Keep modules small and responsibility-focused.
5.  Do not add a database or cloud infrastructure unless a validated
    requirement appears.
6.  Preserve deterministic rule-based behavior when optional
    integrations are unavailable.
