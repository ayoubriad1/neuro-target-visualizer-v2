# AI Scientific Interpretation — design notes

This document describes the optional "AI Interpretation" feature
([`ai_agent.py`](../ai_agent.py) + [`ui_ai.py`](../ui_ai.py)): why it's built the
way it is, exactly what it does, and — just as important — what it does **not**
do. For end-user instructions, see the
[AI Interpretation section of the README](../README.md#ai-interpretation).

## What it is

A single, constrained LLM call — Claude via Anthropic, or ChatGPT via OpenAI,
the user's choice — that turns the regions and affinities currently selected in
the app into a short, readable interpretation covering:

1. The region's general, well-established function (textbook neuroscience).
2. A hypothesis (not a finding) about what the observed relative engagement
   might mean biologically.
3. Therapeutic relevance this class of engagement is typically associated with,
   in general terms.
4. Explicit limitations of the interpretation.
5. A mandatory confidence label (Low or Moderate — never High).

## What it is NOT

It is **not** literature-grounded retrieval-augmented generation (RAG). It does
not query PubMed, Semantic Scholar, or OpenAlex, and it will not produce real
citations, PMIDs, or DOIs — the system prompt explicitly forbids inventing them.

This is a deliberate scope cut from the larger design sketched in
[`ENHANCEMENT_REPORT.md`](../ENHANCEMENT_REPORT.md#roadmap-not-yet-implemented):
a full literature-retrieval + citation-verification pipeline is a multi-week
effort in its own right. Shipping a smaller, honestly-labeled version now was
judged more useful than promising rigor this version doesn't have.

## Bring-your-own-key (BYOK) — why

Any real LLM call costs money per request. This is a free, open-source local
tool; it should never obligate its maintainer, or any one user, to pay for
another user's API usage. Concretely:

- **No API key ships with the app**, and none is fetched from any server the
  maintainer controls.
- The sidebar lets each user paste their own Anthropic or OpenAI key, kept in
  that browser's Streamlit session only (`st.session_state`) — never written to
  disk, never logged.
- [`.env.example`](../.env.example) documents `ANTHROPIC_API_KEY` /
  `OPENAI_API_KEY` as an optional *prefill* convenience for a local deployment
  where the person running the app is also the one paying — the sidebar field
  is always visible and editable, and a key typed there always wins.
- Default models are the cheap/fast tier per provider
  (`claude-haiku-4-5-20251001`, `gpt-4o-mini`), not a frontier model,
  specifically so an accidental click stays cheap. Both fields are freely
  editable if a provider's model catalog moves on.
- The result is cached in `st.session_state` per exact
  `(region selection, provider, model)` combination, so moving a slider or
  switching view mode never silently triggers another paid call — only
  clicking **Generate AI interpretation** does.

## Anti-hallucination prompt design

The system prompt (`ai_agent._SYSTEM_PROMPT`) enforces, in this order:

1. **Structure** — function, biological hypothesis, therapeutic relevance,
   limitations, in that order, so the model doesn't wander into open-ended
   speculation.
2. **A hard ban on inventing studies, authors, PMIDs, or DOIs.** If literature
   directions are relevant, the model must name general topic areas to search
   (e.g. "PET studies of D2 receptor density in striatum"), never a fabricated
   reference.
3. **A hard ban on claiming measured results.** The whole app's input is
   user-entered, illustrative data — the model is told this explicitly and
   forbidden from describing its output as reflecting real receptor occupancy,
   in-vivo concentration, or any experimental finding.
4. **A mandatory confidence label** (Low or Moderate, never High), plus an
   explicit note whenever the model is extrapolating from generic pharmacology
   knowledge rather than region-specific evidence.
5. **A length cap** (350 words) to keep responses — and their cost —
   predictable.

This is a **prompt-level**, not a retrieval- or verification-level, safeguard.
It reduces the *rate* of fabricated specifics but cannot guarantee zero
hallucination the way a real citation-verification loop would (see "Future:
full RAG" below). That's exactly why the UI shows a standing disclaimer
("verify any claim against primary sources") rather than presenting the output
as vetted fact.

## Provider abstraction

`ai_agent.generate_interpretation(provider, api_key, model, prompt)` dispatches
to `_call_anthropic` or `_call_openai`. Both:

- Wrap every SDK-level exception (auth failure, rate limit, network error,
  malformed response) into a single `AIAgentError`, shown to the user via
  `st.error` — the UI never needs to know which provider raised what.
- Handle non-text response content defensively
  (`isinstance(block, anthropic.types.TextBlock)` for Claude,
  `content is not None` for OpenAI's `message.content`). These were **real
  mypy-caught bugs** during development: a tool-use block or an empty response
  would otherwise crash with an unhandled `AttributeError`/`TypeError` deep
  inside a Streamlit callback.

## Testing

[`tests/test_ai_agent.py`](../tests/test_ai_agent.py) mocks `anthropic.Anthropic`
and `openai.OpenAI` entirely — **no real network call happens in the test suite
or in CI**, so running `pytest` never costs money or requires a real key. It
covers:

- Prompt construction (atlas-backed vs. illustrative region labeling).
- The "no API key" and "unknown provider" error paths.
- Both providers' success response handling (including the real
  `anthropic.types.TextBlock` construction, not a mock stand-in).
- Both providers' SDK-error wrapping into `AIAgentError`.

## Future: full RAG

The larger version of this feature, sketched in `ENHANCEMENT_REPORT.md`, would
add:

- Retrieval from PubMed (NCBI E-utilities), Semantic Scholar, and OpenAlex.
- Grounding each claim in a retrieved passage with an inline citation.
- An entailment check verifying the citation actually supports the claim.
- A confidence score calibrated from source agreement, instead of the model's
  own self-report.

That is a substantially larger, separate engineering effort and was
intentionally out of scope for this pass.
