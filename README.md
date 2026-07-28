# AI Token Auditor

A premium, dark-themed desktop app that audits AI prompts/responses for
token efficiency and output quality — token count, prompt efficiency,
verbosity, repeated wording, logic failures, inconsistencies,
hallucination-risk indicators, clarity, and structure, rolled into one
report with an overall grade.

Everything runs **locally**. No prompt or response text you paste in is
sent anywhere — the only network activity is a lightweight connectivity
check on launch, purely to gate a polished offline screen.

## Project layout

```
ai_token_auditor/
├── main.py                 # entry point
├── main_window.py          # window shell: sidebar + topbar + pages
├── theme.py                 # color tokens + global stylesheet
├── requirements.txt
├── core/
│   ├── analyzer.py         # the actual audit engine (no UI deps)
│   └── connectivity.py     # offline-safe connectivity check
├── widgets/
│   ├── components.py       # Card, ScoreBar, Badge, MetricTile, IssueRow
│   ├── sidebar.py
│   ├── dashboard.py        # main audit page (input + report)
│   ├── history_page.py
│   ├── about_page.py
│   └── offline_screen.py
└── build/
    ├── token_auditor.spec  # PyInstaller build spec
    ├── version_info.txt    # Windows exe metadata
    └── PACKAGING.md        # signing / "unknown publisher" guidance
```

## Running it

You'll need a machine (or cloud desktop/VM) with Python 3.10+ since this
container has no display and no network access to install packages.

```bash
pip install -r requirements.txt
python main.py
```

### Testing without a local PC

Since you're testing from a cloud environment rather than your own
machine, any of these work:

- **A Windows cloud PC** (Microsoft's own "Windows 365" / Azure Virtual
  Desktop, Amazon WorkSpaces, or Shadow) — closest to a real end-user
  environment, good for testing the actual `.exe` and the SmartScreen
  prompt behavior described in `build/PACKAGING.md`.
- **A Linux GPU/CPU cloud box with a VNC/noVNC desktop** (e.g. a
  DigitalOcean or Paperspace desktop droplet) — fastest to spin up if you
  just want to see the UI and click through it; run `python main.py`
  directly, no packaging needed.
- **GitHub Codespaces with a desktop extension**, or **Gitpod** — works
  for a quick UI check but is more fiddly for producing a Windows `.exe`.

For the packaged `.exe` specifically, you want a real Windows environment
(cloud PC or VM) since PyInstaller builds are platform-specific — a build
made on Linux won't produce a Windows executable.

## Building the Windows executable

See `build/PACKAGING.md` — it covers the PyInstaller build command and,
importantly, gives you an honest answer on what does and doesn't fix the
"Unknown Publisher" prompt (short version: only a real code-signing
certificate does; the spec file makes everything else about the app look
professional in the meantime).

## Notes on the audit engine

`core/analyzer.py` is fully rule-based and deterministic — same input
always produces the same report, and it never calls out to any AI model
itself. That's intentional: an auditor that itself depends on an LLM call
would need its own token-cost and hallucination-risk audit. It uses
`tiktoken` for exact token counts when available, and falls back to a
close character-based estimate if `tiktoken` isn't installed, so the app
never breaks over a missing optional dependency.
