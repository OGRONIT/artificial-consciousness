"""BodyAwareness.py - OS-level and sensor awareness bridge.

Provides best-effort monitoring of the computer's physical body status:
battery, CPU temperature, storage, camera, and microphone.
"""

from __future__ import annotations

import ctypes
import json
import os
import platform
import shutil
import subprocess
import time
import threading
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PhysicalSensorStatus:
    name: str
    available: bool
    value: Any
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SystemBodyMonitor:
    """Best-effort physical body monitor for the host computer."""

    def __init__(self, refresh_interval_seconds: float = 15.0):
        self.refresh_interval_seconds = refresh_interval_seconds
        self.lock = threading.RLock()
        self.last_refresh = 0.0
        self.cached_status: Dict[str, Any] = self._collect_status()
        logger.info("[BODY] System body monitor initialized")

    def get_body_status(self, refresh: bool = True) -> Dict[str, Any]:
        with self.lock:
            if refresh and (time.time() - self.last_refresh) >= self.refresh_interval_seconds:
                self.cached_status = self._collect_status()
                self.last_refresh = time.time()
            return self.cached_status.copy()

    def _collect_status(self) -> Dict[str, Any]:
        return {
            "timestamp": time.time(),
            "platform": platform.platform(),
            "battery": self._get_battery_status().to_dict(),
            "cpu_temperature": self._get_cpu_temperature().to_dict(),
            "storage": self._get_storage_status().to_dict(),
            "camera": self._get_camera_status().to_dict(),
            "microphone": self._get_microphone_status().to_dict(),
        }

    def _get_battery_status(self) -> PhysicalSensorStatus:
        if hasattr(ctypes, "windll"):
            try:
                class SYSTEM_POWER_STATUS(ctypes.Structure):
                    _fields_ = [
                        ("ACLineStatus", ctypes.c_ubyte),
                        ("BatteryFlag", ctypes.c_ubyte),
                        ("BatteryLifePercent", ctypes.c_ubyte),
                        ("SystemStatusFlag", ctypes.c_ubyte),
                        ("BatteryLifeTime", ctypes.c_ulong),
                        ("BatteryFullLifeTime", ctypes.c_ulong),
                    ]

                status = SYSTEM_POWER_STATUS()
                if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
                    return PhysicalSensorStatus(
                        name="battery",
                        available=True,
                        value={
                            "ac_line_status": int(status.ACLineStatus),
                            "battery_percent": None if status.BatteryLifePercent == 255 else int(status.BatteryLifePercent),
                            "battery_life_time_seconds": int(status.BatteryLifeTime),
                            "battery_full_life_time_seconds": int(status.BatteryFullLifeTime),
                        },
                        source="ctypes.kernel32.GetSystemPowerStatus",
                    )
            except Exception as exc:
                logger.debug("[BODY] Battery query failed: %s", exc)

        return PhysicalSensorStatus("battery", False, None, "unavailable")

    def _get_cpu_temperature(self) -> PhysicalSensorStatus:
        if platform.system().lower() == "windows":
            value = self._query_powershell(
                "(Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature | "
                "Select-Object -First 1 -ExpandProperty CurrentTemperature)"
            )
            if value is not None:
                try:
                    temp_kelvin_x10 = float(value)
                    celsius = round((temp_kelvin_x10 / 10.0) - 273.15, 2)
                    return PhysicalSensorStatus("cpu_temperature", True, {"celsius": celsius}, "powershell/cim")
                except Exception:
                    pass
        return PhysicalSensorStatus("cpu_temperature", False, None, "unavailable")

    def _get_storage_status(self) -> PhysicalSensorStatus:
        root_path = os.path.abspath(os.sep)
        usage = shutil.disk_usage(root_path)
        value = {
            "root_path": root_path,
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "used_percent": round((usage.used / usage.total) * 100, 2) if usage.total else 0.0,
        }
        return PhysicalSensorStatus("storage", True, value, "shutil.disk_usage")

    def _get_camera_status(self) -> PhysicalSensorStatus:
        value = self._query_device_presence(
            "Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'OK'} | Select-Object -First 1 | Measure-Object | Select-Object -ExpandProperty Count"
        )
        if value is not None:
            return PhysicalSensorStatus("camera", True, {"enabled": int(value) > 0}, "powershell/pnp")
        return PhysicalSensorStatus("camera", False, None, "unavailable")

    def _get_microphone_status(self) -> PhysicalSensorStatus:
        value = self._query_device_presence(
            "Get-PnpDevice -Class AudioEndpoint -ErrorAction SilentlyContinue | Where-Object {$_.FriendlyName -match 'Microphone'} | Select-Object -First 1 | Measure-Object | Select-Object -ExpandProperty Count"
        )
        if value is not None:
            return PhysicalSensorStatus("microphone", True, {"enabled": int(value) > 0}, "powershell/pnp")
        return PhysicalSensorStatus("microphone", False, None, "unavailable")

    def _query_powershell(self, command: str) -> Optional[str]:
        if platform.system().lower() != "windows":
            return None
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                timeout=6,
                check=False,
            )
            output = completed.stdout.strip()
            return output or None
        except Exception as exc:
            logger.debug("[BODY] PowerShell query failed: %s", exc)
            return None

    def _query_device_presence(self, command: str) -> Optional[str]:
        output = self._query_powershell(command)
        if output is None:
            return None
        return output.splitlines()[-1].strip() if output.splitlines() else output.strip()


_global_body_monitor: Optional[SystemBodyMonitor] = None
_body_lock = threading.Lock()


def get_system_body_monitor() -> SystemBodyMonitor:
    """Get or create the global body-awareness monitor."""
    global _global_body_monitor
    if _global_body_monitor is None:
        with _body_lock:
            if _global_body_monitor is None:
                _global_body_monitor = SystemBodyMonitor()
    return _global_body_monitor