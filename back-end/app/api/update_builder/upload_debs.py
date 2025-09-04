from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from typing import List
import aiofiles, tempfile, zipfile, os, shutil, asyncio, logging

router = APIRouter(prefix="/builder", tags=["builder"])
logger = logging.getLogger("uvicorn")

CHUNK_SIZE = 1024 * 1024  # 1 MB chunks

async def save_upload_file(upload_file: UploadFile, destination: Path):
    """Stream file from UploadFile to disk asynchronously"""
    async with aiofiles.open(destination, "wb") as out_file:
        while chunk := await upload_file.read(CHUNK_SIZE):
            await out_file.write(chunk)
    await upload_file.close()
    return destination


@router.post("/upload_debs")
async def upload_file(files: List[UploadFile] = File(...)):
    logger.info(f"Received upload request with {len(files)} files")
    for file in files:
        logger.info(f"File name: {file.filename}, Content type: {file.content_type}")
    
    results = []

    for file in files:
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

    if not results:
        return {"message": "No valid .deb files found in the upload"}

    # target debs directory
    debs_dir = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/debs")

    # clear existing debs
    for deb in debs_dir.glob("*.deb"):
        deb.unlink(missing_ok=True)

    # move uploaded debs into debs dir
    for idx, item in enumerate(results, 1):
        dest_path = debs_dir / Path(item).name
        logger.info(f"[{idx}/{len(results)}] Moving {item} → {dest_path}")
        os.replace(item, dest_path)

    return {"message": f"Processed {len(results)} .deb files into {debs_dir}"}
