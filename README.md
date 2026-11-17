# SafeClick

**Cyber Security Awareness Platform for Phishing, Digital Arrest Scams, and Malicious Applications**

![status](https://img.shields.io/badge/status-stage%207%20complete-brightgreen)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

SafeClick lets you paste a suspicious message or link and get an **explainable risk score (0 to 100)**,
the exact signals behind it, and clear next steps, before you click, pay, or install.

> Student project: VTU Community / Societal Project (1BCP308), Cambridge Institute of Technology,
> North Campus. Supports UN SDG 16.
> **Status:** all seven roadmap stages are implemented and covered by tests. It remains a rule-based
> educational tool, not a verdict. No benchmark or accuracy result is claimed.

---

## Why SafeClick

Phishing, "digital arrest" calls (fake police or CBI officers demanding payment), and fake app downloads work
by creating fear and urgency. Most tools check only links or files, or give an unexplained "safe/unsafe" answer.
SafeClick is meant to be a fast, transparent second opinion that also teaches users what to look for.

## Features

- Paste text, a URL, or both and get a score from 0 to 100 with a category.
- **Explainable:** every point in the score maps to a named indicator with a plain-language reason.
- **Three threat families:** phishing, digital arrest scams, malicious app download lures.
- **URL analysis** without ever opening the link.
- **Safe-action advice** matched to the risk level.
- **Learn section** with short awareness guides and checklists.
- **Bring your own model (optional):** add AI assistance using NVIDIA NIM, a local model (Ollama, LM Studio),
  or any OpenAI-compatible endpoint. Off by default; the rule engine works without it.

### What it checks

| Family | Examples of signals |
|---|---|
| Phishing | Urgency, authority impersonation, credential or KYC requests, odd payment channels, generic greetings, prize baiting, obfuscated spelling |
| Digital arrest | Case or FIR claims, "do not tell anyone", stay-on-call pressure, "verification fee", video-call "officer", arrest threats |
| App lures | Direct `.apk` / `.exe` links, sideloading steps, risky permission requests, fake update prompts |
| URLs | Lookalike domains, shorteners, punycode and homoglyphs, misleading subdomains, plain HTTP, embedded credentials, suspicious query parameters |

### Risk categories

| Category | Score | Meaning |
|---|---|---|
| Low | 0 to 24 | Few or no signals. Not a guarantee of safety. |
| Medium | 25 to 49 | Some suspicious signals. Verify through a trusted channel. |
| High | 50 to 74 | Multiple strong signals. Do not act before verifying. |
| Critical | 75 to 100 | Strong scam pattern. Do not click, pay, install, or reply. |

The score is clamped to 0 to 100, reproducible for the same input and rules, and ties at a boundary go to the
higher category. Overlapping signals are grouped so repeated matches cannot inflate the score without limit.

---

## How it works

```
User -> Streamlit UI -> POST /api/analyze -> FastAPI
                                              |-- validation (Pydantic)
                                              |-- text_analyzer
                                              |-- url_analyzer
                                              |-- risk_scorer
                                              |-- llm_client (optional, consent only)
                                              '-- reputation (optional, consent only)
            <- score, category, indicators, recommendations, metadata
```

Design principles: detection is separate from scoring and from the UI, results are always explainable, all input
is untrusted, and external services are optional.

## Tech stack

Python only. **UI:** Streamlit. **API:** FastAPI + Pydantic. **Tests:** pytest.
**Optional AI:** the Python standard library (`urllib`) against any OpenAI-compatible endpoint, so no extra package is needed.
Helper libraries (planned): `tldextract`, `rapidfuzz`, `confusable-homoglyphs`, `validators`, `pyyaml`, `regex`.
No database or cloud infrastructure.

---

## API

`POST /api/analyze` (`application/json`)

**Request**

| Field | Type | Required | Notes |
|---|---|---|---|
| `text` | string | one of | Suspicious message |
| `url` | string | one of | Suspicious URL |
| `options` | object | no | Optional flags, e.g. consent to use an AI model |

**Response**

| Field | Type | Notes |
|---|---|---|
| `score` | integer | 0 to 100 |
| `category` | string | `low`, `medium`, `high`, `critical` |
| `indicators` | array | id, title, family, evidence, explanation, contribution |
| `recommendations` | array | Prioritised plain-language actions |
| `metadata` | object | Detector version, whether any external check was used |

**Errors** (one shared shape): `422` missing or malformed input, `413` too large, `415` wrong content type,
`405` wrong method, `500` generic server error.

---

## Project structure

```
SafeClick/
├── README.md                    # This file
├── AGENTS.md                    # Engineering rules
├── PRD.md, architecture.md, design.md, phases.md, rules.md, memory.md
├── .gitignore                   # .env, .venv, __pycache__, private/
├── .env.example                 # Copy to .env (optional; safe defaults without it)
├── requirements.txt
├── ui/
│   ├── streamlit_app.py         # Home: input, states, results
│   ├── pages/Learn.py           # Awareness content
│   ├── components.py            # Score badge, result card
│   ├── api_client.py            # Calls POST /api/analyze
│   └── theme.py
├── backend/
│   └── app/
│       ├── main.py              # App entry, middleware
│       ├── schemas.py           # Request and response models
│       ├── routes/analyze.py
│       ├── services/            # text_analyzer, url_analyzer, risk_scorer, recommendations, llm_client
│       ├── utils/               # constants, errors, config
│       └── rules/               # JSON rule and word-list files
└── tests/                       # text_analyzer, url_analyzer, scorer, api, api_client, ui_app, llm_client, security
```

Code rules: each function is defined once and reused; shared helpers live in `utils/`, constants in one place,
and detection rules in data files rather than `if` chains.

---

## Getting started

Requires Python 3.11+.

```bash
git clone <your-repo-url> && cd SafeClick
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env              # then edit values

# terminal 1: API
uvicorn backend.app.main:app --reload

# terminal 2: UI
streamlit run ui/streamlit_app.py

# tests
pytest
```

`.env` is optional: the app runs with safe defaults (rules only, AI off) when it is absent.

### Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `ENABLE_LLM` | `false` by default. Turns on optional AI assistance. |
| `LLM_BASE_URL` | OpenAI-compatible endpoint (NVIDIA NIM, Ollama `http://localhost:11434/v1`, LM Studio `http://localhost:1234/v1`, or custom) |
| `LLM_API_KEY` | Key for that endpoint. Never commit it. |
| `LLM_MODEL` | Model ID exactly as the provider lists it |
| `LLM_ALLOW_PRIVATE_NETWORK` | `false` by default. Must be `true` to use a local/private model endpoint (SSRF guard). |
| `ALLOWED_ORIGINS` | CORS origins for the UI |
| `SAFECLICK_API_BASE_URL` | Where the UI reaches the API (default `http://127.0.0.1:8000`) |

`.env` is not auto-loaded unless `python-dotenv` is installed. Either install it and run
`uvicorn backend.app.main:app --env-file .env`, or export the variables in your shell.
Local models work only when the app runs on the same machine as the model and
`LLM_ALLOW_PRIVATE_NETWORK=true` is set.

---

## Security and privacy

- All input is untrusted: validated, length-limited, and never treated as code or markup.
- Submitted URLs are **never** opened, fetched, or followed. Files are never downloaded or run.
- Submissions are **not stored** by default.
- Secrets live in `.env` only. Errors never reveal paths, stack traces, or versions.
- If AI assistance is on, submitted text is sent to the chosen model provider, so the UI asks for consent first.
  Rules stay the source of truth; the model's output is schema-validated and can only raise the score.
- Model URLs and keys come from `.env` and are never logged. Private/loopback endpoint addresses are blocked
  by default to prevent server-side request forgery; using a local model requires the explicit
  `LLM_ALLOW_PRIVATE_NETWORK` opt-in.
- Submitted text may try to instruct the model (prompt injection), so it is passed as delimited data only.

## Testing

Test classes: legitimate message, legitimate URL, suspicious message, obvious scam, digital arrest script,
app lure, deceptive URL, shortened URL, boundary inputs (empty, whitespace, very long, malformed).

Acceptance checks: score always 0 to 100; category always one of four values; categories match the ranges
exactly; every score point maps to a named indicator; legitimate samples stay low; obvious scams reach High or
Critical; URLs are never opened; no secrets in the repository.

## Roadmap

| Stage | Focus | Done |
|---|---|---|
| 1 | Repo setup, README, API contract agreed | [x] |
| 2 | UI skeleton with mock data | [x] |
| 3 | API skeleton, schemas, validation, errors | [x] |
| 4 | Text, URL, and app-lure rules plus scoring | [x] |
| 5 | UI and API integration | [x] |
| 6 | Tests, security review, optional AI assist | [x] |
| 7 | Learn section, polish, demo | [x] |

## Limitations

- Rules miss novel or reworded scams, and coverage of non-English text is limited.
- The score is an indication to support your judgement, not a verdict. A low score is never proof of safety.
- URLs are not visited by design, so live page behaviour is not checked.
- AI output can be wrong or vary between runs, so it only assists the rules.

## Future work

Optional threat-intelligence lookups, wider language coverage, trained classifiers once labelled data exists,
browser extension or share-sheet check, more awareness content.

## License

All rights reserved for now. A licence will be added later.

## Disclaimer

SafeClick is an educational tool. It does not replace professional security advice. If you are a victim of fraud
in India, call **1930** or report at **cybercrime.gov.in**.
