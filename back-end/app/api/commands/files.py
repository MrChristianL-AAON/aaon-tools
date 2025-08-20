from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse

import shutil

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = f"uploaded_{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "message": f"File saved to {save_path}"}

@router.get("/command/{filename}}")
async def download_file(filename: str):
    file_path = f"uploaded_{filename}"
    return FileResponse(path=file_path, filename=filename)