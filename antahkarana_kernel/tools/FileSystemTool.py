"""Simple filesystem tool for reading and writing files."""
import os
from typing import Dict, Optional


class FileSystemTool:
    name = 'filesystem'

    def run(self, operation: str, path: str, content: Optional[str] = None, mode: str = 'w') -> Dict:
        path = os.path.abspath(path)
        if operation == 'read':
            if not os.path.exists(path):
                return {'ok': False, 'error': 'not_found'}
            with open(path, 'r', encoding='utf-8') as f:
                return {'ok': True, 'content': f.read()}
        elif operation in ('write', 'overwrite'):
            d = os.path.dirname(path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            with open(path, mode, encoding='utf-8') as f:
                f.write(content or '')
            return {'ok': True}
        elif operation == 'exists':
            return {'ok': True, 'exists': os.path.exists(path)}
        else:
            return {'ok': False, 'error': 'unsupported_operation'}
