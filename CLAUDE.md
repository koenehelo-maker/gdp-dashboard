# CLAUDE.md

## Project

Streamlit demo that charts World Bank GDP data. Entry point is `streamlit_app.py`, data is `data/gdp_data.csv`, direct dependencies are `streamlit` and `pandas` (`requirements.in`, locked in `requirements.txt`). Run with `streamlit run streamlit_app.py`.

`.github/CODEOWNERS` assigns every file to `@koenehelo-maker`. It previously named `@streamlit/community-cloud`, left over from the Streamlit template; that was changed in #8. GitHub never asks a PR's author for review, so this only routes reviews when someone else opens a PR or branch protection requires code-owner review.

CI (`.github/workflows/ci.yml`) runs on every PR and push to `main`, on Python 3.11 and 3.13. It runs `pytest tests`, which executes the app headlessly with Streamlit's `AppTest` and fails on any exception, then starts `streamlit run` and checks `/_stcore/health`. Run the tests locally with `pip install -r requirements.txt pytest==9.2.0 && pytest tests`.

Dependencies are locked. `requirements.in` lists the direct dependencies (`streamlit==1.66.1`, `pandas==3.1.1`). `requirements.txt` is generated from it by `uv pip compile` and pins all 34 packages, including transitive ones like numpy and pyarrow, with markers where Python 3.11 and 3.12+ need different versions. Do not edit `requirements.txt` by hand. To change or upgrade a dependency, edit `requirements.in` (or pass `--upgrade-package <name>` to upgrade only a transitive dependency), then run:

```bash
uv pip compile requirements.in --universal --python-version 3.11 -o requirements.txt
```

Commit both files. CI's "Lock file in sync" job re-runs that command and fails if `requirements.txt` changes. CI pins `pytest==9.2.0` separately. Streamlit Community Cloud, the devcontainer and the README all install from `requirements.txt`, so they get the locked versions.

Dependabot (`.github/dependabot.yml`) opens update PRs every Monday 06:00 SAST for Python packages, grouping minor and patch bumps into one PR, and monthly for GitHub Actions. Dependabot's support for a `uv pip compile` lock is not documented, so treat each Python PR with care: if "Lock file in sync" fails, check out the branch, regenerate the lock with the command above (adding `--upgrade-package <name>`), and push. Security alerts and security-update PRs are separate repository settings (Settings > Code security).

## Claude Code tooling

Cloud sessions start in a fresh container. Anything installed by hand (plugins, skills, CLI tools) is lost when the container is reclaimed. Only what is committed to this repo persists.

### Active (persisted via `.claude/settings.json`)

| Plugin | Use | Notes |
|---|---|---|
| Humanizer (`blader/humanizer`) | Strip AI tells from prose | `/humanizer:humanizer` |
| Watch (`bradautomates/claude-video`) | Frames + transcript from a video URL or file | Needs `ffmpeg` and `yt-dlp`; `.claude/hooks/session-start.sh` installs them in cloud sessions. YouTube also needs Deno, which is not installed. |
| HyperFrames (`heygen-com/hyperframes`) | Code-built video | The claude.ai HyperFrames connector makes hosted HeyGen projects; the plugin writes local HTML. Pick one per job. |
| Blender Skills (`arjun988/blender-skills` v1.3.0, commit `8f778d2`) | 94 Blender skills in `.claude/skills/` (MIT, licence in `LICENSE-blender-skills`) | Markdown only; skillspector rated all 94 SAFE. Built for Blender MCP, which needs Blender running locally, so in cloud sessions it gives guidance only. Its Windows-only `.mcp.json` was not copied. Delete `.claude/skills/` if the skill list crowds out other skills. |

### Deliberately not persisted

| Tool | Why | To use anyway |
|---|---|---|
| Superpowers | Software-engineering workflow; loads into every session and clashes with gstack and the document skills | `/plugin marketplace add obra/superpowers-marketplace`, then install `superpowers@superpowers-marketplace` |
| Impeccable | Hooks run a compiled binary on every session start, edit and stop | `/plugin marketplace add pbakaus/impeccable`. Only worth it for UI work on this dashboard. |
| gstack | Not a plugin; `./setup` takes minutes. Browser skills fail in cloud containers. | Install on a local machine. Useful subset: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/spec`, `/retro`, `/investigate`. |
| Last 30 Days | Can read browser cookies; the consent gate is enforced by the prompt, not the code | Decline cookie access on work machines |
| Remotion | Company licence required for organisations with more than 3 employees | Do not use for Telkom work without a licence |
| prompts.chat (`f/prompts.chat`) | Plugin files scan clean, but its `skill-lookup` skill installs user-submitted skills into `.claude/skills/` without a scan, and `improve_prompt` sends prompt text to the prompts.chat server, which calls OpenAI. The proxy blocks `prompts.chat`, so the MCP server cannot connect in cloud sessions. | Browse the site or the CC0 `prompts.csv` in the repo instead. Do not send Telkom content to `improve_prompt`. |
| Graphify MCP (`https://api.graphify.com/mcp`, open draft PR #1) | Graphify's own hosted server, so official, but it indexes your GitHub repos on Graphify's servers. Separately, a Graphify GitHub App posts a "Graphify" check on PRs here (first seen on #14, 5 Nov 2026), so it already has access to this repo; review or remove it under Settings > GitHub Apps. The proxy blocks `api.graphify.com`, and a code graph adds little to a one-file app. | Set it up in a large codebase on a local machine. For code context here, use the GitHub MCP already connected in cloud sessions. |
| NotebookLM skill (`ArtemXTech/personal-os-skills`, open draft PR #2) | Scripts scan CAUTION (24/100) but read clean. The risk is its unofficial `notebooklm-py` / `nlm` clients: they sign in to Google through a browser and store session cookies in plain text in `~/.notebooklm/`. `load_channel.py` scrapes YouTube's internal API. It needs a browser and an Obsidian vault, so it cannot run in cloud sessions. | Prefer Google's official Gemini Notebook (formerly NotebookLM) MCP server, `https://notebook.googleapis.com/mcp`, connected with `claude mcp add` on a local machine (see developers.google.com/notebook/docs/mcp). As of November 2026 it is Public Preview, personal Google accounts only (no Workspace, so not Telkom accounts), uses OAuth plus a Google Cloud project, and lists notebook and source tools but no ask/query tool. The proxy blocks `developers.google.com`, so check the page from a local browser. |

### Rules learned

- Scan third-party skills before installing: `uv tool install git+https://github.com/NVIDIA/skillspector.git`, then `skillspector scan <dir> --recursive --no-llm`. The static scan is noisy (most "DO_NOT_INSTALL" ratings come from API-key reads in tests and docs), so read the high-severity findings instead of trusting the rating.
- Do not add gstack's suggested CLAUDE.md section ("use /browse for all web browsing, never use Chrome tools"). It routes all browsing through a tool that does not work here.
- Do not run gstack team mode (`./setup --team`); it commits gstack into the repo as a requirement.
- Superpowers is on Anthropic's official marketplace (`superpowers@claude-plugins-official`), but that marketplace is not registered in cloud containers.
- `/reload-plugins` does not work over a remote connection. Start a new session to load newly installed plugins.
- Installing third-party plugins is blocked by the permission classifier unless the user explicitly approves it in the conversation.
- Cloud Chromium is Playwright build 1194. Tools that pin a newer build (gstack needs 1234) cannot download one; `playwright install` is blocked.
