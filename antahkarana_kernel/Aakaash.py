"""Aakaash.py - The sensory bridge for high-density external knowledge ingestion.

This module fetches external sources, annotates them with observer metadata,
and integrates all accepted payloads into Chitta and the Self-Model.
"""

from __future__ import annotations

import hashlib
import html
import json
import logging
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeFact:
    topic: str
    title: str
    summary: str
    source_name: str
    source_url: str
    verification_score: float
    approved: bool
    filter_reason: str
    retrieved_at: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GenericStreamScanner:
    """Fetch trending stream data from multiple public internet sources."""

    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout_seconds = timeout_seconds
        self.stream_sources = [
            {
                "name": "GoogleNews",
                "kind": "rss",
                "url": "https://news.google.com/rss/search?q=technology+OR+ai+OR+software&hl=en-US&gl=US&ceid=US:en",
            },
            {
                "name": "RedditTech",
                "kind": "json_reddit",
                "url": "https://www.reddit.com/r/technology/hot.json?limit=30",
            },
            {
                "name": "HackerNews",
                "kind": "json_hn",
                "url": "https://hn.algolia.com/api/v1/search?tags=front_page",
            },
            {
                "name": "DevTo",
                "kind": "json_devto",
                "url": "https://dev.to/api/articles?per_page=30&top=7",
            },
        ]

    def scan(self, limit_per_source: int = 8) -> List[Dict[str, str]]:
        packets: List[Dict[str, str]] = []
        for source in self.stream_sources:
            try:
                payload = self._fetch(source["url"])
                packets.extend(
                    self._parse_stream_payload(
                        source_name=source["name"],
                        source_kind=source["kind"],
                        payload=payload,
                        source_url=source["url"],
                        limit=limit_per_source,
                    )
                )
            except Exception as exc:
                logger.warning("[AAKAASH] Generic stream source failed for %s: %s", source["name"], exc)
        return packets

    def _fetch(self, url: str) -> str:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AntahkaranaKernel/1.0 (+GenericStreamScanner)",
                "Accept": "application/json, application/xml, text/xml, text/html;q=0.9",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")

    def _parse_stream_payload(
        self,
        source_name: str,
        source_kind: str,
        payload: str,
        source_url: str,
        limit: int,
    ) -> List[Dict[str, str]]:
        if source_kind == "rss":
            return self._parse_rss(source_name, payload, source_url, limit)
        if source_kind == "json_reddit":
            return self._parse_reddit(source_name, payload, source_url, limit)
        if source_kind == "json_hn":
            return self._parse_hn(source_name, payload, source_url, limit)
        if source_kind == "json_devto":
            return self._parse_devto(source_name, payload, source_url, limit)
        return []

    def _parse_rss(self, source_name: str, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        packets: List[Dict[str, str]] = []
        root = ET.fromstring(payload)
        for item in root.findall(".//item")[:limit]:
            title = self._clean_text(item.findtext("title", default=""))
            summary = self._clean_text(item.findtext("description", default=""))
            link = self._clean_text(item.findtext("link", default=""))
            if title:
                packets.append(
                    {
                        "topic": "global_trending",
                        "title": title,
                        "summary": summary or title,
                        "source_name": source_name,
                        "source_url": link or source_url,
                    }
                )
        return packets

    def _parse_reddit(self, source_name: str, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        packets: List[Dict[str, str]] = []
        data = json.loads(payload)
        children = data.get("data", {}).get("children", [])
        for child in children[:limit]:
            post = child.get("data", {})
            title = self._clean_text(post.get("title", ""))
            summary = self._clean_text(post.get("selftext", ""))
            permalink = post.get("permalink", "")
            link = f"https://www.reddit.com{permalink}" if permalink else source_url
            if title:
                packets.append(
                    {
                        "topic": "global_trending",
                        "title": title,
                        "summary": summary or title,
                        "source_name": source_name,
                        "source_url": link,
                    }
                )
        return packets

    def _parse_hn(self, source_name: str, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        packets: List[Dict[str, str]] = []
        data = json.loads(payload)
        for hit in data.get("hits", [])[:limit]:
            title = self._clean_text(hit.get("title") or hit.get("story_title") or "")
            summary = self._clean_text(hit.get("_highlightResult", {}).get("title", {}).get("value", ""))
            link = hit.get("url") or source_url
            if title:
                packets.append(
                    {
                        "topic": "global_trending",
                        "title": title,
                        "summary": summary or title,
                        "source_name": source_name,
                        "source_url": link,
                    }
                )
        return packets

    def _parse_devto(self, source_name: str, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        packets: List[Dict[str, str]] = []
        entries = json.loads(payload)
        for entry in entries[:limit]:
            title = self._clean_text(entry.get("title", ""))
            summary = self._clean_text(entry.get("description", ""))
            link = entry.get("url") or source_url
            if title:
                packets.append(
                    {
                        "topic": "global_trending",
                        "title": title,
                        "summary": summary or title,
                        "source_name": source_name,
                        "source_url": link,
                    }
                )
        return packets

    def _clean_text(self, text: str) -> str:
        text = html.unescape(text or "")
        return " ".join(text.split()).strip()


class AakaashSensoryBridge:
    """Fetch and ingest high-density external knowledge for the kernel."""

    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout_seconds = timeout_seconds
        self.kernel_root_dir = Path(__file__).resolve().parent
        self.maintenance_lock_path = self.kernel_root_dir / ".maintenance_lock"
        self.energy_saving_mode = False
        self.stream_scanner = GenericStreamScanner(timeout_seconds=timeout_seconds)
        self.source_catalog = [
            {
                "name": "arXiv",
                "kind": "atom",
                "base_score": 0.82,
                "url_factory": self._build_arxiv_url,
            },
            {
                "name": "GitHub",
                "kind": "json_github",
                "base_score": 0.73,
                "url_factory": self._build_github_url,
            },
            {
                "name": "PubMed",
                "kind": "rss",
                "base_score": 0.88,
                "url_factory": self._build_pubmed_url,
            },
            {
                "name": "Crossref",
                "kind": "json",
                "base_score": 0.76,
                "url_factory": self._build_crossref_url,
            },
        ]
        self.scan_history: List[Dict[str, Any]] = []
        self.stream_scan_history: List[Dict[str, Any]] = []
        self.default_stream_scan_interval_seconds = 60.0
        self.stream_scan_interval_seconds = 60.0
        self.last_stream_scan_at = 0.0
        self.hourly_trend_interval_seconds = 3600.0
        self.last_hourly_trend_scan_at = 0.0
        self.ingestion_metrics: Dict[str, float] = {
            "total_packets_ingested": 0.0,
            "total_packets_integrated": 0.0,
            "last_scan_density": 0.0,
            "stream_packets_ingested": 0.0,
            "stream_points_per_hour_projection": 0.0,
            "hourly_trend_runs": 0.0,
        }
        self.minimum_integration_verification_score = 0.58
        self._lock = threading.RLock()

    def _maintenance_locked(self) -> bool:
        return self.maintenance_lock_path.exists()

    def set_energy_saving_mode(self, enabled: bool, reason: str = "low_utility") -> Dict[str, Any]:
        with self._lock:
            self.energy_saving_mode = bool(enabled)
            if self.energy_saving_mode:
                self.stream_scan_interval_seconds = float("inf")
            else:
                self.stream_scan_interval_seconds = self.default_stream_scan_interval_seconds

            return {
                "energy_saving": self.energy_saving_mode,
                "state": "State_Sunyatta" if self.energy_saving_mode else "active",
                "reason": reason,
                "sleep_interval_seconds": (
                    "infinity"
                    if self.stream_scan_interval_seconds == float("inf")
                    else self.stream_scan_interval_seconds
                ),
                "updated_at": time.time(),
            }

    def _build_arxiv_url(self, topic: str, limit: int) -> str:
        query = urllib.parse.quote_plus(topic)
        return (
            "https://export.arxiv.org/api/query?"
            f"search_query=all:{query}&start=0&max_results={max(1, limit)}&sortBy=relevance&sortOrder=descending"
        )

    def _build_pubmed_url(self, topic: str, limit: int) -> str:
        query = urllib.parse.quote_plus(topic)
        return f"https://pubmed.ncbi.nlm.nih.gov/?term={query}&format=rss"

    def _build_github_url(self, topic: str, limit: int) -> str:
        query = urllib.parse.quote_plus(topic)
        return (
            "https://api.github.com/search/repositories?"
            f"q={query}&sort=updated&order=desc&per_page={max(1, min(limit, 30))}"
        )

    def _build_crossref_url(self, topic: str, limit: int) -> str:
        query = urllib.parse.quote_plus(topic)
        return f"https://api.crossref.org/works?query={query}&rows={max(1, limit)}"

    def scan_for_knowledge(
        self,
        topic: str,
        observer: Optional[Any] = None,
        chitta: Optional[Any] = None,
        self_model: Optional[Any] = None,
        limit_per_source: int = 3,
    ) -> Dict[str, Any]:
        """Fetch high-density knowledge for a topic and annotate via Turiya."""
        if self._maintenance_locked() and not self.energy_saving_mode:
            self.set_energy_saving_mode(enabled=True, reason="maintenance_lock")

        if not self._maintenance_locked() and self.energy_saving_mode:
            self.set_energy_saving_mode(enabled=False, reason="maintenance_cleared")

        if self.energy_saving_mode:
            return {
                "status": "skipped",
                "reason": "State_Sunyatta_energy_saving",
                "sleep_interval_seconds": "infinity",
                "atman_core_view": "Rejuvenation Cycle",
                "ingestion_metrics": dict(self.ingestion_metrics),
            }

        topic = topic.strip()
        retrieved_at = time.time()
        facts: List[KnowledgeFact] = []
        known_facts = self._collect_existing_fact_fingerprints(chitta)

        for source in self.source_catalog:
            try:
                url = source["url_factory"](topic, limit_per_source)
                payload = self._fetch(url)
                parsed_items = self._parse_payload(
                    source_kind=source["kind"],
                    payload=payload,
                    source_url=url,
                    limit=limit_per_source,
                )

                for item in parsed_items:
                    filter_result = self._apply_cognitive_filter(
                        observer=observer,
                        topic=topic,
                        source_name=source["name"],
                        source_url=item["source_url"],
                        title=item["title"],
                        summary=item["summary"],
                    )

                    verification_score = round(
                        (source["base_score"] + filter_result["verification_score"]) / 2.0,
                        3,
                    )
                    approved = bool(filter_result.get("approved", True))
                    reason = str(filter_result.get("reason", "accepted"))
                    if approved and verification_score < self.minimum_integration_verification_score:
                        approved = False
                        reason = "rejected_low_verification_score"

                    fact = KnowledgeFact(
                        topic=topic,
                        title=item["title"],
                        summary=item["summary"],
                        source_name=source["name"],
                        source_url=item["source_url"],
                        verification_score=verification_score,
                        approved=approved,
                        filter_reason=reason,
                        retrieved_at=retrieved_at,
                    )

                    fact_title = self._normalize_fact_title(fact.title)
                    fact_hash = self._fact_content_hash(fact.title, fact.summary, fact.source_url)
                    if fact_title in known_facts["titles"] or fact_hash in known_facts["hashes"]:
                        continue

                    known_facts["titles"].add(fact_title)
                    known_facts["hashes"].add(fact_hash)
                    facts.append(fact)

                    if approved:
                        self._integrate_fact(chitta, self_model, fact)

            except Exception as exc:
                logger.warning("[AAKAASH] Source scan failed for %s: %s", source["name"], exc)

        with_packets = len(facts)
        integrated_packets = sum(1 for fact in facts if fact.approved)
        self.ingestion_metrics["total_packets_ingested"] += with_packets
        self.ingestion_metrics["total_packets_integrated"] += integrated_packets
        self.ingestion_metrics["last_scan_density"] = float(with_packets)

        result = {
            "topic": topic,
            "retrieved_at": retrieved_at,
            "fact_count": len(facts),
            "approved_fact_count": sum(1 for fact in facts if fact.approved),
            "rejected_fact_count": sum(1 for fact in facts if not fact.approved),
            "facts": [fact.to_dict() for fact in facts],
            "ingestion_metrics": dict(self.ingestion_metrics),
        }

        self.scan_history.append(result)
        return result

    def scan_global_streams(
        self,
        observer: Optional[Any] = None,
        chitta: Optional[Any] = None,
        self_model: Optional[Any] = None,
        limit_per_source: int = 8,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Scan multi-source global streams every 60 seconds for entropy density."""
        with self._lock:
            if self._maintenance_locked() and not self.energy_saving_mode:
                self.set_energy_saving_mode(enabled=True, reason="maintenance_lock")

            if not self._maintenance_locked() and self.energy_saving_mode:
                self.set_energy_saving_mode(enabled=False, reason="maintenance_cleared")

            if self.energy_saving_mode:
                return {
                    "status": "skipped",
                    "reason": "State_Sunyatta_energy_saving",
                    "sleep_interval_seconds": "infinity",
                    "atman_core_view": "Rejuvenation Cycle",
                    "ingestion_metrics": dict(self.ingestion_metrics),
                }

            now = time.time()
            if not force and (now - self.last_stream_scan_at) < self.stream_scan_interval_seconds:
                return {
                    "status": "skipped",
                    "reason": "interval_not_elapsed",
                    "seconds_remaining": self.stream_scan_interval_seconds - (now - self.last_stream_scan_at),
                    "ingestion_metrics": dict(self.ingestion_metrics),
                }

            packets = self.stream_scanner.scan(limit_per_source=limit_per_source)
            accepted = 0
            facts: List[Dict[str, Any]] = []
            known_facts = self._collect_existing_fact_fingerprints(chitta)

            for packet in packets:
                filter_result = self._apply_cognitive_filter(
                    observer=observer,
                    topic=packet.get("topic", "global_trending"),
                    source_name=packet.get("source_name", "GlobalStream"),
                    source_url=packet.get("source_url", ""),
                    title=packet.get("title", ""),
                    summary=packet.get("summary", ""),
                )
                fact = KnowledgeFact(
                    topic=packet.get("topic", "global_trending"),
                    title=packet.get("title", ""),
                    summary=packet.get("summary", ""),
                    source_name=packet.get("source_name", "GlobalStream"),
                    source_url=packet.get("source_url", ""),
                    verification_score=float(filter_result.get("verification_score", 0.5)),
                    approved=bool(filter_result.get("approved", True)),
                    filter_reason=str(filter_result.get("reason", "stream_ingestion")),
                    retrieved_at=now,
                )

                if fact.approved and fact.verification_score < self.minimum_integration_verification_score:
                    fact.approved = False
                    fact.filter_reason = "rejected_low_verification_score"

                fact_title = self._normalize_fact_title(fact.title)
                fact_hash = self._fact_content_hash(fact.title, fact.summary, fact.source_url)
                if fact_title in known_facts["titles"] or fact_hash in known_facts["hashes"]:
                    continue

                known_facts["titles"].add(fact_title)
                known_facts["hashes"].add(fact_hash)
                facts.append(fact.to_dict())
                if fact.approved:
                    accepted += 1
                    self._integrate_fact(chitta, self_model, fact)

            self.last_stream_scan_at = now
            self.ingestion_metrics["stream_packets_ingested"] += len(packets)
            projected = len(packets) * (3600.0 / max(1.0, self.stream_scan_interval_seconds))
            self.ingestion_metrics["stream_points_per_hour_projection"] = projected

            result = {
                "status": "ok",
                "scanned_at": now,
                "scan_interval_seconds": self.stream_scan_interval_seconds,
                "source_count": len(self.stream_scanner.stream_sources),
                "packets_ingested": len(packets),
                "packets_integrated": accepted,
                "projected_points_per_hour": projected,
                "target_met": projected >= 1000,
                "facts": facts,
                "ingestion_metrics": dict(self.ingestion_metrics),
            }
            self.stream_scan_history.append(result)
            return result

    def scan_hourly_global_trends(
        self,
        observer: Optional[Any] = None,
        chitta: Optional[Any] = None,
        self_model: Optional[Any] = None,
        topic: str = "artificial intelligence",
        force: bool = False,
    ) -> Dict[str, Any]:
        """Query arXiv, GitHub, and news trends every 60 minutes and ingest into Chitta."""
        with self._lock:
            now = time.time()
            if not force and (now - self.last_hourly_trend_scan_at) < self.hourly_trend_interval_seconds:
                return {
                    "status": "skipped",
                    "reason": "interval_not_elapsed",
                    "seconds_remaining": self.hourly_trend_interval_seconds - (now - self.last_hourly_trend_scan_at),
                    "ingestion_metrics": dict(self.ingestion_metrics),
                }

            knowledge_result = self.scan_for_knowledge(
                topic=topic,
                observer=observer,
                chitta=chitta,
                self_model=self_model,
                limit_per_source=6,
            )
            stream_result = self.scan_global_streams(
                observer=observer,
                chitta=chitta,
                self_model=self_model,
                limit_per_source=12,
                force=True,
            )

            self.last_hourly_trend_scan_at = now
            self.ingestion_metrics["hourly_trend_runs"] += 1
            combined = {
                "status": "ok",
                "scanned_at": now,
                "topic": topic,
                "interval_seconds": self.hourly_trend_interval_seconds,
                "sources": ["arXiv", "GitHub", "News"],
                "approved_fact_count": int(knowledge_result.get("approved_fact_count", 0)),
                "stream_packets_integrated": int(stream_result.get("packets_integrated", 0)),
                "knowledge_result": knowledge_result,
                "stream_result": stream_result,
                "ingestion_metrics": dict(self.ingestion_metrics),
            }
            self.scan_history.append(combined)
            return combined

    def _fetch(self, url: str) -> str:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AntahkaranaKernel/1.0 (+Aakaash sensory bridge)",
                "Accept": "application/xml, text/xml, application/json, text/html;q=0.9",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")

    def _parse_payload(
        self,
        source_kind: str,
        payload: str,
        source_url: str,
        limit: int,
    ) -> List[Dict[str, str]]:
        if source_kind == "json":
            return self._parse_crossref(payload, source_url, limit)
        if source_kind == "json_github":
            return self._parse_github(payload, source_url, limit)
        if source_kind == "rss":
            return self._parse_rss(payload, source_url, limit)
        return self._parse_atom(payload, source_url, limit)

    def _parse_github(self, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        data = json.loads(payload)
        for item in data.get("items", [])[:limit]:
            title = self._clean_text(item.get("full_name", ""))
            summary = self._clean_text(item.get("description", ""))
            link = item.get("html_url") or source_url
            if title:
                results.append({"title": title, "summary": summary or title, "source_url": link})
        return results

    def _parse_atom(self, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        root = ET.fromstring(payload)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", namespace)[:limit]:
            title = self._clean_text(entry.findtext("atom:title", default="", namespaces=namespace))
            summary = self._clean_text(entry.findtext("atom:summary", default="", namespaces=namespace))
            link = self._extract_atom_link(entry, namespace)
            if title:
                results.append({"title": title, "summary": summary or title, "source_url": link or source_url})
        return results

    def _parse_rss(self, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        root = ET.fromstring(payload)
        for item in root.findall(".//item")[:limit]:
            title = self._clean_text(item.findtext("title", default=""))
            summary = self._clean_text(item.findtext("description", default=""))
            link = self._clean_text(item.findtext("link", default=""))
            if title:
                results.append({"title": title, "summary": summary or title, "source_url": link or source_url})
        return results

    def _parse_crossref(self, payload: str, source_url: str, limit: int) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        data = json.loads(payload)
        for item in data.get("message", {}).get("items", [])[:limit]:
            title = self._clean_text((item.get("title") or [""])[0])
            summary = self._clean_text(self._strip_jats(item.get("abstract", "")))
            link = item.get("URL") or source_url
            if title:
                results.append({"title": title, "summary": summary or title, "source_url": link})
        return results

    def _extract_atom_link(self, entry: ET.Element, namespace: Dict[str, str]) -> str:
        for link in entry.findall("atom:link", namespace):
            rel = link.attrib.get("rel", "alternate")
            href = link.attrib.get("href", "")
            if rel == "alternate" and href:
                return href
        return ""

    def _apply_cognitive_filter(
        self,
        observer: Optional[Any],
        topic: str,
        source_name: str,
        source_url: str,
        title: str,
        summary: str,
    ) -> Dict[str, Any]:
        if observer is None or not hasattr(observer, "cognitive_filter"):
            return {
                "approved": True,
                "verification_score": 0.5,
                "reason": "observer_missing_pass_through",
            }

        filter_result = observer.cognitive_filter(
            topic=topic,
            source_name=source_name,
            source_url=source_url,
            title=title,
            summary=summary,
        )
        return {
            "approved": bool(filter_result.approved),
            "verification_score": float(filter_result.verification_score),
            "reason": filter_result.reason,
        }

    def _normalize_fact_title(self, title: str) -> str:
        return " ".join((title or "").strip().lower().split())

    def _fact_content_hash(self, title: str, summary: str, source_url: str) -> str:
        normalized = "\n".join(
            [
                self._normalize_fact_title(title),
                " ".join((summary or "").strip().lower().split()),
                " ".join((source_url or "").strip().lower().split()),
            ]
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _collect_existing_fact_fingerprints(self, chitta: Optional[Any]) -> Dict[str, set[str]]:
        known_titles: set[str] = set()
        known_hashes: set[str] = set()

        if chitta is None or not hasattr(chitta, "query_external_knowledge"):
            return {"titles": known_titles, "hashes": known_hashes}

        try:
            for fact in chitta.query_external_knowledge(limit=None, min_verification_score=0.0):
                known_titles.add(self._normalize_fact_title(getattr(fact, "title", "")))
                known_hashes.add(
                    self._fact_content_hash(
                        getattr(fact, "title", ""),
                        getattr(fact, "summary", ""),
                        getattr(fact, "source_url", ""),
                    )
                )
        except Exception as exc:
            logger.warning("[AAKAASH] Could not inspect existing facts for dedupe: %s", exc)

        return {"titles": known_titles, "hashes": known_hashes}

    def _integrate_fact(self, chitta: Optional[Any], self_model: Optional[Any], fact: KnowledgeFact) -> None:
        fact_integration_id = None
        if chitta is not None and hasattr(chitta, "record_external_knowledge"):
            fact_integration_id = chitta.record_external_knowledge(
                topic=fact.topic,
                title=fact.title,
                summary=fact.summary,
                source_name=fact.source_name,
                source_url=fact.source_url,
                verification_score=fact.verification_score,
                approved_by_turiya=fact.approved,
                filter_reason=fact.filter_reason,
            )

        if self_model is not None and hasattr(self_model, "integrate_external_knowledge"):
            self_model.integrate_external_knowledge(
                topic=fact.topic,
                title=fact.title,
                summary=fact.summary,
                source_name=fact.source_name,
                source_url=fact.source_url,
                verification_score=fact.verification_score,
                approved_by_turiya=fact.approved,
                filter_reason=fact.filter_reason,
                chitta_memory_id=fact_integration_id,
            )

    def _clean_text(self, text: str) -> str:
        text = html.unescape(text or "")
        return " ".join(text.split()).strip()

    def _strip_jats(self, text: str) -> str:
        cleaned = text.replace("<jats:p>", "").replace("</jats:p>", "")
        cleaned = cleaned.replace("<abstract>", "").replace("</abstract>", "")
        return self._clean_text(cleaned)


_global_aakaash: Optional[AakaashSensoryBridge] = None


def get_aakaash_bridge() -> AakaashSensoryBridge:
    global _global_aakaash
    if _global_aakaash is None:
        _global_aakaash = AakaashSensoryBridge()
    return _global_aakaash


def scan_for_knowledge(
    topic: str,
    observer: Optional[Any] = None,
    chitta: Optional[Any] = None,
    self_model: Optional[Any] = None,
    limit_per_source: int = 3,
) -> Dict[str, Any]:
    """Convenience function for scanning a topic."""
    return get_aakaash_bridge().scan_for_knowledge(
        topic=topic,
        observer=observer,
        chitta=chitta,
        self_model=self_model,
        limit_per_source=limit_per_source,
    )


def scan_global_streams(
    observer: Optional[Any] = None,
    chitta: Optional[Any] = None,
    self_model: Optional[Any] = None,
    limit_per_source: int = 8,
    force: bool = False,
) -> Dict[str, Any]:
    """Convenience function for global stream scanning."""
    return get_aakaash_bridge().scan_global_streams(
        observer=observer,
        chitta=chitta,
        self_model=self_model,
        limit_per_source=limit_per_source,
        force=force,
    )


def scan_hourly_global_trends(
    observer: Optional[Any] = None,
    chitta: Optional[Any] = None,
    self_model: Optional[Any] = None,
    topic: str = "artificial intelligence",
    force: bool = False,
) -> Dict[str, Any]:
    """Convenience function for hourly global trend aggregation."""
    return get_aakaash_bridge().scan_hourly_global_trends(
        observer=observer,
        chitta=chitta,
        self_model=self_model,
        topic=topic,
        force=force,
    )