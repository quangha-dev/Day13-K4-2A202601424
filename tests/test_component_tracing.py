from __future__ import annotations

from app.mock_llm import FakeLLM
from app.mock_rag import retrieve


def test_rag_retrieve_is_wrapped_as_an_observed_component() -> None:
    assert hasattr(retrieve, "__wrapped__")


def test_llm_generate_is_wrapped_as_an_observed_component() -> None:
    assert hasattr(FakeLLM.generate, "__wrapped__")
