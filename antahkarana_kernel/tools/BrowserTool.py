"""Browser tool for simple HTTP fetches (requests-backed)."""
import requests
from typing import Dict, Optional


class BrowserTool:
    name = 'browser'

    def run(self, url: str, method: str = 'GET', timeout: Optional[int] = 10, **kwargs) -> Dict:
        try:
            r = requests.request(method, url, timeout=timeout, **kwargs)
            return {'ok': True, 'status_code': r.status_code, 'text': r.text, 'url': r.url}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
