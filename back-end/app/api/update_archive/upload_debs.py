from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from typing import List

import tempfile, zipfile, os, shutil

router = APIRouter(prefix="/builder", tags=["builder"])


# http://127.0.0.1:8000/api/builder/upload
@router.post("/upload_debs")
async def upload_file(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        filename = file.filename

        # If it's a zip archive → extract contents
        if filename.endswith(".zip"):
            tmp_zip = Path(tempfile.gettempdir()) / filename
            with open(tmp_zip, "wb") as f:
                f.write(await file.read())

            extract_dir = Path(tempfile.gettempdir()) / f"{filename}_extracted"
            with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            for root, _, extracted_files in os.walk(extract_dir):
                for ef in extracted_files:
                    if ef.endswith(".deb"):
                        results.append(Path(root) / ef)

            # cleanup extracted contents after parsing
            shutil.rmtree(extract_dir, ignore_errors=True)
            tmp_zip.unlink(missing_ok=True)

        # If it’s a single .deb (from drag-drop or folder upload) -- browsers don't actually upload folders, just the contents
        elif filename.endswith(".deb"):
            tmp_file = Path(tempfile.gettempdir()) / filename
            with open(tmp_file, "wb") as f:
                f.write(await file.read())
            results.append(tmp_file)

        # unsupported file type - skip it      
        else:
            continue

    if not results:
        return {"message": "No valid .deb files found in the upload"}

    # target debs directory
    debs_dir = Path(__file__).parent / "debs"
    debs_dir.mkdir(exist_ok=True)

    # clear existing debs
    for deb in debs_dir.glob("*.deb"):
        deb.unlink(missing_ok=True)

    # move uploaded debs into debs dir
    for item in results:
        dest_path = debs_dir / Path(item).name
        os.replace(item, dest_path)

    return {"message": f"Processed {len(results)} .deb files into {debs_dir}"}
