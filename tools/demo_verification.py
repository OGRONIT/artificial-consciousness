import os
import sys
import json
from pathlib import Path

# Ensure project root is on sys.path so package imports work when run as a script
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from antahkarana_kernel.IntentParser import IntentParser
from antahkarana_kernel.DomainCrawler import DomainCrawler
from antahkarana_kernel.KnowledgeStore import KnowledgeStore


def run_demo():
    print('=== Intent Parser Demo ===')
    p = IntentParser()
    examples = [
        'run tests for the project',
        'research Python async',
        'edit file and update timeout in InteractiveBridge.py',
    ]
    for t in examples:
        print('Input:', t)
        print('Parsed:', p.parse(t))

    print('\n=== DomainCrawler Demo (mocked fetch) ===')
    # ensure domain config exists
    cfg_dir = os.path.join(os.path.dirname(__file__), '..', 'antahkarana_kernel', 'domain_configs')
    os.makedirs(cfg_dir, exist_ok=True)
    cfg_path = os.path.join(cfg_dir, 'python.json')
    if not os.path.exists(cfg_path):
        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump({'sources': ['https://example.com/testpage']}, f)

    ks = KnowledgeStore()
    crawler = DomainCrawler(store=ks, domain_configs_dir=cfg_dir)

    class DummyResp:
        status_code = 200
        text = '<html>dummy content about asyncio</html>'

    import antahkarana_kernel.DomainCrawler as DCmod
    DCmod.requests.get = lambda u, timeout=10: DummyResp()

    out = crawler.crawl_urls(None, domain='python', limit=2)
    print('Crawl output:', out)

    print('\n=== KnowledgeStore Semantic Query Demo ===')
    ks.add_knowledge('general', 'demo', 'This page discusses asyncio, coroutines, and Python async programming.')
    try:
        results = ks.query_semantic('what is a coroutine', top_k=3)
        print('Semantic results (top):')
        for r in results:
            print('-', r.get('source'), 'score=', r.get('_score'))
    except RuntimeError as e:
        print('Semantic query not available:', e)


if __name__ == '__main__':
    run_demo()
