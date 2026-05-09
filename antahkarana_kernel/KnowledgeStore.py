"""Simple persistent KnowledgeStore for Layer 4.

This is a minimal, file-backed store that supports adding knowledge and naive querying.
"""
import json
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


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
        entry = {'domain': domain, 'source': source, 'content': content}
        # Attempt to compute and store an embedding if model available (best-effort)
        try:
            emb = self._compute_embedding_for_text(content)
            if emb is not None:
                # store as list of floats for JSON
                entry['embedding'] = [float(x) for x in emb]
        except Exception as e:
            # Non-fatal: log and continue without embeddings
            logger.debug("KnowledgeStore: embedding not available: %s", e)

        items.append(entry)
        self._save(items)
        return {'ok': True}

    def _ensure_embedding_model(self):
        # Lazy import of sentence-transformers model; return True if available
        if hasattr(self, '_embed_model') and self._embed_model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer
            # Use a small, fast model if available
            self._embed_model = SentenceTransformer('all-MiniLM-L6-v2')
            return True
        except Exception as e:
            self._embed_model = None
            logger.debug('Embedding model not available: %s', e)
            return False

    def _compute_embedding_for_text(self, text: str):
        # Return numpy array or list; None if model unavailable
        if not self._ensure_embedding_model():
            return None
        try:
            emb = self._embed_model.encode(text, convert_to_numpy=True)
            return emb
        except Exception as e:
            logger.debug('Failed to compute embedding: %s', e)
            return None

    def query_semantic(self, query: str, domain: Optional[str] = None, top_k: int = 5):
        """
        Perform a semantic search over stored knowledge. Requires `sentence-transformers`.
        Returns top_k matching items with similarity scores.
        """
        if not self._ensure_embedding_model():
            raise RuntimeError('Semantic search requires sentence-transformers; install it to enable semantic queries')

        import numpy as np

        items = self._load()
        candidates = []
        for it in items:
            if domain and it.get('domain') != domain:
                continue
            if not it.get('embedding'):
                continue
            candidates.append(it)

        if not candidates:
            return []

        query_emb = self._compute_embedding_for_text(query)
        if query_emb is None:
            raise RuntimeError('Failed to compute query embedding')

        # Build matrix of embeddings
        emb_matrix = np.vstack([np.array(it['embedding'], dtype=float) for it in candidates])
        # Normalize to compute cosine similarity safely
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            sims = cosine_similarity(query_emb.reshape(1, -1), emb_matrix)[0]
        except Exception:
            # Fallback: simple dot / norms
            qn = query_emb / (np.linalg.norm(query_emb) + 1e-12)
            em = emb_matrix / (np.linalg.norm(emb_matrix, axis=1, keepdims=True) + 1e-12)
            sims = (em @ qn).tolist()

        scored = list(zip(candidates, sims))
        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for it, score in scored[:top_k]:
            r = dict(it)
            r['_score'] = float(score)
            results.append(r)
        return results

    def query(self, keyword: str, domain: Optional[str] = None) -> List[Dict]:
        items = self._load()
        res = []
        for it in items:
            if domain and it.get('domain') != domain:
                continue
            if keyword.lower() in (it.get('content') or '').lower() or keyword.lower() in (it.get('source') or '').lower():
                res.append(it)
        return res
