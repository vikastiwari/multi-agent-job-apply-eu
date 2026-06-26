# Known Bugs and Issues

1. **PDF Generation Dependency Error (Resolved):** `requirements.txt` incorrectly listed `pdfkit` instead of `fpdf2`, causing an `ImportError` on `main.py` initialization. Fixed in Phase 2 commit.
2. **Environment Variable Pathing in Tests (Resolved):** When mocking `os.path.exists` globally in Pytest, `python-dotenv` fails with `Starting path not found`. This was resolved by using a dynamic `side_effect` lambda instead of a static `return_value = False` during Phase 4 async testing.
