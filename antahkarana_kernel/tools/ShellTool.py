"""Shell tool wrapper to run commands in a subprocess."""
import subprocess
from typing import Dict, Optional


class ShellTool:
    name = 'shell'

    def run(self, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None) -> Dict:
        try:
            res = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
            return {
                'ok': True,
                'returncode': res.returncode,
                'stdout': res.stdout,
                'stderr': res.stderr,
            }
        except subprocess.TimeoutExpired as e:
            return {'ok': False, 'error': 'timeout'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
