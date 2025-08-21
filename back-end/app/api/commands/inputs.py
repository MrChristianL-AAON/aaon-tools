from fastapi import APIRouter, UploadFile, HTTPException, File

from pydantic import BaseModel, constr
from pathlib import Path
from typing import Annotated

import os

router = APIRouter(prefix="/inputs")

commands_dir = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/commands")

SAVE_PATH_SERIAL = commands_dir / "_output" / "serial_number.txt"
SAVE_PATH_SERIAL.parent.mkdir(parents=True, exist_ok=True)

SAVE_PATH_JSON = commands_dir / "json" / "commands.json"
SAVE_PATH_JSON.parent.mkdir(parents=True, exist_ok=True)


class SerialNumberInput(BaseModel):
    serial1: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    serial2: Annotated[str, constr(strip_whitespace=True, min_length=1)]

@router.post("/serial-numbers")
async def save_serial_numbers(payload: SerialNumberInput):
    if payload.serial1 != payload.serial2:
        raise HTTPException(status_code=400, detail="Serial numbers do not match")
    
    try:
        SAVE_PATH_SERIAL.write_text(f"{payload.serial1.strip()}\n")
        return {
            "message": "Serial numbers saved successfully", 
            "serial_number": payload.serial1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save serial numbers: {str(e)}")


@router.post("/json-file")
async def receive_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        SAVE_PATH_JSON.write_bytes(contents)
        return {"message": f"File saved successfully as {SAVE_PATH_JSON.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))