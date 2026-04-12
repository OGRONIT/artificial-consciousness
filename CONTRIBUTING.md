# Contributing

Thanks for your interest in improving this project.

## Development Setup
1. Clone repo
2. Open PowerShell in repo root
3. Run:
   ```powershell
   .\install_conscious_engine.ps1
   ```
4. Activate venv if needed:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

## Code Guidelines
- Keep changes focused and minimal.
- Preserve existing architecture boundaries in `antahkarana_kernel/modules`.
- Avoid committing runtime-generated data, logs, or local keys.
- Add/update docs when behavior changes.

## Pull Request Checklist
- [ ] Code runs locally
- [ ] No secrets committed
- [ ] `.env` not tracked
- [ ] Relevant docs updated
- [ ] CI passes

## Commit Style
Use clear messages, for example:
- `feat: add bridge fallback guard`
- `fix: handle 429 rate-limit parse`
- `docs: update quickstart`

## Reporting Issues
Open a GitHub issue with:
- What you ran
- Expected behavior
- Actual behavior
- Logs/screenshots (without secrets)
