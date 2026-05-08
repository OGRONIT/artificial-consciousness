"""Simple persistent KnowledgeStore for Layer 4.

This is a minimal, file-backed store that supports adding knowledge and naive querying.
"""
import json
import os
from typing import List, Dict, Optional


class KnowledgeStore:
    def __init__(self, path: Optional[str] = None):
        if path:
            self.path = path
        else:
            self.path = os.path.join(os.path.dirname(__file__), 'knowledge_store.json')
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load(self) -> List[Dict]:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, items: List[Dict]):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)

    def add_knowledge(self, domain: str, source: str, content: str):
        items = self._load()
        items.append({'domain': domain, 'source': source, 'content': content})
        self._save(items)
        return {'ok': True}

    def query(self, keyword: str, domain: Optional[str] = None) -> List[Dict]:
        items = self._load()
        res = []
        for it in items:
            if domain and it.get('domain') != domain:
                continue
            if keyword.lower() in (it.get('content') or '').lower() or keyword.lower() in (it.get('source') or '').lower():
                res.append(it)
        return res
