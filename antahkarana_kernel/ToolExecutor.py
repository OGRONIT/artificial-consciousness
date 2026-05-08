"""ToolExecutor for Layer 3 — registry and dispatcher for PC-control tools."""
from typing import Any, Dict
import importlib
import importlib.util
import os


class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        # attempt to auto-register tools from tools package
        self._auto_register_tools()

    def _auto_register_tools(self):
        tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
        if not os.path.isdir(tools_dir):
            return

        for fname in os.listdir(tools_dir):
            if not fname.endswith('.py') or fname.startswith('_'):
                continue

            module_stem = fname[:-3]
            mod = None

            # First try package import (works for `python -m ...`).
            mod_name = 'antahkarana_kernel.tools.' + module_stem
            try:
                mod = importlib.import_module(mod_name)
            except Exception:
                mod = None

            # Fallback to file import (works for `python antahkarana_kernel\\ToolExecutor.py`).
            if mod is None:
                module_path = os.path.join(tools_dir, fname)
                try:
                    spec = importlib.util.spec_from_file_location(
                        f'antahkarana_tool_{module_stem}',
                        module_path,
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                except Exception:
                    mod = None

            if mod is None:
                continue

            try:
                cls = None
                for attr_name in dir(mod):
                    if attr_name.endswith('Tool'):
                        attr = getattr(mod, attr_name)
                        if isinstance(attr, type):
                            cls = attr
                            break
                if cls:
                    inst = cls()
                    name = getattr(inst, 'name', module_stem.lower())
                    self.register(name, inst)
            except Exception:
                # best-effort auto-register; ignore failures
                pass

    def register(self, name: str, tool: Any):
        self.tools[name] = tool

    def execute(self, tool_name: str, **kwargs) -> Dict:
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not registered")
        # tools expose a `run` method
        run = getattr(tool, 'run', None)
        if not callable(run):
            raise ValueError(f"Tool '{tool_name}' has no runnable interface")
        return run(**kwargs)


executor = ToolExecutor()

if __name__ == '__main__':
    print('Tools registered:', list(executor.tools.keys()))
