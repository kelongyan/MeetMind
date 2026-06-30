import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Check, Pencil, X } from "lucide-react";
import type { UpdateInsightPayload } from "../../api";
import { ReviewButton } from "../shared/review-button";

export function InsightReviewControls({
  disabled,
  item,
  onUpdate,
}: {
  disabled: boolean;
  item: { id: string; title: string; body: string; status: string };
  onUpdate: (insightId: string, payload: UpdateInsightPayload) => void;
}) {
  const [editOpen, setEditOpen] = useState(false);
  const [editTitle, setEditTitle] = useState(item.title);
  const [editBody, setEditBody] = useState(item.body);

  function openEdit() {
    setEditTitle(item.title);
    setEditBody(item.body);
    setEditOpen(true);
  }

  function saveEdit() {
    onUpdate(item.id, {
      title: editTitle.trim() || item.title,
      body: editBody.trim() || item.body,
    });
    setEditOpen(false);
  }

  return (
    <>
      <ReviewButton disabled={disabled} onClick={openEdit}>
        <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
        编辑
      </ReviewButton>
      {item.status !== "confirmed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "confirmed" })}
          tone="success"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
          确认
        </ReviewButton>
      ) : null}
      {item.status !== "dismissed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "dismissed" })}
          tone="danger"
        >
          <X className="h-3.5 w-3.5" aria-hidden="true" />
          忽略
        </ReviewButton>
      ) : null}

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑洞察</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="insight-title">标题</Label>
              <Input
                id="insight-title"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="insight-body">内容</Label>
              <Textarea
                id="insight-body"
                value={editBody}
                onChange={(e) => setEditBody(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>
              取消
            </Button>
            <Button onClick={saveEdit}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
