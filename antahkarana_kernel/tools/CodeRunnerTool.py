"""Code runner tool: run python files or test commands."""
import subprocess
from typing import Dict, Optional, List


class CodeRunnerTool:
    name = 'coderunner'

    def run(self, kind: str = 'python', path: Optional[str] = None, args: Optional[List[str]] = None, timeout: Optional[int] = None) -> Dict:
        if kind == 'python' and path:
            cmd = ['python', path] + (args or [])
        elif kind == 'pytest':
            cmd = ['pytest'] + (args or [])
        else:
            return {'ok': False, 'error': 'unsupported_kind'}

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {'ok': True, 'returncode': res.returncode, 'stdout': res.stdout, 'stderr': res.stderr}
        except subprocess.TimeoutExpired:
            return {'ok': False, 'error': 'timeout'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
