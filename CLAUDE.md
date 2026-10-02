# CLAUDE.md

## Project

Streamlit demo that charts World Bank GDP data. Entry point is `streamlit_app.py`, data is `data/gdp_data.csv`, dependencies are `streamlit` and `pandas` (`requirements.txt`). Run with `streamlit run streamlit_app.py`.

Tests in `tests/` use Streamlit's `AppTest` to run the app headless: `pip install -r requirements.txt pytest`, then `pytest -q`. `.github/workflows/ci.yml` runs them on every pull request and on pushes to `main`.

## Claude Code tooling

Cloud sessions start in a fresh container. Anything installed by hand (plugins, skills, CLI tools) is lost when the container is reclaimed. Only what is committed to this repo persists.

### Active (persisted via `.claude/settings.json`)

| Plugin | Use | Notes |
|---|---|---|
| Humanizer (`blader/humanizer`) | Strip AI tells from prose | `/humanizer:humanizer` |
| Watch (`bradautomates/claude-video`) | Frames + transcript from a video URL or file | Needs `ffmpeg` and `yt-dlp`; `.claude/hooks/session-start.sh` installs them in cloud sessions. YouTube also needs Deno, which is not installed. |
| HyperFrames (`heygen-com/hyperframes`) | Code-built video | The claude.ai HyperFrames connector makes hosted HeyGen projects; the plugin writes local HTML. Pick one per job. |

### Deliberately not persisted

| Tool | Why | To use anyway |
|---|---|---|
| Superpowers | Software-engineering workflow; loads into every session and clashes with gstack and the document skills | `/plugin marketplace add obra/superpowers-marketplace`, then install `superpowers@superpowers-marketplace` |
| Impeccable | Hooks run a compiled binary on every session start, edit and stop | `/plugin marketplace add pbakaus/impeccable`. Only worth it for UI work on this dashboard. |
| gstack | Not a plugin; `./setup` takes minutes. Browser skills fail in cloud containers. | Install on a local machine. Useful subset: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/spec`, `/retro`, `/investigate`. |
| Last 30 Days | Can read browser cookies; the consent gate is enforced by the prompt, not the code | Decline cookie access on work machines |
| Remotion | Company licence required for organisations with more than 3 employees | Do not use for Telkom work without a licence |
| prompts.chat (`f/prompts.chat`) | Plugin files scan clean, but its `skill-lookup` skill installs user-submitted skills into `.claude/skills/` without a scan, and `improve_prompt` sends prompt text to the prompts.chat server, which calls OpenAI. The proxy blocks `prompts.chat`, so the MCP server cannot connect in cloud sessions. | Browse the site or the CC0 `prompts.csv` in the repo instead. Do not send Telkom content to `improve_prompt`. |

### Rules learned

- Scan third-party skills before installing: `uv tool install git+https://github.com/NVIDIA/skillspector.git`, then `skillspector scan <dir> --recursive --no-llm`. The static scan is noisy (most "DO_NOT_INSTALL" ratings come from API-key reads in tests and docs), so read the high-severity findings instead of trusting the rating.
- Do not add gstack's suggested CLAUDE.md section ("use /browse for all web browsing, never use Chrome tools"). It routes all browsing through a tool that does not work here.
- Do not run gstack team mode (`./setup --team`); it commits gstack into the repo as a requirement.
- Superpowers is on Anthropic's official marketplace (`superpowers@claude-plugins-official`), but that marketplace is not registered in cloud containers.
- `/reload-plugins` does not work over a remote connection. Start a new session to load newly installed plugins.
- Installing third-party plugins is blocked by the permission classifier unless the user explicitly approves it in the conversation.
- Cloud Chromium is Playwright build 1194. Tools that pin a newer build (gstack needs 1234) cannot download one; `playwright install` is blocked.
