"""Domain crawler for Layer 4 — lightweight content fetcher that feeds KnowledgeStore."""
from typing import List, Optional
import requests
from .KnowledgeStore import KnowledgeStore
import os


class DomainCrawler:
    def __init__(self, store: Optional[KnowledgeStore] = None):
        self.store = store or KnowledgeStore()

    def crawl_urls(self, urls: List[str], domain: str = 'general', limit: int = 10):
        count = 0
        for u in urls:
            if count >= limit:
                break
            try:
                r = requests.get(u, timeout=10)
                if r.status_code == 200:
                    self.store.add_knowledge(domain, u, r.text)
                    count += 1
            except Exception:
                continue
        return {'ok': True, 'fetched': count}
