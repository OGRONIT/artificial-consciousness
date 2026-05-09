import os
import tempfile
import json
from unittest import mock

import pytest

from antahkarana_kernel.IntentParser import IntentParser
from antahkarana_kernel.DomainCrawler import DomainCrawler
from antahkarana_kernel.KnowledgeStore import KnowledgeStore


def test_intent_parser_runs_tests_target():
    p = IntentParser()
    res = p.parse('run tests for the project')
    assert res['action'] == 'run'
    # Expect target to be 'project' not 'the'
    assert res['target'] == 'project'


def test_domain_crawler_uses_domain_config_and_stores(tmp_path):
    # create a temp knowledge store path
    ks_path = tmp_path / 'ks.json'
    store = KnowledgeStore(path=str(ks_path))

    # create a domain config directory with a python.json
    cfg_dir = os.path.join(os.path.dirname(__file__), '..', 'domain_configs')
    os.makedirs(cfg_dir, exist_ok=True)
    cfg_path = os.path.join(cfg_dir, 'python.json')
    with open(cfg_path, 'w', encoding='utf-8') as f:
        json.dump({'sources': ['https://example.com/testpage']}, f)

    crawler = DomainCrawler(store=store, domain_configs_dir=cfg_dir)

    # Patch requests.get to avoid network calls
    class DummyResp:
        status_code = 200
        text = '<html>dummy</html>'

    with mock.patch('antahkarana_kernel.DomainCrawler.requests.get', return_value=DummyResp()):
        out = crawler.crawl_urls(None, domain='python', limit=2)
    assert out.get('ok') is True
    assert out.get('fetched', 0) >= 1

    # Verify store has content
    items = store._load()
    assert any('dummy' in (it.get('content') or '') for it in items)


def test_knowledgestore_semantic_query_behaviour(tmp_path):
    ks_path = tmp_path / 'ks_sem.json'
    store = KnowledgeStore(path=str(ks_path))
    store.add_knowledge('general', 'src', 'This text talks about asyncio and coroutines in Python.')

    # If sentence-transformers not installed, expect RuntimeError instructing to install
    try:
        res = store.query_semantic('what is a coroutine', top_k=1)
        # If it returns, ensure it's a list
        assert isinstance(res, list)
    except RuntimeError as e:
        assert 'sentence-transformers' in str(e) or 'Semantic search requires' in str(e)


if __name__ == '__main__':
    pytest.main([__file__])
