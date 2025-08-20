from fastapi import APIRouter, UploadFile, HTTPException, File

from pydantic import BaseModel, constr
from pathlib import Path
from typing import Annotated

router = APIRouter(prefix="/inputs")

SAVE_PATH_SERIAL = Path("serial_number.txt")
SAVE_PATH_JSON = Path("input_commands.json")


class SerialNumberInput(BaseModel):
    serial1: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    serial2: Annotated[str, constr(strip_whitespace=True, min_length=1)]

@router.post("/serial-numbers")
async def save_serial_numbers(payload: SerialNumberInput):
    if payload.serial1 != payload.serial2:
        raise HTTPException(status_code=400, detail="Serial numbers do not match")
    
    try:
        SAVE_PATH_SERIAL.write_text(f"{payload.serial1}\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save serial numbers: {str(e)}")
    return {
        "message": "Serial numbers saved successfully", 
        "serial_number": payload.serial1
        }

@router.post("/json-file")
async def receive_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        SAVE_PATH_JSON.write_bytes(contents)
        return {"message": f"File saved successfully as {SAVE_PATH_JSON.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))