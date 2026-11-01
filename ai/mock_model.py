"""A genuine Strands custom model provider backed by canned responses.

``MockModel`` extends :class:`strands.models.Model` so the three Thiran AI
agents are real ``strands.Agent`` instances driven by the Strands agent loop.
It does *not* bypass the SDK: the agent loop calls :meth:`MockModel.stream`
and consumes the ``StreamEvent`` dicts it yields, exactly as it would for a
Bedrock- or Gemini-backed model.

The implementation targets the installed Strands SDK (v1.63.0). All abstract
methods of ``Model`` are implemented: ``stream``, ``structured_output``,
``get_config``, ``update_config``.
"""

from __future__ import annotations

import json
import re
from typing import Any, AsyncGenerator, AsyncIterable, Optional, TypedDict, TypeVar

from strands.models import Model
from strands.types.content import Messages
from strands.types.streaming import StreamEvent

from .mock_responses import (
    CATEGORY_KEYWORDS,
    DIFFICULTY_KEYWORDS,
    INTENT_KEYWORDS,
    LANGUAGE_KEYWORDS,
    get_response,
)

T = TypeVar("T")

# Default per-request language when the prompt gives no language hint and the
# model was constructed without one.
_DEFAULT_LANGUAGE = "english"


class MockModel(Model):
    """Deterministic, language-aware mock model for Strands agents."""

    class ModelConfig(TypedDict, total=False):
        """Configuration for the mock model.

        Attributes:
            model_id: Identifier for this provider.
            language: Default response language ("english"/"tamil"/"tanglish").
            chunk_words: Words per streamed text delta (light streaming).
            params: Optional free-form parameters, for parity with real
                providers.
        """

        model_id: str
        language: str
        chunk_words: int
        params: Optional[dict[str, Any]]

    def __init__(self, **model_config: Any) -> None:
        """Initialize the mock model.

        Args:
            **model_config: Overrides for :class:`ModelConfig`. ``language``
                sets the default response language; ``chunk_words`` controls
                the streaming granularity (defaults to 4 words per delta).
        """
        self.config: MockModel.ModelConfig = {
            "model_id": "thiran-mock",
            "language": _DEFAULT_LANGUAGE,
            "chunk_words": 4,
            "params": None,
        }
        self.config.update(model_config)  # type: ignore[typeddict-item]

    # -- configuration accessors (abstract) --------------------------------

    def update_config(self, **model_config: Any) -> None:
        """Update the model configuration in place."""
        self.config.update(model_config)  # type: ignore[typeddict-item]

    def get_config(self) -> "MockModel.ModelConfig":
        """Return the current model configuration."""
        return self.config

    # -- intent / parameter inference --------------------------------------

    @staticmethod
    def _latest_user_text(messages: Messages) -> str:
        """Concatenate text from the most recent user message."""
        for message in reversed(messages):
            if message.get("role") != "user":
                continue
            parts: list[str] = []
            for block in message.get("content", []):
                if isinstance(block, dict) and "text" in block:
                    parts.append(str(block["text"]))
            if parts:
                return " ".join(parts)
        return ""

    @staticmethod
    def _classify(text: str, keyword_map: dict[str, tuple[str, ...]], default: str) -> str:
        """Return the first key whose keywords appear in ``text``."""
        lowered = text.lower()
        for key, keywords in keyword_map.items():
            if any(kw in lowered for kw in keywords):
                return key
        return default

    def _select_text(
        self, messages: Messages, system_prompt: Optional[str]
    ) -> str:
        """Pick a deterministic canned response for the request.

        The intent, category, and difficulty are inferred primarily from the
        system prompt (which the agents set), with the latest user message as
        a secondary signal. Language defaults to the configured language but a
        prompt-level language hint overrides it.
        """
        prompt_text = " ".join(filter(None, [system_prompt or "", self._latest_user_text(messages)]))

        intent = self._classify(prompt_text, INTENT_KEYWORDS, "question")
        category = self._classify(prompt_text, CATEGORY_KEYWORDS, "software")
        difficulty = self._classify(prompt_text, DIFFICULTY_KEYWORDS, "beginner")
        language = self._classify(
            prompt_text, LANGUAGE_KEYWORDS, self.config.get("language", _DEFAULT_LANGUAGE)
        )

        return get_response(intent, category, difficulty, language)

    # -- streaming (abstract) ----------------------------------------------

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[Any] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: Any | None = None,
        system_prompt_content: list[Any] | None = None,
        invocation_state: dict[str, Any] | None = None,
        cancel_signal: Any | None = None,
        agent_metadata: Any | None = None,
        structured_output_model: type[Any] | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamEvent]:
        """Yield a well-formed Strands event stream for the canned response.

        The signature mirrors ``strands.models.Model.stream`` in v1.63.0 so
        this is a true override. The method emits, in order: ``messageStart``,
        ``contentBlockStart``, one ``contentBlockDelta`` per word-chunk,
        ``contentBlockStop``, ``messageStop`` (``end_turn``), and a final
        ``metadata`` event carrying valid ``usage`` and ``metrics``.

        On the agent's forced structured-output turn, the structured-output
        tool is present in ``tool_specs``. The mock then emits a ``toolUse``
        content block whose ``input`` is the canned content shaped to the
        tool's schema, which the SDK validates via its structured-output tool.
        """
        text = self._select_text(messages, system_prompt)

        struct_tool = self._find_structured_output_tool(tool_specs)
        if struct_tool is not None:
            async for event in self._stream_tool_use(struct_tool, text, messages, system_prompt):
                yield event
            return

        input_tokens = self._estimate_tokens(messages, system_prompt)
        output_tokens = self._estimate_tokens_from_text(text)

        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockStart": {"contentBlockIndex": 0, "start": {}}}

        for chunk in self._chunk_text(text):
            yield {
                "contentBlockDelta": {
                    "contentBlockIndex": 0,
                    "delta": {"text": chunk},
                }
            }

        yield {"contentBlockStop": {"contentBlockIndex": 0}}
        yield {"messageStop": {"stopReason": "end_turn"}}
        yield {
            "metadata": {
                "usage": {
                    "inputTokens": input_tokens,
                    "outputTokens": output_tokens,
                    "totalTokens": input_tokens + output_tokens,
                },
                "metrics": {"latencyMs": 0},
            }
        }

    async def _stream_tool_use(
        self,
        tool_spec: dict[str, Any],
        text: str,
        messages: Messages,
        system_prompt: Optional[str],
    ) -> AsyncIterable[StreamEvent]:
        """Emit a tool-use stream that satisfies the structured-output tool.

        The tool input is built from the tool's JSON input schema, filling
        string fields with the canned ``text`` and other fields with
        type-appropriate placeholders.
        """
        tool_name = tool_spec.get("name", "StructuredOutputTool")
        tool_input = self._input_from_schema(tool_spec.get("inputSchema"), text)

        input_tokens = self._estimate_tokens(messages, system_prompt)
        payload = json.dumps(tool_input, ensure_ascii=False)
        output_tokens = self._estimate_tokens_from_text(payload)

        yield {"messageStart": {"role": "assistant"}}
        yield {
            "contentBlockStart": {
                "contentBlockIndex": 0,
                "start": {"toolUse": {"name": tool_name, "toolUseId": "mock-structured-1"}},
            }
        }
        yield {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": payload}},
            }
        }
        yield {"contentBlockStop": {"contentBlockIndex": 0}}
        yield {"messageStop": {"stopReason": "tool_use"}}
        yield {
            "metadata": {
                "usage": {
                    "inputTokens": input_tokens,
                    "outputTokens": output_tokens,
                    "totalTokens": input_tokens + output_tokens,
                },
                "metrics": {"latencyMs": 0},
            }
        }

    @staticmethod
    def _find_structured_output_tool(
        tool_specs: list[Any] | None,
    ) -> Optional[dict[str, Any]]:
        """Return the structured-output tool spec if the agent provided one.

        The structured-output tool is identified by its JSON input schema; any
        single tool the agent forces on a structured turn is treated as the
        target. Returns None when no tools are supplied (normal turns).
        """
        if not tool_specs:
            return None
        for spec in tool_specs:
            if isinstance(spec, dict) and spec.get("inputSchema"):
                return spec
        return None

    def _input_from_schema(
        self, input_schema: Any, text: str
    ) -> dict[str, Any]:
        """Build a tool-input dict from a JSON Schema, filling placeholders."""
        schema: dict[str, Any] = {}
        if isinstance(input_schema, dict):
            # ToolSpec inputSchema is typically {"json": {<schema>}}.
            schema = input_schema.get("json", input_schema)
        properties = schema.get("properties", {}) if isinstance(schema, dict) else {}

        values: dict[str, Any] = {}
        for name, prop in properties.items():
            json_type = prop.get("type") if isinstance(prop, dict) else None
            values[name] = self._placeholder_for_json_type(json_type, text)
        return values

    @staticmethod
    def _placeholder_for_json_type(json_type: Any, text: str) -> Any:
        """Return a placeholder value for a JSON Schema type."""
        if json_type == "string":
            return text
        if json_type == "integer":
            match = re.search(r"\d+", text)
            return int(match.group()) if match else 7
        if json_type == "number":
            return 7.0
        if json_type == "boolean":
            return True
        if json_type == "array":
            return [text]
        if json_type == "object":
            return {"text": text}
        return text

    # -- structured output (abstract) --------------------------------------

    async def structured_output(
        self,
        output_model: type[T],
        prompt: Messages,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Produce a schema-validated response from canned content.

        Mirrors the SDK convention: stream model events, then yield a final
        ``{"output": <instance>}`` event whose value validates against
        ``output_model``.
        """
        async for event in self.stream(
            prompt, system_prompt=system_prompt, structured_output_model=output_model, **kwargs
        ):
            yield {"event": event}

        text = self._select_text(prompt, system_prompt)
        instance = self._build_model_instance(output_model, text)
        yield {"output": instance}

    # -- helpers -----------------------------------------------------------

    def _chunk_text(self, text: str) -> list[str]:
        """Split ``text`` into light word-based chunks for streaming.

        Whitespace is preserved by re-joining with single spaces and keeping a
        trailing space on all but the final chunk, so the reassembled text
        reads naturally.
        """
        words = text.split()
        if not words:
            return [text]
        size = max(1, int(self.config.get("chunk_words", 4) or 4))
        chunks: list[str] = []
        for i in range(0, len(words), size):
            piece = " ".join(words[i : i + size])
            if i + size < len(words):
                piece += " "
            chunks.append(piece)
        return chunks

    @staticmethod
    def _estimate_tokens_from_text(text: str) -> int:
        """Cheap character-based token estimate (~4 chars/token)."""
        return max(1, len(text) // 4)

    def _estimate_tokens(self, messages: Messages, system_prompt: Optional[str]) -> int:
        """Estimate input tokens from messages plus the system prompt."""
        total = len(system_prompt or "")
        for message in messages:
            for block in message.get("content", []):
                if isinstance(block, dict) and "text" in block:
                    total += len(str(block["text"]))
        return max(1, total // 4)

    @staticmethod
    def _build_model_instance(output_model: type[T], text: str) -> T:
        """Construct a Pydantic ``output_model`` instance from canned text.

        String fields receive the canned text; other field types receive a
        type-appropriate placeholder. This keeps structured output working in
        mock mode without a real LLM. Falls back gracefully if field metadata
        is unavailable.
        """
        fields = getattr(output_model, "model_fields", None)
        if not fields:
            # Not a Pydantic v2 model we can introspect; try a best effort.
            try:
                return output_model()  # type: ignore[call-arg]
            except Exception:  # noqa: BLE001 - last-resort placeholder path
                return output_model.__new__(output_model)  # type: ignore[misc]

        values: dict[str, Any] = {}
        for name, field in fields.items():
            annotation = getattr(field, "annotation", str)
            values[name] = MockModel._placeholder_for(annotation, text)
        return output_model(**values)  # type: ignore[call-arg]

    @staticmethod
    def _placeholder_for(annotation: Any, text: str) -> Any:
        """Return a value appropriate to a field's annotation."""
        origin = getattr(annotation, "__name__", str(annotation)).lower()
        if annotation is str or "str" in origin:
            return text
        if annotation is int or "int" in origin:
            # Extract a leading integer from the text if present, else a score.
            match = re.search(r"\d+", text)
            return int(match.group()) if match else 7
        if annotation is float or "float" in origin:
            return 7.0
        if annotation is bool or "bool" in origin:
            return True
        if "list" in origin:
            return [text]
        if "dict" in origin:
            return {"text": text}
        return text
