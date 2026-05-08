"""ToolExecutor for Layer 3 — registry and dispatcher for PC-control tools."""
from typing import Any, Dict
import importlib
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
            if fname.endswith('.py') and not fname.startswith('_'):
                mod_name = 'antahkarana_kernel.tools.' + fname[:-3]
                try:
                    mod = importlib.import_module(mod_name)
                    cls = getattr(mod, list(filter(lambda n: n.endswith('Tool'), dir(mod)))[0], None)
                    if cls:
                        inst = cls()
                        name = getattr(inst, 'name', fname[:-3])
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
