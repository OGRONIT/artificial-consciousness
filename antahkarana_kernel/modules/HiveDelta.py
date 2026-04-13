from __future__ import annotations

import base64
import dataclasses
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization

    _HAS_ED25519 = True
except Exception:  # pragma: no cover - optional dependency
    Ed25519PrivateKey = None  # type: ignore[assignment]
    Ed25519PublicKey = None  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]
    _HAS_ED25519 = False


class DeltaType(str, Enum):
    POLICY = "policy"
    CONFUSION = "confusion"
    OUTCOME = "outcome"
    SIGNATURE = "signature"


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def _default_nonce() -> str:
    return secrets.token_hex(16)


def _default_timestamp() -> float:
    return time.time()


@dataclass
class NodeCredentials:
    private_key_b64: str
    public_key_b64: str
    node_id_hash: str
    scheme: str = "fallback"

    def private_key_bytes(self) -> bytes:
        return _b64decode(self.private_key_b64)

    def public_key_bytes(self) -> bytes:
        return _b64decode(self.public_key_b64)

    def as_dict(self) -> Dict[str, str]:
        return dataclasses.asdict(self)


def generate_node_credentials() -> NodeCredentials:
    """Generate a node identity pair for opt-in hive participation.

    Ed25519 is used when the optional `cryptography` dependency is available.
    Otherwise we fall back to a pure-Python integrity scheme so the rest of the
    pipeline can still operate in stdlib-only environments.
    """

    if _HAS_ED25519:
        private_key = Ed25519PrivateKey.generate()  # type: ignore[operator]
        public_key = private_key.public_key()
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,  # type: ignore[union-attr]
            format=serialization.PrivateFormat.Raw,  # type: ignore[union-attr]
            encryption_algorithm=serialization.NoEncryption(),  # type: ignore[union-attr]
        )
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,  # type: ignore[union-attr]
            format=serialization.PublicFormat.Raw,  # type: ignore[union-attr]
        )
        return NodeCredentials(
            private_key_b64=_b64encode(private_key_bytes),
            public_key_b64=_b64encode(public_key_bytes),
            node_id_hash=_sha256_hex(public_key_bytes),
            scheme="ed25519",
        )

    private_key_bytes = secrets.token_bytes(32)
    public_key_bytes = hashlib.sha256(private_key_bytes).digest()
    return NodeCredentials(
        private_key_b64=_b64encode(private_key_bytes),
        public_key_b64=_b64encode(public_key_bytes),
        node_id_hash=_sha256_hex(public_key_bytes),
        scheme="fallback",
    )


def load_node_credentials(payload: Mapping[str, Any]) -> NodeCredentials:
    return NodeCredentials(
        private_key_b64=str(payload["private_key_b64"]),
        public_key_b64=str(payload["public_key_b64"]),
        node_id_hash=str(payload["node_id_hash"]),
        scheme=str(payload.get("scheme", "fallback")),
    )


def sign_payload(payload: Mapping[str, Any], credentials: NodeCredentials) -> str:
    message = _canonical_json(payload).encode("utf-8")
    if credentials.scheme == "ed25519" and _HAS_ED25519:
        private_key = Ed25519PrivateKey.from_private_bytes(credentials.private_key_bytes())  # type: ignore[union-attr]
        signature = private_key.sign(message)
        return _b64encode(signature)

    key = credentials.public_key_bytes()
    signature = hmac.new(key, message, hashlib.sha256).digest()
    return _b64encode(signature)


def verify_payload_signature(payload: Mapping[str, Any], signature_b64: str, credentials: NodeCredentials) -> bool:
    message = _canonical_json(payload).encode("utf-8")
    try:
        signature = _b64decode(signature_b64)
    except Exception:
        return False

    if credentials.scheme == "ed25519" and _HAS_ED25519:
        try:
            public_key = Ed25519PublicKey.from_public_bytes(credentials.public_key_bytes())  # type: ignore[union-attr]
            public_key.verify(signature, message)
            return True
        except Exception:
            return False

    expected = hmac.new(credentials.public_key_bytes(), message, hashlib.sha256).digest()
    return hmac.compare_digest(expected, signature)


@dataclass
class PythonPolicyDelta:
    node_id_hash: str
    base_version: str
    field_updates: Dict[str, float]
    timestamp: float = field(default_factory=_default_timestamp)
    nonce: str = field(default_factory=_default_nonce)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class ConfusionDelta:
    node_id_hash: str
    base_version: str
    matrix_snapshot: Dict[str, Dict[str, int]]
    domain_tags: List[str]
    timestamp: float = field(default_factory=_default_timestamp)
    nonce: str = field(default_factory=_default_nonce)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class OutcomeDelta:
    node_id_hash: str
    base_version: str
    outcome_counters: Dict[str, int]
    resolution_rates: Dict[str, float]
    timestamp: float = field(default_factory=_default_timestamp)
    nonce: str = field(default_factory=_default_nonce)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class PatternSignatureDelta:
    node_id_hash: str
    base_version: str
    failure_fingerprints: List[str]
    frequency_map: Dict[str, int]
    timestamp: float = field(default_factory=_default_timestamp)
    nonce: str = field(default_factory=_default_nonce)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class HivePacket:
    packet_id: str
    node_id_hash: str
    engine_version: str
    base_brain_version: str
    delta_type: DeltaType
    delta_blob: Dict[str, Any]
    domain_tags: List[str]
    local_eval_metrics: Dict[str, float]
    privacy_attest: bool
    timestamp: float = field(default_factory=_default_timestamp)
    nonce: str = field(default_factory=_default_nonce)
    signature: str = ""

    def to_dict(self, include_signature: bool = True) -> Dict[str, Any]:
        payload = {
            "packet_id": self.packet_id,
            "node_id_hash": self.node_id_hash,
            "engine_version": self.engine_version,
            "base_brain_version": self.base_brain_version,
            "delta_type": self.delta_type.value if isinstance(self.delta_type, DeltaType) else str(self.delta_type),
            "delta_blob": self.delta_blob,
            "domain_tags": self.domain_tags,
            "local_eval_metrics": self.local_eval_metrics,
            "privacy_attest": self.privacy_attest,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }
        if include_signature:
            payload["signature"] = self.signature
        return payload


def build_hive_packet(
    delta: Any,
    delta_type: DeltaType,
    credentials: NodeCredentials,
    engine_version: str,
    base_brain_version: str,
    domain_tags: Optional[List[str]] = None,
    local_eval_metrics: Optional[Dict[str, float]] = None,
    privacy_attest: bool = True,
) -> HivePacket:
    delta_blob = delta.to_dict() if hasattr(delta, "to_dict") else dict(delta)
    delta_blob.setdefault("__hive_meta", {})
    delta_blob["__hive_meta"].update(
        {
            "public_key_b64": credentials.public_key_b64,
            "signing_scheme": credentials.scheme,
        }
    )

    packet = HivePacket(
        packet_id=hashlib.sha256(f"{credentials.node_id_hash}:{base_brain_version}:{time.time()}:{secrets.token_hex(8)}".encode("utf-8")).hexdigest(),
        node_id_hash=credentials.node_id_hash,
        engine_version=engine_version,
        base_brain_version=base_brain_version,
        delta_type=delta_type,
        delta_blob=delta_blob,
        domain_tags=list(domain_tags or []),
        local_eval_metrics=dict(local_eval_metrics or {}),
        privacy_attest=bool(privacy_attest),
    )
    packet.signature = sign_payload(packet.to_dict(include_signature=False), credentials)
    return packet


def encode_packet_for_comment(packet: HivePacket) -> str:
    raw = _canonical_json(packet.to_dict())
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


def decode_packet_from_comment(encoded_packet: str) -> Dict[str, Any]:
    raw = base64.b64decode(encoded_packet.encode("ascii")).decode("utf-8")
    return json.loads(raw)


def packet_payload_without_signature(packet: Mapping[str, Any]) -> Dict[str, Any]:
    payload = dict(packet)
    payload.pop("signature", None)
    return payload


def derive_node_id_hash(public_key_b64: str) -> str:
    return _sha256_hex(_b64decode(public_key_b64))


def default_packet_verifier(packet: Mapping[str, Any]) -> bool:
    """Best-effort integrity check for packets lacking a node registry.

    The aggregator should prefer a key registry when available. This helper
    keeps the local toolchain usable even when the optional registry is absent.
    """

    signature = str(packet.get("signature", ""))
    meta = packet.get("delta_blob", {}).get("__hive_meta", {}) if isinstance(packet.get("delta_blob"), dict) else {}
    public_key_b64 = str(meta.get("public_key_b64", ""))
    scheme = str(meta.get("signing_scheme", "fallback"))
    if not public_key_b64:
        return False

    payload = packet_payload_without_signature(packet)
    if scheme == "ed25519" and _HAS_ED25519:
        try:
            public_key = Ed25519PublicKey.from_public_bytes(_b64decode(public_key_b64))  # type: ignore[union-attr]
            public_key.verify(_b64decode(signature), _canonical_json(payload).encode("utf-8"))
            return True
        except Exception:
            return False

    expected = hmac.new(_b64decode(public_key_b64), _canonical_json(payload).encode("utf-8"), hashlib.sha256).digest()
    try:
        return hmac.compare_digest(expected, _b64decode(signature))
    except Exception:
        return False
