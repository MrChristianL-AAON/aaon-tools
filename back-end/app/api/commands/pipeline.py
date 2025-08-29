import subprocess
from fastapi import APIRouter
from pathlib import Path

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

def strip_ansi_codes(text: str) -> str:
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

@router.post("/start")
def trigger_pipeline():
    launcher_path = Path("C:/Users/christian.leonard/Documents/code/IoT/Stratus/commands/launcher.sh")
    launcher_dir = launcher_path.parent

    if not launcher_path.exists():
        return {"error": f"Script not found at {launcher_path}"}

    serial_path = launcher_dir / "_output" / "serial_number.txt"
    if not serial_path.exists():
        return {"error": f"Serial number file not found at {serial_path}"}

    serial_number = serial_path.read_text().strip()

    try:
        result = subprocess.run(
            ["bash", str(launcher_path), "fast", serial_number],
            capture_output=True,
            text=True,
            errors='replace',
            cwd=str(launcher_dir),
            timeout=120
        )

        stdout_clean = strip_ansi_codes(result.stdout) if result.stdout else ""
        stderr_clean = strip_ansi_codes(result.stderr) if result.stderr else ""

        return {
            "message": "Pipeline completed",
            "return_code": result.returncode,
            "stdout": stdout_clean,
            "stderr": stderr_clean,
            "success": result.returncode == 0,
            "script_exists": launcher_path.exists()
        }
    except subprocess.TimeoutExpired:
        return {"error": "Script timed out"}
    except Exception as e:
        return {"error": str(e)}