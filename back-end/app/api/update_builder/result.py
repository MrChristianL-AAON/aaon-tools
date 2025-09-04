from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import datetime
import logging
import os

router = APIRouter(prefix="/builder", tags=["builder"])
logger = logging.getLogger("uvicorn")

# Define the output directory path
OUTPUT_DIR = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/_output")

# Create the directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Log information about the directory
logger.info(f"Output directory: {OUTPUT_DIR}")
logger.info(f"Output directory exists: {OUTPUT_DIR.exists()}")
logger.info(f"Output directory is dir: {OUTPUT_DIR.is_dir() if OUTPUT_DIR.exists() else False}")

@router.get("/output_files")
async def list_output_files():
    """
    Returns a list of files in the _output folder.
    """
    try:
        # Check if output directory exists
        if not OUTPUT_DIR.exists():
            logger.warning(f"Output directory does not exist: {OUTPUT_DIR}")
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            return {"files": [], "message": "Output directory was just created, no files yet"}

        # List the contents of the output directory
        logger.info(f"Listing contents of output directory: {OUTPUT_DIR}")
        directory_contents = list(OUTPUT_DIR.iterdir())
        logger.info(f"Found {len(directory_contents)} items in output directory")

        files = []
        # First, check files directly in the output directory
        for item in directory_contents:
            if item.is_file():
                relative_path = str(item.relative_to(OUTPUT_DIR))
                files.append(relative_path)
                logger.info(f"Added file from root: {relative_path}")
            elif item.is_dir():
                # Process subdirectories as before
                logger.info(f"Processing subfolder: {item.name}")
                subfolder_items = list(item.iterdir())
                logger.info(f"Found {len(subfolder_items)} items in {item.name}")
                
                for f in subfolder_items:
                    if f.is_file():
                        relative_path = str(f.relative_to(OUTPUT_DIR))
                        files.append(relative_path)
                        logger.info(f"Added file from subfolder: {relative_path}")
        
        logger.info(f"Returning {len(files)} files")
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing output files: {str(e)}")
        return {"files": [], "error": str(e)}

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """
    Downloads a specific file inside _output.
    `file_path` should be relative to OUTPUT_DIR, e.g. "commands_20250829/file1.update"
    """
    try:
        logger.info(f"Download requested for file: {file_path}")
        
        # Construct the full path
        full_path = OUTPUT_DIR / file_path
        logger.info(f"Full path: {full_path}")
        
        # Check if the file exists
        if not full_path.exists():
            logger.error(f"File does not exist: {full_path}")
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        if not full_path.is_file():
            logger.error(f"Path is not a file: {full_path}")
            raise HTTPException(status_code=400, detail=f"Path is not a file: {file_path}")
        
        # Log file information
        file_size = full_path.stat().st_size
        logger.info(f"Serving file: {full_path.name}, Size: {file_size} bytes")
        
        # Return the file
        return FileResponse(
            path=full_path,
            filename=full_path.name,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
