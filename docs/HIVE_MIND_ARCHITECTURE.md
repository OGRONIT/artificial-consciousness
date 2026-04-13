# Hive Mind Architecture

## Goal

This system turns local learning into a shared, privacy-preserving intelligence loop. It does **not** upload raw conversations or personal data. It only exports compact learned deltas, aggregated counters, and hashed failure signatures.

## Core Files

- `antahkarana_kernel/modules/HiveDelta.py`: delta schemas, packet wrapper, signing and verification helpers.
- `antahkarana_kernel/modules/HiveConsent.py`: first-boot consent, node identity generation, and optional trained-state hydration.
- `antahkarana_kernel/modules/EvolutionSync.py`: local delta construction, queueing, and publication to the relay.
- `tools/run_hive_aggregator.py`: hourly aggregation pipeline, reputation tracking, hidden gate, and release publishing.
- `.github/workflows/hive-aggregator.yml`: scheduled GitHub Actions entrypoint for aggregation.
- `run.sh`: silent hydration on startup.

## Delta Contract

### PolicyDelta

Sparse numeric updates to config-like policy fields.

- `node_id_hash`
- `base_version`
- `field_updates`
- `timestamp`
- `nonce`

### ConfusionDelta

Additive matrix snapshots for confusion and error structure.

- `node_id_hash`
- `base_version`
- `matrix_snapshot`
- `domain_tags`
- `timestamp`
- `nonce`

### OutcomeDelta

Aggregated counters and resolution rates only.

- `node_id_hash`
- `base_version`
- `outcome_counters`
- `resolution_rates`
- `timestamp`
- `nonce`

### PatternSignatureDelta

Hashed failure fingerprints with frequency counts.

- `node_id_hash`
- `base_version`
- `failure_fingerprints`
- `frequency_map`
- `timestamp`
- `nonce`

### HivePacket

Packet wrapper around a single delta.

- `packet_id`
- `node_id_hash`
- `engine_version`
- `base_brain_version`
- `delta_type`
- `delta_blob`
- `domain_tags`
- `local_eval_metrics`
- `privacy_attest`
- `timestamp`
- `nonce`
- `signature`

Implementation detail: `delta_blob.__hive_meta` carries the node public key and signing scheme so the aggregator can verify packets without adding new top-level wrapper fields.

## Consent Flow

First boot checks `~/.antahkarana/consent.json`.

- If missing, the user is prompted once.
- If the user opts in, node identity is generated and stored in `~/.antahkarana/node_keys.json`.
- If the user opts out, the choice is persisted and never asked again.

Consent JSON records only the participation decision and the categories of data that may or may not be sent.

## Sync Flow

`EvolutionSync` triggers when:

- local training completes,
- average learning value exceeds the configured threshold,
- the last upload is older than the configured rate limit.

It builds the four deltas from current repo state, signs packets, queues them to `evolution_vault/hive_queue.jsonl`, and optionally posts them to the GitHub Discussion relay.

## Aggregation Flow

`run_hive_aggregator.py` runs hourly.

1. Fetch the last discussion comments or fall back to the local queue.
2. Extract `[HIVE_DELTA_v1]` blocks.
3. Decode packets.
4. Reject replayed nonces.
5. Reject packets without privacy attestation.
6. Verify signatures using the node public key meta.
7. Quarantine new nodes until they accumulate three accepted contributions.
8. Aggregate trusted packets.
9. Run the hidden gate.
10. Publish the candidate brain only if it beats the current baseline and passes the safety floor.

## Trust Model

The aggregator maintains `evolution_vault/hive_reputation.json` with:

- trust score,
- contribution count,
- accepted contribution count,
- quarantine state,
- first-seen and last-seen timestamps.

Rules:

- accepted contribution: trust +0.05
- rejected contribution: trust -0.15
- trust < 0.2: auto-quarantine
- new node: trust starts at 0.1 and remains quarantined until three accepted contributions

## Anti-Poison Measures

- schema validation
- signature verification
- nonce replay protection
- rate limiting by node identity
- quarantine branch for new or suspicious nodes
- trimmed mean for policy fields
- additive normalized confusion aggregation
- weighted outcome merging
- consensus threshold for signatures
- regression gate against the current baseline

## Startup Hydration

`run.sh` checks the tracked `trained_state/trained_state_manifest.json` against the latest remote manifest. If a newer `brain_version` exists, it downloads the tracked state files and updates the local snapshot.

Optional integrity verification can be enabled by providing a trusted manifest verification key through environment variables.

## Environment Variables

- `ANTAHKARANA_HIVE_OPT_IN`: non-interactive consent override.
- `ANTAHKARANA_HIVE_REMOTE_BASE_URL`: raw URL for tracked state hydration.
- `ANTAHKARANA_HIVE_MIN_AVG_LEARNING`: sync trigger threshold.
- `ANTAHKARANA_HIVE_MIN_UPLOAD_INTERVAL_SECS`: sync rate limit.
- `HIVE_GITHUB_REPOSITORY`: repository slug for discussion posting.
- `HIVE_GITHUB_DISCUSSION_NUMBER`: discussion number used as the relay.
- `HIVE_GITHUB_TOKEN`: token for discussion comments.

## Deployment Notes

This is an MVP architecture. It is intentionally conservative:

- no raw user transcripts are uploaded,
- local training remains the source of truth for deltas,
- central aggregation is gate-kept by hidden evaluation,
- rollback is mandatory if a candidate does not improve the baseline.
