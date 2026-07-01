from __future__ import annotations

from app.providers.qa.base import (
    AnswerSynthesisRequest,
    AnswerSynthesisResponse,
)

REFUSAL_MESSAGE = "证据不足，无法根据当前会议内容回答这个问题。"

_MAX_EVIDENCE = 3


class ExtractiveAnswerSynthesizer:
    provider_name = "extractive"
    model_name = "extractive-v2"

    def synthesize(self, request: AnswerSynthesisRequest) -> AnswerSynthesisResponse:
        if not request.evidence:
            return AnswerSynthesisResponse(
                content=REFUSAL_MESSAGE,
                selected_evidence_ids=[],
                model_name=self.model_name,
            )

        top_k = request.evidence[:_MAX_EVIDENCE]
        parts: list[str] = []
        selected_ids: list[str] = []

        # Group evidence by source type for structured presentation.
        action_items = [e for e in top_k if e.source_type == "action_item"]
        insights = [e for e in top_k if e.source_type == "insight_item"]
        transcript = [
            e for e in top_k if e.source_type not in ("action_item", "insight_item")
        ]

        if action_items:
            lines = ["待办事项："]
            for item in action_items:
                owner = item.metadata.get("owner_text")
                due = item.metadata.get("due_text") or item.metadata.get("due_date")
                owner_text = f"（{owner}）" if isinstance(owner, str) and owner else ""
                due_text = (
                    f"，截止：{due}" if isinstance(due, str) and due.strip() else ""
                )
                lines.append(f"  • {item.source_text}{owner_text}{due_text}")
                selected_ids.append(item.id)
            parts.append("\n".join(lines))

        if insights:
            lines = ["会议要点："]
            for item in insights:
                title = item.metadata.get("title") or item.source_text
                lines.append(f"  • {title}：{item.quote}")
                selected_ids.append(item.id)
            parts.append("\n".join(lines))

        if transcript:
            lines = ["会议记录原文："]
            for item in transcript:
                lines.append(f"  • {item.quote}")
                selected_ids.append(item.id)
            parts.append("\n".join(lines))

        # Fallback: if somehow no items matched known types, use all evidence.
        if not parts:
            for item in top_k:
                parts.append(item.quote or item.source_text)
                selected_ids.append(item.id)

        content = "\n\n".join(parts)
        return AnswerSynthesisResponse(
            content=content,
            selected_evidence_ids=selected_ids,
            model_name=self.model_name,
        )
