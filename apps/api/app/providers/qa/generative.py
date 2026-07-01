from __future__ import annotations

import json

from app.providers.qa.base import (
    AnswerEvidence,
    AnswerSynthesisRequest,
    AnswerSynthesisResponse,
)

_SYSTEM_PROMPT = (
    "你是 MeetMind 会议助手，根据提供的会议证据回答用户问题。\n"
    "规则：\n"
    "1. 只使用提供的证据回答问题，不要编造信息。\n"
    "2. 在回答末尾列出引用的证据编号，格式：[引用: 编号1, 编号2]。\n"
    "3. 如果证据不足以回答问题，明确告知用户。\n"
    "4. 回答简洁、准确、结构化。"
)


class LLMAnswerSynthesizer:
    """Generative answer synthesizer using an OpenAI-compatible LLM."""

    provider_name = "llm"

    def __init__(self, *, api_key: str, model: str, base_url: str | None = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def synthesize(self, request: AnswerSynthesisRequest) -> AnswerSynthesisResponse:
        if not request.evidence:
            return AnswerSynthesisResponse(
                content="证据不足，无法根据当前会议内容回答这个问题。",
                selected_evidence_ids=[],
                model_name=self.model,
            )

        from openai import OpenAI

        kwargs: dict[str, object] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        client = OpenAI(**kwargs)  # type: ignore[arg-type]

        user_content = _build_user_prompt(request)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )

        content = _extract_content(response)
        selected_ids = _parse_cited_ids(content, request.evidence)

        return AnswerSynthesisResponse(
            content=content,
            selected_evidence_ids=selected_ids,
            model_name=self.model,
        )


def _build_user_prompt(request: AnswerSynthesisRequest) -> str:
    evidence_lines: list[str] = []
    for item in request.evidence:
        evidence_lines.append(
            f"[编号: {item.id}] "
            f"(类型: {item.source_type}, 相关度: {item.score:.2f})\n"
            f"  内容: {item.source_text}\n"
            f"  引用: {item.quote}"
        )
    return "\n\n".join(
        [
            f"问题：{request.question}",
            "",
            "相关证据：",
            *evidence_lines,
        ]
    )


def _extract_content(response: object) -> str:
    """Extract text from chat completion, with reasoning-model fallback."""
    message = response.choices[0].message  # type: ignore[index,union-attr]

    content = getattr(message, "content", None)
    if content:
        return content

    # Reasoning model fallback (e.g. LongCat-2.0).
    reasoning = getattr(message, "reasoning_content", None)
    if reasoning:
        text = reasoning.strip()
        if text.startswith("```"):
            first_newline = text.index("\n") if "\n" in text else 3
            text = text[first_newline + 1 :]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        return text

    return json.dumps(getattr(message, "model_dump", lambda: {})())


def _parse_cited_ids(content: str, evidence: list[AnswerEvidence]) -> list[str]:
    """Extract evidence IDs that the LLM cited in its response."""
    {item.id for item in evidence}
    cited: list[str] = []
    for item in evidence:
        # Match by full ID substring in the response text.
        if item.id in content:
            cited.append(item.id)

    # If the LLM didn't cite anything explicitly, cite the top evidence.
    if not cited and evidence:
        cited.append(evidence[0].id)

    return cited
