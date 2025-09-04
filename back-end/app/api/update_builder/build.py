from fastapi import APIRouter, BackgroundTasks
from pathlib import Path
import subprocess
from typing import List

router = APIRouter(prefix="/builder", tags=["builder"])

# http://127.0.0.1:8000/api/builder/build

# api because of main.py include_router
# builder because of this router prefix 
# build because of this router get

# the build page
@router.get("/build")
def get_build():
    return {"message": "Updater builder endpoint"}


# trigger the update build script
@router.post("/build_update")
def trigger_update(background_tasks: BackgroundTasks):
    updater_path = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/build_deb_package.sh")
    updater_dir = updater_path.parent

    if not updater_path.exists():
        return {"error": f"Script not found at {updater_path}"}

    def run_script():
        try:
            result = subprocess.run(
                ["bash", str(updater_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(updater_dir),
                timeout=120
            )
            print("Pipeline finished:", result.returncode)
            print("stdout:", result.stdout)
            print("stderr:", result.stderr)
        except subprocess.TimeoutExpired:
            print("Pipeline timed out")
        except Exception as e:
            print("Pipeline failed:", str(e))

    # Run build in the background so request returns immediately
    background_tasks.add_task(run_script)

    return {"message": "Pipeline started in background"}
