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
import { Check, Pencil, Play, X } from "lucide-react";
import type { UpdateActionItemPayload } from "../../api";
import { ReviewButton } from "../shared/review-button";

const REVIEWER_USER_ID = "local-user";

export function ActionReviewControls({
  disabled,
  item,
  onUpdate,
}: {
  disabled: boolean;
  item: { id: string; title: string; ownerText?: string | null; dueText?: string | null; status: string };
  onUpdate: (actionItemId: string, payload: UpdateActionItemPayload) => void;
}) {
  const [editOpen, setEditOpen] = useState(false);
  const [editDescription, setEditDescription] = useState(item.title);
  const [editOwner, setEditOwner] = useState(item.ownerText ?? "");
  const [editDue, setEditDue] = useState(item.dueText ?? "");

  function openEdit() {
    setEditDescription(item.title);
    setEditOwner(item.ownerText ?? "");
    setEditDue(item.dueText ?? "");
    setEditOpen(true);
  }

  function saveEdit() {
    onUpdate(item.id, {
      description: editDescription.trim() || item.title,
      owner_text: editOwner.trim() || null,
      due_text: editDue.trim() || null,
    });
    setEditOpen(false);
  }

  const status = item.status;

  return (
    <>
      <ReviewButton disabled={disabled} onClick={openEdit}>
        <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
        编辑
      </ReviewButton>
      {status === "proposed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() =>
            onUpdate(item.id, {
              status: "confirmed",
              confirmed_by_user_id: REVIEWER_USER_ID,
            })
          }
          tone="success"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
          确认
        </ReviewButton>
      ) : null}
      {status === "confirmed" ? (
        <ReviewButton disabled={disabled} onClick={() => onUpdate(item.id, { status: "in_progress" })}>
          <Play className="h-3.5 w-3.5" aria-hidden="true" />
          开始
        </ReviewButton>
      ) : null}
      {status === "confirmed" || status === "in_progress" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "done" })}
          tone="success"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
          完成
        </ReviewButton>
      ) : null}
      {status !== "done" && status !== "canceled" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "canceled" })}
          tone="danger"
        >
          <X className="h-3.5 w-3.5" aria-hidden="true" />
          取消
        </ReviewButton>
      ) : null}

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑行动项</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="action-description">描述</Label>
              <Textarea
                id="action-description"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="action-owner">负责人</Label>
              <Input
                id="action-owner"
                value={editOwner}
                onChange={(e) => setEditOwner(e.target.value)}
                placeholder="例如：张三"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="action-due">截止时间</Label>
              <Input
                id="action-due"
                value={editDue}
                onChange={(e) => setEditDue(e.target.value)}
                placeholder="例如：2026-07-15"
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
