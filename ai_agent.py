"""Optional, provider-agnostic LLM client for the AI scientific-interpretation
feature. Bring-your-own-key: the app never bundles or pays for API access —
the user supplies their own Anthropic or OpenAI key (entered in the sidebar,
kept session-only, or via environment variable as a prefill convenience).

This is a single constrained LLM call, NOT literature-grounded RAG (see
ENHANCEMENT_REPORT.md for that larger, PubMed/Semantic Scholar/OpenAlex-backed
proposal). It's restricted to general neuropharmacology knowledge and
explicitly forbidden from inventing citations — clearly labeled as such in
the UI so it's never mistaken for a literature review.
"""
from models import RegionEntry

PROVIDERS = ["Claude (Anthropic)", "ChatGPT (OpenAI)"]

# Sensible cheap/fast defaults so a casual user doesn't accidentally burn
# frontier-model prices on a short interpretation. Both fields are editable
# in the UI - check your provider's current model catalog if a name goes stale.
DEFAULT_MODELS = {
    "Claude (Anthropic)": "claude-haiku-4-5-20251001",
    "ChatGPT (OpenAI)": "gpt-4o-mini",
}

_SYSTEM_PROMPT = """\
You are assisting a neuroscience researcher in interpreting output from an \
illustrative visualization tool - not a docking engine or a literature database. \
Binding-affinity values are manually entered by the user; they are NOT measured, \
NOT from a docking simulation, and NOT retrieved from any paper.

For each region provided, briefly cover:
1. The region's general, well-established function (textbook neuroscience knowledge only).
2. What it would plausibly mean, biologically, if a ligand engaged this region at the \
given relative strength - phrased as a hypothesis, not a finding.
3. Therapeutic relevance this class of engagement is typically associated with, in general terms.
4. Explicit limitations of this specific interpretation.

Hard constraints - do not violate these:
- Never invent, cite, or imply a specific study, paper, author, PMID, or DOI. If literature \
directions are relevant, name general topic areas to search (e.g. "PET studies of D2 receptor \
density in striatum"), never a fabricated reference.
- Never claim this reflects measured receptor occupancy, in-vivo concentration, or any real \
experimental result.
- State a confidence level (Low or Moderate - never High, since none of this is measured data), \
and say explicitly when you are extrapolating from general knowledge rather than region-specific \
evidence.
- Keep the entire response under 350 words, in Markdown.
"""


class AIAgentError(RuntimeError):
    """Raised for any user-facing failure (missing SDK, bad key, API error)."""


def build_user_prompt(regions: list[RegionEntry], atlas_sources: dict[str, str | None]) -> str:
    lines = ["Selected regions and user-entered affinities:"]
    for r in regions:
        source = atlas_sources.get(r.name)
        provenance = f"atlas-backed ({source})" if source else "illustrative point (no atlas)"
        lines.append(
            f"- {r.name}: {r.kcal:.1f} kcal/mol ({r.normalized_intensity:.0f}% normalized "
            f"intensity), region model: {provenance}"
        )
    return "\n".join(lines)


def _call_anthropic(api_key: str, model: str, user_prompt: str) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise AIAgentError(
            "The 'anthropic' package isn't installed. Run: pip install anthropic"
        ) from e
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=700,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        block = response.content[0]
        if not isinstance(block, anthropic.types.TextBlock):
            raise AIAgentError("Unexpected response format from the Anthropic API "
                               "(non-text content block).")
        return block.text
    except AIAgentError:
        raise
    except Exception as e:
        raise AIAgentError(f"Anthropic API error: {e}") from e


def _call_openai(api_key: str, model: str, user_prompt: str) -> str:
    try:
        import openai
    except ImportError as e:
        raise AIAgentError(
            "The 'openai' package isn't installed. Run: pip install openai"
        ) from e
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            max_tokens=700,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        if content is None:
            raise AIAgentError("OpenAI API returned an empty response.")
        return content
    except AIAgentError:
        raise
    except Exception as e:
        raise AIAgentError(f"OpenAI API error: {e}") from e


def generate_interpretation(provider: str, api_key: str, model: str, user_prompt: str) -> str:
    if not api_key:
        raise AIAgentError("No API key provided.")
    if provider == "Claude (Anthropic)":
        return _call_anthropic(api_key, model, user_prompt)
    if provider == "ChatGPT (OpenAI)":
        return _call_openai(api_key, model, user_prompt)
    raise AIAgentError(f"Unknown provider: {provider}")
