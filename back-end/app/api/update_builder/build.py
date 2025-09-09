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
        build_success = False
        try:
            # Run the build script first
            build_result = subprocess.run(
                ["bash", str(updater_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(updater_dir),
                timeout=300  # Increased timeout for larger builds
            )
            print("Pipeline finished:", build_result.returncode)
            print("stdout:", build_result.stdout)
            print("stderr:", build_result.stderr)
            
            # Check if build was successful
            if build_result.returncode == 0:
                build_success = True
            else:
                print("Build failed with return code:", build_result.returncode)
                
            # Now run the archival script if build was successful
            if build_success:
                archive_path = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/remote_update_manager/scripts/archive.py")
                if not archive_path.exists():
                    print(f"Archive script not found at {archive_path}")
                    return
                    
                try:
                    archive_result = subprocess.run(
                        ["python", str(archive_path)],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        cwd=str(archive_path.parent),
                        timeout=60
                    )
                    print("Archive script finished:", archive_result.returncode)
                    print("stdout:", archive_result.stdout)
                    print("stderr:", archive_result.stderr)
                    
                    if archive_result.returncode != 0:
                        print(f"Archive script failed with return code: {archive_result.returncode}")
                except subprocess.TimeoutExpired:
                    print("Archive script timed out")
                except Exception as e:
                    print(f"Archive script failed: {str(e)}")
                    
        except subprocess.TimeoutExpired:
            print("Pipeline timed out")
        except Exception as e:
            print("Pipeline failed:", str(e))

    # Run build in the background so request returns immediately
    background_tasks.add_task(run_script)

    return {"message": "Pipeline started in background. Archival will run automatically upon successful build."}