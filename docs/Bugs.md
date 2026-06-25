# Known Bugs and Issues

1. **PDF Generation Dependency Error (Resolved):** `requirements.txt` incorrectly listed `pdfkit` instead of `fpdf2`, causing an `ImportError` on `main.py` initialization. Fixed in Phase 2 commit.
