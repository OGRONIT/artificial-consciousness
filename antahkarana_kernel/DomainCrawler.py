"""Domain crawler for Layer 4 — lightweight content fetcher that feeds KnowledgeStore."""
from typing import List, Optional
import requests
from .KnowledgeStore import KnowledgeStore
import os
import json


class DomainCrawler:
    def __init__(self, store: Optional[KnowledgeStore] = None, domain_configs_dir: Optional[str] = None):
        self.store = store or KnowledgeStore()
        # Load domain config defaults (best-effort). If not provided,
        # attempt to read domain_configs next to this file.
        self.domain_configs = {}
        if domain_configs_dir is None:
            domain_configs_dir = os.path.join(os.path.dirname(__file__), 'domain_configs')
        self._load_domain_configs(domain_configs_dir)

    def _load_domain_configs(self, dpath: str):
        try:
            for fname in os.listdir(dpath):
                if fname.endswith('.json'):
                    path = os.path.join(dpath, fname)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            self.domain_configs[fname[:-5]] = json.load(f)
                    except Exception:
                        continue
        except Exception:
            # ignore if directory missing
            pass

    def crawl_urls(self, urls: Optional[List[str]] = None, domain: str = 'general', limit: int = 10):
        """
        Crawl the provided list of URLs. If `urls` is None or empty and a domain
        is provided, attempt to look up default `sources` from domain configs.
        """
        # If no explicit URLs provided, try reading from domain configs
        if not urls:
            cfg = self.domain_configs.get(domain)
            if cfg:
                urls = cfg.get('sources') or []

        if not urls:
            return {'ok': False, 'fetched': 0, 'error': 'no_urls'}

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
