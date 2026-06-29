from __future__ import annotations

from app.providers.llm.base import LLMExtractionRequest, LLMExtractionResponse


class OpenAILLMExtractor:
    provider_name = "openai"

    def __init__(self, *, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def extract(self, request: LLMExtractionRequest) -> LLMExtractionResponse:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": _system_prompt(request.prompt_version),
                },
                {
                    "role": "user",
                    "content": _user_prompt(request),
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "meetmind_structured_extraction",
                    "schema": request.json_schema,
                    "strict": True,
                }
            },
        )
        return LLMExtractionResponse(
            content=response.output_text,
            model_name=self.model,
        )


def _system_prompt(prompt_version: str) -> str:
    return "\n".join(
        [
            "You extract structured meeting insights from transcript segments.",
            "Return only JSON that satisfies the provided schema.",
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
