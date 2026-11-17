# SafeClick --- Product and Technical Design

> Status: Proposed design derived from the README. Visual styling and
> interaction details below are implementation guidance, not claims
> about an existing UI.

## 1. Design goals

SafeClick should feel: - Clear: users can understand the result
quickly. - Calm: avoid panic-inducing language and unnecessary alarm. -
Explainable: show why a score was assigned. - Actionable: tell users
what to do next. - Accessible: readable on common desktop and mobile
screen sizes. - Privacy-conscious: explain when content leaves the
device for optional AI processing.

## 2. Main user journey

``` text
Home
  |
  v
Paste message and/or URL
  |
  v
Analyze
  |
  v
Loading state
  |
  +--> Validation/error state
  |
  v
Risk result
  |
  +--> Score and category
  +--> Indicators and evidence
  +--> Recommended next steps
  +--> Learn more
```

## 3. Screen structure

### Home / Analyzer

1.  Header: SafeClick name and short purpose statement.
2.  Input panel:
    -   Message text area.
    -   URL input.
    -   Helper text explaining that either field or both may be
        supplied.
3.  Optional AI control:
    -   Off by default.
    -   Clear explanation that submitted content may be sent to the
        selected model provider.
    -   Explicit consent before use.
4.  Primary action: Analyze.
5.  Privacy note: submitted URLs are analyzed without opening them.
6.  Learn section entry point.

### Results

1.  Overall score from 0 to 100.
2.  Risk category: Low, Medium, High, or Critical.
3.  Short plain-language interpretation.
4.  Indicator list:
    -   Indicator title.
    -   Threat family.
    -   Evidence found.
    -   Why it matters.
    -   Score contribution.
5.  Prioritized recommendations.
6.  Metadata, including detector version and whether an external check
    was used.
7.  Analyze another item action.

### Learn page

Use short, practical awareness guides for: - Phishing messages. -
Digital arrest scams. - Malicious application downloads. - Suspicious
URLs. - Verification habits and safe next steps.

Keep educational content concise and avoid reproducing harmful
instructions.

## 4. Risk presentation

  ------------------------------------------------------------------------
  Category                                     Score Suggested
                                                     presentation
  --------------------- ---------------------------- ---------------------
  Low                                          0--24 Neutral/green status;
                                                     explicitly say this
                                                     is not a safety
                                                     guarantee

  Medium                                      25--49 Amber status;
                                                     encourage independent
                                                     verification

  High                                        50--74 Orange status; advise
                                                     not to act until
                                                     verified

  Critical                                   75--100 Red status; strongly
                                                     advise against
                                                     clicking, paying,
                                                     installing, or
                                                     replying
  ------------------------------------------------------------------------

Do not use color alone to communicate risk. Always show the category
label and explanatory text.

Suggested copy: - Low: "Few risk signals were detected. This does not
guarantee the content is safe." - Medium: "Some suspicious signals were
found. Verify using a trusted channel." - High: "Several strong warning
signs were found. Do not act before verifying." - Critical: "A strong
scam pattern was detected. Do not click, pay, install, or reply."

## 5. Indicator design

Each indicator should answer: - What was detected? - Where was it
detected? - Why does it matter? - How much did it contribute to the
score?

Example presentation (illustrative only):

**Urgency pressure** - Family: Phishing - Evidence: A message demands
immediate action. - Explanation: Scammers may use time pressure to
prevent careful verification. - Contribution: Display the actual
configured contribution returned by the scorer.

Never invent evidence. If a detector cannot provide a reliable excerpt,
show a concise reason without fabricating a quote.

## 6. Interaction states

The UI should account for: - Empty input. - Invalid input. - Input too
long. - Analyzing. - Successful result. - No indicators detected. - API
unavailable. - Unexpected server error. - Optional AI unavailable. - AI
consent not granted.

Errors should be actionable and should not expose internal
implementation details.

## 7. Content and accessibility

-   Use plain language and define technical terms.
-   Keep text contrast high.
-   Use clear labels for inputs.
-   Ensure keyboard navigation for interactive controls.
-   Avoid relying on red/green color alone.
-   Use readable spacing and headings.
-   Keep warning messages direct, not sensational.
-   Do not describe a low score as "safe" or "verified."

## 8. Streamlit implementation guidance

-   Use native Streamlit widgets before custom components.
-   Reuse shared UI components for score badges and indicator/result
    cards.
-   Keep API communication in `ui/api_client.py`.
-   Keep theme values centralized in `ui/theme.py`.
-   Avoid duplicating backend detection logic in the UI.
-   Do not put secrets in UI source code.
-   Keep the UI responsive within Streamlit's supported layout
    capabilities.

## 9. Visual direction

A clean, trustworthy security-tool aesthetic is recommended: - Simple
layout. - Strong typographic hierarchy. - Restrained use of warning
colors. - Clear score visualization. - Minimal decoration. - No fake
security seals, guarantees, or claims of certification.

Exact brand colors, logo, typography, and component measurements have
not been specified in the README and should be decided during UI
implementation.
