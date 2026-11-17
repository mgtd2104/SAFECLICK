# SafeClick --- Product Requirements Document (PRD)

**Product:** SafeClick\
**Document status:** Draft\
**Project type:** Student project --- VTU Community / Societal Project
(1BCP308)\
**Institution:** Cambridge Institute of Technology, North Campus\
**Primary platform:** Python web application\
**Version:** 0.1

> This PRD is based on the supplied project README. Requirements not
> specified there are identified as proposed or open decisions. Features
> remain planned until implemented and verified.

## 1. Product summary

SafeClick is a cybersecurity-awareness platform that lets a user paste a
suspicious message, URL, or both and receive an explainable risk score
from 0 to 100, the indicators behind the score, and practical next
steps.

The product focuses on three threat families: - Phishing. - Digital
arrest scams. - Malicious application download lures.

It also examines URL characteristics without opening the submitted URL.

## 2. Problem statement

People may be pressured by suspicious messages, fake authority claims,
payment demands, or malicious application links. Many users need a quick
second opinion that explains the warning signs rather than returning
only an unexplained "safe" or "unsafe" label.

SafeClick aims to support user awareness and judgement through
transparent indicators and plain-language recommendations.

## 3. Product goals

1.  Accept suspicious text and/or a URL.
2.  Identify relevant warning signals across the supported threat
    families.
3.  Produce a reproducible, explainable score from 0 to 100.
4.  Show the evidence and reason behind each indicator.
5.  Give recommendations matched to the risk level.
6.  Provide short educational material.
7.  Operate without an AI model or external service.
8.  Protect user-submitted content and avoid automatically visiting
    suspicious URLs.

## 4. Non-goals

The baseline product is not intended to: - Guarantee that a message or
URL is safe. - Replace professional cybersecurity advice. -
Automatically investigate or visit suspicious websites. - Download,
install, or execute suspicious files. - Act as a law-enforcement or
fraud-reporting authority. - Guarantee detection of every scam or newly
emerging attack. - Require a database or cloud infrastructure. - Require
AI for core analysis.

## 5. Target users

The README describes the product as a student cybersecurity-awareness
tool. The following user groups are proposed based on that purpose:

-   Everyday users who receive suspicious messages or links.
-   Students learning to recognize online scams.
-   People who want an understandable explanation of suspicious content.

These are intended audiences, not validated research findings.

## 6. Core user stories

### Analysis

-   As a user, I want to paste a suspicious message so I can see its
    warning signs.
-   As a user, I want to submit a URL without opening it so I can
    inspect suspicious URL characteristics.
-   As a user, I want to submit both text and a URL so the tool can
    assess available signals together.

### Explanation

-   As a user, I want to see a score and risk category so I can
    understand the overall assessment.
-   As a user, I want to see each indicator's evidence and explanation
    so I understand why it was flagged.
-   As a user, I want practical next steps matched to the result.

### Learning

-   As a user, I want short awareness guides so I can recognize common
    scam patterns in the future.

### Optional AI

-   As a user, I want optional AI assistance so I can request additional
    explanation.
-   As a user, I want to know before content is sent to an external
    model provider and explicitly consent to that processing.

## 7. Functional requirements

### FR-01: Input

The system shall accept: - Suspicious message text. - A URL. - Both text
and URL.

At least one of text or URL must be supplied.

### FR-02: Validation

The API shall validate request structure and input size. Empty,
malformed, or oversized input shall be handled using the documented
error contract.

### FR-03: Text analysis

The system shall examine text for indicators associated with: -
Phishing. - Digital arrest scams. - Malicious application lures.

Examples include urgency, authority impersonation, credential/KYC
requests, unusual payment channels, secrecy pressure, case/FIR claims,
stay-on-call pressure, and app-installation lures.

### FR-04: URL analysis

The system shall inspect URL characteristics such as: - Lookalike
domains. - URL shorteners. - Punycode and homoglyphs. - Misleading
subdomains. - Plain HTTP. - Embedded credentials. - Suspicious query
parameters.

The system shall not open, fetch, or follow the submitted URL.

### FR-05: Explainable indicators

Every score contribution shall map to a named indicator with: - ID. -
Title. - Threat family. - Evidence. - Plain-language explanation. -
Contribution.

### FR-06: Risk scoring

The system shall return an integer score from 0 to 100.

The score shall: - Be clamped to 0--100. - Be reproducible for the same
input and rule version. - Group overlapping signals so repeated matches
cannot inflate the score without limit. - Assign boundary ties to the
higher category.

### FR-07: Risk categories

  ------------------------------------------------------------------------
  Category                                     Score Required meaning
  --------------------- ---------------------------- ---------------------
  Low                                          0--24 Few or no signals;
                                                     not a guarantee of
                                                     safety

  Medium                                      25--49 Some suspicious
                                                     signals; verify
                                                     through a trusted
                                                     channel

  High                                        50--74 Multiple strong
                                                     signals; do not act
                                                     before verifying

  Critical                                   75--100 Strong scam pattern;
                                                     do not click, pay,
                                                     install, or reply
  ------------------------------------------------------------------------

### FR-08: Recommendations

The system shall return prioritized plain-language recommendations
appropriate to the detected signals and risk category.

### FR-09: Learn section

The UI shall provide short awareness guides and checklists.

### FR-10: Optional AI assistance

AI assistance may be provided through NVIDIA NIM, a local model such as
Ollama or LM Studio, or another OpenAI-compatible endpoint.

AI shall: - Be off by default. - Require explicit user consent before
submitted content is sent externally. - Be optional; core rule-based
analysis must work without it. - Have output validated against a
schema. - Never lower the rule-based score.

### FR-11: Metadata

The response shall include detector version and whether an external
check was used.

## 8. API requirements

### Endpoint

`POST /api/analyze`

### Request fields

  Field       Type     Required
  ----------- -------- ---------------------------------
  `text`      string   At least one of `text` or `url`
  `url`       string   At least one of `text` or `url`
  `options`   object   No

### Response fields

  Field               Type      Description
  ------------------- --------- --------------------------------------------
  `score`             integer   0--100
  `category`          string    low, medium, high, critical
  `indicators`        array     Structured detection evidence
  `recommendations`   array     Prioritized next steps
  `metadata`          object    Detector version and external-check status

### Error responses

  Status   Meaning
  -------- ----------------------------
  405      Wrong method
  413      Input too large
  415      Wrong content type
  422      Missing or malformed input
  500      Generic server error

Use one shared error response shape. Never expose internal paths, stack
traces, secrets, or versions in generic errors.

## 9. Non-functional requirements

### Security

-   Treat all input as untrusted.
-   Validate and length-limit input.
-   Do not open submitted URLs.
-   Do not download or execute files.
-   Protect secrets in environment variables.
-   Prevent prompt injection from being treated as trusted instructions.
-   Keep external AI processing opt-in.
-   Preserve SSRF protections for hosted configurable endpoints.

### Privacy

-   Submissions are not stored by default.
-   Do not log secrets or unnecessary submitted content.
-   Clearly disclose when AI processing sends content to a provider.
-   External checks must be optional and consent-based.

### Reliability

-   Baseline rule-based analysis must work without external services.
-   Optional integration failures must not disable core analysis.
-   API errors must use a consistent response format.

### Explainability

-   Each score contribution must map to a named indicator.
-   Evidence and explanation must be returned in structured form.
-   Do not present the score as a definitive verdict.

### Maintainability

-   Reuse functions.
-   Centralize constants and shared helpers.
-   Keep detection rules in data files where appropriate.
-   Prefer standard-library features where adequate.
-   Avoid unnecessary dependencies and abstractions.

## 10. User interface requirements

The Streamlit UI shall provide: - An input area for suspicious text. - A
URL input. - An Analyze action. - Clear validation and error states. - A
score and category display. - An indicator/evidence list. -
Recommendations. - A Learn section. - An optional AI consent flow if AI
is implemented.

Exact visual branding and layout are design decisions to be finalized
during implementation.

## 11. Success and acceptance criteria

The project is acceptable for its planned baseline when: - Text, URL,
and combined submissions are supported. - Score always stays within
0--100. - Category boundaries match the specified ranges. - Every score
contribution maps to a named indicator. - Overlapping signals are
grouped. - Legitimate examples generally remain low under the documented
rule set. - Representative obvious scams reach High or Critical under
the documented test cases. - Submitted URLs are never opened or
fetched. - Secrets are not committed. - The API contract and error
shapes are tested. - The UI displays the API's explanation and
recommendations. - Optional AI remains off by default and requires
consent.

These checks do not establish a measured detection accuracy rate. Any
accuracy claim requires a labelled dataset, documented methodology, and
reproducible evaluation.

## 12. Limitations

-   Rules may miss novel or reworded scams.
-   Non-English coverage is limited.
-   Low risk is not proof of safety.
-   URLs are not visited, so live page behavior is not assessed.
-   AI output can be wrong or vary between runs.
-   The system is an educational aid, not a definitive security verdict.

## 13. Roadmap

The planned sequence is: 1. Repository setup, README, and API contract.
2. UI skeleton with mock data. 3. API skeleton, schemas, validation, and
errors. 4. Text, URL, and app-lure rules plus scoring. 5. UI/API
integration. 6. Tests, security review, and optional AI. 7. Learn
section, polish, and demo.

Future work may include optional threat-intelligence lookups, wider
language coverage, trained classifiers after labelled data exists, and a
browser extension or share-sheet check.

## 14. Open decisions

The README does not yet specify: - Exact maximum input lengths. - Exact
indicator weights and overlap-grouping algorithm. - Exact recommendation
mapping. - Supported languages beyond the stated limited non-English
coverage. - Whether optional reputation checks will be included in the
first release. - Exact visual brand system. - Evaluation dataset and
performance targets.

These must be decided and documented before the related functionality is
treated as finalized.
