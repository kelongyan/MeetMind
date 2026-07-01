from __future__ import annotations

import json

from app.providers.llm.base import LLMExtractionRequest, LLMExtractionResponse


class OpenAILLMExtractor:
    provider_name = "openai"

    def __init__(
        self, *, api_key: str, model: str, base_url: str | None = None
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def extract(self, request: LLMExtractionRequest) -> LLMExtractionResponse:
        from openai import OpenAI

        kwargs: dict[str, object] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        client = OpenAI(**kwargs)  # type: ignore[arg-type]

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": _system_prompt(request.prompt_version),
                },
                {
                    "role": "user",
                    "content": _user_prompt(request),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "meetmind_structured_extraction",
                    "schema": request.json_schema,
                    "strict": True,
                },
            },
        )

        content = _extract_content(response)
        return LLMExtractionResponse(
            content=content,
            model_name=self.model,
        )


def _extract_content(response: object) -> str:
    """Extract text content from a chat completion response.

    Handles reasoning models (e.g. LongCat-2.0) that place their output
    in ``reasoning_content`` instead of the standard ``content`` field.
    """
    message = response.choices[0].message  # type: ignore[index,union-attr]

    # Standard path: content is populated.
    content = getattr(message, "content", None)
    if content:
        return content

    # Reasoning model fallback: output lives in reasoning_content.
    reasoning = getattr(message, "reasoning_content", None)
    if reasoning:
        # Strip markdown code fences if present.
        text = reasoning.strip()
        if text.startswith("```"):
            first_newline = text.index("\n") if "\n" in text else 3
            text = text[first_newline + 1 :]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        return text

    # Last resort: serialise the whole message for debugging.
    return json.dumps(getattr(message, "model_dump", lambda: {})())


def _system_prompt(prompt_version: str) -> str:
    return "\n".join(
        [
            "You extract structured meeting insights from transcript segments.",
            "Return only JSON that satisfies the provided schema.",
            "Identify logical section boundaries based on topic shifts in the",
            "transcript. Each section should have a concise title and optional",
            "summary describing its content.",
            "Every decision, risk, open question, and action item must include at",
            "least one citation using an existing transcript segment_id.",
            "Do not invent owners, due dates, decisions, or facts that are not in",
            "the transcript.",
            f"Prompt version: {prompt_version}",
        ]
    )


def _user_prompt(request: LLMExtractionRequest) -> str:
    lines = [
        "Transcript segments:",
        *[
            (
                f"- segment_id={segment.segment_id} "
                f"time={segment.start_ms}-{segment.end_ms}ms "
                f"text={segment.text}"
            )
            for segment in request.transcript
        ],
    ]
    if request.retry_instruction:
        lines.extend(["", f"Retry instruction: {request.retry_instruction}"])
    return "\n".join(lines)
