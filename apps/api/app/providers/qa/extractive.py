from __future__ import annotations

from app.providers.qa.base import (
    AnswerSynthesisRequest,
    AnswerSynthesisResponse,
)

REFUSAL_MESSAGE = "证据不足，无法根据当前会议内容回答这个问题。"


class ExtractiveAnswerSynthesizer:
    provider_name = "extractive"
    model_name = "extractive-v1"

    def synthesize(
        self, request: AnswerSynthesisRequest
    ) -> AnswerSynthesisResponse:
        if not request.evidence:
            return AnswerSynthesisResponse(
                content=REFUSAL_MESSAGE,
                selected_evidence_ids=[],
                model_name=self.model_name,
            )

        top = request.evidence[0]
        owner = top.metadata.get("owner_text")
        due = top.metadata.get("due_text") or top.metadata.get("due_date")
        if isinstance(owner, str) and owner.strip():
            due_text = f"，截止/时间：{due}" if isinstance(due, str) and due else ""
            content = f"{owner} 负责：{top.source_text}{due_text}。"
        else:
            content = f"根据会议记录：{top.quote}"

        return AnswerSynthesisResponse(
            content=content,
            selected_evidence_ids=[top.id],
            model_name=self.model_name,
        )
