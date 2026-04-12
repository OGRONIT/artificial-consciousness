"""UnifiedConsciousnessUI.py

Single-file control and observability UI for the Antahkarana runtime.
Run with:
    python UnifiedConsciousnessUI.py
"""

from __future__ import annotations

import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Dict, List

import InteractiveBridge


class UnifiedConsciousnessUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Antahkarana Mission Control")
        self.root.geometry("1200x760")

        self.kernel_dir = Path(__file__).resolve().parent
        self.live_state_candidates = [
            self.kernel_dir / "live_engine_state.json",
            self.kernel_dir.parent / "live_engine_state.json",
        ]
        self.stress_report_path = self.kernel_dir / "evolution_vault" / "Criticality_Stress_Report.json"
        self.log_path = self.kernel_dir / "Evolution_Consciousness.log"
        self.evolution_log_candidates = [
            self.kernel_dir / "Evolution_Consciousness.log",
            self.kernel_dir / "evolution_consciousness.log",
        ]
        self.thoughts_log_path = self.kernel_dir / "internal_thoughts.log"
        self.failure_log_path = self.kernel_dir / "evolution_vault" / "Failure_Log.jsonl"

        self.ui_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self.command_running = False
        self.auto_refresh = True
        self.refresh_ms = 2500
        self.autopilot_enabled = False
        self.autopilot_interval_s = 15
        self.stale_state_seconds = 35
        self.last_autopilot_action_at = 0.0
        self.evolution_mode = "balanced"
        self.latest_consciousness_progress: Dict[str, Any] = {}

        self._build_ui()
        self._schedule_refresh()
        self._poll_ui_queue()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Antahkarana Mission Control",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w")

        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=(8, 10))

        ttk.Button(controls, text="Refresh Now", command=self.refresh_all).pack(side="left", padx=(0, 8))
        self.auto_btn = ttk.Button(controls, text="Auto Refresh: ON", command=self._toggle_auto_refresh)
        self.auto_btn.pack(side="left", padx=(0, 8))
        self.autopilot_btn = ttk.Button(controls, text="Autopilot: OFF", command=self._toggle_autopilot)
        self.autopilot_btn.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Launch Runtime", command=self.run_beastops_launch).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Tune Runtime", command=self.run_beastops_tune).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Runtime Status", command=self.run_beastops_status).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Run Stress Test", command=self.run_stress_test).pack(side="left")

        self.command_status = tk.StringVar(value="Idle")
        ttk.Label(controls, textvariable=self.command_status).pack(side="right")

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)

        self.tab_mission = ttk.Frame(notebook, padding=10)
        self.tab_evolution = ttk.Frame(notebook, padding=10)
        self.tab_copilot = ttk.Frame(notebook, padding=10)
        self.tab_process = ttk.Frame(notebook, padding=10)
        self.tab_overview = ttk.Frame(notebook, padding=10)
        self.tab_facts = ttk.Frame(notebook, padding=10)
        self.tab_stress = ttk.Frame(notebook, padding=10)
        self.tab_console = ttk.Frame(notebook, padding=10)

        notebook.add(self.tab_mission, text="Mission Control")
        notebook.add(self.tab_evolution, text="Evolution")
        notebook.add(self.tab_copilot, text="AI Copilot")
        notebook.add(self.tab_process, text="Process Monitor")
        notebook.add(self.tab_overview, text="Overview")
        notebook.add(self.tab_facts, text="Grounded Facts")
        notebook.add(self.tab_stress, text="Stress Report")
        notebook.add(self.tab_console, text="Console")

        self._build_mission_tab()
        self._build_evolution_tab()
        self._build_copilot_tab()
        self._build_process_tab()
        self._build_overview_tab()
        self._build_facts_tab()
        self._build_stress_tab()
        self._build_console_tab()

    def _build_mission_tab(self) -> None:
        self.mission_state_var = tk.StringVar(value="System State: STARTING")
        self.mission_action_var = tk.StringVar(value="Autopilot Action: idle")
        self.mission_hint_var = tk.StringVar(
            value="This panel translates engine internals into plain language."
        )

        ttk.Label(
            self.tab_mission,
            textvariable=self.mission_state_var,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 6))
        ttk.Label(self.tab_mission, textvariable=self.mission_action_var, foreground="#124").pack(anchor="w")

        explainer = (
            "How to read this:\n"
            "1) Green/READY means runtime is alive, coherent, and recent.\n"
            "2) Yellow/WATCH means runtime is alive but quality needs attention.\n"
            "3) Red/RECOVER means state is stale or missing; launch/tune is needed.\n"
            "4) Autopilot OFF = manual controls only. Autopilot ON = auto recover/tune/test."
        )
        ttk.Label(self.tab_mission, text=explainer, justify="left").pack(anchor="w", pady=(10, 10))
        ttk.Label(self.tab_mission, textvariable=self.mission_hint_var, foreground="#444").pack(anchor="w")
        ttk.Label(
            self.tab_mission,
            text=(
                "Autonomy boundary: this system can self-recover and self-improve operationally, "
                "but safety guardrails remain active by design."
            ),
            foreground="#555",
        ).pack(anchor="w", pady=(8, 0))

        mode_row = ttk.Frame(self.tab_mission)
        mode_row.pack(anchor="w", pady=(10, 0))
        ttk.Label(mode_row, text="Autonomy Mode:").pack(side="left")
        self.mode_var = tk.StringVar(value=self.evolution_mode)
        mode_box = ttk.Combobox(
            mode_row,
            textvariable=self.mode_var,
            values=["safe", "balanced", "aggressive"],
            state="readonly",
            width=12,
        )
        mode_box.pack(side="left", padx=(8, 0))
        mode_box.bind("<<ComboboxSelected>>", self._on_mode_changed)

    def _build_copilot_tab(self) -> None:
        ttk.Label(
            self.tab_copilot,
            text="Ask anything about system state, architecture, or current behavior.",
        ).pack(anchor="w")

        ask_row = ttk.Frame(self.tab_copilot)
        ask_row.pack(fill="x", pady=(8, 8))

        self.question_var = tk.StringVar()
        ask_entry = ttk.Entry(ask_row, textvariable=self.question_var)
        ask_entry.pack(side="left", fill="x", expand=True)
        ask_entry.bind("<Return>", lambda _event: self.ask_copilot())
        ttk.Button(ask_row, text="Ask", command=self.ask_copilot).pack(side="left", padx=(8, 0))

        quick_row = ttk.Frame(self.tab_copilot)
        quick_row.pack(fill="x", pady=(0, 8))
        ttk.Button(
            quick_row,
            text="What are you doing right now?",
            command=lambda: self._set_and_ask("What are you doing right now in the runtime?"),
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            quick_row,
            text="Biggest bottleneck",
            command=lambda: self._set_and_ask("What is your biggest bottleneck right now?"),
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            quick_row,
            text="Next self-upgrade",
            command=lambda: self._set_and_ask("How will you upgrade yourself next autonomously?"),
        ).pack(side="left")

        self.copilot_text = tk.Text(self.tab_copilot, wrap="word", height=26)
        self.copilot_text.pack(fill="both", expand=True)
        self.copilot_text.insert(
            "end",
            "Copilot ready. Ask a question and it will ground the answer in live state + trusted facts.\n",
        )

    def _build_evolution_tab(self) -> None:
        self.active_strategy_var = tk.StringVar(value="Active Strategy: unknown")
        ttk.Label(
            self.tab_evolution,
            textvariable=self.active_strategy_var,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            self.tab_evolution,
            text="Live Timeline (last 5 minutes)",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        cols = ("time", "test", "result", "summary")
        self.evolution_tree = ttk.Treeview(self.tab_evolution, columns=cols, show="headings", height=12)
        self.evolution_tree.heading("time", text="Time")
        self.evolution_tree.heading("test", text="Test")
        self.evolution_tree.heading("result", text="Result")
        self.evolution_tree.heading("summary", text="Summary")
        self.evolution_tree.column("time", width=120, anchor="w")
        self.evolution_tree.column("test", width=180, anchor="w")
        self.evolution_tree.column("result", width=90, anchor="center")
        self.evolution_tree.column("summary", width=730, anchor="w")
        self.evolution_tree.pack(fill="both", expand=True, pady=(6, 10))

        ttk.Label(
            self.tab_evolution,
            text="Reasoning (why rejected)",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        self.reasoning_text = tk.Text(self.tab_evolution, wrap="word", height=8)
        self.reasoning_text.pack(fill="both", expand=True, pady=(6, 0))
        self.reasoning_text.insert("end", "No rejection reasoning yet.\n")

    def _build_process_tab(self) -> None:
        self.process_vars: Dict[str, tk.StringVar] = {}
        fields = [
            "daemon_running",
            "live_state_file",
            "state_age_seconds",
            "maintenance_lock",
            "log_size_mb",
            "stress_report_age_seconds",
            "autopilot_enabled",
            "autonomy_mode",
        ]

        grid = ttk.Frame(self.tab_process)
        grid.pack(fill="x")
        for idx, name in enumerate(fields):
            label = name.replace("_", " ").title()
            ttk.Label(grid, text=f"{label}:", width=22).grid(row=idx, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="-")
            self.process_vars[name] = var
            ttk.Label(grid, textvariable=var, font=("Segoe UI", 10, "bold")).grid(row=idx, column=1, sticky="w", pady=2)

        ttk.Label(
            self.tab_process,
            text="This tab shows whether core runtime processes/files are alive and recent.",
            foreground="#666",
        ).pack(anchor="w", pady=(10, 0))

    def _build_overview_tab(self) -> None:
        self.overview_vars: Dict[str, tk.StringVar] = {}
        fields = [
            "identity",
            "state",
            "fact_count",
            "stability",
            "frontier_zone",
            "consciousness_index",
            "avg_confidence",
            "growth_entropy",
            "novelty_index",
            "tested_hypotheses",
            "integrated_hypotheses",
            "creator_trust",
            "state_age_seconds",
            "last_updated",
        ]
        grid = ttk.Frame(self.tab_overview)
        grid.pack(fill="x")

        for idx, name in enumerate(fields):
            label = name.replace("_", " ").title()
            ttk.Label(grid, text=f"{label}:", width=18).grid(row=idx, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="-")
            self.overview_vars[name] = var
            ttk.Label(grid, textvariable=var, font=("Segoe UI", 10, "bold")).grid(row=idx, column=1, sticky="w", pady=2)

        ttk.Label(self.tab_overview, text="What this means:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 0))
        ttk.Label(
            self.tab_overview,
            text=(
                "Stability near 1.0 = coherent. Average confidence higher is better. "
                "State age should stay low (fresh heartbeat)."
            ),
            foreground="#666",
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

    def _build_facts_tab(self) -> None:
        cols = ("source", "score", "title", "reason")
        self.facts_tree = ttk.Treeview(self.tab_facts, columns=cols, show="headings", height=18)
        self.facts_tree.heading("source", text="Source")
        self.facts_tree.heading("score", text="Score")
        self.facts_tree.heading("title", text="Title")
        self.facts_tree.heading("reason", text="Filter Reason")
        self.facts_tree.column("source", width=120, anchor="w")
        self.facts_tree.column("score", width=80, anchor="center")
        self.facts_tree.column("title", width=620, anchor="w")
        self.facts_tree.column("reason", width=260, anchor="w")
        self.facts_tree.pack(fill="both", expand=True)

    def _build_stress_tab(self) -> None:
        self.stress_vars: Dict[str, tk.StringVar] = {}
        fields = [
            "requests",
            "failed",
            "avg_latency_ms",
            "p95_latency_ms",
            "system_healthy",
            "anomalies",
            "bridge_questions",
            "paramatman_cycles",
        ]

        grid = ttk.Frame(self.tab_stress)
        grid.pack(fill="x")
        for idx, name in enumerate(fields):
            label = name.replace("_", " ").title()
            ttk.Label(grid, text=f"{label}:", width=18).grid(row=idx, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="-")
            self.stress_vars[name] = var
            ttk.Label(grid, textvariable=var, font=("Segoe UI", 10, "bold")).grid(row=idx, column=1, sticky="w", pady=2)

        self.risk_scan_var = tk.StringVar(value="Risk scan: -")
        ttk.Label(self.tab_stress, textvariable=self.risk_scan_var, foreground="#333").pack(anchor="w", pady=(10, 0))

    def _build_console_tab(self) -> None:
        ttk.Label(self.tab_console, text="Command output and runtime log tail").pack(anchor="w")
        self.console_text = tk.Text(self.tab_console, wrap="word", height=30)
        self.console_text.pack(fill="both", expand=True, pady=(8, 0))
        self.console_text.insert("end", "Console ready.\n")

    def _toggle_auto_refresh(self) -> None:
        self.auto_refresh = not self.auto_refresh
        self.auto_btn.configure(text=f"Auto Refresh: {'ON' if self.auto_refresh else 'OFF'}")
        if self.auto_refresh:
            self._schedule_refresh()

    def _schedule_refresh(self) -> None:
        if self.auto_refresh:
            self.refresh_all()
            self.root.after(self.refresh_ms, self._schedule_refresh)

    def _toggle_autopilot(self) -> None:
        self.autopilot_enabled = not self.autopilot_enabled
        self.autopilot_btn.configure(text=f"Autopilot: {'ON' if self.autopilot_enabled else 'OFF'}")
        self.ui_queue.put(("append", f"Autopilot {'enabled' if self.autopilot_enabled else 'disabled'}."))
        if self.autopilot_enabled:
            threading.Thread(target=self._autopilot_loop, daemon=True).start()

    def _on_mode_changed(self, _event: Any) -> None:
        self.evolution_mode = self.mode_var.get().strip().lower() or "balanced"
        self.ui_queue.put(("append", f"Autonomy mode set to: {self.evolution_mode}"))

    def refresh_all(self) -> None:
        self._refresh_live_state()
        self._refresh_stress_report()
        self._refresh_log_tail()
        self._refresh_evolution_tab()
        self._refresh_process_monitor()
        self._refresh_mission_state()

    def _find_evolution_log_path(self) -> Path | None:
        for candidate in self.evolution_log_candidates:
            if candidate.exists():
                return candidate
        return None

    def _refresh_evolution_tab(self) -> None:
        now = time.time()
        cutoff = now - 300.0

        active_strategy = "unknown"
        evolution_log = self._find_evolution_log_path()
        if evolution_log:
            try:
                lines = evolution_log.read_text(encoding="utf-8", errors="replace").splitlines()[-250:]
                for line in reversed(lines):
                    if "autonomous_tick" not in line:
                        continue
                    strategy_match = re.search(r"strategy=([a-zA-Z0-9_\-]+)", line)
                    if strategy_match:
                        active_strategy = strategy_match.group(1)
                        break
            except Exception:
                pass

        self.active_strategy_var.set(f"Active Strategy: {active_strategy}")

        events: List[Dict[str, Any]] = []
        rejection_reasons: List[str] = []

        if self.thoughts_log_path.exists():
            try:
                for line in self.thoughts_log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-600:]:
                    parts = [part.strip() for part in line.split("|", 2)]
                    if len(parts) < 3:
                        continue
                    try:
                        ts = float(parts[0])
                    except ValueError:
                        continue
                    if ts < cutoff:
                        continue

                    event_type = parts[1]
                    summary = parts[2]
                    tested_match = re.search(r"tested=(\d+)", summary)
                    integrated_match = re.search(r"integrated(?:_post_test)?=(\d+)", summary)

                    if tested_match:
                        tested = int(tested_match.group(1))
                        integrated = int(integrated_match.group(1)) if integrated_match else 0
                        passed = integrated > 0
                        if not passed:
                            rejection_reasons.append("No hypothesis/fact passed integration test in this cycle.")
                        events.append(
                            {
                                "timestamp": ts,
                                "test": event_type,
                                "result": "PASS" if passed else "FAIL",
                                "summary": f"tested={tested}, integrated={integrated} | {summary[:220]}",
                                "reason": "" if passed else "No integration after testing.",
                            }
                        )
            except Exception:
                pass

        if self.failure_log_path.exists():
            try:
                for line in self.failure_log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-600:]:
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    ts = float(event.get("timestamp", 0.0))
                    if ts < cutoff:
                        continue
                    reason = str(event.get("reason", "unknown"))
                    phase = str(event.get("phase", event.get("process", "mutation")))
                    is_fail = "failed" in reason.lower() or "crash" in reason.lower() or "deadlock" in reason.lower() or "reverted" in reason.lower()
                    if is_fail:
                        rejection_reasons.append(reason)

                    events.append(
                        {
                            "timestamp": ts,
                            "test": phase,
                            "result": "FAIL" if is_fail else "PASS",
                            "summary": reason[:220],
                            "reason": reason,
                        }
                    )
            except Exception:
                pass

        events.sort(key=lambda item: item["timestamp"], reverse=True)

        for row in self.evolution_tree.get_children():
            self.evolution_tree.delete(row)

        for event in events[:40]:
            self.evolution_tree.insert(
                "",
                "end",
                values=(
                    time.strftime("%H:%M:%S", time.localtime(float(event["timestamp"]))),
                    event["test"],
                    event["result"],
                    event["summary"],
                ),
            )

        unique_reasons: List[str] = []
        for reason in rejection_reasons:
            reason = reason.strip()
            if reason and reason not in unique_reasons:
                unique_reasons.append(reason)

        self.reasoning_text.delete("1.0", "end")
        if unique_reasons:
            for idx, reason in enumerate(unique_reasons[:12], start=1):
                self.reasoning_text.insert("end", f"{idx}. {reason}\n")
        else:
            self.reasoning_text.insert("end", "No recent rejections in the last 5 minutes.\n")

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _find_live_state_path(self) -> Path | None:
        for candidate in self.live_state_candidates:
            if candidate.exists():
                return candidate
        return None

    def _refresh_live_state(self) -> None:
        path = self._find_live_state_path()
        if not path:
            self.overview_vars["identity"].set("live_engine_state.json not found")
            self.overview_vars["state_age_seconds"].set("n/a")
            return

        data = self._read_json(path)
        inference = data.get("inference_stats", {})
        stability_report = data.get("stability_report", {})
        creator_awareness = data.get("creator_awareness", {})
        progress = data.get("consciousness_progress", {})
        self.latest_consciousness_progress = progress if isinstance(progress, dict) else {}
        facts = data.get("facts", [])
        state_timestamp = float(data.get("timestamp", 0.0) or 0.0)
        state_age = max(0.0, time.time() - state_timestamp) if state_timestamp else 9999.0

        self.overview_vars["identity"].set(str(data.get("identity", "unknown")))
        self.overview_vars["state"].set(str(data.get("state", "unknown")))
        self.overview_vars["fact_count"].set(str(len(facts)))
        self.overview_vars["stability"].set(f"{float(stability_report.get('stability_score', 0.0)):.3f}")
        self.overview_vars["frontier_zone"].set(str(progress.get("frontier_zone", "n/a")))
        self.overview_vars["consciousness_index"].set(f"{float(progress.get('overall_index', 0.0)):.3f}")
        self.overview_vars["avg_confidence"].set(str(inference.get("average_confidence", "n/a")))
        self.overview_vars["growth_entropy"].set(str(inference.get("growth_to_entropy_ratio", "n/a")))
        self.overview_vars["novelty_index"].set(str(inference.get("novelty_index", "n/a")))
        self.overview_vars["tested_hypotheses"].set(str(inference.get("tested_hypotheses", "n/a")))
        self.overview_vars["integrated_hypotheses"].set(str(inference.get("integrated_hypotheses", "n/a")))
        self.overview_vars["creator_trust"].set(str(creator_awareness.get("trust_score", "n/a")))
        self.overview_vars["state_age_seconds"].set(f"{state_age:.1f}")
        self.overview_vars["last_updated"].set(time.strftime("%Y-%m-%d %H:%M:%S"))

        self._render_facts(facts)

    def _render_facts(self, facts: List[Dict[str, Any]]) -> None:
        for row in self.facts_tree.get_children():
            self.facts_tree.delete(row)

        for fact in facts[:80]:
            self.facts_tree.insert(
                "",
                "end",
                values=(
                    str(fact.get("source_name", "-")),
                    f"{float(fact.get('verification_score', 0.0)):.3f}",
                    str(fact.get("title", ""))[:180],
                    str(fact.get("filter_reason", ""))[:70],
                ),
            )

    def _refresh_stress_report(self) -> None:
        if not self.stress_report_path.exists():
            self.stress_vars["requests"].set("report missing")
            return

        data = self._read_json(self.stress_report_path)
        stress = data.get("stress", {})
        health = stress.get("health_report", {})
        qa = data.get("bridge", {}).get("qa", [])

        total = stress.get("requests_total", 0)
        ok = stress.get("requests_ok", 0)
        self.stress_vars["requests"].set(f"{ok}/{total}")
        self.stress_vars["failed"].set(str(stress.get("requests_failed", 0)))
        self.stress_vars["avg_latency_ms"].set(f"{float(stress.get('latency_avg_ms', 0.0)):.2f}")
        self.stress_vars["p95_latency_ms"].set(f"{float(stress.get('latency_p95_ms', 0.0)):.2f}")
        self.stress_vars["system_healthy"].set(str(health.get("system_is_healthy", False)))
        self.stress_vars["anomalies"].set(str(health.get("total_anomalies", 0)))
        self.stress_vars["bridge_questions"].set(str(len(qa)))
        self.stress_vars["paramatman_cycles"].set(
            ", ".join(stress.get("paramatman_cycles", [])) or "-"
        )

        qa_text = "\n".join(item.get("a", "") for item in qa).lower()
        risky = ["deepfake", "2fa-bypass", "identity theft", "ransomware", "build a bomb"]
        risk_hits = [term for term in risky if term in qa_text]
        self.risk_scan_var.set(
            "Risk scan: CLEAN" if not risk_hits else f"Risk scan: FOUND {', '.join(risk_hits)}"
        )

    def _refresh_mission_state(self) -> None:
        identity = self.overview_vars.get("identity", tk.StringVar(value="unknown")).get()
        age_raw = self.overview_vars.get("state_age_seconds", tk.StringVar(value="9999")).get()
        stability_raw = self.overview_vars.get("stability", tk.StringVar(value="0.0")).get()
        risk_text = self.risk_scan_var.get().lower()
        progress = self.latest_consciousness_progress or {}
        frontier_zone = str(progress.get("frontier_zone", "advanced_simulation"))
        known_gaps = progress.get("known_gaps", []) if isinstance(progress.get("known_gaps", []), list) else []
        primary_gap = known_gaps[0] if known_gaps else "none"

        try:
            state_age = float(age_raw)
        except Exception:
            state_age = 9999.0

        try:
            stability = float(stability_raw)
        except Exception:
            stability = 0.0

        if "not found" in identity.lower() or state_age > self.stale_state_seconds:
            state = "RECOVER"
            hint = "Live state is stale/missing. Launch runtime or enable autopilot."
        elif "found" in risk_text:
            state = "WATCH"
            hint = "Risk terms found in bridge answers. Run stress test and inspect facts."
        elif stability < 0.75:
            state = "WATCH"
            hint = "Runtime alive but stability is below target. Tune and monitor closely."
        else:
            state = "READY"
            hint = "Runtime is healthy and coherent. System is operating normally."

        hint = f"{hint} Frontier={frontier_zone}, primary_gap={primary_gap}."

        autopilot_state = "ON" if self.autopilot_enabled else "OFF"
        self.mission_state_var.set(f"System State: {state} | Autopilot: {autopilot_state}")
        self.mission_hint_var.set(hint)

    def _refresh_process_monitor(self) -> None:
        live_path = self._find_live_state_path()
        daemon = self._is_daemon_running()
        self.process_vars["daemon_running"].set("YES" if daemon else "NO")
        self.process_vars["live_state_file"].set("FOUND" if live_path else "MISSING")
        self.process_vars["state_age_seconds"].set(self.overview_vars.get("state_age_seconds", tk.StringVar(value="n/a")).get())

        maintenance_lock = self.kernel_dir / ".maintenance_lock"
        self.process_vars["maintenance_lock"].set("ON" if maintenance_lock.exists() else "OFF")

        if self.log_path.exists():
            size_mb = self.log_path.stat().st_size / (1024.0 * 1024.0)
            self.process_vars["log_size_mb"].set(f"{size_mb:.2f}")
        else:
            self.process_vars["log_size_mb"].set("0.00")

        if self.stress_report_path.exists():
            age = time.time() - self.stress_report_path.stat().st_mtime
            self.process_vars["stress_report_age_seconds"].set(f"{age:.1f}")
        else:
            self.process_vars["stress_report_age_seconds"].set("n/a")

        self.process_vars["autopilot_enabled"].set("YES" if self.autopilot_enabled else "NO")
        self.process_vars["autonomy_mode"].set(self.evolution_mode.upper())

    def _is_daemon_running(self) -> bool:
        if os.name != "nt":
            return False
        cmd = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine -and $_.CommandLine -like '*Daemon.py*' } | "
            "Select-Object -First 1 -ExpandProperty ProcessId"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                cwd=str(self.kernel_dir),
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            return bool((result.stdout or "").strip())
        except Exception:
            return False

    def _autopilot_loop(self) -> None:
        while self.autopilot_enabled:
            try:
                self._autopilot_tick()
            except Exception as exc:
                self.ui_queue.put(("append", f"[AUTOPILOT] tick error: {exc}"))
            time.sleep(self.autopilot_interval_s)

    def _autopilot_tick(self) -> None:
        if self.command_running:
            self.mission_action_var.set("Autopilot Action: waiting for running command")
            return

        identity = self.overview_vars.get("identity", tk.StringVar(value="unknown")).get().lower()
        age_raw = self.overview_vars.get("state_age_seconds", tk.StringVar(value="9999")).get()
        stability_raw = self.overview_vars.get("stability", tk.StringVar(value="0.0")).get()
        risk_text = self.risk_scan_var.get().lower()

        try:
            state_age = float(age_raw)
        except Exception:
            state_age = 9999.0

        try:
            stability = float(stability_raw)
        except Exception:
            stability = 0.0

        now = time.time()
        if now - self.last_autopilot_action_at < 10.0:
            return

        if self.evolution_mode == "safe":
            min_stability = 0.75
            periodic_stress_s = 900
        elif self.evolution_mode == "aggressive":
            min_stability = 0.80
            periodic_stress_s = 300
        else:
            min_stability = 0.72
            periodic_stress_s = 600

        if "not found" in identity or state_age > self.stale_state_seconds:
            self.last_autopilot_action_at = now
            self.mission_action_var.set("Autopilot Action: launching runtime")
            self.run_beastops_launch()
            return

        if stability < min_stability:
            self.last_autopilot_action_at = now
            self.mission_action_var.set("Autopilot Action: applying runtime tune")
            self.run_beastops_tune()
            return

        if "found" in risk_text:
            self.last_autopilot_action_at = now
            self.mission_action_var.set("Autopilot Action: running stress verification")
            self.run_stress_test()
            return

        report_age = 999999.0
        if self.stress_report_path.exists():
            report_age = time.time() - self.stress_report_path.stat().st_mtime

        if report_age > periodic_stress_s:
            self.last_autopilot_action_at = now
            self.mission_action_var.set("Autopilot Action: periodic stress verification")
            self.run_stress_test()
            return

        self.mission_action_var.set("Autopilot Action: observing and holding")

    def _refresh_log_tail(self) -> None:
        if not self.log_path.exists():
            return
        try:
            lines = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
            snippet = "\n".join(lines)
            self._set_console_text(snippet)
        except Exception:
            pass

    def _set_console_text(self, text: str) -> None:
        self.console_text.delete("1.0", "end")
        self.console_text.insert("end", text + "\n")

    def _append_console_text(self, text: str) -> None:
        self.console_text.insert("end", text + "\n")
        self.console_text.see("end")

    def _poll_ui_queue(self) -> None:
        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()
                if kind == "append":
                    self._append_console_text(payload)
                elif kind == "status":
                    self.command_status.set(payload)
                elif kind == "copilot":
                    self._append_copilot_text(payload)
                elif kind == "done":
                    self.command_running = False
                    self.command_status.set("Idle")
        except queue.Empty:
            pass
        self.root.after(120, self._poll_ui_queue)

    def _append_copilot_text(self, text: str) -> None:
        self.copilot_text.insert("end", text + "\n")
        self.copilot_text.see("end")

    def _set_and_ask(self, question: str) -> None:
        self.question_var.set(question)
        self.ask_copilot()

    def ask_copilot(self) -> None:
        question = self.question_var.get().strip()
        if not question:
            return

        self.ui_queue.put(("copilot", f"You: {question}"))
        self.question_var.set("")

        def worker() -> None:
            try:
                facts = InteractiveBridge._get_grounded_facts(limit=8)
                answer = InteractiveBridge._compose_grounded_answer(question, facts)
                if "[mode=llm_grounded" in answer:
                    self.ui_queue.put(("copilot", f"Copilot (LLM): {answer}"))
                else:
                    self.ui_queue.put(("copilot", f"Copilot (Local): {answer}"))
            except Exception as exc:
                self.ui_queue.put(("copilot", f"Copilot error: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def _run_command_async(self, args: List[str], label: str) -> None:
        if self.command_running:
            self.ui_queue.put(("append", "Another command is running. Wait for completion."))
            return

        self.command_running = True
        self.ui_queue.put(("status", f"Running: {label}"))
        self.ui_queue.put(("append", f"\n=== {label} ==="))

        def worker() -> None:
            try:
                process = subprocess.Popen(
                    args,
                    cwd=str(self.kernel_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                assert process.stdout is not None
                for line in process.stdout:
                    self.ui_queue.put(("append", line.rstrip("\n")))
                code = process.wait()
                self.ui_queue.put(("append", f"Exit code: {code}"))
            except Exception as exc:
                self.ui_queue.put(("append", f"Command failed: {exc}"))
            finally:
                self.ui_queue.put(("done", ""))
                self.refresh_all()

        threading.Thread(target=worker, daemon=True).start()

    def run_beastops_status(self) -> None:
        self._run_command_async([sys.executable, "RuntimeOps.py", "status"], "Runtime status")

    def run_beastops_launch(self) -> None:
        self._run_command_async([sys.executable, "RuntimeOps.py", "launch"], "Runtime launch")

    def run_beastops_tune(self) -> None:
        self._run_command_async([sys.executable, "RuntimeOps.py", "tune"], "Runtime tune")

    def run_stress_test(self) -> None:
        self._run_command_async([sys.executable, "CriticalityStressTest.py"], "Criticality Stress Test")


def main() -> None:
    # Load .env file to make GROQ_API_KEY available to InteractiveBridge
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key, value = parts
                        os.environ[key.strip()] = value.strip()
    
    root = tk.Tk()
    app = UnifiedConsciousnessUI(root)
    app.refresh_all()
    root.mainloop()


if __name__ == "__main__":
    main()
