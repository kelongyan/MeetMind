from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
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

        relative_path = storage_uri.removeprefix("local://")
        target = (self.root / relative_path).resolve()
        root = self.root.resolve()
        if root not in target.parents:
            return

        target.unlink(missing_ok=True)
