# Known Bugs and Issues

1. **PDF Generation Dependency Error (Resolved):** `requirements.txt` incorrectly listed `pdfkit` instead of `fpdf2`, causing an `ImportError` on `main.py` initialization. Fixed in Phase 2 commit.
2. **Environment Variable Pathing in Tests (Resolved):** Resolution: Modified `os.path.exists` mock to a `side_effect` lambda that checks the target path, enabling real `python-dotenv` checks.

## Phase 5: Voice AI Integration

*   **Bug:** `livekit-plugins-google` install conflicts and test failures due to `async` test definitions without `pytest-asyncio` and `open()` mocking blocking `worker.py` writes.
*   **Resolution:** Installed `pytest-asyncio`, patched `builtins.open` via `new_callable=MagicMock`, and fixed module-level `sys` imports to satisfy `patch('sys.argv')`.
