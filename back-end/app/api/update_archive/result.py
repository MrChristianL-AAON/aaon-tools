from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import datetime

router = APIRouter(prefix="/builder", tags=["builder"])

OUTPUT_DIR = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/output_files")
async def list_output_files():
    """
    Returns a list of files in the _output folder.
    """
    files = []
    for folder in OUTPUT_DIR.iterdir():
        if folder.is_dir():
            for f in folder.iterdir():
                if f.is_file():
                    files.append(str(f.relative_to(OUTPUT_DIR)))
    return {"files": files}

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """
    Downloads a specific file inside _output.
    `file_path` should be relative to OUTPUT_DIR, e.g. "commands_20250829/file1.update"
    """
    full_path = OUTPUT_DIR / file_path

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=full_path,
        filename=full_path.name,
        media_type="application/octet-stream"
    )
