import subprocess
from fastapi import APIRouter

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/start")
def trigger_pipeline():
    try:
        result = subprocess.run(
            ["bash", "C:/Users/christian.leonard/Documents/code/IoT/Stratus/commands/launcher.sh", "help"],
            capture_output=True,
            text=True
        )
        print("Return code:", result.returncode)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return {"message": "Pipeline started successfully"}
    except Exception as e:
        return {"error": str(e)}