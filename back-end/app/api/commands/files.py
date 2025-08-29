from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from pathlib import Path
import shutil

import datetime

router = APIRouter()

commands_dir = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/commands")

UPLOAD_DIR = commands_dir / "json"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = commands_dir / "_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "message": f"File saved to {save_path}"}

@router.get("/command")
async def list_files():
    files = [f.name for f in OUTPUT_DIR.iterdir() if f.is_file()]
    return {"files": files}


@router.get("/command/{filename}")
async def download_file(filename: str):
    yyyymmdd = datetime.datetime.now().strftime("%Y%m%d")
    folder_name = f"commands_{yyyymmdd}"
    file_name = f"Stratus_{yyyymmdd}.command"
    
    file_path = OUTPUT_DIR / folder_name / file_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename)

