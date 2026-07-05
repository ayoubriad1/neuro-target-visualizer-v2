from unittest.mock import MagicMock, patch

import pytest

from ai_agent import AIAgentError, build_user_prompt, generate_interpretation
from models import make_region_entry


def test_build_user_prompt_labels_atlas_and_illustrative():
    regions = [make_region_entry("Thalamus", -9.0), make_region_entry("Cerebellum", -3.0)]
    prompt = build_user_prompt(regions, {
        "Thalamus": "Harvard-Oxford subcortical",
        "Cerebellum": None,
    })
    assert "Thalamus" in prompt
    assert "atlas-backed (Harvard-Oxford subcortical)" in prompt
    assert "Cerebellum" in prompt
    assert "illustrative point (no atlas)" in prompt


def test_generate_interpretation_requires_api_key():
    with pytest.raises(AIAgentError, match="No API key"):
        generate_interpretation("Claude (Anthropic)", "", "claude-haiku-4-5-20251001", "prompt")


def test_generate_interpretation_unknown_provider():
    with pytest.raises(AIAgentError, match="Unknown provider"):
        generate_interpretation("Gemini", "fake-key", "some-model", "prompt")


def test_generate_interpretation_claude_wraps_sdk_errors():
    with patch("anthropic.Anthropic") as mock_client_cls:
        mock_client_cls.return_value.messages.create.side_effect = RuntimeError("401 unauthorized")
        with pytest.raises(AIAgentError, match="Anthropic API error"):
            generate_interpretation("Claude (Anthropic)", "bad-key", "claude-haiku-4-5-20251001", "prompt")


def test_generate_interpretation_claude_returns_text_block():
    import anthropic

    real_text_block = anthropic.types.TextBlock(text="This is a test interpretation.", type="text")
    with patch("anthropic.Anthropic") as mock_client_cls:
        mock_response = MagicMock()
        mock_response.content = [real_text_block]
        mock_client_cls.return_value.messages.create.return_value = mock_response
        result = generate_interpretation(
            "Claude (Anthropic)", "fake-key", "claude-haiku-4-5-20251001", "prompt"
        )
        assert result == "This is a test interpretation."


def test_generate_interpretation_openai_wraps_sdk_errors():
    with patch("openai.OpenAI") as mock_client_cls:
        mock_client_cls.return_value.chat.completions.create.side_effect = RuntimeError("bad key")
        with pytest.raises(AIAgentError, match="OpenAI API error"):
            generate_interpretation("ChatGPT (OpenAI)", "bad-key", "gpt-4o-mini", "prompt")


def test_generate_interpretation_openai_returns_content():
    with patch("openai.OpenAI") as mock_client_cls:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="A test reply."))]
        mock_client_cls.return_value.chat.completions.create.return_value = mock_response
        result = generate_interpretation("ChatGPT (OpenAI)", "fake-key", "gpt-4o-mini", "prompt")
        assert result == "A test reply."
