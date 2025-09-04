from fastapi import APIRouter, UploadFile, File, Depends, Body
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiofiles, tempfile, zipfile, os, shutil, asyncio, logging

router = APIRouter(prefix="/builder", tags=["builder"])
logger = logging.getLogger("uvicorn")

CHUNK_SIZE = 1024 * 1024  # 1 MB chunks

# Define the debs directory path
DEBS_DIR = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/debs")

async def clear_debs():
    """Clear all DEB files from the debs directory"""
    try:
        # Create directory if it doesn't exist
        DEBS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Count existing files
        existing_files = list(DEBS_DIR.glob("*.deb"))
        count = len(existing_files)
        
        # Clear existing debs
        for deb in existing_files:
            logger.info(f"Deleting file: {deb}")
            deb.unlink(missing_ok=True)
        
        logger.info(f"Cleared {count} files from {DEBS_DIR}")
        return {"message": f"Cleared {count} DEB files", "count": count}
    except Exception as e:
        logger.error(f"Error clearing DEB files: {str(e)}")
        return {"error": f"Failed to clear DEB files: {str(e)}", "count": 0}

async def save_upload_file(upload_file: UploadFile, destination: Path):
    """Stream file from UploadFile to disk asynchronously"""
    async with aiofiles.open(destination, "wb") as out_file:
        while chunk := await upload_file.read(CHUNK_SIZE):
            await out_file.write(chunk)
    await upload_file.close()
    return destination


@router.post("/clear_debs")
async def clear_debs_endpoint():
    """Endpoint to clear all DEB files from the directory"""
    return await clear_debs()


@router.post("/upload_debs")
async def upload_file(files: Optional[List[UploadFile]] = File(None)):
    # If no files provided, return error
    if not files:
        return {"error": "No files provided", "count": 0}
    logger.info(f"Received upload request with {len(files)} files")
    for file in files:
        logger.info(f"File name: {file.filename}, Content type: {file.content_type}")
    
    try:
        # target debs directory
        debs_dir = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/debs")
        
        # Create debs directory if it doesn't exist
        debs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Debs directory: {debs_dir}, exists: {debs_dir.exists()}")

        # Process files in batches - this is a batch processing handler
        # Don't clear debs directory at the start - we might be receiving files in multiple batches
        
        results = []
        for file in files:
            try:
                filename = file.filename

                # If it's a zip archive → extract contents
                if filename.endswith(".zip"):
                    tmp_zip = Path(tempfile.gettempdir()) / filename
                    logger.info(f"Saving ZIP: {filename}")
                    await save_upload_file(file, tmp_zip)

                    extract_dir = Path(tempfile.gettempdir()) / f"{filename}_extracted"
                    logger.info(f"Extracting ZIP to {extract_dir}")
                    # run extraction in threadpool (zipfile is sync)
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lambda: zipfile.ZipFile(tmp_zip, "r").extractall(extract_dir))

                    for root, _, extracted_files in os.walk(extract_dir):
                        for ef in extracted_files:
                            if ef.endswith(".deb"):
                                ef_path = Path(root) / ef
                                logger.info(f"Found deb in zip: {ef_path}")
                                results.append(ef_path)

                    # cleanup zip + extracted folder
                    shutil.rmtree(extract_dir, ignore_errors=True)
                    tmp_zip.unlink(missing_ok=True)

                elif filename.endswith(".deb"):
                    tmp_file = Path(tempfile.gettempdir()) / filename
                    logger.info(f"Saving DEB: {filename}")
                    await save_upload_file(file, tmp_file)
                    results.append(tmp_file)

                else:
                    logger.warning(f"Skipping unsupported file: {filename}")
                    continue
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                # Continue with other files

        if not results:
            return {"message": "No valid .deb files found in the upload", "count": 0}

        # Move uploaded debs into debs dir (don't clear existing files)
        moved_files = 0
        for idx, item in enumerate(results, 1):
            try:
                dest_path = debs_dir / Path(item).name
                logger.info(f"[{idx}/{len(results)}] Moving {item} → {dest_path}")
                os.replace(item, dest_path)
                moved_files += 1
            except Exception as e:
                logger.error(f"Error moving file {item}: {str(e)}")

        return {
            "message": f"Processed {moved_files} .deb files into {debs_dir}",
            "count": moved_files,
            "total_files": len(files),
            "processed_files": len(results)
        }
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return {"error": str(e), "count": 0}
