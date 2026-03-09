"""CLI for Verbatim: record browser demos from URL + prompt."""

import asyncio
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from verbatim import __version__
from verbatim.runner import run_recording

load_dotenv()


@click.command()
@click.argument("url", type=str)
@click.argument("prompt", type=str)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output video path (default: verbatim_<timestamp>.mp4 in cwd)",
)
@click.option(
    "--headless/--no-headless",
    default=False,
    help="Run browser in headless mode (default: no-headless for visible demo)",
)
def main(
    url: str,
    prompt: str,
    output_path: Path | None,
    headless: bool,
) -> None:
    """
    Record a demo video by having an AI agent complete a task on a website.

    URL: Starting page (e.g. https://example.com).

    PROMPT: What the agent should do (e.g. "Click Sign in and fill the form with test@example.com").

    The agent uses the browser-use library to navigate and interact with the page;
    the session is recorded to an MP4 file suitable for docs or tutorials.

    Example:

        verbatim https://myapp.com/docs "Open the API section" -o demo.mp4
    """
    if not output_path:
        from datetime import datetime

        output_path = Path.cwd() / f"verbatim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    click.echo(f"Verbatim {__version__}")
    click.echo(f"URL: {url}")
    click.echo(f"Prompt: {prompt}")
    click.echo(f"Output: {output_path}")
    click.echo("Starting browser and agent…")

    try:
        result = asyncio.run(
            run_recording(
                url,
                prompt,
                output_path,
                headless=headless,
            )
        )
        click.echo(click.style(f"Done. Video saved to: {result}", fg="green"))
    except FileNotFoundError as e:
        click.echo(click.style(str(e), fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
