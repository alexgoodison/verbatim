"""Run browser-use agent from a URL + prompt and save a demo video."""

import shutil
import tempfile
from pathlib import Path

from browser_use import Agent, Browser, ChatBrowserUse


def build_task(url: str, prompt: str) -> str:
    """Build the agent task: start at URL, then complete the user prompt."""
    return (
        f"First navigate to this URL: {url}\n\n"
        f"Then complete the following task:\n{prompt}"
    )


async def run_recording(
    url: str,
    prompt: str,
    output_path: Path,
    *,
    headless: bool = False,
) -> Path:
    """
    Run the browser-use agent from the given URL with the prompt,
    record the session to a video file, and save it to output_path.

    Returns the path where the video was saved.
    """
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="verbatim_") as tmpdir:
        record_dir = Path(tmpdir) / "video"
        record_dir.mkdir()

        browser = Browser(
            record_video_dir=str(record_dir),
            headless=headless,
        )

        agent = Agent(
            task=build_task(url, prompt),
            llm=ChatBrowserUse(),
            browser=browser,
        )

        try:
            await agent.run()
        finally:
            await browser.stop()

        # Find the recorded video (browser-use saves on context close)
        videos = list(record_dir.glob("*.mp4"))
        if not videos:
            raise FileNotFoundError(
                "No video was recorded. Install optional deps: pip install 'browser-use[video]'"
            )
        # Use the most recently modified if multiple (e.g. multiple pages)
        recorded = max(videos, key=lambda p: p.stat().st_mtime)
        shutil.copy2(recorded, output_path)

    return output_path
