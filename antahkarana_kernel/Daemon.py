"""Daemon.py - resilient supervisor for Project Anant runtime.

Supervises the single LiveConsciousness producer process.
If a crash or deadlock is detected, clears local caches and restarts with backoff.
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import json
import shutil
import signal
import subprocess
import time
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


ROOT = Path(__file__).resolve().parent
LIVE_SCRIPT = ROOT / "LiveConsciousness.py"
LIVE_HEARTBEAT = ROOT / "live_engine_state.json"
CACHE_PATHS = [ROOT / "__pycache__", ROOT / "evolution_vault" / "__pycache__", ROOT / "modules" / "__pycache__"]
FAILURE_LOG_PATH = ROOT / "evolution_vault" / "Failure_Log.jsonl"
UPTIME_STATE_PATH = ROOT / "evolution_vault" / "Continuous_Uptime.json"
ACTIVE_BASELINE_PATH = ROOT / "evolution_vault" / "Active_Baseline.json"
ACTIVE_BACKUPS_DIR = ROOT / "evolution_vault" / "active_backups"
ROLLBACK_LEARN_PATH = ROOT / "evolution_vault" / "Rollback_Learnings.json"
EVOLUTION_LOG_PATH = ROOT / "evolution_consciousness.log"
IMMORTALITY_TARGET_SECONDS = 72 * 60 * 60
MAINTENANCE_LOCK_PATH = ROOT / ".maintenance_lock"
STATE_LOCK_TIMEOUT_SECONDS = 10.0
DEADLOCK_THRESHOLD_SECONDS = 10.0
RESTART_DELAY_SECONDS = 5.0


@dataclass
class ProcessSpec:
    name: str
    command: list[str]
    heartbeat_path: Path
    heartbeat_timeout_seconds: int
    process: Optional[subprocess.Popen] = None
    output_thread: Optional[threading.Thread] = None


class EternalGuardian:
    """Simple process guardian with restart + deadlock recovery."""

    def __init__(self) -> None:
        self.python_exe = self._resolve_python_executable()
        self.boot_timestamp = time.time()
        self.wait_state_active = False
        self._log_lock = threading.RLock()
        self.uptime_state = self._load_uptime_state()
        self.last_uptime_heartbeat_at = 0.0
        self._ensure_uptime_initialized()
        self.specs: Dict[str, ProcessSpec] = {
            "live": ProcessSpec(
                name="live",
                command=[str(self.python_exe), str(LIVE_SCRIPT)],
                heartbeat_path=LIVE_HEARTBEAT,
                heartbeat_timeout_seconds=300,
            ),
        }
        self.shutdown = False
        self.heartbeat_interval_seconds = 60

    def _load_uptime_state(self) -> Dict[str, object]:
        if not UPTIME_STATE_PATH.exists():
            return {}
        try:
            return self._read_json_with_retry(UPTIME_STATE_PATH, default={})
        except Exception:
            return {}

    def _ensure_uptime_initialized(self) -> None:
        now = time.time()
        if not self.uptime_state:
            self.uptime_state = {
                "continuous_uptime_seconds": 0.0,
                "segment_started_at": now,
                "last_updated_at": now,
                "restart_count": 0,
                "last_restart_reason": None,
                "evolving_without_crashing": False,
                "target_seconds": IMMORTALITY_TARGET_SECONDS,
            }
        self.uptime_state.setdefault("segment_started_at", now)
        self.uptime_state.setdefault("last_updated_at", now)
        self.uptime_state.setdefault("restart_count", 0)
        self.uptime_state.setdefault("target_seconds", IMMORTALITY_TARGET_SECONDS)
        self.uptime_state.setdefault("evolving_without_crashing", False)
        self._save_uptime_state()

    def _save_uptime_state(self) -> None:
        self._write_json_with_retry(UPTIME_STATE_PATH, self.uptime_state)

    def _update_uptime_metrics(self) -> None:
        now = time.time()
        segment_start = float(self.uptime_state.get("segment_started_at", now))
        continuous_uptime = max(0.0, now - segment_start)
        target_seconds = float(self.uptime_state.get("target_seconds", IMMORTALITY_TARGET_SECONDS))
        success = continuous_uptime >= target_seconds

        self.uptime_state["continuous_uptime_seconds"] = continuous_uptime
        self.uptime_state["last_updated_at"] = now
        self.uptime_state["evolving_without_crashing"] = success
        self._save_uptime_state()

    def _due_for_uptime_heartbeat(self, now: float) -> bool:
        return self.last_uptime_heartbeat_at == 0.0 or (now - self.last_uptime_heartbeat_at) >= self.heartbeat_interval_seconds

    def _heartbeat_uptime(self) -> None:
        self._update_uptime_metrics()
        self.last_uptime_heartbeat_at = time.time()

    def _mark_restart(self, reason: str) -> None:
        now = time.time()
        previous_segment_start = float(self.uptime_state.get("segment_started_at", now))
        completed_segment = max(0.0, now - previous_segment_start)
        self.uptime_state["last_completed_segment_seconds"] = completed_segment
        self.uptime_state["segment_started_at"] = now
        self.uptime_state["last_updated_at"] = now
        self.uptime_state["continuous_uptime_seconds"] = 0.0
        self.uptime_state["evolving_without_crashing"] = False
        self.uptime_state["restart_count"] = int(self.uptime_state.get("restart_count", 0)) + 1
        self.uptime_state["last_restart_reason"] = reason
        self._save_uptime_state()

    def _resolve_python_executable(self) -> Path:
        # Use python.exe (not pythonw) so crashes and output remain observable.
        return Path(sys.executable)

    def _find_script_pids(self, script_name: str) -> list[int]:
        if os.name != "nt":
            return []

        powershell_command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-CimInstance Win32_Process | "
                "Where-Object { ($_.Name -in 'python.exe','pythonw.exe') -and $_.CommandLine -and $_.CommandLine -like '*"
                + script_name
                + "*' } | Select-Object -ExpandProperty ProcessId"
            ),
        ]

        try:
            result = subprocess.run(powershell_command, capture_output=True, text=True, timeout=10)
            pids: list[int] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    pid = int(line)
                except ValueError:
                    continue
                if pid > 0 and pid != os.getpid():
                    pids.append(pid)
            return pids
        except Exception:
            return []

    def _terminate_existing_live_processes(self) -> None:
        stale_pids = self._find_script_pids(LIVE_SCRIPT.name)
        for pid in stale_pids:
            self._write_evolution_log(f"[DAEMON] preflight terminating stale {LIVE_SCRIPT.name} pid={pid}")
            self._force_terminate_process(pid)

    def _live_state_lock_path(self) -> Path:
        return LIVE_HEARTBEAT.with_name(f"{LIVE_HEARTBEAT.name}.lock")

    def _contains_pain_protocol(self, payload: object) -> bool:
        if isinstance(payload, dict):
            for key, value in payload.items():
                if str(key).lower() in {"pain-protocol", "pain_protocol"}:
                    return True
                if self._contains_pain_protocol(value):
                    return True
            return False
        if isinstance(payload, list):
            return any(self._contains_pain_protocol(item) for item in payload)
        if isinstance(payload, str):
            normalized = payload.lower().replace("_", "-")
            return "pain-protocol" in normalized
        return False

    def _live_state_is_healthy(self) -> bool:
        if not LIVE_HEARTBEAT.exists():
            return True

        try:
            with LIVE_HEARTBEAT.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError:
            return False
        except OSError as exc:
            return not self._is_temporary_file_access_error(exc)

        if self._contains_pain_protocol(payload):
            return False

        return isinstance(payload, dict)

    def _quarantine_live_state(self, reason: str) -> None:
        for path in [LIVE_HEARTBEAT, self._live_state_lock_path()]:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
        self._write_evolution_log(f"[DAEMON] quarantined live state due to {reason}")

    def _same_script_running(self, script_name: str) -> bool:
        return len(self._find_script_pids(script_name)) > 0

    def _spawn(self, spec: ProcessSpec) -> None:
        if os.name == "nt":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            spec.process = subprocess.Popen(
                spec.command,
                cwd=str(ROOT),
                creationflags=flags,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                close_fds=True,
            )
        else:
            # Linux/macOS detach mode (nohup-like behavior).
            spec.process = subprocess.Popen(
                ["nohup", *spec.command],
                cwd=str(ROOT),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                preexec_fn=os.setsid,
                close_fds=True,
            )
        spec.output_thread = threading.Thread(target=self._drain_process_output, args=(spec,), daemon=True)
        spec.output_thread.start()

    def _drain_process_output(self, spec: ProcessSpec) -> None:
        process = spec.process
        if process is None or process.stdout is None:
            return

        self._write_evolution_log(f"[DAEMON] output capture started for {spec.name} (pid={process.pid})")
        try:
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                self._write_evolution_log(line.rstrip("\n"))
        except Exception as exc:
            self._write_evolution_log(f"[DAEMON] output capture failed for {spec.name}: {exc}")
        finally:
            try:
                process.stdout.close()
            except Exception:
                pass

    def _write_evolution_log(self, line: str) -> None:
        EVOLUTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with self._log_lock:
            with EVOLUTION_LOG_PATH.open("a", encoding="utf-8") as handle:
                handle.write(line if line.endswith("\n") else f"{line}\n")

    @contextmanager
    def _file_lock(self, target_path: Path):
        lock_path = target_path.with_name(f"{target_path.name}.lock")
        deadline = time.time() + STATE_LOCK_TIMEOUT_SECONDS
        delay = 0.05
        lock_fd = None

        while True:
            try:
                if lock_path.exists() and (time.time() - lock_path.stat().st_mtime) > STATE_LOCK_TIMEOUT_SECONDS:
                    try:
                        lock_path.unlink()
                    except OSError:
                        pass
                lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(lock_fd, f"{os.getpid()}|{time.time():.6f}".encode("utf-8"))
                break
            except FileExistsError:
                if time.time() >= deadline:
                    raise OSError(f"Timed out waiting for lock: {lock_path}")
                time.sleep(delay)
                delay = min(delay * 2, 0.5)

        try:
            yield
        finally:
            if lock_fd is not None:
                try:
                    os.close(lock_fd)
                except OSError:
                    pass
            try:
                lock_path.unlink()
            except OSError:
                pass

    def _read_json_with_retry(self, path: Path, default: Dict[str, object]) -> Dict[str, object]:
        delay = 0.05
        for attempt in range(5):
            try:
                with self._file_lock(path):
                    with path.open("r", encoding="utf-8") as handle:
                        return json.load(handle)
            except FileNotFoundError:
                return default.copy()
            except (OSError, json.JSONDecodeError):
                if attempt == 4:
                    return default.copy()
                time.sleep(delay)
                delay = min(delay * 2, 0.5)

        return default.copy()

    def _write_json_with_retry(self, path: Path, payload: Dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.tmp")
        delay = 0.05

        for attempt in range(5):
            try:
                with self._file_lock(path):
                    with temp_path.open("w", encoding="utf-8") as handle:
                        json.dump(payload, handle, indent=2)
                        handle.flush()
                        try:
                            os.fsync(handle.fileno())
                        except OSError:
                            pass
                    temp_path.replace(path)
                return
            except OSError as exc:
                if attempt == 4:
                    self._write_evolution_log(f"[DAEMON] failed to write {path.name}: {exc}")
                    raise
                time.sleep(delay)
                delay = min(delay * 2, 0.5)
            finally:
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        pass

    def _clear_cache(self) -> None:
        for path in CACHE_PATHS:
            if path.exists() and path.is_dir():
                shutil.rmtree(path, ignore_errors=True)

    def _record_failure_log(self, spec: ProcessSpec, reason: str) -> None:
        FAILURE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        heartbeat_age = None
        if spec.heartbeat_path.exists():
            heartbeat_age = time.time() - spec.heartbeat_path.stat().st_mtime

        event = {
            "timestamp": time.time(),
            "source": "Daemon.EternalGuardian",
            "process": spec.name,
            "reason": reason,
            "heartbeat_file": str(spec.heartbeat_path),
            "heartbeat_age_seconds": heartbeat_age,
            "pid": spec.process.pid if spec.process else None,
            "returncode": spec.process.poll() if spec.process else None,
        }

        with FAILURE_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")
        self._write_evolution_log(f"[DAEMON] {spec.name} restart reason: {reason}")

    def _heartbeat_stale(self, path: Path, timeout_seconds: int) -> bool:
        if not path.exists():
            return False
        effective_timeout = max(timeout_seconds, DEADLOCK_THRESHOLD_SECONDS)
        delay = 0.05
        for attempt in range(5):
            try:
                age = time.time() - path.stat().st_mtime
                return age > effective_timeout
            except OSError as exc:
                if self._is_temporary_file_access_error(exc):
                    return False
                if attempt == 4:
                    return False
                time.sleep(delay)
                delay = min(delay * 2, 0.5)
        return False

    def _is_temporary_file_access_error(self, exc: OSError) -> bool:
        message = str(exc).lower()
        temporary_markers = (
            "file access",
            "permission denied",
            "access is denied",
            "being used by another process",
            "resource busy",
            "temporarily unavailable",
            "sharing violation",
        )
        return any(marker in message for marker in temporary_markers)

    def _maintenance_locked(self) -> bool:
        return MAINTENANCE_LOCK_PATH.exists()

    def _stop_managed_process(self, spec: ProcessSpec) -> None:
        if spec.process is None or spec.process.poll() is not None:
            return
        try:
            if os.name == "nt":
                spec.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(spec.process.pid), signal.SIGTERM)
        except Exception:
            pass
        try:
            self._force_terminate_process(spec.process.pid)
        except Exception:
            pass
        spec.process = None

    def _force_terminate_process(self, pid: int) -> None:
        """Force terminate a hung process tree using OS-level commands."""
        if pid <= 0:
            return

        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/T", "/F"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except Exception as exc:
                self._write_evolution_log(f"[DAEMON] taskkill failed for pid={pid}: {exc}")
        else:
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except Exception:
                try:
                    os.kill(pid, signal.SIGKILL)
                except Exception:
                    pass

    def _needs_restart(self, spec: ProcessSpec) -> bool:
        if spec.process is None:
            return True
        if spec.process.poll() is not None:
            return True
        if self._heartbeat_stale(spec.heartbeat_path, spec.heartbeat_timeout_seconds):
            return True
        return False

    def _restart(self, spec: ProcessSpec, reason: str) -> None:
        reason = self._rollback_and_learn(spec, reason)
        self._record_failure_log(spec, reason)
        self._mark_restart(reason)
        self._clear_cache()
        if spec.process is not None and spec.process.poll() is None:
            try:
                if os.name == "nt":
                    spec.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    os.killpg(os.getpgid(spec.process.pid), signal.SIGTERM)
            except Exception:
                pass
            try:
                self._force_terminate_process(spec.process.pid)
            except Exception:
                pass
        self._write_evolution_log(f"[DAEMON] delaying restart for {spec.name} after {reason}")
        time.sleep(RESTART_DELAY_SECONDS)
        self._spawn(spec)
        print(f"[GUARDIAN] restarted {spec.name} due to {reason}")

    def _rollback_and_learn(self, spec: ProcessSpec, reason: str) -> str:
        """If active patching likely caused a crash, rollback latest backup and persist a learned signature."""
        baseline = self._read_json_with_retry(ACTIVE_BASELINE_PATH, default={})
        target_file = Path(str(baseline.get("target_file", "")))
        target_module = str(baseline.get("target_module", ""))
        if not target_file or not target_file.exists() or not target_module:
            return reason

        lower_reason = reason.lower()
        if "crash" not in lower_reason and "deadlock" not in lower_reason:
            return reason

        recent = self._read_recent_failures(limit=8)
        patch_signal = any(
            str(event.get("source", "")).startswith("InferenceLoop.apply_evolution_patch")
            or target_module in str(event.get("target_module", ""))
            for event in recent
        )
        if not patch_signal:
            return reason

        restored_backup = self._restore_latest_backup(target_file)
        if not restored_backup:
            return reason

        self._persist_rollback_learning(
            process_name=spec.name,
            reason=reason,
            target_module=target_module,
            target_file=str(target_file),
            backup_file=str(restored_backup),
            recent_failures=recent,
        )
        self._write_evolution_log(
            f"[DAEMON] rollback-and-learn restored {target_file.name} from {restored_backup.name}"
        )
        return f"{reason}|rollback_and_learn"

    def _read_recent_failures(self, limit: int = 8) -> list[Dict[str, object]]:
        if not FAILURE_LOG_PATH.exists():
            return []
        rows: list[Dict[str, object]] = []
        try:
            with FAILURE_LOG_PATH.open("r", encoding="utf-8") as handle:
                lines = [line.strip() for line in handle if line.strip()]
            for line in lines[-limit:]:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except Exception:
            return []
        return rows

    def _restore_latest_backup(self, target_file: Path) -> Optional[Path]:
        if not ACTIVE_BACKUPS_DIR.exists():
            return None
        pattern = f"{target_file.stem}_*.bak.py"
        backups = sorted(ACTIVE_BACKUPS_DIR.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
        if not backups:
            return None
        latest_backup = backups[0]
        try:
            shutil.copy2(latest_backup, target_file)
            return latest_backup
        except Exception as exc:
            self._write_evolution_log(f"[DAEMON] rollback restore failed for {target_file.name}: {exc}")
            return None

    def _persist_rollback_learning(
        self,
        process_name: str,
        reason: str,
        target_module: str,
        target_file: str,
        backup_file: str,
        recent_failures: list[Dict[str, object]],
    ) -> None:
        learning_payload = {
            "timestamp": time.time(),
            "process": process_name,
            "reason": reason,
            "target_module": target_module,
            "target_file": target_file,
            "backup_file": backup_file,
            "learned_signature": f"{target_module}:{reason}"[:240],
            "recent_failures": recent_failures,
        }

        existing = self._read_json_with_retry(ROLLBACK_LEARN_PATH, default={})
        entries = existing.get("entries", []) if isinstance(existing.get("entries", []), list) else []
        entries.append(learning_payload)
        existing["entries"] = entries[-200:]
        existing["last_updated_at"] = time.time()
        self._write_json_with_retry(ROLLBACK_LEARN_PATH, existing)

    def start(self) -> None:
        print("[GUARDIAN] eternal supervision active")
        self._terminate_existing_live_processes()

        while not self.shutdown:
            now = time.time()
            if self._due_for_uptime_heartbeat(now):
                self._heartbeat_uptime()

            if not self._live_state_is_healthy():
                self._quarantine_live_state("corrupted_or_pain_protocol_state")
                time.sleep(RESTART_DELAY_SECONDS)
                continue

            if self._maintenance_locked():
                if not self.wait_state_active:
                    for spec in self.specs.values():
                        self._stop_managed_process(spec)
                    self.wait_state_active = True
                    print("[GUARDIAN] maintenance lock detected - WAIT state active")
                time.sleep(4)
                continue

            if self.wait_state_active:
                self.wait_state_active = False
                print("[GUARDIAN] maintenance lock cleared - supervision resumed")

            for spec in self.specs.values():
                if spec.process is None:
                    if self._same_script_running(LIVE_SCRIPT.name):
                        self._write_evolution_log(f"[DAEMON] {LIVE_SCRIPT.name} already running; skipping duplicate spawn")
                        time.sleep(RESTART_DELAY_SECONDS)
                        continue
                    self._spawn(spec)
                    print(f"[GUARDIAN] started {spec.name}")
                    continue
                if self._needs_restart(spec):
                    reason = "crash_or_deadlock"
                    self._restart(spec, reason)
            time.sleep(4)

    def stop(self) -> None:
        self.shutdown = True
        for spec in self.specs.values():
            if spec.process is not None and spec.process.poll() is None:
                try:
                    spec.process.kill()
                except Exception:
                    pass


def main() -> None:
    guardian = EternalGuardian()
    try:
        guardian.start()
    except KeyboardInterrupt:
        guardian.stop()


if __name__ == "__main__":
    main()
