from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from shutil import rmtree
from uuid import UUID, uuid4

from fastapi import UploadFile


@dataclass(frozen=True)
class StoredUpload:
    storage_uri: str
    sha256: str
    size_bytes: int
    created: bool


class LocalObjectStorage:
    def __init__(self, root: str) -> None:
        self.root = Path(root)

    async def save_upload(
        self, meeting_id: UUID, upload: UploadFile, suffix: str
    ) -> StoredUpload:
        temp_dir = self.root / "_tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"{uuid4().hex}.upload"
        digest = sha256()
        size_bytes = 0

        with temp_path.open("wb") as handle:
            while chunk := await upload.read(1024 * 1024):
                size_bytes += len(chunk)
                digest.update(chunk)
                handle.write(chunk)

        sha = digest.hexdigest()
        target_dir = self.root / str(meeting_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{sha}{suffix}"
        created = not target_path.exists()
        if created:
            temp_path.replace(target_path)
        else:
            temp_path.unlink(missing_ok=True)

        return StoredUpload(
            storage_uri=f"local://{meeting_id}/{sha}{suffix}",
            sha256=sha,
            size_bytes=size_bytes,
            created=created,
        )

    def delete_uri(self, storage_uri: str) -> None:
        if not storage_uri.startswith("local://"):
            return

        target = self.path_for_uri(storage_uri)
        target.unlink(missing_ok=True)

    def delete_meeting(self, meeting_id: UUID) -> None:
        target = self._safe_child_path(str(meeting_id))
        rmtree(target, ignore_errors=True)

    def path_for_uri(self, storage_uri: str) -> Path:
        if not storage_uri.startswith("local://"):
            raise ValueError("Only local:// storage URIs are supported")

        relative_path = storage_uri.removeprefix("local://")
        return self._safe_child_path(relative_path)

    def _safe_child_path(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        root = self.root.resolve()
        if root not in target.parents:
            raise ValueError("Storage URI escapes the configured root")
        return target
