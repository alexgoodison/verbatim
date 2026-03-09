# Verbatim

**Record AI-driven browser demos from a URL and a prompt.** Uses [browser-use](https://github.com/browser-use/browser-use) to navigate your app, complete the task you describe, and save a demo video for docs, tutorials, or marketing.

## Install

Requires **Python 3.11+**. From the project directory:

**Option A – uv (recommended):**

```bash
cd verbatim
uv sync
# Then run with:
uv run verbatim <URL> "<PROMPT>" [ -o output.mp4 ]
```

**Option B – pip (or conda base):**

```bash
cd verbatim
pip install -e ".[video]"
# Then run (with your env activated):
verbatim <URL> "<PROMPT>" [ -o output.mp4 ]
```

**Option C – run without installing the script:** from the project root with the package on `PYTHONPATH`:

```bash
cd verbatim
pip install -e ".[video]"   # one-time install
python -m verbatim.cli https://example.com "Your prompt" -o docs/demo.mp4
```

Video recording uses the optional `browser-use[video]` extra (imageio + ffmpeg). If you skip it, the CLI will run but no video file will be produced.

## Configure

Create a `.env` in the project (or your working directory) with an LLM API key. Verbatim uses browser-use’s default model (Browser Use API); you can use their cloud or another provider:

```bash
# Optional: Browser Use Cloud (sign up for API key)
BROWSER_USE_API_KEY=your-key

# Or use another provider (see browser-use docs)
# GOOGLE_API_KEY=...
# ANTHROPIC_API_KEY=...
# OPENAI_API_KEY=...
```

## Usage

```bash
verbatim <URL> "<PROMPT>" [ -o output.mp4 ] [ --headless ]
```

- **URL** – Starting page (e.g. `https://myapp.com`).
- **PROMPT** – What the agent should do (e.g. *"Click Sign in and fill the form with test@example.com"*).
- **-o / --output** – Where to save the demo video (default: `verbatim_<timestamp>.mp4` in the current directory).
- **--headless** – Run the browser in headless mode (default is headed so you can watch the demo).

### Examples

```bash
# Record a short flow and save to docs/demo.mp4
verbatim https://myapp.com "Open the API section and scroll to Authentication" -o docs/demo.mp4

# Generate a timestamped file in the current directory
verbatim https://example.com "Click 'More information' and then the first link"
```

### Web UI

From the project root you can run a local UI to start generations and view previously created recordings:

```bash
# Install UI deps (once)
pip install -e ".[ui]"
# Or: pip install -r requirements.txt && pip install -r ui/requirements-ui.txt

# Run the UI server (from project root)
python -m uvicorn ui.server:app --reload --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000 in your browser. New recordings are saved under `ui/recordings/`.

The agent will open the URL, complete the prompt, and the session will be recorded to an MP4 you can drop into tech docs, READMEs, or tutorials.

## How it works

1. Verbatim starts a browser (Chromium) with video recording enabled.
2. It launches a [browser-use](https://github.com/browser-use/browser-use) agent with a task: “Navigate to &lt;URL&gt;, then: &lt;PROMPT&gt;”.
3. The agent uses the LLM (default: Browser Use API) to decide actions (click, type, scroll, etc.) and performs them.
4. When the run finishes, the browser is closed and the recording is saved to the path you passed with `-o` (or the default filename).

## License

MIT.
