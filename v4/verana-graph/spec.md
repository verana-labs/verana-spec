# Verana Graph spec

## Abstract

The Verifiable Trust ecosystem publishes its trust topology across many places: DID Documents expose Linked Verifiable Presentations, a Verifiable Public Registry (VPR) records permissions and credential schemas, and trust-resolution clients (such as [verana-indexer](https://github.com/verana-labs/verana-indexer)) compute and cache per-DID `TrustResult`s on demand. Each of these systems answers a narrow question: *"is this specific DID trusted right now?"* None of them answers *"show me every trusted service operated by organization X"* or *"list every Verifiable Service in country DE that exposes an MCP endpoint."*

**Verana Graph** is the conformant implementation of the DID Indexing role anticipated by § DID Indexing of the VPR specification. It consumes trust-resolution events, distills them into a structured graph of DIDs and their relationships, and exposes the graph through a GraphQL API tailored to discovery use cases for Verifiable AI Agents, search engines, and analytics.

This specification defines the data model, the ingestion contract with upstream trust-resolution services, the GraphQL query surface, and the normative requirements for interoperable implementations.

## About This Document

Reading this specification requires prior understanding of the [Verifiable Trust Specification](https://verana-labs.github.io/verifiable-trust-spec/) and the [VPR Specification](https://verana-labs.github.io/verifiable-trust-vpr-spec/). All terminology not redefined here inherits the meaning of its upstream definition.

Verana Graph is a **read-only** index. It does not issue credentials, does not grant permissions, does not own state that is not derivable from its upstream sources. Its single responsibility is to surface, in structured form, the trust information that is already publicly verifiable elsewhere.

## Conformance

As with sections marked non-normative, all diagrams, examples, and notes in this specification are non-normative. Everything else is normative. The key words MAY, MUST, MUST NOT, OPTIONAL, RECOMMENDED, REQUIRED, SHOULD, and SHOULD NOT are interpreted per [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) when and only when they appear in all capitals.

Normative requirements are prefixed `[TG-]` (Trust Graph).

## Terminology

Terms inherited from upstream specs are referenced by `[[ref: …]]`. Delta terminology specific to Verana Graph:

[[def: trust graph, graph]]:
~ The structured representation of DIDs, credentials, permissions, service endpoints, and their interrelationships, maintained by a Verana Graph implementation.

[[def: trust graph node, node]]:
~ A distinct entity in the [[ref: trust graph]]. One of `Did`, `Corporation`, `Ecosystem`, `CredentialSchema`, `ServiceEndpoint`, `LinkedVerifiablePresentation`, `EcsCredential`, `Vtc`, or `Participation` (see [Entity catalogue](#entity-catalogue)).

[[def: trust graph edge, edge]]:
~ A directed relationship between two [[ref: nodes]], labelled with a relation type (see [Edges](#edges)).

[[def: trust-resolution event, resolution event]]:
~ A single observation of a DID's trust status at a given block height, carrying the full verified credential set and Participation chains. Delivered to Verana Graph via the WebSocket subscription contract defined in [Ingestion](#ingestion).

[[def: architecture pattern, pattern]]:
~ The deployment shape of a [[ref: Verifiable Service]] as defined by [VS-REQ-3] and [VS-REQ-4] of the Verifiable Trust Specification. **Pattern A** denotes self-issuance (the VS is its own ORG/PERSONA); **Pattern B** denotes delegated issuance (a separate ORG/PERSONA DID issues the VS's Service Credential).

## General Requirements

### Datetime encoding

[TG-DT-1] Every datetime value defined or surfaced by this specification — including but not limited to `evaluatedAtTime`, `expiresAtTime`, `validFrom`, `validUntil`, `lastSlashedAtTime`, `lastObservedAtTime`, the inline `cgf.activeSince` / `egf.activeSince` fields, the upstream `blockTime`, and any future datetime field added in a backwards-compatible revision — MUST be encoded as an ISO 8601 / RFC 3339 datetime string **in UTC**. Each value MUST include the date, the time (with seconds), and the trailing `Z` UTC designator. Fractional seconds are OPTIONAL. Local times, non-UTC offsets (e.g. `+02:00`), date-only values, and timezone-less times MUST NOT be used. The normative regular expression is:

```regex
^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z$
```

This matches the upstream Indexer v4 [Datetime encoding](../verana-indexer/spec.md#datetime-encoding) constraint, exposed as the reusable `#/$defs/Iso8601DateTime` definition in the indexer's published JSON Schemas. Wherever this specification labels a field as `timestamp` in an entity table, the value of that field MUST satisfy this constraint.

## Ingestion

Verana Graph builds and maintains its index by subscribing to a conformant Verana Indexer ([Indexer v4 Specification](../verana-indexer/spec.md)) and dereferencing the resolution responses it returns. No state is accepted from any other source.

### Visibility and retention model

[TG-ACT-1] The graph represents **only what is currently useful and trustable**. It does not provide point-in-time, time-travel, or historical queries. Concretely:

- Time-travel parameters MUST NOT appear on the graph's own query surface; the graph fixes its evaluation point at the latest applied block at all times.
- The graph MUST persist `Participation` records only when `state = ACTIVE`. Records arriving in any other state (`FUTURE`, `INACTIVE`, `EXPIRED`, `REVOKED`, `SLASHED`, `REPAID`) MUST NOT be visible to the graph; if such a record was previously `ACTIVE` it MUST be hard-deleted on first re-resolution that observes the new state, together with every edge anchored on it.
- Sub-records carrying their own validity window (e.g. `validFrom`/`validUntil` on credentials, AnonCreds VTC `from`/`to`, or any per-record expiry signal) MUST be hard-deleted on first observation of the expiry; the graph never returns record-level-expired data. The upstream resolve response's top-level `expiresAtTime` is **not** a record-level validity window — it is the DID's *trust-evaluation* expiry horizon, handled separately per [[TG-ACT-3]] (retention + default query filter, not deletion).
- A per-DID-owned record (`ServiceEndpoint`, `LinkedVerifiablePresentation`, `EcsCredential`, `Participation`) or any edge that disappears from a fresh resolve MUST be hard-deleted (no tombstones, no historical retention). Retention exceptions for the chain-immutable entities (`Corporation`, `Ecosystem`, `CredentialSchema`) are stated in [[TG-ACT-2]].
- A `Vtc` record MUST be hard-deleted once no `LinkedVerifiablePresentation` in the graph still references it (no inbound `CONTAINS_VTC` edge). This covers VPs re-signed without the VTC and VPs removed entirely. Implementations MAY use reference counting on inbound edges or periodic sweeps; orphan `Vtc` records MUST NOT accumulate. No equivalent rule applies to `Corporation`, `Ecosystem`, or `CredentialSchema`: per [[TG-ACT-2]] those entities are chain-immutable and never deleted from the graph once observed.

[TG-ACT-2] `Corporation`, `Ecosystem`, and `CredentialSchema` are **chain-immutable**: once observed, the corresponding graph records MUST be retained for the lifetime of the graph and MUST NOT be hard-deleted by any rule of [[TG-ACT-1]]. Concretely:

- Their identities (`Corporation.id` = bech32 group address, `Ecosystem.id` = uint64, `CredentialSchema.id` = uint64) are stable for the lifetime of the entry.
- `Corporation.did` and `Ecosystem.did` are mutable; on DID rotation the graph MUST update the field on the existing record without creating a new record or deleting the old one. The previous controller's resolve will stop surfacing the entity inline; the new controller's resolve will surface it instead. Disappearance from any one DID's resolve MUST NOT trigger deletion.
- `Ecosystem` and `CredentialSchema` carry a mutable `archived: boolean` field whose transitions are bidirectional (archive ↔ unarchive). The graph MUST observe both directions, which requires `includeArchived: true` on the resolve request per [[TG-INGEST-2]].
- When `archived: true`, the entity MUST NOT be returned as a direct query result on its own entity surface, but MUST remain reachable by traversal from any other entity that references it (e.g. a `Vtc.ecosystemId` pointing to an archived `Ecosystem`, or a `Participation.credentialSchemaId` pointing to an archived `CredentialSchema`). The chain enforces that no new `Participation` may be created against an archived `CredentialSchema`; this constraint is not enforced by the graph.

[TG-ACT-3] The upstream resolve response's top-level `expiresAtTime` (required per [`response.schema.json`](../verana-indexer/schemas/v4/vt/response.schema.json)) is the wall-clock expiry of the indexer's trust evaluation for the resolved DID. The graph MUST persist it on the corresponding `Did` record (see [`Did`](#did) entity table). A DID is **trust-expired** when its persisted `expiresAtTime < now` at query time. Trust-expired DIDs MUST NOT be hard-deleted by any rule of [[TG-ACT-1]]; they MUST be retained for referential integrity, in the same spirit as archived Ecosystems and CredentialSchemas under [[TG-ACT-2]]. Concretely:

- Query semantics on the trust surface MUST exclude trust-expired entries from **direct** results — specifically: the trust-expired `Did` itself (as a Verifiable Service), any `Corporation` whose current `did` equals the trust-expired DID, and any `Ecosystem` whose current `did` equals the trust-expired DID. No opt-in is offered to include them. The asymmetry with [[TG-ACT-2]]'s bidirectional `archived` flag is intentional: archived Ecosystems and CredentialSchemas remain meaningful on the trust surface for historical attribution and for validating credentials issued under them prior to archival, whereas a trust-expired DID is by definition not currently trustable and therefore has no legitimate role as a direct hit on the trust surface.
- Trust-expired DIDs and the records anchored on them MUST remain reachable by **traversal** from other entities (e.g. as the parent of a `Participation`, or via inbound edges from other DIDs' resolves), so referential queries continue to resolve.
- The gate is purely query-time `expiresAtTime < now` evaluated against the persisted value: if a subsequent resolve refreshes the DID with a future `expiresAtTime`, the trust-expired predicate lifts automatically at the next query. No deletion / undeletion is involved.

### Subscription contract

The rules in this subsection refer to the following per-instance ingestion state. An implementation MUST maintain at least:

| Variable           | Definition                                                                                                                                                                                                                                                                                                                                          |
| ---                | ---                                                                                                                                                                                                                                                                                                                                                 |
| `B`                | The bootstrap snapshot block, captured from the WebSocket `ready.block` field per [[TG-INGEST-3]]. The graph applies all bootstrap calls at `atBlock = B - 1`.                                                                                                                                                                                       |
| `block`            | The block height carried by an incoming `ChangeEnvelope` (WebSocket envelope or `listChanges` entry), as defined by the indexer's [`changes.schema.json`](../verana-indexer/schemas/v4/vt/changes.schema.json). The graph uses this value as `atBlock` when reconciling that envelope's changes.                                                |
| `blockTime`        | The wall-clock timestamp carried by an incoming `ChangeEnvelope`. The graph uses it for `lastObservedAtTime` on the records it touches.                                                                                                                                                                                                                  |
| `previousBlock`    | The block height of the most recently *received* WebSocket envelope, regardless of whether its changes have been reconciled yet. Used to detect gaps in the live stream via the predicate `block > previousBlock + 1` in [[TG-INGEST-5]]. Initialised to `B - 1` at bootstrap and updated on every received envelope.                                |
| `lastAppliedBlock` | The highest block height for which every change envelope (from the WebSocket or from `listChanges`) has been fully reconciled into the graph and durably committed. Initialised to `B - 1` once [[TG-INGEST-3]] step 4 completes, advanced monotonically thereafter, persisted across restarts. Used by [[TG-INGEST-5]] as the gap-recovery resume point: gap-recovery starts at `fromBlock = lastAppliedBlock + 1`. |
| `lastBlockInGap`   | Within a single gap-recovery pass driven by [[TG-INGEST-5]], the highest `block` returned by the iterated `listChanges` calls. Used as the optional coalescing target.                                                                                                                                                                               |

`previousBlock` and `lastAppliedBlock` are intentionally distinct: `previousBlock` advances on *receipt* of an envelope (so gap detection sees the freshest stream position), whereas `lastAppliedBlock` advances only on *durable commit* (so a crash between receipt and commit is recoverable via gap-recovery from `lastAppliedBlock + 1`).

[TG-INGEST-1] A Verana Graph implementation MUST open a WebSocket subscription to the upstream Indexer's `subscribeChanges` endpoint with **all channels enabled** and **all opt-in sub-flags set to `true`**, so that no resolver-observable change escapes the graph. The `dids[]` field MUST be omitted, which subscribes to every DID indexed by the upstream resolver. The canonical control message — which MUST validate against the indexer's [`subscribe.schema.json`](../verana-indexer/schemas/v4/vt/subscribe.schema.json) — is:

```json
{
   "action": "subscribe",
   "channels": {
      "trust":          true,
      "corporation":    { "includeDepositChanges":     true },
      "participations": {
         "includeWeightChanges":       true,
         "includeParticipantCounts":   true,
         "includeIssuedCredentials":   true,
         "includeVerifiedCredentials": true
      },
      "ecsCredentials": true,
      "presentations":  true,
      "services":       true,
      "ecosystems": {
         "includeParticipantCounts":   true,
         "includeIssuedCredentials":   true,
         "includeVerifiedCredentials": true
      }
   }
}
```

[TG-INGEST-2] For every `resolve` call issued by Verana Graph (bootstrap or block handler; per [[TG-DEREF-1]] there are no other call sites), the request MUST set every optional selector to its broadest value subject to two scope constraints: (a) `participations.states` MUST be `["ACTIVE"]` per [[TG-ACT-1]] (non-`ACTIVE` Participations are never persisted); (b) `includeArchived` MUST be `true` on both `ecosystems` and `credentialSchemas` per [[TG-ACT-2]] (archived entities remain visible-by-reference in the graph and the archive flag is bidirectional, so the graph must observe both transitions). The canonical request payload — which MUST validate against the indexer's [`request.schema.json`](../verana-indexer/schemas/v4/vt/request.schema.json), with the response shape following [`response.schema.json`](../verana-indexer/schemas/v4/vt/response.schema.json) — is:

```json
{
   "did":           "<did>",
   "corporation":   true,
   "participations": {
      "states": ["ACTIVE"]
   },
   "ecsCredentials": true,
   "services":       true,
   "presentations": {
      "unresolvableCredentialIds": true,
      "invalidCredentialIds":      true
   },
   "ecosystems": {
      "includeArchived": true,
      "credentialSchemas": { "includeArchived": true }
   }
}
```

`atTime` MUST be omitted. `atBlock` MUST be set to the **block of evidence** for the call:

- the bootstrap snapshot block `B - 1` for the enumeration and per-DID resolves of [[TG-INGEST-3]];
- the `block` of the WebSocket envelope for the live resolves of [[TG-INGEST-4]];
- the `block` of the `listChanges` entry for the gap-recovery resolves of [[TG-INGEST-5]].

Anchoring every call to its block of evidence is the indexer's documented pattern (per [Indexer v4 §subscribeChanges](../verana-indexer/spec.md#subscribechanges--websocket-subscription), the client calls `/vt/v1/resolve` at `atBlock = <block of the change envelope>` to obtain the new state for any non-`trust` channel). It makes change processing deterministic, makes gap-recovery replay-safe, aligns `lastObservedAtBlock` with the actual block of evidence, and avoids races in which a resolve at "latest" silently observes state from a block later than the triggering event. [[TG-ACT-1]]'s prohibition on time-travel applies to the graph's own query surface, not to its indexer-facing input.

Note that filtering `resolve` to `states: ["ACTIVE"]` does **not** cause transitions out of `ACTIVE` to be missed. Per the indexer specification, the `subscribeChanges` `participations` channel is **not** state-filterable: it fires on **every** state transition of a `Participation` involving a subscribed DID, including `ACTIVE → {INACTIVE, EXPIRED, REVOKED, SLASHED, REPAID}` and `FUTURE → ACTIVE`. The state filter applies only to the *response* of `resolve`. On each `participations` notification the graph re-resolves with the request above and reconciles by **diff-from-absence**: any locally persisted `Participation` for the subject DID that is no longer present in the new response MUST be hard-deleted per [[TG-ACT-1]] / [[TG-PROV-1]]. This single mechanism imports newly-`ACTIVE` participations and evicts those that have left `ACTIVE`, without requiring the graph to subscribe to or persist any non-`ACTIVE` state.

[TG-INGEST-3] A Verana Graph implementation MUST bootstrap an initial snapshot before applying any live block message, following the [Indexer Bootstrap pattern](../verana-indexer/spec.md#bootstrap-pattern):

1. Capture `B = ready.block` from the WebSocket `ready` message.
2. Buffer all incoming WebSocket block messages without applying.
3. Enumerate the DID universe at block `B - 1` via `GET /vt/v1/dids?atBlock=B-1`, paginating through `nextCursor`, to align the snapshot with the WebSocket cut-over.
4. Resolve each enumerated DID via `POST /vt/v1/resolve` using the request payload of [[TG-INGEST-2]] with `atBlock = B - 1`, persisting the resulting state into the graph.
5. Apply the buffered WebSocket block messages from block `B` onwards.

[TG-INGEST-4] On every WebSocket `block` message received after bootstrap, the graph MUST, for each entry in `changes[]`:

1. Apply the inline `trust` payload (when present) directly to the corresponding `Did` record, overwriting the trust-core fields atomically and setting `lastObservedAtTime = blockTime`.
2. If any other channel flag in the entry is `true`, issue **one** `resolve` call as defined in [[TG-INGEST-2]] with `atBlock = block` and reconcile the result against the persisted state per [[TG-PROV-1]] and [[TG-EDGE-1]].

A single `resolve` call per `(did, block)` is REQUIRED regardless of how many channel flags are simultaneously set: the response carries every section the graph subscribes to, so per-channel calls are forbidden as redundant.

[TG-INGEST-5] On a detected gap in the WebSocket sequence (`block > previousBlock + 1`) or following a connection drop, the graph MUST resume via the Indexer's `listChanges` from `fromBlock = lastAppliedBlock + 1` until either `nextFromBlock` is `null` or it overlaps the smallest block held in the resume buffer. Each `listChanges` entry MUST be applied as in [[TG-INGEST-4]] using `atBlock = entry.block`, then the buffered WebSocket messages are replayed with deduplication by `(did, block)`. For gaps larger than an implementation-defined threshold, an implementation MAY coalesce the per-`(did, block)` resolves into a single resolve per unique DID at `atBlock = lastBlockInGap`, since [[TG-ACT-1]] makes the graph's terminal state independent of the intermediate transitions; the buffered WebSocket replay still uses per-block `atBlock`.

### Resource dereferencing

A resolve response carries three classes of reference, treated differently by the graph:

- **Referenced DIDs are not chased.** Each referenced DID is itself a member of the indexer's DID universe (`listIndexedDids` enumerates every Corporation `did`, every Ecosystem `did`, and every Participant `did`) and is therefore covered by the global subscription mandated in [[TG-INGEST-1]]. Its own change envelope will arrive on its own block, and its bootstrap resolve is handled in bulk by [[TG-INGEST-3]] step 4. Edges reference their target by the target entity's stable identity column per [[TG-EDGE-1]]; the target entity record materialises when *that DID* is reconciled.
- **Inline governance-framework metadata is persisted directly.** Per [Indexer v4 §Example resolution response](../verana-indexer/spec.md#example-resolution-response), `corporation.cgf` and `ecosystems[].egf` arrive in-band as compact summaries (active version + activation timestamp + per-language document URLs + `digestSRI`s). The graph persists these objects verbatim on the corresponding `Corporation` / `Ecosystem` records; no separate resource-load call is needed.
- **Out-of-band resource bodies are fetched explicitly**: credential-schema bodies (via the indexer's resource-load API, one-shot per record), Linked Verifiable Presentations (via plain HTTP GET against the VP URL), and — optionally — CGF/EGF document bodies (via plain HTTP GET against the URLs in the inline metadata) when the implementation wants to index document content for full-text search.

[TG-DEREF-1] When reconciling a resolve response for a DID `X`, a Verana Graph implementation MUST NOT issue any further `resolve` calls for the DIDs referenced from that response (`ecsCredentials[].credentialSubject.id`). Resolving forward from `X`'s response would (a) duplicate work that the global subscription of [[TG-INGEST-1]] already guarantees and (b) introduce unbounded recursion through the trust graph. Edges SOURCE→TARGET are persisted by stable identity per [[TG-EDGE-1]]; if the target's entity record has not yet been observed (transient during bootstrap), the edge is still committed and the join completes when the target's own resolve is reconciled.

[TG-DEREF-2] **Credential schemas are immutable.** A given schema `id` is permanently bound to a single body whose `digestSRI` never changes; an edit to a schema is published as a *new* `id`. The graph therefore loads each schema **at most once over the lifetime of any given `CredentialSchema` record**:

1. The first time an `ecosystems[].credentialSchemas[]` entry surfaces a schema `id` in a resolve response and that id is not already held as a `CredentialSchema` record, the graph MUST call the indexer's **resource-load API for schemas** (the indexer endpoint that loads VPR `CredentialSchema` resources by stable id, the indexer's wrapper around [VPR `MOD-CS-QRY-2`](https://github.com/verana-labs/verifiable-trust-vpr-spec/blob/main/spec.md#mod-cs-qry-2-get-credential-schema)), validate the response body's hash against the surfaced `digestSRI`, and persist body + metadata (`id`, `type`, `digestSRI`) as a `CredentialSchema` record. The graph never bypasses the indexer to query VPR directly. Schema ids surface uniformly across the resolve response: `ecosystems[].credentialSchemas[].id`, `participations[].credentialSchemaId`, `ecsCredentials[].credentialSchemaId`, and `presentations[].vtcCredentials[].credentialSchemaId` all reference the same stable identifier; only `ecosystems[].credentialSchemas[]` triggers a schema-load (the other surfaces reference schemas by id without loading them). By the time a `Participation`, `EcsCredential`, or `Vtc` is reconciled, the owning Ecosystem's resolve will already have persisted the schema (via its own `ecosystems` channel), or the referenced schema record will materialise when that Ecosystem is subsequently reconciled — in either case the edge anchored on `credentialSchemaId` is committed immediately per [[TG-EDGE-1]] regardless of materialisation order.
2. On every subsequent surfacing of the same schema `id` the graph MUST reuse the persisted record without issuing any further schema-load call. Only `lastObservedAtTime` and `lastObservedAtBlock` are updated, so that the diff-from-absence rule of [[TG-PROV-1]] continues to apply.

The only schema state that can change is the **archived flag**, which is surfaced via the controlling Ecosystem's `ecosystems` channel. Since [[TG-INGEST-2]] requests `credentialSchemas.includeArchived: true`, archive and unarchive transitions are observed as a flip of the `archived` field on the surfaced `ecosystems[].credentialSchemas[]` entry; the graph updates `CredentialSchema.archived` accordingly per [[TG-ACT-2]], and the schema record together with every edge anchored on it is preserved across both transitions. The body is never re-loaded — the schema is content-immutable, so a hypothetical re-fetch would return byte-identical bytes.

[TG-DEREF-2a] **Ecosystem Governance Framework (inline).** For each entry of `ecosystems[]` carrying an `egf` object, the graph MUST persist the `egf` object verbatim on the corresponding `Ecosystem` record (active `version`, `activeSince`, and the `documents[]` array of `(language, url, digestSRI)` triples). No resource-load call is required — the indexer surfaces the active GF inline.

The graph MAY additionally HTTP-GET each `egf.documents[].url` and persist the document body alongside the metadata, validating the fetched bytes against the surfaced `digestSRI`; this is RECOMMENDED for implementations that offer full-text search over EGFs and OPTIONAL otherwise. **Governance-framework document bodies are immutable**: a given `digestSRI` permanently identifies the same bytes. The graph therefore SHOULD key its document-body cache by `digestSRI` so that any body the graph has ever fetched is reused on every subsequent surfacing of the same `digestSRI` — regardless of which Ecosystem, which EGF version, which language entry, or which block surfaces it. An EGF rotation that introduces a *new* `digestSRI` (a genuinely new body) MAY trigger one new fetch; an EGF rotation that re-surfaces an unchanged `digestSRI` (e.g. a doc that survives the rotation, or a body the graph already cached from another Ecosystem) MUST NOT trigger any fetch.

[TG-DEREF-2b] **Corporation Governance Framework (inline).** Same shape as [[TG-DEREF-2a]], applied to `corporation.cgf`: the graph MUST persist `cgf` verbatim on the corresponding `Corporation` record and MAY HTTP-GET each `cgf.documents[].url` for full-text indexing. The same global immutability invariant applies — each CGF document `digestSRI` is fetched **at most once, ever**, and the cache is shared with the EGF cache of [[TG-DEREF-2a]] (a `digestSRI` is a `digestSRI`, irrespective of whether the indexer surfaced it under `cgf` or `egf`).

[TG-DEREF-3] **Linked Verifiable Presentations carry non-ECS VTCs only.** A VP exposed under `presentations[]` carries Verifiable Trust Credentials voluntarily presented by the DID holder *in addition to* the mandatory ECS credentials (`ServiceCredential`, `OrganizationCredential`, `PersonaCredential`), which the indexer surfaces separately under `ecsCredentials[]`. Each entry of `presentations[].vtcCredentials[]` is a structured reference `{id, credentialSchemaId, ecosystemId}` to one non-ECS VTC; `unresolvableCredentialIds[]` and `invalidCredentialIds[]` are observability-only flat lists of credential ids the indexer could not resolve or found invalid.

For each `presentations[]` entry the graph MUST:

1. Persist a `LinkedVerifiablePresentation` record with the VP `id`, `serviceId`, and the `unresolvableCredentialIds[]` / `invalidCredentialIds[]` arrays.
2. For each `vtcCredentials[]` entry: materialise a `Vtc` record (keyed by the credential `id`) holding `credentialSchemaId` and `ecosystemId`, create the `CONTAINS_VTC: LVP → Vtc` edge, and create the standard `BASED_ON_SCHEMA: Vtc → CredentialSchema` and `GOVERNED_BY: Vtc → Ecosystem` edges anchored on those stable ids.

The indexer has already fetched the VP, verified its signature against the holder's DID Document, and classified every credential it contains, so the graph trusts the classification per [[TG-DEREF-1]] and is NOT required to re-fetch the VP body for its core entity-and-edge model.

Implementations that wish to additionally index the *subject claims* of these VTCs (e.g. to support search facets such as “Verifiable Services presenting a Diploma credential whose `degreeType = MSc`”) MAY HTTP-GET the VP URL, re-verify the VP signature against the holder's DID Document, extract each credential whose `id` appears in `vtcCredentials[].id`, and persist its body alongside the corresponding `Vtc` record. This body fetch is OPTIONAL, is subject to the per-block dedup of [[TG-DEREF-4]], and SHOULD be skipped when the live envelope's `presentations` channel flag is `false` (the VP contents cannot have changed in that case).

[TG-DEREF-4] Out-of-band resource fetches fall into two tiers:

- **Immutable resources — fetched at most once, ever.** Credential schemas ([[TG-DEREF-2]]) and CGF / EGF document bodies ([[TG-DEREF-2a]] / [[TG-DEREF-2b]]) are content-immutable: a given schema `id` and a given GF-document `digestSRI` are permanently bound to one body. The graph MUST maintain a process-wide cache keyed by schema `id` for schemas and by `digestSRI` for GF documents, and MUST return cached bytes on every subsequent surfacing — *regardless of which block, which channel, or which DID surfaces them*. Per-block dedup is therefore redundant for these channels and MUST NOT be imposed as the dedup boundary; the cache itself is the dedup primitive.
- **Mutable resources — deduplicated per `(resource-id, current block)`.** Optional Linked Verifiable Presentation body fetches ([[TG-DEREF-3]]) target URLs whose payload can change over time (the holder re-signs the VP whenever its credential set changes). Multiple resolves at the same block referencing the same VP URL MUST trigger only one fetch; the dedup key is the VP URL itself, not the originating DID.

Inline metadata in the resolve response (`corporation.cgf`, `ecosystems[].egf`, `presentations[].vtcCredentials[]` and friends) requires no fetch and no dedup.

### Channel-to-section mapping

For traceability, the table below records which resolver response sections each upstream channel signals are derived from. Note that, per [[TG-INGEST-4]], the graph always issues the maximum-selector request defined in [[TG-INGEST-2]] regardless of which subset of channels signalled the change; the table is informative.

| Channel          | Resolve response sections consumed                                                                  |
| ---              | ---                                                                                                 |
| `trust`          | core fields (`trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`)    |
| `corporation`    | `corporation`                                                                                       |
| `participations` | `participations[]`                                                                                  |
| `ecsCredentials` | `ecsCredentials[]`                                                                                  |
| `presentations`  | `presentations[]`                                                                                   |
| `services`       | `services[]`                                                                                        |
| `ecosystems`     | `ecosystems[]`                                                                                      |

## Persistence Model

The persistence model is dual-projected:

- **Graph traversal** — every relationship surfaced by the resolver is materialised as a typed edge between two entity records, so a query rooted at a DID can walk to its Corporation, Ecosystems, Credential Schemas, peer DIDs, issued/received Credentials, and Service Endpoints in bounded steps.
- **Faceted search** — every searchable entity type (Verifiable Service, Ecosystem, Corporation, Credential Schema, Service Endpoint) carries a flat field projection that supports full-text and structured filtering (country, organisation kind, service type, schema, freshness, …).

Both projections are derived deterministically from the same upstream resolve responses. A conformant implementation MAY share storage between the two projections (e.g. a single graph database with secondary search indexes) or split them (e.g. graph database + search engine), provided both surfaces are kept in sync per [[TG-INGEST-4]].

### Freshness fields

Every persisted entity and every persisted edge MUST carry the following freshness fields, in addition to the entity-specific or edge-specific fields defined later in this section:

| Field                 | Description                                                                                                                                  |
| ---                   | ---                                                                                                                                          |
| `lastObservedAtTime`  | Wall-clock timestamp of the resolve response from which the graph most recently persisted this record (the `blockTime` of the corresponding ingestion envelope per [[TG-INGEST-3]] / [[TG-INGEST-4]] / [[TG-INGEST-5]]).                                                              |
| `lastObservedAtBlock` | VPR block height of the resolve response from which the graph most recently persisted this record (the envelope's `block`, which equals the `atBlock` used on the resolve call per [[TG-INGEST-2]]).                                                                  |

[TG-PROV-1] On every resolve response received per [[TG-INGEST-3]] / [[TG-INGEST-4]] / [[TG-INGEST-5]], every persisted field whose value differs from the new response MUST be overwritten and `lastObservedAtTime` and `lastObservedAtBlock` updated. Records or edges no longer present in the new response, or whose state has left `ACTIVE`, or whose record-level validity window has elapsed, MUST be hard-deleted per [[TG-ACT-1]]. Trust-expired DIDs (per [[TG-ACT-3]]) are NOT hard-deleted; they are retained and gated only at query time. The graph does NOT retain history.

### Entity catalogue

The graph persists exactly the following entity types. Each record is keyed by the **identity** column shown, which is always a **stable VPR identifier** — never a mutable DID for entities (`Corporation`, `Ecosystem`, `Participation`) whose DID is permitted to rotate over their lifetime. Records are linked by typed edges (see [Edges](#edges)) and are never collapsed across entity types.

| Entity                        | Identity                                                          | Sourced from                                                                                                |
| ---                           | ---                                                               | ---                                                                                                         |
| `Did`                         | `did` (string)                                                    | every queried DID + every DID referenced from a resolve response                                            |
| `Corporation`                 | `id` (bech32 group address)                                       | the singular `corporation` object of any resolve response (including inline `cgf` per [[TG-DEREF-2b]]). Per VPR's per-Corporation `did` uniqueness invariant, a DID is the `did` of at most one Corporation, so the indexer surfaces it as a single object — not an array. The `did` is envelope-derived (not repeated on the object). Per VPR the Corporation entry extends a Cosmos SDK group (1:1 with the group) and has no uint64 id of its own; the underlying group's bech32 address serves as its stable identifier and is named `id` for consistency with other VPR-id-keyed entities |
| `Ecosystem`                   | `id` (uint64, VPR ledger id)                                      | `ecosystems[]` of any resolve response (including inline `egf` per [[TG-DEREF-2a]]). Keyed by `id` because per VPR `Ecosystem.did` is permitted to rotate; `id` is the stable ledger primary key |
| `CredentialSchema`            | `id` (uint64, VPR ledger id)                                      | `ecosystems[].credentialSchemas[]`, augmented with the indexer schema-load API ([[TG-DEREF-2]]). Per VPR every schema has a stable ledger `id` permanently bound to one body via its `digestSRI`; an edit to a schema is published as a *new* `id`. The URI form (`vpr:verana:<network>/cs/v1/js/<id>`) is deterministic from `(network, id)` and is not stored as a separate field — it is reconstructed when needed (e.g. for TRQP `resource` arguments) |
| `ServiceEndpoint`             | DID Document service entry `id` (string)                          | `services[]`                                                                                                |
| `LinkedVerifiablePresentation`| VP `id` (URL)                                                     | `presentations[]`                                                                                           |
| `EcsCredential`               | credential `id` (string)                                          | `ecsCredentials[]`                                                                                          |
| `Vtc`                         | credential `id` (string)                                          | `presentations[].vtcCredentials[]`. One record per non-ECS Verifiable Trust Credential carried by some VP. Disjoint from `EcsCredential` (ECS credentials are surfaced separately and never appear in `vtcCredentials[]`) |
| `Participation`               | `id` (uint64, VPR `Participant.id`)                               | `participations[]` of any resolve response. Each entry's `did` is envelope-derived (equals the resolved `did`, by the channel rule "a Participation entry the DID is part of") and is not repeated per entry; the graph reads `Participation.didId` from `response.did`. Keyed by `id`, the stable VPR ledger primary key                                                                                              |

#### `Did`

| Field             | Type                                | Source                                                                                                                  | Notes                                                                                                              |
| ---               | ---                                 | ---                                                                                                                     | ---                                                                                                                |
| `did`             | string                              | `did`                                                                                                                   | Identity                                                                                                           |
| `trusted`         | bool                                | `trusted`                                                                                                                | VS-REQ-2/3/4 trust flag at last evaluation                                                                         |
| `evaluatedAtTime` | timestamp                           | `evaluatedAtTime`                                                                                                       |                                                                                                                    |
| `evaluatedAtBlock`| uint64                              | `evaluatedAtBlock`                                                                                                      |                                                                                                                    |
| `expiresAtTime`   | timestamp                           | `expiresAtTime`                                                                                                          | Wall-clock expiry of the indexer's trust evaluation for this DID. When `< now` the DID is **trust-expired** per [[TG-ACT-3]]: the record is retained for traversal, but the DID — and any `Corporation` / `Ecosystem` whose current `did` equals this DID — MUST NOT appear as a direct hit on the trust surface (no opt-in). Always present (required by the indexer's response schema) |
| `corporationId`   | account                             | `corporationId`                                                                                                         | Stable id (bech32 group address) of the unique Corporation that owns this DID — by VPR's per-Corporation `did` uniqueness invariant and the per-Participant `(did, corporation)` consistency invariant, this is simultaneously the Corp the DID *represents* and the **operating** Corp that authorises every Participation's `vsOperator` account. Direct edge anchor for `OPERATED_BY: Did → Corporation`. Trust-core field; always present when the DID is surfaced (every surfaced DID has a Corp). The per-Participation `vsOperator` accounts (one per Participant entry) live on `Participation` records, not here — a `vsOperator` is a Participant-scoped grant, not a DID-scoped one |
| `pattern`         | enum (`A` \| `B`)                   | derived during ingestion (see [[def: architecture pattern]])                                                            | `A` = self-issued; `B` = delegated. No `null` value: a DID without a presented `ServiceCredential` is not [[ref: trusted]] per [VS-REQ-2] of the Verifiable Trust Specification and is therefore never surfaced by the indexer in the first place |
| `serviceTypes`    | string[]                            | `services[].type` (DID Document service entries)                                                                        | Search-facing facet (e.g. `did-communication`, `LinkedDomains`, `MCP`). For the VS-level service type asserted by the `ServiceCredential`, see [`EcsCredential.ServiceCredential.type`](#ecscredential) |

#### `Corporation`

The `corporation` object surfaced in a resolve response is a **singular** (per VPR's per-Corporation `did` uniqueness invariant): a DID is the `did` of at most one Corporation, so the indexer surfaces it as a single object rather than an array. The `did` field is derived from the response **envelope** (`response.did`) rather than from the object itself — by the indexer's channel rule the `corporation`'s `did` equals the resolved DID. This mirrors the envelope-derivation pattern used by [`Ecosystem`](#ecosystem) and [`Participation`](#participation).

| Field           | Type             | Source                       | Notes                                                |
| ---             | ---              | ---                          | ---                                                  |
| `id`            | account          | `corporation.id`             | **Identity.** Bech32 address of the underlying Cosmos SDK group (1:1 with the group). Per VPR the Corporation has no uint64 id of its own; the group address serves as the stable primary key |
| `did`           | string           | envelope: `response.did`     | The Corporation's current DID. **Mutable** — may be rotated by the controlling group; the record is preserved because the identity is `id`, not `did` |
| `deposit`       | Coin             | `corporation.deposit`        | Search ranking signal (numeric range)                |
| `lastSlashedAtTime` | timestamp \| `null` | `corporation.lastSlashedAtTime`  |                                               |
| `slashedEvents` | uint             | `corporation.slashedEvents`  | Search ranking signal                                |
| `slashedValue`  | Coin \| `null`   | `corporation.slashedValue`   |                                                      |
| `cgf`           | object \| `null` | `corporation.cgf` (inline, per [[TG-DEREF-2b]]) | active CGF: `{ version, activeSince?, documents: [{language, url, digestSRI}] }`. Persisted verbatim; document bodies optionally fetched and stored alongside per [[TG-DEREF-2b]]. `null` only when the Corporation has not yet published any GF |

#### `Ecosystem`

For each `ecosystems[]` entry surfaced in a resolve response, the `did` field is derived from the response **envelope** (`response.did`) rather than from per-entry data: by the indexer's channel rule, every entry in `ecosystems[]` is an ecosystem the resolved DID *represents*, so all entries in one response share the resolved DID. The controlling-Corporation binding (`corporationId`) is surfaced **per entry** even though, per VPR's per-Ecosystem `(did, corporation)` consistency invariant, every Ecosystem with a given `did` is controlled by the same Corporation — so all `ecosystems[i].corporationId` values within any single resolve response are necessarily equal. The redundancy is intentional: each entry remains self-describing for streaming consumers, and the controlling-Corp binding is *not* equivalent to the envelope-level `corporationId` (the Corp that **owns** the DID per Invariant 1) — the Corp owning a DID and the Corp controlling Ecosystems claiming that DID MAY differ (e.g. an Ecosystem run by Corp `C₂` under Corp `C₁`'s DID brand).

| Field                     | Type            | Source                                                                                            | Notes                                                                                                       |
| ---                       | ---             | ---                                                                                               | ---                                                                                                         |
| `id`                      | uint64          | `ecosystems[].id`                                                                                 | **Identity.** VPR ledger id; immutable for the lifetime of the Ecosystem entry                              |
| `did`                     | string          | envelope: `response.did`                                                                          | The Ecosystem's current DID. **Mutable** — may be rotated by the controlling Corporation; the record is preserved because the identity is `id`, not `did` |
| `archived`                | boolean         | `ecosystems[].archived`                                                                           | **Mutable**, bidirectional (archive ↔ unarchive). When `true`, the Ecosystem MUST NOT be returned as a direct query result but MUST remain reachable by traversal from any referencing entity, per [[TG-ACT-2]] |
| `corporationId`           | account         | `ecosystems[].corporationId`                                                                      | edge anchor to `Corporation` by stable id (bech32 group address) of the controlling Corporation. Surfaced per entry rather than envelope-derived because the controlling Corp MAY differ from the envelope-level `corporationId` (the Corp that *owns* the DID per Invariant 1) — though per Invariant 3 all `ecosystems[i].corporationId` values within a single response are necessarily equal to one another |
| `participants`            | map<role, uint> | `ecosystems[].participants`                                                                       | aggregate per-role count, search ranking signal                                                             |
| `issuedCredentials`       | uint64          | `ecosystems[].issuedCredentials`                                                                  | search ranking signal                                                                                       |
| `verifiedCredentials`     | uint64          | `ecosystems[].verifiedCredentials`                                                                | search ranking signal                                                                                       |
| `credentialSchemaIds`               | uint64[]        | `ecosystems[].credentialSchemas[].id`                                                                       | edge anchor to `CredentialSchema` records by stable id. Anchors the `OWNS_SCHEMA: Ecosystem → CredentialSchema` edge                                                                                              |
| `egf`                     | object \| `null`| `ecosystems[].egf` (inline, per [[TG-DEREF-2a]])                                                  | active EGF: `{ version, activeSince?, documents: [{language, url, digestSRI}] }`. Persisted verbatim; document bodies optionally fetched and stored alongside per [[TG-DEREF-2a]]. `null` only when the Ecosystem has not yet published any GF |

#### `CredentialSchema`

| Field                 | Type                          | Source                                                                                                              | Notes                                                                          |
| ---                   | ---                           | ---                                                                                                                 | ---                                                                            |
| `id`                  | uint64                        | `ecosystems[].credentialSchemas[].id`                                                                                         | **Identity.** VPR ledger id; immutable for the lifetime of the schema record (per VPR, an edit produces a new schema with a new `id`). The sole identity used by the graph and by the indexer's schema-load API. The URI form (`vpr:verana:<network>/cs/v1/js/<id>`) is deterministic from `(network, id)` and is reconstructed when needed (e.g. for TRQP `resource` arguments); it is not stored as a separate field |
| `type`                | string                        | `…schema.type`                                                                                                      | e.g. `JsonSchema`                                                              |
| `digestSRI`           | string                        | `…schema.digestSRI`                                                                                                 | SHA-384 of the canonical schema body                                           |
| `archived`            | boolean                       | `ecosystems[].credentialSchemas[].archived`                                                                         | **Mutable**, bidirectional (archive ↔ unarchive). When `true`, the schema MUST NOT be returned as a direct query result but MUST remain reachable by traversal from any referencing entity, per [[TG-ACT-2]]. The chain enforces that no new `Participation` may be created against an archived schema; existing `ACTIVE` Participations linked to it remain valid |
| `ecosystemId`         | uint64                        | derived from the parent `ecosystems[]` entry whose `credentialSchemas[]` contains this `id` (or from the schema body's owning-trust-registry field when loaded via the schema-load API) | edge anchor to `Ecosystem` by stable id. **Exactly one** — a schema is owned by a single controlling Ecosystem and is never shared, per VPR. Immutable for the lifetime of the record |
| `participants`        | map<role, uint>               | `ecosystems[].credentialSchemas[].participants`                                                                               | search ranking signal                                                          |
| `issuedCredentials`   | uint64                        | `ecosystems[].credentialSchemas[].issuedCredentials`                                                                          | search ranking signal                                                          |
| `verifiedCredentials` | uint64                        | `ecosystems[].credentialSchemas[].verifiedCredentials`                                                                        | search ranking signal                                                          |
| `body`                | JSON Schema                   | result of [[TG-DEREF-2]] schema-load                                                                                | persisted atomically with the rest of the record; never `null` once the record exists, since [[TG-DEREF-2]] step 1 creates the record only after the load + digestSRI validation succeed |

#### `ServiceEndpoint`

A `ServiceEndpoint` record corresponds 1:1 to a non-`LinkedVerifiablePresentation` entry of the DID Document. Linked-VP entries are persisted as `LinkedVerifiablePresentation` records (next subsection) and are not duplicated here.

| Field             | Type                | Source                       | Notes                                                                |
| ---               | ---                 | ---                          | ---                                                                  |
| `id`              | string              | `services[].id`              | Identity (DID Document service entry id)                             |
| `didId`           | string              | the queried DID              | edge anchor to `Did`                                                 |
| `type`            | string              | `services[].type`            | e.g. `did-communication`, `MCP`, `A2A`, `LinkedDomains`              |
| `serviceEndpoint` | string \| object    | `services[].serviceEndpoint` | preserved verbatim                                                   |
| `accept`          | string[] \| `null`  | `services[].accept`          | when present                                                         |

#### `LinkedVerifiablePresentation`

The non-ECS VTCs carried by this VP are **not** stored on the LVP record as a flat list. Instead, each entry of `presentations[].vtcCredentials[]` is materialised as a separate `Vtc` record (see [`Vtc`](#vtc) below) and linked via the `CONTAINS_VTC: LVP → Vtc` edge. Mandatory ECS credentials are surfaced separately under `ecsCredentials[]` and are NOT referenced from the LVP.

| Field                       | Type     | Source                                       | Notes                                                                |
| ---                         | ---      | ---                                          | ---                                                                  |
| `id`                        | URL      | `presentations[].id`                         | Identity                                                             |
| `serviceId`                 | string   | `presentations[].serviceId`                  | DID Document service entry that exposes this VP                      |
| `didId`                     | string   | the queried DID                              | edge anchor to `Did`                                                 |
| `unresolvableCredentialIds` | string[] | `presentations[].unresolvableCredentialIds`  | observability only; not followed                                     |
| `invalidCredentialIds`      | string[] | `presentations[].invalidCredentialIds`       | observability only; not followed                                     |

#### `Vtc`

A `Vtc` record represents one non-ECS Verifiable Trust Credential surfaced under some `presentations[].vtcCredentials[]` entry. The graph materialises one `Vtc` record per such entry. The same credential `id` MAY be referenced by multiple VPs (the same VTC carried in more than one VP, by the same or different holders), in which case all referencing LVPs link to the same `Vtc` record via separate `CONTAINS_VTC` edges. ECS credentials are surfaced separately and materialised as `EcsCredential` records; the two entity types are disjoint.

| Field                 | Type   | Source                                                 | Notes                                                                                                                                                                                                          |
| ---                   | ---    | ---                                                    | ---                                                                                                                                                                                                            |
| `id`                  | string | `presentations[].vtcCredentials[].id`                  | **Identity.** The VTC's credential `id` (URN, did-URL fragment, or other credential identifier)                                                                                                                |
| `credentialSchemaId`            | uint64 | `presentations[].vtcCredentials[].credentialSchemaId`            | edge anchor to `CredentialSchema` by stable id                                                                                                                                                                 |
| `ecosystemId`         | uint64 | `presentations[].vtcCredentials[].ecosystemId`         | edge anchor to `Ecosystem` (issuing ecosystem) by stable id                                                                                                                                                    |
| `participantId`       | uint64 | `presentations[].vtcCredentials[].participantId`       | edge anchor to `Participation` — the HOLDER `Participant` entry tracking this VTC's lifecycle. Surfaced inline so the graph materialises the `HELD_AS` edge without a JOIN                                     |
| `issuerParticipantId` | uint64 | `presentations[].vtcCredentials[].issuerParticipantId` | edge anchor to `Participation` — the ISSUER `Participant` entry that issued this VTC. Anchors the `ISSUED_BY: Vtc → Participation` edge; the issuer's DID is recoverable as `Participation.didId` of the referenced entry |

#### `EcsCredential`

A single record per ECS credential surfaced under `ecsCredentials[]`. The record discriminator is `ecsSchema`, with one of the three ECS shapes the graph indexes — `ServiceCredential`, `OrganizationCredential`, `PersonaCredential` — all normatively defined by the [Verifiable Trust spec](https://github.com/verana-labs/verifiable-trust-spec). `UserAgentCredential` is **not** persisted: User Agents are clients of Verifiable Services and fall outside the graph's DID-indexing scope.

Common fields (all entries):

| Field              | Type                   | Source                                  | Notes                                                                                                          |
| ---                | ---                    | ---                                     | ---                                                                                                            |
| `id`               | string                 | `ecsCredentials[].id`                   | **Identity** (credential `id`)                                                                                 |
| `ecsSchema`        | enum                   | `ecsCredentials[].ecsSchema`            | `ServiceCredential` \| `OrganizationCredential` \| `PersonaCredential`. Retained for type-based query (alongside the stable `credentialSchemaId`). The graph does not persist `UserAgentCredential` entries (see the section preamble) |
| `ecsSchemaVersion` | string                 | `ecsCredentials[].ecsSchemaVersion`     | e.g. `v4`                                                                                                      |
| `credentialSchemaId`         | uint64                 | `ecsCredentials[].credentialSchemaId`             | edge anchor to `CredentialSchema` (the ECS schema) by stable id                                                |
| `issuerParticipantId` | uint64              | `ecsCredentials[].issuerParticipantId`  | edge anchor to `Participation` — the ISSUER `Participant` entry (`role = ISSUER`, `credentialSchemaId = this credential's credentialSchemaId`, `did = issuer DID`) that issued this credential. The issuer's DID is recoverable as `Participation.didId` of the referenced entry; the VC body's `issuer` claim is no longer surfaced inline by the indexer. Anchors the `ISSUED_BY: EcsCredential → Participation` edge |
| `ecosystemId`      | uint64                 | `ecsCredentials[].ecosystemId`          | edge anchor to `Ecosystem` (issuing ecosystem) by stable id. The VC body's original `ecosystem` DID claim is not surfaced inline by the indexer; consumers needing it can fetch the VC body via the parent VP |
| `participantId`    | uint64                 | `ecsCredentials[].participantId`        | edge anchor to `Participation` — the HOLDER `Participant` entry (`role = HOLDER`, `credentialSchemaId = this credential's credentialSchemaId`, `did = subjectDid`) that tracks this credential's lifecycle (issuance, validity, revocation). Surfaced as a stable id so the graph can materialise the `HELD_AS` edge without a 3-way JOIN |
| `subjectDid`       | string                 | `ecsCredentials[].credentialSubject.id` | edge anchor to `Did`                                                                                           |
| `validFrom`        | timestamp              | `ecsCredentials[].validFrom`            |                                                                                                                |
| `validUntil`       | timestamp \| `null`    | `ecsCredentials[].validUntil`           |                                                                                                                |

Per-shape additional fields, all sourced from `credentialSubject` and persisted verbatim. The lists below MUST cover the full set of `credentialSubject` properties normatively defined by the corresponding ECS schema in the [Verifiable Trust spec](https://github.com/verana-labs/verifiable-trust-spec); when the upstream schema adds a property in a backwards-compatible revision, the graph MUST persist it on the matching shape. The DID identifier `credentialSubject.id` is already projected as `EcsCredential.subjectDid` (see common fields above) and is not re-listed here.

`ServiceCredential` (subject = the VS DID) — `credentialSubject` fields per [ECS-SERVICE]:

- **mandatory**: `name`, `type`, `description`, `logo` (Data URI: `data:image/(png|jpeg|svg+xml);base64,…`), `minimumAgeRequired` (integer, 0–255), `termsAndConditions` (URI), `privacyPolicy` (URI)
- **optional**: `descriptionFormat` (`text/plain` default \| `text/markdown`), `termsAndConditionsDigestSri` (SRI digest), `privacyPolicyDigestSri` (SRI digest)

`OrganizationCredential` (subject = the legal-entity DID) — `credentialSubject` fields per [ECS-ORG]:

- **mandatory**: `name`, `logo` (Data URI), `registryId`, `address`, `countryCode` (ISO 3166-1 alpha-2, `^[A-Z]{2}$`)
- **optional**: `registryUri` (URI), `legalJurisdiction` (`^[A-Z]{2}(-[A-Z0-9]{1,3})?$`), `organizationKind`, `lei` (`^[A-Z0-9]{20}$`)

`PersonaCredential` (subject = the natural-person DID) — `credentialSubject` fields per [ECS-PERSONA]:

- **mandatory**: `name`, `controllerCountryCode` (ISO 3166-1 alpha-2, `^[A-Z]{2}$`)
- **optional**: `description`, `descriptionFormat` (`text/plain` default \| `text/markdown`), `avatar` (Data URI), `controllerJurisdiction` (`^[A-Z]{2}(-[A-Z0-9]{1,3})?$`)

#### `Participation`

For each `participations[]` entry surfaced in a resolve response, **two** fields are derived from the response **envelope** rather than from per-entry data: the `didId` (every entry's `Participant.did` equals the resolved DID, by the indexer's channel rule) and the `corporationId` (per VPR's per-Participant `(did, corporation)` consistency invariant, every Participation of a given DID shares the same controlling Corporation, surfaced as the envelope-level `corporationId` scalar). Neither is repeated per entry. The `vsOperator` account, by contrast, **is** surfaced per entry because each Participant's VS Operator Authorization grant is a distinct on-chain object — the controlling Corp's group MAY authorise different operator accounts for different Participants. This mirrors the envelope-derivation pattern used by [`Corporation`](#corporation) and [`Ecosystem`](#ecosystem). DID-less VPR Participant entries (`Participant.did = null` per VPR) are out of the graph's DID-centric view — they never appear in any DID's `participations[]` and therefore never become `Participation` records.

| Field                      | Type                          | Source                                                                                                  | Notes                                                                                                |
| ---                        | ---                           | ---                                                                                                     | ---                                                                                                  |
| `id`                       | uint64                        | `participations[].id`                                                                                   | **Identity.** VPR `Participant.id` — stable ledger primary key                                       |
| `corporationId`            | account                       | envelope: `response.corporationId`                                                                      | edge anchor to `Corporation` by stable controller address. Envelope-derived per VPR Invariant 2 — every Participation of a given DID shares the same controlling Corporation, so the indexer does not repeat it per entry. Equals `Did.corporationId` of the resolved DID |
| `didId`                    | string                        | envelope: `response.did`                                                                                | edge anchor to `Did`. Always present (DID-less VPR Participant entries are not surfaced; see intro above) |
| `vsOperator`               | account                       | `participations[].vsOperator`                                                                           | Cosmos account address authorised (via VS Operator Authorization granted by the controlling Corporation's group) to act as the VS operator for **this specific Participant entry**. Different Participations of the same DID under the same Corporation MAY carry different `vsOperator` accounts. Surfaced per entry because each Participant's VS Operator Authorization grant is a distinct on-chain object |
| `credentialSchemaId`                 | uint64                        | `participations[].credentialSchemaId`                                                                             | edge anchor to `CredentialSchema` by stable id (resolved against `CredentialSchema.id`)              |
| `ecosystemId`              | uint64                        | `participations[].ecosystemId`                                                                          | Stable id of the Ecosystem owning the referenced schema. **Denormalisation for direct access** — derivable from `credentialSchemaId` via the 1:1 Schema → Ecosystem ownership (see [[TG-EDGE-3]]). Stored as a field; no separate `IN_ECOSYSTEM` edge is materialised |
| `role`                     | enum                          | `participations[].role`                                                                                 | `HOLDER` \| `ISSUER` \| `VERIFIER` \| `ISSUER_GRANTOR` \| `VERIFIER_GRANTOR` \| `ECOSYSTEM`          |
| `state`                    | enum                          | `participations[].state`                                                                                | always `ACTIVE` in persisted records (per [[TG-ACT-1]]; non-ACTIVE participations are not visible in the graph) |
| `weight`                   | Coin                          | `participations[].weight`                                                                               | trust deposit bonded to this Participation                                                           |
| `issuedCredentials`        | uint64 \| `null`              | `participations[].issuedCredentials`                                                                    | only meaningful for `ISSUER` role                                                                    |
| `verifiedCredentials`      | uint64 \| `null`              | `participations[].verifiedCredentials`                                                                  | only meaningful for `VERIFIER` role                                                                  |
| `participantsByChildRole`  | map<role, uint> \| `null`     | `participations[].participants`                                                                         | only meaningful for grantor and `ECOSYSTEM` roles                                                    |

The primary key is `id` (VPR `Participant.id`). Per [[TG-ACT-1]], a Participation that leaves `ACTIVE` MUST be hard-deleted on the next reconciliation; if VPR later allocates a new Participant entry for the same `(corporation, did, schema, role)` tuple, it will carry a new `id` and is therefore treated as a brand-new record. The persisted `didId` is always the resolved DID under which this Participation was surfaced (envelope-derived); the same VPR Participant entry will never produce two records with different `didId`s because `Participant.did` is itself stable per the entry's lifetime.

### Edges

The following directed, typed edges are materialised between entity records. All edges carry the freshness fields listed in [Freshness fields](#freshness-fields); an edge is hard-deleted when the relationship it expresses no longer appears in a fresh resolve, per [[TG-ACT-1]].

| Edge label             | Source → Target                                          | Source data (anchor field)                                                                                  |
| ---                    | ---                                                      | ---                                                                                                         |
| `OPERATED_BY`          | `Did` → `Corporation`                                    | `Did.corporationId` matches `Corporation.id` (the unique Corp that owns this DID, surfaced directly by the indexer as the top-level `corporationId` scalar; by VPR Invariants 1+2 this is also the operating Corp authorising every Participation's `vsOperator` for this DID. Distinct from `Ecosystem.corporationId` — the Corp that *controls* an Ecosystem claiming this DID (per Invariant 3) MAY differ from the Corp that *owns* the DID per Invariant 1) |
| `CONTROLS`             | `Corporation` → `Ecosystem`                              | `Ecosystem.corporationId` matches `Corporation.id`                                                          |
| `EXPOSES_SERVICE`      | `Did` → `ServiceEndpoint`                                | `services[]` of `Did`'s resolve response                                                                    |
| `REFERENCES_VP`        | `Did` → `LinkedVerifiablePresentation`                   | `presentations[]`                                                                                           |
| `SUBJECT_OF_CREDENTIAL`| `Did` → `EcsCredential`                                  | `EcsCredential.subjectDid`                                                                                  |
| `ISSUED_BY`            | `EcsCredential` → `Participation`                        | `EcsCredential.issuerParticipantId` (ISSUER Participant entry; resolved against `Participation.id`). Replaces the previous `Did → EcsCredential` edge anchored on the DID-typed `issuer` field. Two-hop `EcsCredential —ISSUED_BY→ P ←PARTICIPATES_IN— Did` recovers the issuer DID                              |
| `ISSUED_BY`            | `Vtc` → `Participation`                                  | `Vtc.issuerParticipantId` (ISSUER Participant entry; resolved against `Participation.id`). Two-hop `Vtc —ISSUED_BY→ P ←PARTICIPATES_IN— Did` recovers the VTC's issuer DID                                                                            |
| `GOVERNED_BY`          | `EcsCredential` → `Ecosystem`                            | `EcsCredential.ecosystemId` (stable id; **not** the VC's mutable `ecosystem` DID claim)                     |
| `PARTICIPATES_IN`      | `Did` → `Participation`                                  | `Participation.didId` (envelope-derived; always present, since DID-less Participations are not surfaced)    |
| `OWNED_BY_CORPORATION` | `Participation` → `Corporation`                          | `Participation.corporationId`                                                                               |
| `FOR_SCHEMA`           | `Participation` → `CredentialSchema`                     | `Participation.credentialSchemaId` (resolved against `CredentialSchema.id`)                                           |
| `BASED_ON_SCHEMA`      | `EcsCredential` → `CredentialSchema`                     | `EcsCredential.credentialSchemaId` (resolved against `CredentialSchema.id`)                                           |
| `OWNS_SCHEMA`          | `Ecosystem` → `CredentialSchema`                         | `Ecosystem.credentialSchemaIds[]` (resolved against `CredentialSchema.id`)                                            |
| `CONTAINS_VTC`         | `LinkedVerifiablePresentation` → `Vtc`                   | one edge per entry in `LVP.vtcCredentials[]`, anchored on the entry's `id` (matches `Vtc.id`)               |
| `BASED_ON_SCHEMA`      | `Vtc` → `CredentialSchema`                               | `Vtc.credentialSchemaId` (resolved against `CredentialSchema.id`)                                                     |
| `GOVERNED_BY`          | `Vtc` → `Ecosystem`                                      | `Vtc.ecosystemId` (issuing ecosystem; stable id)                                                            |
| `HELD_AS`              | `EcsCredential` → `Participation`                        | `EcsCredential.participantId` (HOLDER Participant entry; resolved against `Participation.id`)               |
| `HELD_AS`              | `Vtc` → `Participation`                                  | `Vtc.participantId` (HOLDER Participant entry; resolved against `Participation.id`)                         |

[TG-EDGE-1] An edge MUST be created or updated atomically with the source entity when a resolve response is reconciled. The edge stores the target by one of the target entity's **stable keys** — DID string for `Did`, bech32 group address (`id`) for `Corporation`, VPR `id` (uint64) for `Ecosystem`, `Participation`, and `CredentialSchema` (every schema-targeting edge — `FOR_SCHEMA`, `BASED_ON_SCHEMA`, `OWNS_SCHEMA` — anchors on the schema's stable ledger `id`), VP URL for `LinkedVerifiablePresentation`, service entry id for `ServiceEndpoint`, credential id for `EcsCredential` and `Vtc`. Whether the target's entity record has been materialised yet is a query-time join concern, not a write-time precondition. Per [[TG-DEREF-1]] the missing target MUST NOT be enqueued for resolution — the global subscription of [[TG-INGEST-1]] guarantees that the target's own resolve will eventually arrive, at which point the join completes. No edge in the catalogue anchors on a mutable field: the `Corporation.did` and `Ecosystem.did` fields are not anchors of any edge, structurally preventing DID rotation from invalidating any edge in the graph.

[TG-EDGE-2] Counter fields surfaced as scalars on `Participation`, `Ecosystem`, and `CredentialSchema` (`issuedCredentials`, `verifiedCredentials`, `participants[role]`) represent the broader population of credentials and participants that the upstream resolver does not surface as individual records. The graph MUST NOT synthesise per-credential `EcsCredential` records from these counters; only ECS credentials explicitly surfaced under `ecsCredentials[]` are materialised as records and edges.

[TG-EDGE-3] **Schema → Ecosystem ownership is 1:1.** Per VPR, every `CredentialSchema` is owned by exactly one Ecosystem (see [`CredentialSchema.ecosystemId`](#credentialschema)); schemas are never shared between ecosystems. The `OWNS_SCHEMA: Ecosystem → CredentialSchema` edge is therefore 1-to-N from the Ecosystem side and **exactly 1-to-1 from the Schema side**. A `Participation`'s ecosystem context is therefore deterministically derivable from the schema it references: `Participation —FOR_SCHEMA→ S ←OWNS_SCHEMA— E`. The indexer surfaces this derivation result inline as `participations[].ecosystemId` (denormalised for direct access) and the graph persists it as `Participation.ecosystemId`; the field MUST match `CredentialSchema(Participation.credentialSchemaId).ecosystemId`, and any divergence indicates a bug in upstream state. No separate `IN_ECOSYSTEM` edge is materialised because the field-equality query is sufficient.

This invariant does NOT extend to `EcsCredential` or `Vtc`. For both, the `credentialSchemaId` points to a schema owned by some Ecosystem, while the `ecosystemId` is the *issuing* ecosystem under which the credential was granted — these are independent and may legitimately differ. (`EcsCredential` schemas are ECS schemas owned by the ECS trust registry while the issuing ecosystem is typically a domain ecosystem; for `Vtc` the two often coincide — most non-ECS VTCs are issued under their schema's owning Ecosystem — but the spec imposes no constraint.) The `BASED_ON_SCHEMA` and `GOVERNED_BY` edges from both entity types anchor on `credentialSchemaId` and `ecosystemId` respectively, with no constraint that the two target Ecosystems coincide.

### Indexing strategy

[TG-IDX-1] For graph-traversal queries, the implementation MUST maintain bidirectional adjacency on every edge label listed in [Edges](#edges), so that a query rooted at any entity can walk one hop in either direction in O(1) per edge.

[TG-IDX-2] For faceted-search queries, the implementation MUST maintain inverted indexes on the search-facing fields highlighted as such in the per-entity tables. At minimum, the index set MUST cover:

- `Did.serviceTypes`, `Did.trusted`
- `Corporation.deposit` (numeric range), `Corporation.slashedEvents` (numeric range)
- `Ecosystem.participants[<role>]` (numeric range), `Ecosystem.issuedCredentials` (numeric range), `Ecosystem.verifiedCredentials` (numeric range)
- `CredentialSchema.ecosystemId`, `CredentialSchema.issuedCredentials` (numeric range), `CredentialSchema.verifiedCredentials` (numeric range)
- `ServiceEndpoint.type`
- `EcsCredential.OrganizationCredential.{countryCode, legalJurisdiction, organizationKind, lei, registryId}`
- `EcsCredential.ServiceCredential.{type, name}`
- Free-text indexes on every textual `name`, `description`, `address` field across the catalogue, plus full-text indexes on `Corporation.cgf` and `Ecosystem.egf` document content.
