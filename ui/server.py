"""Web UI for Verbatim: start generations and view recordings."""

import concurrent.futures
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Recordings dir: ui/recordings when running from project root
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
RECORDINGS_DIR = APP_DIR / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Run verbatim in background; one at a time to avoid browser conflicts
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

app = FastAPI(title="Verbatim UI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    url: str
    prompt: str


class Generation(BaseModel):
    id: str
    filename: str
    path: str
    created_at: str
    url: str
    prompt: str | None = None
    status: str = "completed"  # completed | running | failed


def _run_verbatim(url: str, prompt: str, output_path: Path) -> None:
    """Run verbatim CLI in subprocess (blocking)."""
    env = os.environ.copy()
    # Ensure we run from project root so verbatim and .env are found
    cmd = [
        sys.executable,
        "-m",
        "verbatim.cli",
        url,
        prompt,
        "-o",
        str(output_path),
    ]
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env, timeout=3600)


def _list_recordings() -> list[Generation]:
    """List all MP4 files in recordings dir, newest first."""
    generations = []
    for p in sorted(RECORDINGS_DIR.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True):
        stat = p.stat()
        created = datetime.fromtimestamp(stat.st_mtime).isoformat()
        generations.append(
            Generation(
                id=p.stem,
                filename=p.name,
                path=str(p.relative_to(PROJECT_ROOT)),
                created_at=created,
                url="/api/generations/" + p.stem + "/video",
                prompt=None,
                status="completed",
            )
        )
    return generations


@app.get("/api/generations", response_model=list[Generation])
def list_generations():
    """List previously created recordings."""
    return _list_recordings()


@app.post("/api/generations", response_model=Generation)
def start_generation(body: StartRequest):
    """Start a new recording. Runs in background; file appears when done."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"verbatim_{timestamp}.mp4"
    output_path = RECORDINGS_DIR / filename

    def task():
        try:
            _run_verbatim(body.url, body.prompt, output_path)
        except Exception:
            pass  # Could log or mark as failed

    _executor.submit(task)

    return Generation(
        id=output_path.stem,
        filename=filename,
        path=str(output_path.relative_to(PROJECT_ROOT)),
        created_at=datetime.now().isoformat(),
        url="/api/generations/" + output_path.stem + "/video",
        prompt=body.prompt,
        status="running",
    )


@app.get("/api/generations/{generation_id}/video")
def get_video(generation_id: str):
    """Stream a recording by id (filename without .mp4)."""
    path = RECORDINGS_DIR / f"{generation_id}.mp4"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Recording not found")
    return FileResponse(path, media_type="video/mp4")


@app.get("/")
def index():
    """Serve the UI."""
    return FileResponse(APP_DIR / "index.html")
