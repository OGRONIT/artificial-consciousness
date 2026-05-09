"""Intent parser for Layer 1 — lightweight, LLM-free heuristics.

Produces a structured dict with fields: action, target, domain, constraints, raw.
"""
from typing import Dict, Optional
import re
import json
import os


class IntentParser:
    def __init__(self, domain_configs_dir: Optional[str] = None):
        self.domain_configs = {}
        if domain_configs_dir:
            self._load_domain_configs(domain_configs_dir)

    def _load_domain_configs(self, dpath: str):
        try:
            for fname in os.listdir(dpath):
                if fname.endswith('.json'):
                    path = os.path.join(dpath, fname)
                    with open(path, 'r', encoding='utf-8') as f:
                        self.domain_configs[fname[:-5]] = json.load(f)
        except Exception:
            # best-effort loading; ignore errors
            pass

    def parse(self, text: str) -> Dict:
        t = text.strip()
        action = self._extract_action(t)
        target = self._extract_target(t)
        domain = self._detect_domain(t)
        constraints = self._extract_constraints(t)
        return {
            'raw': text,
            'action': action,
            'target': target,
            'domain': domain,
            'constraints': constraints,
        }

    def _extract_action(self, text: str) -> Optional[str]:
        verbs = [
            'fix', 'update', 'fetch', 'get', 'read', 'write', 'edit', 'run', 'execute',
            'push', 'call', 'crawl', 'search', 'test', 'install', 'research', 'study', 'learn'
        ]
        low = text.lower()
        # Prefer the verb that appears earliest in the sentence (by index),
        # rather than relying on a static list order. This avoids choosing
        # verbs that come later in the phrase (e.g. 'update' vs 'edit').
        found = []
        for v in verbs:
            m = re.search(r'\b' + re.escape(v) + r'\b', low)
            if m:
                found.append((m.start(), v))
        if found:
            found.sort(key=lambda x: x[0])
            return found[0][1]
        # fallback: first verb-like token
        m = re.match(r'^(\w+)', low)
        return m.group(1) if m else None

    def _extract_target(self, text: str) -> Optional[str]:
        # URL has highest priority for fetch/crawl commands.
        url_match = re.search(r'(https?://\S+)', text, re.I)
        if url_match:
            return url_match.group(1).rstrip(').,;!')

        # filename pattern
        m = re.search(r'([\w\-./\\]+\.(?:py|js|ts|md|json))', text)
        if m:
            return m.group(1)

        # module/object pattern - skip common articles like "the/a/an" so
        # "run tests for the project" yields "project" rather than "the".
        m2 = re.search(r"\b(?:in|of|for)\s+(?:the\s+|a\s+|an\s+)?([\w_.-]+)\b", text, re.I)
        if m2:
            return m2.group(1)
        return None

    def _detect_domain(self, text: str) -> Optional[str]:
        low = text.lower()
        mapping = {
            'coding': ['coding', 'code', 'python', 'react', 'javascript', 'node', 'docker', 'git', 'pytest'],
            'medical': ['medical', 'patient', 'diagnosis', 'treatment', 'symptom'],
        }
        for domain, kws in mapping.items():
            for k in kws:
                if k in low:
                    return domain

        # fallback to configs
        for cfg in self.domain_configs.keys():
            for k in (self.domain_configs.get(cfg, {}).get('keywords') or []):
                if k.lower() in low:
                    return cfg
        return None

    def _extract_constraints(self, text: str) -> Dict:
        cons = {}
        # quick time constraint
        m = re.search(r'within (\d+) (sec|second|s|minutes|mins|m)', text, re.I)
        if m:
            cons['deadline'] = m.group(1) + ' ' + m.group(2)
        return cons


if __name__ == '__main__':
    p = IntentParser(os.path.join(os.path.dirname(__file__), 'domain_configs'))
    print(p.parse('Fix the bug in InteractiveBridge.py and run tests'))
    print(p.parse('fetch https://example.com and store in coding domain'))
