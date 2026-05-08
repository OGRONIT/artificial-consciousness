"""Domain agent wiring: instantiate IntentParser, ToolExecutor, KnowledgeStore, DomainCrawler.

Provides `handle_command(text)` as a simple entry point for the kernel to use.
"""
from .IntentParser import IntentParser
from .ToolExecutor import executor as default_executor
from .KnowledgeStore import KnowledgeStore
from .DomainCrawler import DomainCrawler
import os


class DomainAgent:
    def __init__(self, base_dir: str = None):
        base_dir = base_dir or os.path.dirname(__file__)
        configs = os.path.join(base_dir, 'domain_configs')
        self.parser = IntentParser(configs)
        self.store = KnowledgeStore()
        self.crawler = DomainCrawler(self.store)
        self.executor = default_executor

    def handle_command(self, text: str) -> dict:
        intent = self.parser.parse(text)
        action = intent.get('action')
        target = intent.get('target')
        domain = intent.get('domain') or 'general'

        # Simple routing rules
        if action in ('fetch', 'get', 'read') and target and target.startswith('http'):
            res = self.executor.execute('browser', url=target)
            if res.get('ok'):
                self.store.add_knowledge(domain, target, res.get('text') or '')
            return {'intent': intent, 'result': res}

        if action in ('crawl',) and 'http' in (text or ''):
            # find URLs naively
            urls = [w for w in text.split() if w.startswith('http')]
            out = self.crawler.crawl_urls(urls, domain=domain)
            return {'intent': intent, 'result': out}

        if action in ('read', 'write', 'edit') and target and target.endswith(('.py', '.md', '.json')):
            if action == 'read':
                res = self.executor.execute('filesystem', operation='read', path=target)
                return {'intent': intent, 'result': res}
            else:
                return {'intent': intent, 'result': {'ok': False, 'error': 'write_not_implemented'}}

        if action in ('run', 'test'):
            # run tests via coderunner
            res = self.executor.execute('coderunner', kind='pytest', args=[])
            return {'intent': intent, 'result': res}

        # fallback: try knowledge store query
        if intent.get('target'):
            qres = self.store.query(intent['target'], domain=domain)
            return {'intent': intent, 'result': {'store_matches': qres}}

        return {'intent': intent, 'result': {'ok': False, 'error': 'unhandled_intent'}}


def create_agent():
    return DomainAgent()


if __name__ == '__main__':
    agent = create_agent()
    print(agent.handle_command('fetch https://example.com and store in coding domain'))
