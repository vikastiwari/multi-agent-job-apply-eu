# Known Bugs and Issues

1. **PDF Generation Dependency Error (Resolved):** `requirements.txt` incorrectly listed `pdfkit` instead of `fpdf2`, causing an `ImportError` on `main.py` initialization. Fixed in Phase 2 commit.
2. **Environment Variable Pathing in Tests (Resolved):** Resolution: Modified `os.path.exists` mock to a `side_effect` lambda that checks the target path, enabling real `python-dotenv` checks.

## Phase 5: Voice AI Integration

*   **Bug:** `livekit-plugins-google` install conflicts and test failures due to `async` test definitions without `pytest-asyncio` and `open()` mocking blocking `worker.py` writes.
*   **Resolution:** Installed `pytest-asyncio`, patched `builtins.open` via `new_callable=MagicMock`, and fixed module-level `sys` imports to satisfy `patch('sys.argv')`.

## Phase 6: Web Dashboard
*   **Bug:** Vite installed Tailwind CSS v4 which strictly requires Node.js v20+, but the WSL Ubuntu environment had Node.js v18.19.1 installed, causing the PostCSS plugin `Cannot find native binding` error and breaking `npm run dev`.
*   **Resolution:** Downgraded to Tailwind CSS v3 (`npm install -D tailwindcss@^3`), reverted `postcss.config.js` to use `tailwindcss: {}`, and re-ran the Vite development server.

*   **Bug:** Gemini 2.5 Flash Free Tier hit 429/503 errors (5 RPM / 20 RPD limits) when `hunter.py` and `worker.py` ran simultaneously, causing agents to fail and sleep continuously.
*   **Resolution:** Upgraded the system's core LLM to `gemini-3.1-flash-lite`, which has significantly higher Free Tier limits (15 RPM / 500 RPD), allowing the swarm to process jobs smoothly in the background.
