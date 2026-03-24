from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import StoredFile, User
from app.schemas.files import FileResponse
from app.services.storage import LocalStorageService


router = APIRouter(prefix="/files", tags=["files"])
storage = LocalStorageService()


@router.post("/upload", response_model=FileResponse)
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stored_name, size = storage.save(file)

    db_file = StoredFile(
        owner_id=current_user.id,
        original_name=file.filename or stored_name,
        stored_name=stored_name,
        content_type=file.content_type,
        size=size,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.get("", response_model=list[FileResponse])
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(StoredFile).filter(StoredFile.owner_id == current_user.id).order_by(StoredFile.id.desc()).all()


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = db.query(StoredFile).filter(
        StoredFile.id == file_id,
        StoredFile.owner_id == current_user.id,
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    path = storage.get_path(db_file.stored_name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")

    return FastAPIFileResponse(path=path, filename=db_file.original_name, media_type=db_file.content_type)


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = db.query(StoredFile).filter(
        StoredFile.id == file_id,
        StoredFile.owner_id == current_user.id,
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    storage.delete(db_file.stored_name)
    db.delete(db_file)
    db.commit()
    return {"message": "File deleted"}