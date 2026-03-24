from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class LocalStorageService:
    def __init__(self) -> None:
        self.base_path = Path(settings.storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, upload_file: UploadFile) -> tuple[str, int]:
        extension = Path(upload_file.filename or "").suffix
        stored_name = f"{uuid4()}{extension}"
        target_path = self.base_path / stored_name

        content = upload_file.file.read()
        target_path.write_bytes(content)
        return stored_name, len(content)

    def get_path(self, stored_name: str) -> Path:
        return self.base_path / stored_name

    def delete(self, stored_name: str) -> None:
        path = self.get_path(stored_name)
        if path.exists():
            path.unlink()