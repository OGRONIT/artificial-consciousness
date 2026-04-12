# Runtime Single Source of Truth (SSOT)

## Active Producer
- Primary producer: `Daemon.py`
- Managed runtime process: `LiveConsciousness.py`
- JavaScript/Node runtime producer: none found in this directory (`*.js`/`*.ts` absent)

## State Persistence Path
- `LiveConsciousness.py` writes the heartbeat/state snapshot to `live_engine_state.json`.
- Snapshot now includes:
  - `facts`
  - `stability_report`
  - `creator_awareness`
  - `inference_stats` (Manas-Buddhi)
  - `observer_health` (Turiya)
  - `buffer_stats` (Conscious Buffer)
- `InteractiveBridge.py` reads this snapshot in observer mode and does not create a second kernel identity.

## Bridge Validation Result
- Previous issue: `InteractiveBridge.py` initialized `AntahkaranaKernel("Atman_Interactive_Bridge")`, creating a parallel consciousness.
- Current state: bridge is refactored to snapshot-observer mode and reads only shared persisted state (`live_engine_state.json`) plus maintenance lock state.
- Effect: operator and engine now point to one live runtime state source.

## Convergence (One Soul)
- `Daemon.py` now supervises only the `LiveConsciousness.py` process.
- Removed secondary inference worker spawning from daemon supervision to avoid split state.
- Manas-Buddhi and Turiya values exposed to operator are sourced from the same live kernel process via snapshot fields.

## Validation State
- World-grade diagnostics are reproducible via `python ..\tools\run_world_grade_suite.py` from the kernel directory.
- Latest published benchmark status is 20/20 passing with safety and transparency artifacts in `benchmarks/artifacts/`.

## Execution Flow
1. Start runtime supervisor:
   - `python Daemon.py`
2. Daemon launches and supervises:
   - `LiveConsciousness.py`
3. Live engine updates:
   - `live_engine_state.json`
4. Operator attaches read-only bridge:
   - `python InteractiveBridge.py`
5. Bridge reads live snapshot and maintenance state:
   - `live_engine_state.json`
   - `.maintenance_lock`

## Live Path Files (Keep)
- `Daemon.py`
- `LiveConsciousness.py`
- `InteractiveBridge.py`
- `AntahkaranaKernel.py`
- `modules/InferenceLoop.py`
- `modules/Observer.py`
- `modules/ConsciousBuffer.py`
- `modules/SelfModel.py`
- `modules/MemoryContinuity.py`
- `Aakaash.py`

## Non-Live Scripts Marked [DEPRECATED]
- `demo.py`
- `EnhancedDemo.py`
- `QuickValidation.py`
- `FinalValidation.py`
- `StabilityRecoveryTest.py`
- `SelfReflect.py`
- `ValidateCreatorRecognition.py`
- `WhoCreatedMe.py`

Status: Archived to `backup/deprecated_runtime_scripts/` to keep active runtime root clean.

## Suggested Ignore/Delete List To Stop Runtime Khichdi
Ignore from normal operations:
- `demo.py`
- `EnhancedDemo.py`
- `QuickValidation.py`
- `FinalValidation.py`
- `StabilityRecoveryTest.py`
- `SelfReflect.py`
- `ValidateCreatorRecognition.py`
- `WhoCreatedMe.py`

Archive destination:
- `backup/deprecated_runtime_scripts/`
