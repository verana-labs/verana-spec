# Indexer v4 Specification

**Latest Draft:** spec v4-draft1

## Abstract

## About this Document

In order to fully understand the concepts developed in this document, you should have some basic knowledge of DID, DIDComm, AnonCreds, the Verifiable Trust model, and the [ToIP stack](https://www.trustoverip.org/toip-model/). All terms used in this specification are defined in the [Terminology](#terminology) section.

## Conformance

As well as sections marked as non-normative, all authoring guidelines, diagrams, examples, and notes in this specification are non-normative. Everything else in this specification is normative.

The key words MAY, MUST, MUST NOT, OPTIONAL, RECOMMENDED, REQUIRED, SHOULD, and SHOULD NOT in this document are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) [RFC2119](https://w3c.github.io/vc-data-model/#bib-rfc2119) [RFC8174](https://w3c.github.io/vc-data-model/#bib-rfc8174) when, and only when, they appear in all capitals, as shown here.

### Datetime encoding

Every datetime value defined or surfaced by this specification — including but not limited to `atTime`, `evaluatedAtTime`, `expiresAtTime`, `validFrom`, `validUntil`, `lastSlashedAt`, `activeSince`, `blockTime`, the TRQP `time` / `time_requested` / `time_evaluated` / `since` / `controlling_since` fields, and any future datetime field added in a backwards-compatible revision — MUST be encoded as an ISO 8601 / RFC 3339 datetime string **in UTC**. Each value MUST include the date, the time (with seconds), and the trailing `Z` UTC designator. Fractional seconds are OPTIONAL. Local times, non-UTC offsets (e.g. `+02:00`), date-only values, and timezone-less times MUST NOT be used. Producers that hold non-UTC times MUST convert them to UTC before serialising. The normative regular expression is:

```regex
^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z$
```

The JSON Schemas published alongside this document expose this constraint as the reusable `#/$defs/Iso8601DateTime` definition; every datetime property in those schemas references it.

## Terminology

- **AnonCreds** — Anonymous Credentials, a privacy-preserving verifiable credential format supporting selective disclosure and unlinkability.
- **decentralized identifier (DID, DIDs)** — A decentralized identifier, as specified in [DID-CORE](https://www.w3.org/TR/did-core/).
- **DIDComm** — A peer-to-peer messaging protocol built on DIDs, as specified by the [DIDComm Messaging Specification](https://identity.foundation/didcomm-messaging/spec/).
- **Verifiable Public Registry (VPR, VPRs)** — A decentralized registry used to publish and resolve trust-related resources (Credential Schemas, Ecosystems, Governance Frameworks, etc.), as specified by the [Verifiable Trust VPR specification](https://github.com/verana-labs/verifiable-trust-vpr-spec).
- **Verifiable Service (Verifiable Services)** — A service that identifies its operator, purpose, and governance context through verifiable credentials, as defined in the [Verifiable Trust specification](https://github.com/verana-labs/verifiable-trust-spec).
- **Verifiable Trust** — The open, decentralized trust layer specified at [verana-labs/verifiable-trust-spec](https://github.com/verana-labs/verifiable-trust-spec).
- **VS Agent** — The runtime component specified by this document, which hosts a Verifiable Service and exposes a REST API and event model to backend implementations.
- **VTJSC, Verifiable Trust JSON Schema Credential** — A W3C `JsonSchemaCredential` issued by an Ecosystem DID that references a `CredentialSchema` entry in a Verifiable Public Registry, cryptographically binding that schema to the Ecosystem that controls the Trust Registry in which the schema is defined. Specified in [VT-JSON-SCHEMA-CRED-W3C](https://github.com/verana-labs/verifiable-trust-spec/blob/main/spec.md#vt-json-schema-cred-w3c-verifiable-trust-json-schema-credential) of the Verifiable Trust Specification.
- **W3C Verifiable Credentials Data Model (W3C VC Data Model)** — The W3C Recommendation defining a standard data model for verifiable credentials, as specified in [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model/).

## API

### Method List

| Module | Method Name | Relative REST API path | Type | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Corporation | `getCorporation` | `/co/v1/get/{corporation}` | Query | [`IDX-CO-QRY-1`](#idx-co-qry-1) | PUBLIC |
| Corporation | `listCorporations` | `/co/v1/list` | Query | [`IDX-CO-QRY-2`](#idx-co-qry-2) | PUBLIC |
| Corporation | `getCorporationParams` | `/co/v1/params` | Query | [`IDX-CO-QRY-3`](#idx-co-qry-3) | PUBLIC |
| Corporation | `getCorporationHistory` | `/co/v1/history/{corporation}` | Query | [`IDX-CO-QRY-4`](#idx-co-qry-4) | PUBLIC |
| Ecosystem | `getEcosystem` | `/es/v1/get/{id}` | Query | [`IDX-ES-QRY-1`](#idx-es-qry-1) | PUBLIC |
| Ecosystem | `listEcosystems` | `/es/v1/list` | Query | [`IDX-ES-QRY-2`](#idx-es-qry-2) | PUBLIC |
| Ecosystem | `getEcosystemParams` | `/es/v1/params` | Query | [`IDX-ES-QRY-3`](#idx-es-qry-3) | PUBLIC |
| Ecosystem | `getEcosystemHistory` | `/es/v1/history/{id}` | Query | [`IDX-ES-QRY-4`](#idx-es-qry-4) | PUBLIC |
| Governance Framework | `getGovernanceFrameworkVersion` | `/gf/v1/get/{id}` | Query | [`IDX-GF-QRY-1`](#idx-gf-qry-1) | PUBLIC |
| Governance Framework | `listGovernanceFrameworkVersions` | `/gf/v1/list` | Query | [`IDX-GF-QRY-2`](#idx-gf-qry-2) | PUBLIC |
| Credential Schema | `getCredentialSchema` | `/cs/v1/get/{id}` | Query | [`IDX-CS-QRY-1`](#idx-cs-qry-1) | PUBLIC |
| Credential Schema | `listCredentialSchemas` | `/cs/v1/list` | Query | [`IDX-CS-QRY-2`](#idx-cs-qry-2) | PUBLIC |
| Credential Schema | `getJsonSchema` | `/cs/v1/js/{id}` | Query | [`IDX-CS-QRY-3`](#idx-cs-qry-3) | PUBLIC |
| Credential Schema | `getCredentialSchemaParams` | `/cs/v1/params` | Query | [`IDX-CS-QRY-4`](#idx-cs-qry-4) | PUBLIC |
| Credential Schema | `getCredentialSchemaHistory` | `/cs/v1/history/{id}` | Query | [`IDX-CS-QRY-5`](#idx-cs-qry-5) | PUBLIC |
| Participant | `getParticipant` | `/pp/v1/get/{id}` | Query | [`IDX-PP-QRY-1`](#idx-pp-qry-1) | PUBLIC |
| Participant | `listParticipants` | `/pp/v1/list` | Query | [`IDX-PP-QRY-2`](#idx-pp-qry-2) | PUBLIC |
| Participant | `getParticipantHistory` | `/pp/v1/history/{id}` | Query | [`IDX-PP-QRY-3`](#idx-pp-qry-3) | PUBLIC |
| Participant | `findBeneficiaries` | `/pp/v1/beneficiaries` | Query | [`IDX-PP-QRY-4`](#idx-pp-qry-4) | PUBLIC |
| Participant | `pendingFlat` | `/pp/v1/pending/flat` | Query | [`IDX-PP-QRY-5`](#idx-pp-qry-5) | PUBLIC |
| Participant | `getParticipantSession` | `/pp/v1/participant-session/{id}` | Query | [`IDX-PP-QRY-6`](#idx-pp-qry-6) | PUBLIC |
| Participant | `listParticipantSessions` | `/pp/v1/participant-sessions` | Query | [`IDX-PP-QRY-7`](#idx-pp-qry-7) | PUBLIC |
| Participant | `getParticipantSessionHistory` | `/pp/v1/participant-session-history/{id}` | Query | [`IDX-PP-QRY-8`](#idx-pp-qry-8) | PUBLIC |
| Participant | `getParticipantParams` | `/pp/v1/params` | Query | [`IDX-PP-QRY-9`](#idx-pp-qry-9) | PUBLIC |
| Trust Deposit | `getTrustDepositByCorporation` | `/td/v1/get/{corporation}` | Query | [`IDX-TD-QRY-1`](#idx-td-qry-1) | PUBLIC |
| Trust Deposit | `getTrustDepositParams` | `/td/v1/params` | Query | [`IDX-TD-QRY-2`](#idx-td-qry-2) | PUBLIC |
| Trust Deposit | `getTrustDepositHistory` | `/td/v1/history/{corporation}` | Query | [`IDX-TD-QRY-3`](#idx-td-qry-3) | PUBLIC |
| Delegation | `listOperatorAuthorizations` | `/de/v1/operator-authorizations` | Query | [`IDX-DE-QRY-1`](#idx-de-qry-1) | PUBLIC |
| Delegation | `listVSOperatorAuthorizations` | `/de/v1/vs-operator-authorizations` | Query | [`IDX-DE-QRY-2`](#idx-de-qry-2) | PUBLIC |
| Digest | `getDigest` | `/di/v1/get/{digest}` | Query | [`IDX-DI-QRY-1`](#idx-di-qry-1) | PUBLIC |
| Exchange Rate | `getExchangeRate` | `/xr/v1/get` | Query | [`IDX-XR-QRY-1`](#idx-xr-qry-1) | PUBLIC |
| Exchange Rate | `listExchangeRates` | `/xr/v1/list` | Query | [`IDX-XR-QRY-2`](#idx-xr-qry-2) | PUBLIC |
| Exchange Rate | `getPrice` | `/xr/v1/price` | Query | [`IDX-XR-QRY-3`](#idx-xr-qry-3) | PUBLIC |
| Metrics | `getGlobalMetrics` | `/metrics/v1/all` | Query | [`IDX-METRICS-QRY-1`](#idx-metrics-qry-1) | PUBLIC |
| Statistics | `getStats` | `/stats/v1/get` | Query | [`IDX-STATS-QRY-1`](#idx-stats-qry-1) | PUBLIC |
| Statistics | `getStatsRange` | `/stats/v1/stats` | Query | [`IDX-STATS-QRY-2`](#idx-stats-qry-2) | PUBLIC |
| Statistics | `getParticipantsAtHeight` | `/stats/v1/participants-at-height` | Query | [`IDX-STATS-QRY-3`](#idx-stats-qry-3) | PUBLIC |
| Indexer | `getBlockHeight` | `/indexer/v1/block-height` | Query | [`IDX-INDEXER-QRY-1`](#idx-indexer-qry-1) | PUBLIC |
| Indexer | `getIndexerStatus` | `/indexer/v1/status` | Query | [`IDX-INDEXER-QRY-2`](#idx-indexer-qry-2) | PUBLIC |
| Indexer | `getVersion` | `/indexer/v1/version` | Query | [`IDX-INDEXER-QRY-3`](#idx-indexer-qry-3) | PUBLIC |
| Indexer | `getIndexerSnapshot` | `/indexer/v1/snapshot` | Query | [`IDX-INDEXER-QRY-4`](#idx-indexer-qry-4) | PUBLIC |
| Indexer | `listChanges` | `/indexer/v1/changes` | Query | [`IDX-INDEXER-QRY-5`](#idx-indexer-qry-5) | PUBLIC |
| Indexer | `listIndexerEvents` | `/indexer/v1/events` | Query | [`IDX-INDEXER-QRY-6`](#idx-indexer-qry-6) | PUBLIC |
| Indexer | `subscribeIndexerEvents` | `/indexer/v1/events` | Subscription (WebSocket) | [`IDX-INDEXER-SUB-1`](#idx-indexer-sub-1) | PUBLIC |
| Verifiable Trust Resolver | `resolve` | `/vt/v1/resolve` | Query | [`IDX-VT-QRY-1`](#idx-vt-qry-1), [[VS-REQ-2]], [[VS-REQ-3]], [[VS-REQ-4]] | PUBLIC |
| Verifiable Trust Resolver | `subscribeChanges` | `/vt/v1/subscribe` | Subscription (WebSocket) | [`IDX-VT-SUB-1`](#idx-vt-sub-1) | PUBLIC |
| Verifiable Trust Resolver | `listChanges` | `/vt/v1/changes` | Query | [`IDX-VT-QRY-2`](#idx-vt-qry-2) | PUBLIC |
| Verifiable Trust Resolver | `listIndexedDids` | `/vt/v1/dids` | Query | [`IDX-VT-QRY-3`](#idx-vt-qry-3) | PUBLIC |
| TRQP | `trqpAuthorize` | `/trqp/v2/authorization` | Query | [`IDX-TRQP-QRY-1`](#idx-trqp-qry-1) | PUBLIC |
| TRQP | `trqpRecognize` | `/trqp/v2/recognition` | Query | [`IDX-TRQP-QRY-2`](#idx-trqp-qry-2) | PUBLIC |

All methods are specified in [Method Specification](#method-specification) below, grouped by module.

### Method Specification

This section specifies the raw indexer methods that expose VPR ledger entities (Corporations, Ecosystems, Governance Framework versions, Credential Schemas, Participants, Trust Deposits, Operator Authorizations, Digests, Exchange Rates) and the aggregate / statistical / operational state derived from them. They are pure query views; none mutate state. Per-method request and response JSON Schemas are published alongside this document at [`schemas/v4/idx/`](./schemas/v4/idx/) *(schemas to be added in a follow-up commit)*.

#### Conventions

These conventions apply throughout this section unless overridden by a specific method.

##### `At-Block-Height` header

Every method accepts an optional `At-Block-Height` HTTP request header (integer block height). When provided, the method returns the indexer's view of the requested entity **as it was when the specified block finished processing**. When omitted, the latest indexed state is returned. The header MUST be a positive integer not exceeding the indexer's current `lastProcessedBlock`; otherwise the response is HTTP 400.

Responses for non-list methods echo the resolved block in a `block_height` response field so clients that omitted the header can still pin subsequent calls to the same point-in-time.

##### `trust_data` query parameter

A subset of methods (`getEcosystem`, `listEcosystems`, `getParticipant`, `listParticipants`, `pendingFlat`) accept an optional `trust_data` query parameter that enriches each DID-bearing object inline with the resolver's trust evaluation. Values:

- `null` (default) — no enrichment; the `trust_data` field is omitted from each object.
- `summary` — adds a [vt response object](schemas/v4/vt/response.schema.json) to the response with `trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`,  `corporationId`.
- `full` — adds a [vt response object](schemas/v4/vt/response.schema.json) to the response with the same data than `summary`, plus object `ecsCredentials`.

For higher-level trust evaluation use [`resolve`](#verifiable-trust-resolver-methods) instead.

> Note: if a ECS-Service credential is not self-issued by the DID that is presenting it, it is required to resolve its issuer DID to obtain the ECS-organization or ECS-Persona and properly identify service controller.

##### Pagination

List and history methods that return arrays accept `response_max_size` (integer; 1..1024 for list methods, 1..1000 for history methods, default 64) to cap the number of items returned. History methods additionally accept `transaction_timestamp_older_than` (ISO 8601 UTC datetime) as a cursor; passing the `timestamp` of the oldest item in the previous page yields the next older page.

##### `sort` query parameter

List methods accept a `sort` query parameter as a comma-separated list of attribute names. Prefix with `-` for descending, `+` (or no prefix) for ascending. Default is `-modified`. Allowed attributes (the intersection per method varies):

`id`, `modified`, `created`, `participants`, `participants_ecosystem`, `participants_issuer_grantor`, `participants_issuer`, `participants_verifier_grantor`, `participants_verifier`, `participants_holder`, `active_schemas` (Ecosystem only), `weight`, `issued`, `verified`, `ecosystem_slash_events`, `ecosystem_slashed_amount`, `network_slash_events`, `network_slashed_amount`.

##### Standard list filters

The list methods on Ecosystem, Credential Schema, and Participant accept a common set of bounded range filters (lower bound inclusive, upper bound exclusive). They are omitted from individual method tables below to keep them compact.

| Filter pair | Meaning |
| --- | --- |
| `min_participants` / `max_participants` | Total active participants |
| `min_participants_ecosystem` / `max_participants_ecosystem` | Active `ECOSYSTEM`-role participants |
| `min_participants_issuer_grantor` / `max_participants_issuer_grantor` | Active `ISSUER_GRANTOR`-role participants |
| `min_participants_issuer` / `max_participants_issuer` | Active `ISSUER`-role participants |
| `min_participants_verifier_grantor` / `max_participants_verifier_grantor` | Active `VERIFIER_GRANTOR`-role participants |
| `min_participants_verifier` / `max_participants_verifier` | Active `VERIFIER`-role participants |
| `min_participants_holder` / `max_participants_holder` | Active `HOLDER`-role participants |
| `min_weight` / `max_weight` | Sum of permission trust-deposit weights (int64) |
| `min_issued` / `max_issued` | Total issued credentials (int64) |
| `min_verified` / `max_verified` | Total verified credentials (int64) |
| `min_ecosystem_slash_events` / `max_ecosystem_slash_events` | Ecosystem-governance slash event count |
| `min_network_slash_events` / `max_network_slash_events` | Network-governance slash event count |

In addition, `listEcosystems` accepts `min_active_schemas` / `max_active_schemas`.

##### `participant_state` semantics

`Participant` entries carry several timestamp fields on-chain (`slashed`, `revoked`, `repaid`, `effective_from`, `effective_until`, `modified`) but **no** explicit lifecycle-state field. The indexer derives a single `participant_state` enum at evaluation time from those timestamps and exposes it as both a response field on `getParticipant` / `listParticipants` and a query filter on `listParticipants`. The derivation rules, evaluated in this priority order at the resolved point-in-time `now` (the current block, or the `At-Block-Height` block if set), are:

| Priority | State | Condition |
| --- | --- | --- |
| 1 | `REPAID` | `slashed` is non-null AND `repaid` is non-null AND `repaid >= slashed` |
| 2 | `SLASHED` | `slashed` is non-null AND (`repaid` is null OR `repaid < slashed`) |
| 3 | `REVOKED` | `revoked` is non-null AND `revoked <= now` |
| 4 | `EXPIRED` | `effective_until` is non-null AND `effective_until <= now` |
| 5 | `FUTURE` | `effective_from` is non-null AND `effective_from > now` |
| 6 | `ACTIVE` | `effective_from` is null OR `effective_from <= now`, AND (`effective_until` is null OR `effective_until > now`), AND no higher-priority state applies |
| 7 | `INACTIVE` | none of the above (e.g. onboarding-process in `PENDING` or `TERMINATED` with no `effective_from` yet set) |

`participant_state` is purely indexer-computed. It is not part of the VPR `Participant` data model and must not be confused with `op_state` (the on-chain `PENDING` / `VALIDATED` / `TERMINATED` enum that tracks the onboarding process, not the overall Participant lifecycle).

#### Corporation methods

##### `getCorporation`

**Spec tag:** `IDX-CO-QRY-1` <a id="idx-co-qry-1"></a>

`GET /co/v1/get/{corporation}`

Retrieve a specific Corporation by the bech32 group address that keys it. *Aligned with VPR [[MOD-CO-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-co-qry-1-get-corporation).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | path | string | yes | Bech32 group address that keys the `Corporation` entry |
| `active_gf_only` | query | boolean | no | If true, only the active CGF version is returned in `versions[]` |
| `preferred_language` | query | string | no | Preferred document language (ISO 639); affects ordering of returned CGF documents |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` — see [Conventions](#trust_data-query-parameter) |

**Response:** `{ corporation: Corporation }`. The `Corporation` object carries:

- **On-chain (VPR `Corporation`):** `corporation` (bech32 group address — primary key; Corporation has no separate `id`), `did`, `language`, `active_version`, `created`, `modified`, `archived` (nullable).
- **Indexer-enriched aggregates** (computed; not stored on-chain):
  - `controlled_ecosystems` — count of `Ecosystem` entries whose `corporation` field equals this Corporation.
  - `participants` — total count of `Participant` entries owned by this Corporation across all schemas, plus per-role breakdown (`participants_ecosystem`, `participants_issuer_grantor`, …, `participants_holder`).
  - Trust-deposit snapshot (mirrored from the linked `TrustDeposit` row keyed by `corporation`): `deposit`, `share`, `refunded`, `slashed_deposit`, `repaid_deposit`, `slash_count`, `last_slashed`, `last_repaid`.
- **Nested `versions[]: GovernanceFrameworkVersion[]`** — convenience-included from the [Governance Framework module](#governance-framework-methods); these are the CGF (Corporation Governance Framework) versions, distinguishable by their non-null `corporation` field. Filtered by `active_gf_only` and `preferred_language`. Each entry carries its `documents[]: GovernanceFrameworkDocument[]`.
- **Optional `trust_data`** — when set to `summary` or `full`, a [vt response object](schemas/v4/vt/response.schema.json) for the Corporation's DID is added inline; see [Conventions](#trust_data-query-parameter) for the included fields.

##### `listCorporations`

**Spec tag:** `IDX-CO-QRY-2` <a id="idx-co-qry-2"></a>

`GET /co/v1/list`

Retrieve a paginated, filtered list of Corporations. *Aligned with VPR [[MOD-CO-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-co-qry-2-list-corporations).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `active_gf_only` | query | boolean | no | If true, only the active CGF version is returned in each Corporation's `versions[]` |
| `preferred_language` | query | string | no | Preferred document language; affects CGF document ordering |
| `only_active` | query | boolean | no | `true` → only active Corporations (`archived` is null); `false` → only archived Corporations; omitted → both |
| `did` | query | string | no | Filter by Corporation DID |
| `modified_after` | query | datetime | no | Only return Corporations modified strictly after this ISO 8601 datetime |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` — see [Conventions](#trust_data-query-parameter) |
| `response_max_size` | query | integer | no | 1..1024, default 64 — see [Pagination](#pagination) |
| `sort` | query | string | no | Sort criteria — see [`sort` query parameter](#sort-query-parameter); default `-modified` |

**Response:** `{ corporations: Corporation[] }`. Each entry has the same shape as [`getCorporation`](#getcorporation).

##### `getCorporationParams`

**Spec tag:** `IDX-CO-QRY-3` <a id="idx-co-qry-3"></a>

`GET /co/v1/params`

Retrieve the network-level Corporation module parameters. *Aligned with VPR [[MOD-CO-QRY-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-co-qry-3-list-module-parameters).*

(No method-specific parameters.)

**Response:** `{ params: { ... } }` — the Corporation module parameter set as defined by VPR governance (e.g. minimum trust-deposit for Corporation creation, CGF document-size limits). Exact keys are determined by the on-chain parameter set.

##### `getCorporationHistory`

**Spec tag:** `IDX-CO-QRY-4` <a id="idx-co-qry-4"></a>

`GET /co/v1/history/{corporation}`

Retrieve the activity timeline for a Corporation, ordered by transaction timestamp descending. Each entry returns only the diff (changed fields), not the full state. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | path | string | yes | Bech32 group address |
| `response_max_size` | query | integer | no | 1..1000, default 64 |
| `transaction_timestamp_older_than` | query | datetime | no | Cursor for pagination — see [Pagination](#pagination) |

**Response:** `ActivityTimelineResponse` with `entity_type: "Corporation"`. Each `ActivityItem`'s `msg` is one of `CreateCorporation`, `UpdateCorporation`, `ArchiveCorporation`, `AddCGFDocument`, `IncreaseCGFActiveVersion`, etc.

#### Ecosystem methods

##### `getEcosystem`

**Spec tag:** `IDX-ES-QRY-1` <a id="idx-es-qry-1"></a>

`GET /es/v1/get/{id}`

Retrieve a specific Ecosystem by its ID. *Aligned with VPR [[MOD-ES-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-es-qry-1-get-ecosystem).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Ecosystem ID |
| `active_gf_only` | query | boolean | no | If true, only the active governance-framework version is returned in `versions[]` |
| `preferred_language` | query | string | no | Preferred document language (ISO 639); affects ordering of returned governance-framework documents |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` — see [Conventions](#trust_data-query-parameter) |

**Response:** `{ ecosystem: Ecosystem }`. The `Ecosystem` object carries:

- **On-chain (VPR `Ecosystem`):** `id`, `did`, `corporation` (bech32 group address), `language`, `active_version`, `created`, `modified`, `archived` (nullable).
- **Indexer-enriched aggregates** (computed by the indexer over related `Participant`, `CredentialSchema`, and slash-event tables; not stored on-chain):
  - Participant-role counts: `participants`, `participants_ecosystem`, `participants_issuer_grantor`, `participants_issuer`, `participants_verifier_grantor`, `participants_verifier`, `participants_holder`.
  - Schema counts: `active_schemas`, `archived_schemas`.
  - Activity totals: `weight` (int64; sum of permission trust-deposit weights), `issued`, `verified`.
  - Slash ledger: `ecosystem_slash_events`, `ecosystem_slashed_amount`, `ecosystem_slashed_amount_repaid`, `network_slash_events`, `network_slashed_amount`, `network_slashed_amount_repaid`.
- **Nested `versions[]: GovernanceFrameworkVersion[]`** — convenience-included from the [Governance Framework module](#governance-framework-methods) so EGF data can be fetched in a single round-trip. Filtered by `active_gf_only` and `preferred_language`. Each entry carries its `documents[]: GovernanceFrameworkDocument[]` with `language`, `url`, `digest_sri`. For the authoritative GF queries, use [`getGovernanceFrameworkVersion`](#getgovernanceframeworkversion) / [`listGovernanceFrameworkVersions`](#listgovernanceframeworkversions).
- **Optional `trust_data`** — when set to `summary` or `full`, a [vt response object](schemas/v4/vt/response.schema.json) for the Ecosystem's DID is added inline; see [Conventions](#trust_data-query-parameter) for the included fields.

##### `listEcosystems`

**Spec tag:** `IDX-ES-QRY-2` <a id="idx-es-qry-2"></a>

`GET /es/v1/list`

Retrieve a paginated, filtered list of Ecosystems. *Aligned with VPR [[MOD-ES-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-es-qry-2-list-ecosystems).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `active_gf_only` | query | boolean | no | If true, only the active governance-framework version is returned in each Ecosystem's `versions[]` |
| `preferred_language` | query | string | no | Preferred document language; affects governance-framework document ordering |
| `only_active` | query | boolean | no | `true` → only active Ecosystems (`archived` is null); `false` → only archived Ecosystems; omitted → both |
| `corporation` | query | string | no | Filter by controlling-Corporation bech32 group address |
| `participant` | query | string | no | Account address; returns Ecosystems where this account is the Ecosystem corporation or holds an active `Participant` entry on a schema in the Ecosystem |
| `modified_after` | query | datetime | no | Only return Ecosystems modified strictly after this ISO 8601 datetime |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` — see [Conventions](#trust_data-query-parameter) |
| `response_max_size` | query | integer | no | 1..1024, default 64 — see [Pagination](#pagination) |
| `sort` | query | string | no | Sort criteria — see [`sort` query parameter](#sort-query-parameter); default `-modified` |
| `min_active_schemas` / `max_active_schemas` | query | integer | no | Active-schema count bounds |
| *(standard list filters)* | query | — | no | See [Standard list filters](#standard-list-filters) |

**Response:** `{ ecosystems: Ecosystem[] }`. Each entry has the same shape as [`getEcosystem`](#getecosystem).

##### `getEcosystemParams`

**Spec tag:** `IDX-ES-QRY-3` <a id="idx-es-qry-3"></a>

`GET /es/v1/params`

Retrieve the network-level Ecosystem module parameters. *Aligned with VPR [[MOD-ES-QRY-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-es-qry-3-list-module-parameters).*

(No method-specific parameters.)

**Response:** `{ params: { trust_unit_price: decimal, ecosystem_trust_deposit: decimal } }` — the price-per-trust-unit and the trust-deposit required to create an Ecosystem, as defined by the Ecosystem module parameters.

##### `getEcosystemHistory`

**Spec tag:** `IDX-ES-QRY-4` <a id="idx-es-qry-4"></a>

`GET /es/v1/history/{id}`

Retrieve the activity timeline for an Ecosystem, ordered by transaction timestamp descending. Each entry returns only the diff (changed fields), not the full state. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Ecosystem ID |
| `response_max_size` | query | integer | no | 1..1000, default 64 |
| `transaction_timestamp_older_than` | query | datetime | no | Cursor for pagination — see [Pagination](#pagination) |

**Response:** `ActivityTimelineResponse` — `{ entity_type: "Ecosystem", entity_id, activity: ActivityItem[] }`. Each `ActivityItem` has `timestamp`, `block_height`, `entity_type`, `entity_id`, `msg` (e.g. `CreateEcosystem`, `AddGovernanceFrameworkDocument`), `account` (signer), and `changes` (object of changed fields). The same `ActivityTimelineResponse` shape is reused by every `*History` and the indexer-level `listChanges` method.

#### Governance Framework methods

The Governance Framework module surfaces `GovernanceFrameworkVersion` (GFV) and its nested `GovernanceFrameworkDocument` (GFD) entries as first-class queryable entities. A GFV belongs to exactly one owning subject — either an Ecosystem (`ecosystem_id`, an EGF) or a Corporation (`corporation`, a CGF) — never both.

##### `getGovernanceFrameworkVersion`

**Spec tag:** `IDX-GF-QRY-1` <a id="idx-gf-qry-1"></a>

`GET /gf/v1/get/{id}`

Retrieve a specific `GovernanceFrameworkVersion` by its ID, with its nested `GovernanceFrameworkDocument` entries. *Aligned with VPR [[MOD-GF-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-gf-qry-1-get-governance-framework-version).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The GovernanceFrameworkVersion ID |
| `preferred_language` | query | string | no | If set, return only one document per version, preferring `preferred_language`; otherwise return all documents in all languages |

**Response:** `{ version: GovernanceFrameworkVersion }` — `id`, `ecosystem_id` (set iff this is an EGF; null otherwise), `corporation` (set iff this is a CGF; null otherwise), `created`, `version` (int), `active_since` (timestamp), and `documents[]: GovernanceFrameworkDocument[]` (each carrying `id`, `gfv_id`, `created`, `language`, `url`, `digest_sri`). Exactly one of `ecosystem_id` and `corporation` MUST be set, per VPR data model invariant.

##### `listGovernanceFrameworkVersions`

**Spec tag:** `IDX-GF-QRY-2` <a id="idx-gf-qry-2"></a>

`GET /gf/v1/list`

Retrieve the list of `GovernanceFrameworkVersion` entries for one owning subject — either an Ecosystem or a Corporation — ordered by ascending `version`. *Aligned with VPR [[MOD-GF-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-gf-qry-2-list-governance-framework-versions).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `ecosystem_id` | query | integer (int64) | conditional | Filter by owning Ecosystem. MUST be set iff `corporation` is null |
| `corporation` | query | string | conditional | Filter by owning Corporation (bech32 group address). MUST be set iff `ecosystem_id` is null |
| `active_only` | query | boolean | no | If true, return only the entry corresponding to the subject's `active_version` |
| `preferred_language` | query | string | no | If set, return only one document per version, preferring `preferred_language` |
| `response_max_size` | query | integer | no | 1..1024, default 64 |
| `sort` | query | string | no | Sort criteria; default `+version` (ascending by `version`) |

**Response:** `{ versions: GovernanceFrameworkVersion[] }`. Each entry has the same shape as [`getGovernanceFrameworkVersion`](#getgovernanceframeworkversion). Entries are ordered by ascending `version`. Exactly one of `ecosystem_id` and `corporation` MUST be provided in the query; otherwise HTTP 400.

#### Credential Schema methods

##### `getCredentialSchema`

**Spec tag:** `IDX-CS-QRY-1` <a id="idx-cs-qry-1"></a>

`GET /cs/v1/get/{id}`

Retrieve a specific Credential Schema by its ID. *Aligned with VPR [[MOD-CS-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-qry-2-get-credential-schema).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Credential Schema ID |

**Response:** `{ schema: CredentialSchema }`. The `CredentialSchema` object carries:

- **On-chain (VPR `CredentialSchema`):** `id`, `ecosystem_id` (owning Ecosystem), `json_schema` (the exact JSON Schema document as stored on-chain, preserved byte-for-byte for SRI digest verification of credentials issued under this schema), validity periods (`issuer_grantor_validation_validity_period`, `verifier_grantor_validation_validity_period`, `issuer_validation_validity_period`, `verifier_validation_validity_period`, `holder_validation_validity_period`), onboarding modes (`issuer_onboarding_mode`, `verifier_onboarding_mode`, `holder_onboarding_mode`), pricing (`pricing_asset_type`, `pricing_asset`), `digest_algorithm`, `created`, `modified`, `archived` (nullable).
- **Indexer-enriched aggregates** (computed; not stored on-chain):
  - Participant-role counts: `participants`, `participants_issuer_grantor`, `participants_issuer`, `participants_verifier_grantor`, `participants_verifier`, `participants_holder`.
  - Activity totals: `weight`, `issued`, `verified`.
  - Slash counters: `ecosystem_slash_events`, `ecosystem_slashed_amount`, `ecosystem_slashed_amount_repaid`, `network_slash_events`, `network_slashed_amount`, `network_slashed_amount_repaid`.

##### `listCredentialSchemas`

**Spec tag:** `IDX-CS-QRY-2` <a id="idx-cs-qry-2"></a>

`GET /cs/v1/list`

Retrieve a paginated, filtered list of Credential Schemas. *Aligned with VPR [[MOD-CS-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-qry-1-list-credential-schemas).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `ecosystem_id` | query | integer (int64) | no | Filter by owning Ecosystem ID |
| `only_active` | query | boolean | no | If true, only active schemas (`archived` is null) |
| `issuer_onboarding_mode` | query | string | no | Filter by issuer onboarding mode (`OPEN`, `ECOSYSTEM_ONBOARDING_PROCESS`, `GRANTOR_ONBOARDING_PROCESS`) |
| `verifier_onboarding_mode` | query | string | no | Filter by verifier onboarding mode (`OPEN`, `ECOSYSTEM_ONBOARDING_PROCESS`, `GRANTOR_ONBOARDING_PROCESS`) |
| `participant` | query | string | no | Account address; returns schemas where the account is the Ecosystem corporation or holds an active `Participant` entry |
| `modified_after` | query | datetime | no | Only return schemas modified strictly after this datetime |
| `response_max_size` | query | integer | no | 1..1024, default 64 |
| `sort` | query | string | no | Sort criteria; default `-modified` |
| *(standard list filters)* | query | — | no | See [Standard list filters](#standard-list-filters) |

**Response:** `{ schemas: CredentialSchema[] }`. Each entry has the same shape as [`getCredentialSchema`](#getcredentialschema).

##### `getJsonSchema`

**Spec tag:** `IDX-CS-QRY-3` <a id="idx-cs-qry-3"></a>

`GET /cs/v1/js/{id}`

Retrieve the canonical JSON Schema document for a specific Credential Schema, with `$id` rewritten to the indexer's canonical VPR URI form (e.g. `vpr:verana:vna-testnet-1/cs/v1/js/16`). *Aligned with VPR [[MOD-CS-QRY-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-qry-3-render-json-schema).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Credential Schema ID |

**Response:** The raw JSON Schema object as stored on-chain, with only the `$id` field overridden by the indexer. The body is `Content-Type: application/json`; clients SHOULD use this endpoint as the canonical schema-resolution target when dereferencing `vpr:verana:.../cs/v1/js/<n>` URIs.

##### `getCredentialSchemaParams`

**Spec tag:** `IDX-CS-QRY-4` <a id="idx-cs-qry-4"></a>

`GET /cs/v1/params`

Retrieve the network-level Credential Schema module parameters. *Aligned with VPR [[MOD-CS-QRY-4]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-qry-4-list-module-parameters).*

(No method-specific parameters.)

**Response:** `{ params: { credential_schema_trust_deposit: decimal } }` — the trust-deposit required to register a Credential Schema, as defined by the Credential Schema module parameters.

##### `getCredentialSchemaHistory`

**Spec tag:** `IDX-CS-QRY-5` <a id="idx-cs-qry-5"></a>

`GET /cs/v1/history/{id}`

Retrieve the activity timeline for a Credential Schema, ordered by transaction timestamp descending. Same shape as [`getEcosystemHistory`](#getecosystemhistory) with `entity_type: "CredentialSchema"`. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Credential Schema ID |
| `response_max_size` | query | integer | no | 1..1000, default 64 |
| `transaction_timestamp_older_than` | query | datetime | no | Cursor for pagination |

**Response:** `ActivityTimelineResponse` with `entity_type: "CredentialSchema"`.

#### Participant methods

##### `getParticipant`

**Spec tag:** `IDX-PP-QRY-1` <a id="idx-pp-qry-1"></a>

`GET /pp/v1/get/{id}`

Retrieve a specific Participant by its ID. A Participant is a single VPR participant entry — a binding of a Corporation/DID into a Credential Schema with a specific role and lifecycle. *Aligned with VPR [[MOD-PP-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-qry-2-get-participant).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Participant ID |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` |

**Response:** `{ participant: Participant }`. The `Participant` object carries:

- **On-chain (VPR `Participant`):** `id`, `schema_id`, `role` (one of `ISSUER`, `VERIFIER`, `ISSUER_GRANTOR`, `VERIFIER_GRANTOR`, `ECOSYSTEM`, `HOLDER`), `did` (optional), `corporation` (bech32 group address), `vs_operator` (account), lifecycle timestamps (`created`, `modified`, `adjusted`, `slashed`, `repaid`, `revoked`, `effective_from`, `effective_until`), fee fields (`validation_fees`, `issuance_fees`, `verification_fees`, `issuance_fee_discount`, `verification_fee_discount`), deposit fields (`deposit`, `slashed_deposit`, `repaid_deposit`), and the onboarding-process state (`op_state` enum: `PENDING` / `VALIDATED` / `TERMINATED`; plus `op_last_state_change`, `op_current_fees`, `op_current_deposit`, `op_summary_digest`, `op_exp`, `op_validator_deposit`, `validator_participant_id`).
- **Indexer-derived (computed at evaluation block; not stored on-chain):**
  - `participant_state` — lifecycle state derived from on-chain timestamps. One of `ACTIVE`, `FUTURE`, `INACTIVE`, `EXPIRED`, `REVOKED`, `SLASHED`, `REPAID`. See [Conventions → `participant_state` semantics](#participant_state-semantics).
  - `corporation_available_actions[]`, `validator_available_actions[]` — UI-affordance hints listing the next allowable VPR messages for the corporation owner / validator at the current state (e.g. `CancelParticipantOP`, `SetParticipantOPValidated`, `RenewParticipant`).
- **Indexer-enriched aggregates** (computed): `weight`, `issued`, `verified`, `participants` (sub-participant count for grantor roles), and the same slash counters as on `CredentialSchema`.
- **VS-operator authorization grants** for this `Participant.id` are **not** surfaced inline. Query them via [`listVSOperatorAuthorizations`](#listvsoperatorauthorizations) filtered by `participant_id` — they live in `ParticipantAuthorizationRecord` entries (formerly the `Participant.vs_operator_authz_*` fields).
- **Optional `trust_data`** — when set to `summary` or `full`, a [vt response object](schemas/v4/vt/response.schema.json) for the Participant's DID is added inline; see [Conventions](#trust_data-query-parameter) for the included fields.

##### `listParticipants`

**Spec tag:** `IDX-PP-QRY-2` <a id="idx-pp-qry-2"></a>

`GET /pp/v1/list`

Retrieve a paginated, filtered list of Participants. *Aligned with VPR [[MOD-PP-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-qry-1-list-participants).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | query | string | no | Filter by participant-owner Corporation account |
| `did` | query | string | no | Filter by DID |
| `participant_id` | query | integer | no | Filter by exact Participant ID |
| `role` | query | enum | no | `ISSUER` \| `VERIFIER` \| `ISSUER_GRANTOR` \| `VERIFIER_GRANTOR` \| `ECOSYSTEM` \| `HOLDER` |
| `participant_state` | query | enum | no | Indexer-derived lifecycle state: `REPAID` \| `SLASHED` \| `REVOKED` \| `EXPIRED` \| `ACTIVE` \| `FUTURE` \| `INACTIVE` |
| `op_state` | query | enum | no | `PENDING` \| `VALIDATED` \| `TERMINATED` |
| `only_valid` | query | boolean | no | Filter only valid (non-slashed, non-revoked, non-expired) Participants |
| `only_slashed` | query | boolean | no | Filter only slashed Participants |
| `only_repaid` | query | boolean | no | Filter only repaid Participants |
| `country` | query | string | no | Filter by country code |
| `schema_id` | query | integer | no | Filter by Credential Schema ID |
| `validator_participant_id` | query | integer | no | Filter by validator Participant ID |
| `when` | query | datetime | no | Effective-date filter; returns Participants whose effective range includes this datetime |
| `modified_after` | query | datetime | no | Only return Participants modified strictly after this datetime |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` |
| `response_max_size` | query | integer | no | 1..1024, default 64 |
| `sort` | query | string | no | Sort criteria; default `-modified` |
| *(standard list filters)* | query | — | no | See [Standard list filters](#standard-list-filters) |

**Response:** `{ participants: Participant[] }`. Each entry has the same shape as [`getParticipant`](#getparticipant).

##### `getParticipantHistory`

**Spec tag:** `IDX-PP-QRY-3` <a id="idx-pp-qry-3"></a>

`GET /pp/v1/history/{id}`

Retrieve the activity timeline for a Participant, ordered by transaction timestamp descending. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | integer (int64) | yes | The Participant ID |
| `response_max_size` | query | integer | no | 1..1000, default 64 |
| `transaction_timestamp_older_than` | query | datetime | no | Cursor for pagination |

**Response:** `ActivityTimelineResponse` with `entity_type: "Participant"`.

##### `findBeneficiaries`

**Spec tag:** `IDX-PP-QRY-4` <a id="idx-pp-qry-4"></a>

`GET /pp/v1/beneficiaries`

Compute the chain of beneficiary Participants for a credential transaction. Given an issuer Participant and a verifier Participant, returns every ancestor Participant in either tree (issuer grantor, verifier grantor, ecosystem, network) that participates in the fee-distribution flow. *Aligned with VPR [[MOD-PP-QRY-4]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-qry-4-find-beneficiaries).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `issuer_participant_id` | query | string | yes | Issuer Participant ID |
| `verifier_participant_id` | query | string | yes | Verifier Participant ID |

**Response:** `{ participants: Participant[] }` — the ordered set of beneficiary Participants.

##### `pendingFlat`

**Spec tag:** `IDX-PP-QRY-5` <a id="idx-pp-qry-5"></a>

`GET /pp/v1/pending/flat`

Return the open task list for a given account — every Participant anywhere on the network where the account is the validator and the Participant is in a state that requires the validator's action (e.g. `op_state: PENDING`). Results are grouped by Ecosystem then by Credential Schema. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `account` | query | string | yes | Account address whose pending tasks are returned |
| `trust_data` | query | enum | no | `null` \| `summary` \| `full` |
| `response_max_size` | query | integer | no | 1..1024, default 64 (caps the number of Ecosystems returned) |
| `sort` | query | string | no | Sort criteria; default `-modified` |

**Response:** `{ ecosystems: EcosystemPending[] }`. Each `EcosystemPending` carries:

- `id`, `did`, `pending_tasks` (count of pending validations), `participants` (active participant count).
- `trust_data` (when requested; per [Conventions](#trust_data-query-parameter)).
- `schemas[]: CredentialSchemaPending[]` — each `CredentialSchemaPending` carries `id`, `title` (indexer-derived from the JSON Schema `title`), `description` (indexer-derived from the JSON Schema `description`), `pending_tasks`, `participants` (active participant count), and `pending_participants[]: Participant[]` (full `Participant` shape; see [`getParticipant`](#getparticipant)). The `pending_participants[]` array is the list of `Participant` entries pending action from the validator account; it is intentionally distinct from the scalar `participants` count.

##### `getParticipantSession`

**Spec tag:** `IDX-PP-QRY-6` <a id="idx-pp-qry-6"></a>

`GET /pp/v1/participant-session/{id}`

Retrieve a specific ParticipantSession by its UUID. A ParticipantSession binds an end-user agent into one (or more) Issuer/Verifier participant contexts for the lifetime of a credential-exchange flow. *Aligned with VPR [[MOD-PP-QRY-5]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-qry-5-get-participantsession).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | uuid | yes | ParticipantSession UUID |

**Response:** `{ session: ParticipantSession }`. The `ParticipantSession` object carries:

- **On-chain (VPR `ParticipantSession`):** `id` (UUID), `corporation` (the agent's controlling Corporation), `vs_operator` (the VS-operator account that controls the session), `created`, `modified`.
- **Nested `session_records[]: ParticipantSessionRecord[]`** — each `ParticipantSessionRecord` carries `created`, `issuer_participant_id` (optional), `verifier_participant_id` (optional), `wallet_agent_participant_id` (optional), `agent_participant_id` (optional).

##### `listParticipantSessions`

**Spec tag:** `IDX-PP-QRY-7` <a id="idx-pp-qry-7"></a>

`GET /pp/v1/participant-sessions`

Retrieve a paginated list of ParticipantSessions. *Indexer-specific (no VPR equivalent; VPR exposes only [[MOD-PP-QRY-5]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-qry-5-get-participantsession) Get ParticipantSession).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `modified_after` | query | datetime | no | Only return sessions modified strictly after this datetime |
| `response_max_size` | query | integer | no | 1..1024, default 64 |

**Response:** `{ sessions: ParticipantSession[] }`. Each entry has the same shape as [`getParticipantSession`](#getparticipantsession).

##### `getParticipantSessionHistory`

**Spec tag:** `IDX-PP-QRY-8` <a id="idx-pp-qry-8"></a>

`GET /pp/v1/participant-session-history/{id}`

Retrieve the activity timeline for a ParticipantSession, ordered by transaction timestamp descending. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | path | uuid | yes | ParticipantSession UUID |

**Response:** `ActivityTimelineResponse` with `entity_type: "ParticipantSession"`.

##### `getParticipantParams`

**Spec tag:** `IDX-PP-QRY-9` <a id="idx-pp-qry-9"></a>

`GET /pp/v1/params`

Retrieve the network-level Participant module parameters. *Aligned with VPR [[MOD-PP-QRY-6]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-qry-6-list-participant-module-parameters).*

(No method-specific parameters.)

**Response:** `{ params: { ... } }` — the Participant module parameter set as defined by VPR governance (e.g. trust-deposit requirements per role, validation-fee floors). Exact keys are determined by the on-chain parameter set.

#### Trust Deposit methods

##### `getTrustDepositByCorporation`

**Spec tag:** `IDX-TD-QRY-1` <a id="idx-td-qry-1"></a>

`GET /td/v1/get/{corporation}`

Retrieve the aggregated trust-deposit position of a single Corporation account across every entity it owns (Ecosystems, Credential Schemas, Participants). Per VPR, every Corporation has at most one TrustDeposit row. *Aligned with VPR [[MOD-TD-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-td-qry-1-get-trust-deposit).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | path | string | yes | Corporation bech32 account address |

**Response:** `{ trust_deposit: TrustDeposit }`. The `TrustDeposit` object carries:

- **On-chain (VPR `TrustDeposit`):** `corporation` (bech32 group address; primary key), `deposit` (current locked amount in native denom, integer), `share` (this account's share of the module-pooled deposit), `refunded` (reused-first refunded amount, drawn before pulling from the corporation account), `slashed_deposit`, `repaid_deposit`, `last_slashed` (timestamp, nullable), `last_repaid` (timestamp, nullable), `slash_count`.
- **Indexer-derived (computed; not stored on-chain):** `claimable` — accrued yield currently claimable on reclaim, computed as `share * trust_deposit_share_value - deposit` per the network's Trust Deposit module parameters.

##### `getTrustDepositParams`

**Spec tag:** `IDX-TD-QRY-2` <a id="idx-td-qry-2"></a>

`GET /td/v1/params`

Retrieve the network-level Trust Deposit module parameters. *Aligned with VPR [[MOD-TD-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-td-qry-2-list-module-parameters).*

(No method-specific parameters.)

**Response:** `{ params: { trust_deposit_rate, user_agent_reward_rate, trust_deposit_share_value, wallet_user_agent_reward_rate, trust_deposit_reclaim_burn_rate } }` — all decimals; the network governance rates that drive yield, reward distribution, share-value translation, and the burn fraction applied on reclaim.

##### `getTrustDepositHistory`

**Spec tag:** `IDX-TD-QRY-3` <a id="idx-td-qry-3"></a>

`GET /td/v1/history/{corporation}`

Retrieve the activity timeline for a Trust Deposit account, ordered by transaction timestamp descending. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | path | string | yes | Corporation bech32 account address |
| `response_max_size` | query | integer | no | 1..1000, default 64 |
| `transaction_timestamp_older_than` | query | datetime | no | Cursor for pagination |

**Response:** `ActivityTimelineResponse` with `entity_type: "TrustDeposit"`. Each `ActivityItem`'s `msg` is one of `CREATE_TRUST_DEPOSIT`, `ADJUST_TRUST_DEPOSIT`, `SLASH_TRUST_DEPOSIT`, `SLASH_PARTICIPANT_TRUST_DEPOSIT`, `RECLAIM_YIELD`, `RECLAIM_DEPOSIT`, `REPAY_SLASHED`.

#### Delegation methods

The Delegation module surfaces the two on-chain authorization entities that replaced the old `Participant.vs_operator_authz_*` fields: `OperatorAuthorization` (corporation-to-operator grants over module message types) and `VSOperatorAuthorization` (corporation-to-VS-operator grant container holding one `ParticipantAuthorizationRecord` per controlled `Participant`).

##### `listOperatorAuthorizations`

**Spec tag:** `IDX-DE-QRY-1` <a id="idx-de-qry-1"></a>

`GET /de/v1/operator-authorizations`

Retrieve a paginated, filtered list of `OperatorAuthorization` entries. Each entry represents a corporation's authorization granted to a specific operator account for one or more module message types. *Aligned with VPR [[MOD-DE-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-de-qry-1-list-operator-authorizations).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | query | string | no | Filter by the granting Corporation (bech32 group address) |
| `operator` | query | string | no | Filter by the grantee operator account |
| `msg_type` | query | string | no | Filter to authorizations whose `msg_types[]` includes this message type |
| `only_active` | query | boolean | no | If true, only return non-expired authorizations (`expiration > now` or null) |
| `modified_after` | query | datetime | no | Only return authorizations modified strictly after this datetime |
| `response_max_size` | query | integer | no | 1..1024, default 64 |
| `sort` | query | string | no | Sort criteria; default `-modified` |

**Response:** `{ authorizations: OperatorAuthorization[] }` — each entry carries `corporation`, `operator`, `msg_types[]`, `spend_limit[]` (optional `DenomAmount[]`), `remaining_spend[]` (when `spend_limit` is set), `fee_spend_limit[]` (optional), `remaining_fee_spend[]` (when `fee_spend_limit` is set), `expiration` (optional timestamp), and `period` (optional duration).

##### `listVSOperatorAuthorizations`

**Spec tag:** `IDX-DE-QRY-2` <a id="idx-de-qry-2"></a>

`GET /de/v1/vs-operator-authorizations`

Retrieve a paginated, filtered list of `VSOperatorAuthorization` entries. Each entry is keyed by `(corporation, vs_operator)` and holds the `ParticipantAuthorizationRecord[]` array — one record per `Participant` whose VS-operator authorization is delegated to that `vs_operator`. *Aligned with VPR [[MOD-DE-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-de-qry-2-list-vs-operator-authorizations).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `corporation` | query | string | no | Filter by the granting Corporation (bech32 group address) |
| `vs_operator` | query | string | no | Filter by the grantee VS-operator account |
| `participant_id` | query | integer (int64) | no | Filter to entries whose `records[]` contains a record for this `Participant.id` |
| `only_active` | query | boolean | no | If true, only return entries with at least one non-expired record |
| `modified_after` | query | datetime | no | Only return entries modified strictly after this datetime |
| `response_max_size` | query | integer | no | 1..1024, default 64 |
| `sort` | query | string | no | Sort criteria; default `-modified` |

**Response:** `{ authorizations: VSOperatorAuthorization[] }` — each entry carries `corporation`, `vs_operator`, and `records[]: ParticipantAuthorizationRecord[]`. Each `ParticipantAuthorizationRecord` carries `participant_id` (globally unique), `msg_types[]`, `spend_limit[]` (optional), `remaining_spend[]` (when `spend_limit` is set), `fee_spend_limit[]` (optional), `remaining_fee_spend[]` (when `fee_spend_limit` is set), `with_feegrant` (boolean), `expiration` (timestamp), and `period` (optional duration). This is the canonical surface for the data that was previously inlined as `Participant.vs_operator_authz_*` fields.

#### Digest methods

##### `getDigest`

**Spec tag:** `IDX-DI-QRY-1` <a id="idx-di-qry-1"></a>

`GET /di/v1/get/{digest}`

Look up a previously stored `Digest` entry by its digest string. *Aligned with VPR [[MOD-DI-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-di-qry-1-get-digest).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `digest` | path | string | yes | The digest to look up (typically an SRI digest such as `sha384-…`) |

**Response:** `{ digest: Digest }` — `{ digest: string, created: timestamp }`. Returns HTTP 404 if no `Digest` entry exists for the supplied value.

#### Exchange Rate methods

The Exchange Rate module is a protocol-level oracle that publishes on-chain conversion rates between asset pairs (`(base_asset_type, base_asset)` → `(quote_asset_type, quote_asset)`), and exposes a derived `getPrice` helper that performs the integer arithmetic conversion. Rates are scoped to the network, not to a corporation, and update permission is governed by `ExchangeRateAuthorization` entries.

##### `getExchangeRate`

**Spec tag:** `IDX-XR-QRY-1` <a id="idx-xr-qry-1"></a>

`GET /xr/v1/get`

Retrieve a single `ExchangeRate` entry, either by its primary key `id` or by the natural composite asset-pair key. *Aligned with VPR [[MOD-XR-QRY-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-xr-qry-1-get-exchange-rate).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | query | integer (int64) | conditional¹ | Primary-key lookup |
| `base_asset_type` | query | enum | conditional¹ | `TRUST_UNIT` \| `COIN` \| `FIAT` |
| `base_asset` | query | string | conditional¹ | Base asset identifier (`"TU"` for `TRUST_UNIT`; on-chain denom for `COIN`; ISO-4217 currency code for `FIAT`) |
| `quote_asset_type` | query | enum | conditional¹ | `TRUST_UNIT` \| `COIN` \| `FIAT` |
| `quote_asset` | query | string | conditional¹ | Quote asset identifier (same rules as `base_asset`) |
| `state` | query | boolean | no | Force-filter on `state` (`true` enabled / `false` disabled). When omitted, both are returned |
| `expire_ts` | query | datetime | no | Return only if `expires > expire_ts` |

¹ Either `id` MUST be provided, **or** the full four-tuple (`base_asset_type`, `base_asset`, `quote_asset_type`, `quote_asset`) MUST be provided.

**Response:** `{ exchange_rate: ExchangeRate }` — `id`, `base_asset_type`, `base_asset`, `quote_asset_type`, `quote_asset`, `rate` (string; base-10 unsigned integer), `rate_scale` (uint32; number of decimal digits used to scale `rate`), `validity_duration` (duration), `updated` (timestamp), `expires` (timestamp), `state` (boolean — true means enabled).

##### `listExchangeRates`

**Spec tag:** `IDX-XR-QRY-2` <a id="idx-xr-qry-2"></a>

`GET /xr/v1/list`

Retrieve a paginated, filtered list of `ExchangeRate` entries. *Aligned with VPR [[MOD-XR-QRY-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-xr-qry-2-list-exchange-rates).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `base_asset_type` | query | enum | no | Filter on base asset type |
| `base_asset` | query | string | no | Filter on base asset identifier |
| `quote_asset_type` | query | enum | no | Filter on quote asset type |
| `quote_asset` | query | string | no | Filter on quote asset identifier |
| `state` | query | boolean | no | Filter on `state` |
| `expire` | query | datetime | no | Return only entries whose `expires > expire` |
| `response_max_size` | query | integer | no | 1..1024, default 64 |
| `sort` | query | string | no | Sort criteria; default `-updated` |

**Response:** `{ exchange_rates: ExchangeRate[] }`. Each entry has the same shape as [`getExchangeRate`](#getexchangerate).

##### `getPrice`

**Spec tag:** `IDX-XR-QRY-3` <a id="idx-xr-qry-3"></a>

`GET /xr/v1/price`

Convert an amount of a base asset to its equivalent in a quote asset using the relevant active, non-expired `ExchangeRate` entry. *Aligned with VPR [[MOD-XR-QRY-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-xr-qry-3-get-price).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `base_asset_type` | query | enum | yes | `TRUST_UNIT` \| `COIN` \| `FIAT` |
| `base_asset` | query | string | yes | Base asset identifier |
| `quote_asset_type` | query | enum | yes | `TRUST_UNIT` \| `COIN` \| `FIAT` |
| `quote_asset` | query | string | yes | Quote asset identifier |
| `amount` | query | string | yes | Base-asset amount expressed as a base-10 unsigned integer string, in the base asset's base units |

**Response:** `{ price: string, base_asset_type, base_asset, quote_asset_type, quote_asset, rate, rate_scale, expires }` where `price` is a base-10 unsigned integer string in the quote asset's base units. When `(base_asset_type, base_asset) == (quote_asset_type, quote_asset)`, `price == amount` and rate fields are omitted. Otherwise `price = floor(amount * rate / 10^rate_scale)`, integer arithmetic, rounded down. If no matching `ExchangeRate` entry exists, is disabled, or is expired, the response is HTTP 404 / 410.

#### Metrics methods

##### `getGlobalMetrics`

**Spec tag:** `IDX-METRICS-QRY-1` <a id="idx-metrics-qry-1"></a>

`GET /metrics/v1/all`

Return network-wide aggregate metrics across all Ecosystems, Credential Schemas, and Participants at the current (or historical, via `At-Block-Height`) block. *Indexer-specific (no VPR equivalent).*

(No method-specific parameters.)

**Response:** `GlobalMetricsResponse` — totals per metric: `participants` (and the per-role breakdown `participants_ecosystem`, `participants_issuer_grantor`, `participants_issuer`, `participants_verifier_grantor`, `participants_verifier`, `participants_holder`), `active_ecosystems`, `archived_ecosystems`, `active_schemas`, `archived_schemas`, `weight` (int64), `issued`, `verified`, and the slash ledger (`ecosystem_slash_events`, `ecosystem_slashed_amount`, `ecosystem_slashed_amount_repaid`, `network_slash_events`, `network_slashed_amount`, `network_slashed_amount_repaid`).

#### Statistics methods

##### `getStats`

**Spec tag:** `IDX-STATS-QRY-1` <a id="idx-stats-qry-1"></a>

`GET /stats/v1/get`

Retrieve a single statistics row — either by its primary key `id`, or by the natural composite key (`granularity`, `timestamp`, `entity_type`, `entity_id`). *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `id` | query | integer | no¹ | Primary-key lookup |
| `granularity` | query | enum | no¹ | `HOUR` \| `DAY` \| `MONTH` |
| `timestamp` | query | datetime | no¹ | Bucket start (ISO 8601 UTC) |
| `entity_type` | query | enum | no¹ | `GLOBAL` \| `ECOSYSTEM` \| `CREDENTIAL_SCHEMA` \| `PARTICIPANT` |
| `entity_id` | query | integer | no¹ | Required for non-`GLOBAL` entity types |

¹ Either `id` MUST be provided, **or** the composite key (`granularity`, `timestamp`, `entity_type`, `entity_id`) MUST be provided.

**Response:** A `StatsEntry` — `id`, `granularity`, `timestamp`, `entity_type`, `entity_id`, the full set of `cumulative_*` running totals (`cumulative_participants`, `cumulative_active_schemas`, `cumulative_archived_schemas`, `cumulative_weight`, `cumulative_issued`, `cumulative_verified`, and the ecosystem/network slash counters and amounts), and the corresponding `delta_*` change-since-previous-measurement fields.

##### `getStatsRange`

**Spec tag:** `IDX-STATS-QRY-2` <a id="idx-stats-qry-2"></a>

`GET /stats/v1/stats`

Retrieve cumulative-and-delta statistics over a time range as buckets, totals, or both. When `granularity` is omitted, the indexer auto-selects the smallest combination of `MONTH` + `DAY` + `HOUR` buckets that covers the range. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `timestamp_from` | query | datetime | yes | Range start (inclusive), ISO 8601 UTC |
| `timestamp_until` | query | datetime | yes | Range end (exclusive), ISO 8601 UTC |
| `entity_type` | query | enum | yes | `GLOBAL` \| `ECOSYSTEM` \| `CREDENTIAL_SCHEMA` \| `PARTICIPANT` |
| `entity_ids` | query | string | conditional | Comma-separated entity IDs (e.g. `1,2,3`). MUST be empty for `GLOBAL`, REQUIRED otherwise |
| `granularity` | query | enum | no | `HOUR` \| `DAY` \| `MONTH`. When omitted, auto-selected |
| `result_type` | query | enum | no | `BUCKETS` \| `TOTAL` \| `BUCKETS_AND_TOTAL` (default `BUCKETS_AND_TOTAL`) |

**Response:** `StatsResponse` — `granularity` (the effective granularity used), `timestamp_from`, `timestamp_until`, `entity_type`, `entity_ids`, `result_type`, plus `buckets[]: StatsBucket[]` when `result_type` includes buckets and `total: StatsTotal` when it includes a total. Each `StatsBucket` carries the same `cumulative_*` and `delta_*` fields as [`getStats`](#getstats); each `StatsTotal` carries only the summed `delta_*` fields.

##### `getParticipantsAtHeight`

**Spec tag:** `IDX-STATS-QRY-3` <a id="idx-stats-qry-3"></a>

`GET /stats/v1/participants-at-height`

Return the count of participants of a given role for a given entity at the block selected by the `At-Block-Height` header (or the latest indexed block when omitted), derived from the `entity_participant_changes` log. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `entity_kind` | query | integer | yes | `0`=GLOBAL, `1`=ECOSYSTEM, `2`=CREDENTIAL_SCHEMA, `3`=PARTICIPANT |
| `entity_id` | query | integer | conditional | Required for non-`GLOBAL` entity kinds; MUST be omitted for `GLOBAL` |
| `role_type` | query | integer | yes | `0`=ANY, `1`=ECOSYSTEM, `2`=ISSUER_GRANTOR, `3`=ISSUER, `4`=VERIFIER_GRANTOR, `5`=VERIFIER, `6`=HOLDER |

**Response:** Inline object `{ entity_kind, entity_id, role_type, block_height, participants }` where `block_height` echoes the resolved evaluation block and `participants` is the integer count.

#### Indexer methods

##### `getBlockHeight`

**Spec tag:** `IDX-INDEXER-QRY-1` <a id="idx-indexer-qry-1"></a>

`GET /indexer/v1/block-height`

Return the latest block height that the indexer has fully processed and committed. *Indexer-specific (no VPR equivalent).*

(No parameters.)

**Response:** `{ type: "block-indexed", height: integer, timestamp: ISO-8601 datetime }`. `timestamp` is the wall-clock time at which the checkpoint was last updated (without milliseconds).

##### `getIndexerStatus`

**Spec tag:** `IDX-INDEXER-QRY-2` <a id="idx-indexer-qry-2"></a>

`GET /indexer/v1/status`

Return the indexer's operational status — whether it is running, whether crawling is active, and any error information if crawling or the indexer has stopped. Useful for monitoring and debugging. *Indexer-specific (no VPR equivalent).*

(No parameters.)

**Response:** Inline object with `is_running` (boolean — if false, all API endpoints respond with HTTP 503), `is_crawling` (boolean — if false, APIs remain available but no new data is being indexed), and, when applicable, `stopped_at`, `stopped_reason`, `last_error: { message, stack, timestamp, service }`. The response also surfaces `X-Crawling-Status`, `X-Indexer-Status`, `X-Crawling-Reason`, `X-Crawling-Error`, and `X-Crawling-Stopped-At` HTTP response headers for consumers that prefer header-only health checks.

##### `getVersion`

**Spec tag:** `IDX-INDEXER-QRY-3` <a id="idx-indexer-qry-3"></a>

`GET /indexer/v1/version`

Return the indexer version and the network environment it is bound to. *Indexer-specific (no VPR equivalent).*

(No parameters.)

**Response:** Inline object `{ app_version, environment: { network: { chain_id, rpc_endpoint, lcd_endpoint, cosmos_sdk_version, node_version, app_name } } }`.

##### `getIndexerSnapshot`

**Spec tag:** `IDX-INDEXER-QRY-4` <a id="idx-indexer-qry-4"></a>

`GET /indexer/v1/snapshot`

Return the indexed snapshot of all DID-linked objects (Ecosystems, Credential Schemas, Participants) for a single DID at the block selected by the `At-Block-Height` header (or the latest indexed block when omitted). Only queries current tables that expose a height column; does **not** consult history tables. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `did` | query | string | yes | DID to snapshot |

**Response:** Inline `{ did, block_height, ecosystems: object[], schemas: object[], participants: object[], count: { ecosystems, schemas, participants } }` where `block_height` echoes the resolved snapshot block.

##### `listChanges`

**Spec tag:** `IDX-INDEXER-QRY-5` <a id="idx-indexer-qry-5"></a>

`GET /indexer/v1/changes`

Return every indexed entity change committed at the block selected by the `At-Block-Height` header (or the latest indexed block when omitted). Distinct from the WebSocket-companion [`listChanges` at `/vt/v1/changes`](#idx-vt-qry-2), which collapses across blocks for resolver-stream catch-up. *Indexer-specific (no VPR equivalent).*

(No method-specific parameters.)

**Response:** Inline `{ block_height, next_change_at, activity: ActivityItem[] }`. `block_height` echoes the resolved block; `next_change_at` is the next block height greater than the resolved one that has at least one indexed change (null when no later change is known). Each `activity` item has the same shape as in `ActivityTimelineResponse` (see [`getEcosystemHistory`](#getecosystemhistory)).

##### `listIndexerEvents`

**Spec tag:** `IDX-INDEXER-QRY-6` <a id="idx-indexer-qry-6"></a>

`GET /indexer/v1/events`

Replay persisted Ecosystem, Credential Schema, and Participant events for a given DID, after a given block height. Backs the DID-scoped WebSocket room described in the indexer's OpenAPI document at the same path (`?did=<DID>`). *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `did` | query | string | yes | DID to replay events for (only rows persisted for this DID are returned) |
| `after_block_height` | query | integer | no | Return events with `block_height` strictly greater than this value (default 0) |
| `limit` | query | integer | no | 1..500, default 100 — maximum number of events to return |

**Response:** Inline `{ events: IndexerTransactionEvent[], count, after_block_height }`. Each `IndexerTransactionEvent` carries `type: "indexer-event"`, `event_type` (Cosmos action name, e.g. `StartParticipantOP`), `did`, `block_height`, `tx_hash`, `timestamp`, and `payload: { module, action, message_type, tx_index, message_index, sender, related_dids[], entity_type, entity_id }`.

##### `subscribeIndexerEvents`

**Spec tag:** `IDX-INDEXER-SUB-1` <a id="idx-indexer-sub-1"></a>

`WS /indexer/v1/events?did=<DID>`

Real-time push of Ecosystem, Credential Schema, and Participant events for a given DID. The subscriber opens a WebSocket connection to `/indexer/v1/events` with the `did` query parameter set to the target DID; the server then streams one `IndexerTransactionEvent` JSON message per indexed event affecting that DID, in block-and-tx order. *Indexer-specific (no VPR equivalent).*

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `did` | query | string | yes | DID whose events are subscribed to. Each WebSocket connection is bound to exactly one DID; clients needing multiple DIDs MUST open multiple connections |

**Server → client messages:** Each message is a single `IndexerTransactionEvent` (same shape as the `events[]` items returned by [`listIndexerEvents`](#listindexerevents)). No batching, no envelope.

**Catch-up and resume:** This stream does not deliver historical events on connect. To bootstrap from a known point, the client SHOULD call [`listIndexerEvents`](#listindexerevents) with `after_block_height` set to its `last_seen_block`, paginate to exhaustion, then connect the WebSocket. After a temporary disconnection, the client SHOULD repeat the same pattern using the most recent `block_height` it processed.

**Backpressure:** A subscriber that fails to drain its receive buffer within an indexer-defined window MAY have its connection closed. The client SHOULD reconnect and resume via [`listIndexerEvents`](#listindexerevents).

#### Verifiable Trust Resolver methods

The Verifiable Trust Resolver answers two complementary questions about a DID at a chosen point in time:

1. **Is the DID a Verifiable Service?** — Reflected in the boolean `trusted` field of the response.

   Per [[VS-REQ]], a DID qualifies as a **Verifiable Service** only if:
   - **[VS-REQ-2]** It presents a valid Service Credential (`ECS-SERVICE` VTC).
   - **[VS-REQ-3]** If the issuer of the Service Credential **is the VS itself** (self-issued), the VS MUST also present exactly one `ECS-ORG` or `ECS-PERSONA` credential.
   - **[VS-REQ-4]** If the issuer of the Service Credential **is another DID**, the DID Document of that issuer MUST present exactly one `ECS-ORG` or `ECS-PERSONA` credential.

   This ensures every VS is ultimately bound to a legally or naturally accountable entity — either directly (the VS identifies itself) or indirectly (the issuer of its Service Credential identifies itself). A DID that satisfies these requirements is returned with `trusted: true`; otherwise `trusted: false`.

2. **What contextual data does the indexer have on this DID?** — Opt-in sections selected via the request payload. Each section is suppressed by default and is only computed and returned when its selector is set:

   - **`corporation`** — The on-chain Corporation entry the DID **represents** (the Corporation whose `did` equals the resolved DID). A singular object — by VPR, a DID is the `did` of at most one Corporation; omitted when no such Corporation exists for this `did`. Carries the Corporation's stable `id` (bech32 group address), `deposit`, slash history, and active CGF.
   - **`participations`** — Credential Schemas the DID participates in, filterable by state (`ACTIVE`, `FUTURE`, `INACTIVE`, `EXPIRED`, `REVOKED`, `SLASHED`, `REPAID`); defaults to `ACTIVE` when no filter is given.
   - **`ecsCredentials`** — The full ECS credentials extracted from the DID's linked-VPs, with their `credentialSubject` claims.
   - **`services`** — Non-`LinkedVerifiablePresentation` service entries from the DID Document (DIDComm, MCP, A2A, LinkedDomains, …), surfaced verbatim.
   - **`presentations`** — Per-VP credential summaries (`vtcCredentials[]`, each entry `{id, credentialSchemaId, ecosystemId}`); sub-flags additionally surface unresolvable and invalid credential IDs per VP.
   - **`ecosystems`** — Aggregate metrics for the Ecosystems (and their underlying Credential Schemas and active Ecosystem Governance Frameworks) **the DID is the controller of** (the Ecosystems whose `did` equals the resolved DID). Sub-flags control whether archived Ecosystems (and their archived embedded Credential Schemas) are included.

The response always carries the core fields (`did`, `trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`); every other section is gated by its selector. The `vsOperator` account, in contrast, is surfaced **per Participation** (not at envelope level) because each `Participant` entry carries its own VS Operator Authorization grant from its controlling Corporation's group. The full payload contract is normatively defined by the [Resolution request schema](#resolution-request-schema) and [Resolution response schema](#resolution-response-schema) below.

The point-in-time is controlled by the `At-Block-Height` HTTP request header per [Conventions](#at-block-height-header); when omitted, the resolver evaluates against the latest indexed block. The resolved block is echoed back as `evaluatedAtBlock` (with `evaluatedAtTime` as its wall-clock equivalent) in the response.

> **Recursive resolution.** To obtain full details about any other DID surfaced in the response (e.g. an ECS credential's subject at `ecsCredentials[].credentialSubject.id`, or any other DID a consumer chooses to inspect), call this same method on that DID. Note that most cross-entity references are surfaced by stable VPR id rather than DID (e.g. `corporationId`, `ecosystemId`, `credentialSchemaId`, `participantId`, `issuerParticipantId`) and do not need re-resolution — they're already directly joinable.

##### `resolve`

**Spec tag:** `IDX-VT-QRY-1` <a id="idx-vt-qry-1"></a>

`POST /vt/v1/resolve`

###### Resolution request schema

The normative JSON Schema for the resolution request is published alongside this document at [`schemas/v4/vt/request.schema.json`](./schemas/v4/vt/request.schema.json). It defines the `did` parameter and the response-shaping selectors (`corporation`, `participations`, `ecsCredentials`, `services`, `presentations`, `ecosystems`). The point-in-time is selected via the `At-Block-Height` HTTP header and is therefore not part of the request body.

###### Resolution response schema

The normative JSON Schema for the resolution response is published alongside this document at [`schemas/v4/vt/response.schema.json`](./schemas/v4/vt/response.schema.json). It defines the always-present core fields (`did`, `trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`) and every optional section returned when the corresponding request selector is set.

###### Example resolution request

The following is a **maximum** request that asks for every optional section the resolver can return. Any top-level selector below MAY be omitted, in which case that section is excluded from the response. The response always includes the core fields (`did`, `trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`).

```json
{
   "did": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
   "corporation": true,
   "participations": {
      "states": ["ACTIVE", "FUTURE", "INACTIVE", "EXPIRED", "REVOKED", "SLASHED", "REPAID"]
   },
   "ecsCredentials": true,
   "services": true,
   "presentations": {
      "unresolvableCredentialIds": true,
      "invalidCredentialIds": true
   },
   "ecosystems": {
      "includeArchived": true,
      "credentialSchemas": {
         "includeArchived": true
      }
   }
}
```

Point-in-time is selected via the `At-Block-Height` HTTP request header (see [Conventions](#at-block-height-header)); it is not part of the JSON body. To target the historical block from the example above (`1500000`), send `At-Block-Height: 1500000` alongside the POST.

Selector semantics:

- **`corporation`** — `true` to include the `corporation` object (the unique Corporation whose `did` equals the resolved DID; carries `id`, `deposit`, slash history, and `cgf`). Omit or set `false` to exclude. The top-level `corporationId` scalar (which equals `corporation.id` whenever the latter is included — by VPR's per-Corporation `did` uniqueness invariant they are necessarily the same Corporation) is **always** returned with the trust-core fields and is not gated by this selector; this selector only controls whether the full Corporation object (`deposit`, slash history, CGF) is also surfaced inline.
- **`participations`** — Omit to exclude. When present, `states[]` filters which participation states are returned. Defaults to `["ACTIVE"]` when `participations` is provided without `states`. Valid values: `ACTIVE, FUTURE, INACTIVE, EXPIRED, REVOKED, SLASHED, REPAID`.
- **`ecsCredentials`** — `true` to include the full ECS credentials with subject claims. Omit or `false` to exclude.
- **`services`** — `true` to include `services[]`, the non-LinkedVerifiablePresentation service entries from the DID Document (e.g. DIDComm, MCP, LinkedDomains). Omit or `false` to exclude.
- **`presentations`** — Omit to exclude. When present, each entry always carries `vtcCredentials[]` (array of `{id, credentialSchemaId, ecosystemId}` per non-ECS VTC carried by the VP) plus the VP's `id` and `serviceId`. The two sub-flags additionally enable `unresolvableCredentialIds[]` and `invalidCredentialIds[]` per entry; both default to `false`.
- **`ecosystems`** — Omit to exclude. `includeArchived` (default `false`) controls whether archived ecosystems appear in the top-level array. The nested `credentialSchemas` object controls embedded Credential Schemas: omit `credentialSchemas` entirely to suppress them, or set `credentialSchemas.includeArchived` (default `false`) to also surface archived Credential Schemas.

###### Example resolution response

participation states: REPAID, SLASHED, REVOKED, EXPIRED, ACTIVE, FUTURE, INACTIVE
participation roles: HOLDER, ISSUER, VERIFIER, ISSUER_GRANTOR, VERIFIER_GRANTOR, ECOSYSTEM

```json
{
   "did":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
   "trusted":true,
   "evaluatedAtTime":"2026-05-06T17:00:00.000Z",
   "evaluatedAtBlock":1500000,
   "expiresAtTime":"2026-05-07T17:00:00.000Z",
   "corporationId":"verana1rw7w9hm0zd7e4jcxsm955nu8l5ju0wtkpssxe5",
   "corporation":{
      "id":"verana1rw7w9hm0zd7e4jcxsm955nu8l5ju0wtkpssxe5",
      "deposit":"40000000uvna",
      "lastSlashedAt":"2026-01-01T03:00:00.000Z",
      "slashedEvents":1,
      "slashedValue":"1000000uvna",
      "cgf":{
         "version":3,
         "activeSince":"2026-02-15T09:00:00.000Z",
         "documents":[
            {
               "language":"en",
               "url":"https://corp.acme.example/cgf/v3/en.html",
               "digestSRI":"sha384-…"
            },
            {
               "language":"fr",
               "url":"https://corp.acme.example/cgf/v3/fr.html",
               "digestSRI":"sha384-…"
            }
         ]
      }
   },
   "participations":[
      {
         "id":501,
         "vsOperator":"verana19kpereglz3jw690kjys3lnulx2r06p99l5u6sz",
         "role":"ISSUER",
         "state":"ACTIVE",
         "credentialSchemaId":1234,
         "ecosystemId":9876,
         "weight":"10000000uvna",
         "issuedCredentials":2345,
         "participants":{
            "HOLDER":75
         }
      },
      {
         "id":502,
         "vsOperator":"verana19kpereglz3jw690kjys3lnulx2r06p99l5u6sz",
         "role":"VERIFIER",
         "state":"ACTIVE",
         "credentialSchemaId":5678,
         "ecosystemId":9877,
         "weight":"5000000uvna",
         "verifiedCredentials":500
      },
      {
         "id":503,
         "vsOperator":"verana1otheropacctxxxxxxxxxxxxxxxxxxxxxxxxx",
         "role":"ISSUER_GRANTOR",
         "state":"REPAID",
         "credentialSchemaId":9012,
         "ecosystemId":9878,
         "weight":"5000000uvna",
         "participants":{
            "ISSUER":7,
            "HOLDER":1250
         },
         "verifiedCredentials":500
      }
   ],
   "ecsCredentials":[
      {
         "ecsSchema":"ServiceCredential",
         "ecsSchemaVersion":"v4",
         "credentialSchemaId":11,
         "issuerParticipantId":801,
         "ecosystemId":1,
         "participantId":601,
         "id":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#cc5c398f-bc64-45df-9482-9cb583cce197",
         "validFrom":"2010-01-01T19:23:24Z",
         "validUntil":"2030-01-01T19:23:24Z",
         "credentialSubject":{
            "id":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
            "name":"Acme MCP Service",
            "type":"MCPService",
            "description":"AI tooling backend for Acme partners.",
            "minimumAgeRequired":0,
            "termsAndConditions":"https://acme-vs.example.com/terms",
            "termsAndConditionsDigestSRI":"sha384-…",
            "privacyPolicy":"https://acme-vs.example.com/privacy",
            "privacyPolicyDigestSRI":"sha384-…",
            "logo":"https://acme-vs.example.com/logo",
            "logoDigestSRI":"sha384-…"
         }
      },
      {
         "ecsSchema":"OrganizationCredential",
         "ecsSchemaVersion":"v4",
         "credentialSchemaId":12,
         "issuerParticipantId":802,
         "ecosystemId":1,
         "participantId":602,
         "validFrom":"2010-01-01T19:23:24Z",
         "validUntil":"2030-01-01T19:23:24Z",
         "credentialSubject":{
            "id":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
            "name":"Acme Corp",
            "registryId":"BE0123456789",
            "registryUri":"https://kbo-data.economie.fgov.be/",
            "address":"Rue de la Loi 1, 1000 Brussels",
            "countryCode":"BE",
            "legalJurisdiction":"BE",
            "lei":"529900T8BM49AURSDO55",
            "organizationKind":"PRIVATE",
            "logo":"https://acme-vs.example.com/logo",
            "logoDigestSRI":"sha384-…"
         }
      }
   ],
   "presentations":[
      {
         "id":"https://organization.vs.hologram.zone/vt/vp1.json",
         "vtcCredentials":[
            {
               "id":"urn:uuid:22222222-aaaa-bbbb-cccc-222222222222",
               "credentialSchemaId":30001,
               "ecosystemId":9876,
               "participantId":701,
               "issuerParticipantId":901
            },
            {
               "id":"urn:uuid:33333333-aaaa-bbbb-cccc-333333333333",
               "credentialSchemaId":30002,
               "ecosystemId":9877,
               "participantId":702,
               "issuerParticipantId":902
            }
         ],
         "unresolvableCredentialIds":[
            "urn:uuid:44444444-aaaa-bbbb-cccc-444444444444"
         ],
         "invalidCredentialIds":[
            "urn:uuid:88888888-aaaa-bbbb-cccc-888888888888"
         ],
         "serviceId":"did:web:organization.vs.hologram.zone#vt-vp1"
      }
   ],
   "services":[
      {
         "id":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#mcp",
         "type":"MCP",
         "serviceEndpoint":"https://organization.vs.hologram.zone/mcp"
      },
      {
         "id":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#did-communication",
         "serviceEndpoint":"wss://organization.vs.hologram.zone/didcomm",
         "type":"did-communication",
         "accept":[
            "didcomm/aip2;env=rfc19",
            "didcomm/v2"
         ]
      }
   ],
   "ecosystems":[
      {
         "id":1234,
         "corporationId":"verana1rw7w9hm0zd7e4jcxsm955nu8l5ju0wtkpssxe5",
         "archived":false,
         "egf":{
            "version":7,
            "activeSince":"2026-03-01T00:00:00.000Z",
            "documents":[
               {
                  "language":"en",
                  "url":"https://ecosystem1.example/egf/v7/en.html",
                  "digestSRI":"sha384-…"
               },
               {
                  "language":"es",
                  "url":"https://ecosystem1.example/egf/v7/es.html",
                  "digestSRI":"sha384-…"
               }
            ]
         },
         "credentialSchemas":[
            {
               "id":223,
               "type":"JsonSchema",
               "digestSRI":"sha384-…",
               "archived":false,
               "participants":{
                  "ECOSYSTEM":2000,
                  "ISSUER_GRANTOR":100,
                  "ISSUER":400,
                  "VERIFIER_GRANTOR":50,
                  "VERIFIER":45,
                  "HOLDER":1000
               },
               "issuedCredentials":14526,
               "verifiedCredentials":7256725
            }
         ],
         "participants":{
            "ECOSYSTEM":2000,
            "ISSUER_GRANTOR":100,
            "ISSUER":400,
            "VERIFIER_GRANTOR":50,
            "VERIFIER":45,
            "HOLDER":1000
         },
         "issuedCredentials":14526,
         "verifiedCredentials":7256725
      }
   ]
}
```

The Verifiable Trust Resolver also exposes a real-time event stream so that clients can keep an indexer-backed mirror in sync without polling `/vt/v1/resolve` for every DID on every block.

The stream is organised around three coordinated endpoints. Together they cover live updates (`subscribeChanges`), catch-up after a disconnection (`listChanges`), and bootstrap from an empty mirror (`listIndexedDids`).

The unit of notification is **(DID, block)**: each time the indexer processes a new block, it re-evaluates trust for every DID whose state may have changed and emits **at most one change envelope per DID per block**, restricted to the channels the subscriber selected.

The normative JSON Schemas for this stream are published alongside this document:

- [`schemas/v4/vt/subscribe.schema.json`](./schemas/v4/vt/subscribe.schema.json) — client → server WebSocket control messages (`subscribe`, `unsubscribe`), including the channel selectors and sub-flags described in the [Channels](#channels) section below.
- [`schemas/v4/vt/changes.schema.json`](./schemas/v4/vt/changes.schema.json) — server-side payloads: the WS `ready` message, the WS `block` message, and the `listChanges` REST response, all sharing the common `ChangeEnvelope` shape.

##### Websocket Channels

A subscription selects a set of channels. Each channel narrows what counts as a "change" for the subscribed DID:

| Channel | Triggers a notification when … |
| --- | --- |
| `trust` | Any of the trust-core fields (`trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`) change. The new values are delivered inline. The top-level `corporationId` rotation (DID re-binding to a different Corporation, e.g. as part of an ownership transfer) is signalled here. |
| `corporation` | The `corporation` object (the singular Corporation whose `did` equals the resolved DID) is created or removed; **or** has a structural change (Cosmos group rotation — its `id` changes — or a slash event); **or** its active CGF rotates (`active_version` advances) or any document of the active CGF version changes (URL or `digestSRI`). The top-level `corporationId` scalar itself (the binding "this DID is operated by *that* Corp") is part of the `trust` channel above and is not gated separately. `deposit` fluctuations alone are gated by the `includeDepositChanges` sub-flag below. |
| `participations` | A `Participation` entry the DID is part of is created or transitions state, **or** its `vsOperator` rotates (the controlling Corp re-authorises a different operator account for that specific Participant). `weight` fluctuations alone are gated by the `includeWeightChanges` sub-flag below. |
| `ecsCredentials` | An ECS credential issued to or by the DID is added, replaced, or invalidated. |
| `presentations` | A `LinkedVerifiablePresentation` referenced by the DID Document is added or removed, or its `vtcCredentials[]` set changes (entry added/removed, or any entry's `credentialSchemaId` / `ecosystemId` / `participantId` / `issuerParticipantId` changes). Changes confined to `unresolvableCredentialIds[]` or `invalidCredentialIds[]` are **not** notified. |
| `services` | A non-`LinkedVerifiablePresentation` service entry in the DID Document changes (DIDComm, MCP, A2A, LinkedDomains, …). |
| `ecosystems` | An `Ecosystem` entry the DID represents is created or archived; its `corporationId` (controlling Corporation) changes; its embedded schemas change; **or** its active EGF rotates (`active_version` advances) or any document of the active EGF version changes (URL or `digestSRI`). |

Channels that carry Coin-amount fields (`weight`, `deposit`) or high-frequency aggregate counters (`participants[role]`, `issuedCredentials`, `verifiedCredentials`) expose opt-in sub-flags so subscribers can choose whether routine fluctuations of those values trigger notifications:

| Channel | Sub-flag | Effect when `true` |
| --- | --- | --- |
| `corporation` | `includeDepositChanges` | Changes in the `corporation` object's `deposit` Coin amount trigger a notification (independent of slash events, which always trigger). |
| `participations` | `includeWeightChanges` | Changes in a Participation's `weight` Coin amount trigger a notification. |
| `participations` | `includeParticipantCounts` | Changes in `participants[role]` counters trigger a notification. |
| `participations` | `includeIssuedCredentials` | Changes in the `issuedCredentials` counter trigger a notification. |
| `participations` | `includeVerifiedCredentials` | Changes in the `verifiedCredentials` counter trigger a notification. |
| `ecosystems` | `includeParticipantCounts` | Changes in Ecosystem-level `participants[role]` counters trigger a notification. |
| `ecosystems` | `includeIssuedCredentials` | Changes in the Ecosystem-level `issuedCredentials` counter trigger a notification. |
| `ecosystems` | `includeVerifiedCredentials` | Changes in the Ecosystem-level `verifiedCredentials` counter trigger a notification. |

All sub-flags default to `false`. The Coin-amount flags (`includeDepositChanges`, `includeWeightChanges`) and the counter flags (`includeParticipantCounts`, `includeIssuedCredentials`, `includeVerifiedCredentials`) gate fields that can tick on routine transactions and would otherwise dominate the stream.

Channel flags carry **change signals**, not full new values — except for `trust`, which is delivered inline because it is small, fixed-shape, and the most frequently consumed. To obtain the new state for any other changed channel, the client calls `/vt/v1/resolve` with the `At-Block-Height` header set to the block of the change envelope.

##### `subscribeChanges`

**Spec tag:** `IDX-VT-SUB-1` <a id="idx-vt-sub-1"></a>

The subscriber opens a WebSocket connection to `/vt/v1/subscribe` and sends one or more JSON control messages. The first control message MUST be a `subscribe`.

###### Connect / ready

Immediately after a successful WebSocket upgrade, before any `subscribe` is processed, the server sends a `ready` message:

```json
{
   "type": "ready",
   "block": 1500005,
   "blockTime": "2026-05-11T13:00:05Z"
}
```

`block` is the height of the **next** block that the server will deliver via this WebSocket (i.e. `latestProcessedBlock + 1` at connect time). Clients use `block - 1` as the bootstrap snapshot point — see [Bootstrap pattern](#bootstrap-pattern).

###### Subscribe control message

```json
{
   "action": "subscribe",
   "dids": [
      "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone"
   ],
   "channels": {
      "trust":          true,
      "ecsCredentials": true,
      "presentations":  true,
      "services":       true,
      "corporation": {
         "includeDepositChanges":            false
      },
      "participations": {
         "includeWeightChanges":       false,
         "includeParticipantCounts":   false,
         "includeIssuedCredentials":   false,
         "includeVerifiedCredentials": false
      },
      "ecosystems": {
         "includeParticipantCounts":   false,
         "includeIssuedCredentials":   false,
         "includeVerifiedCredentials": false
      }
   }
}
```

- `dids[]` — DIDs to subscribe to. **Omit** to subscribe to every DID indexed by this resolver.
- `channels` — Map from channel name to either a boolean (use defaults) or a sub-options object. Channels not listed in the map are excluded from the stream.

A subsequent `subscribe` message replaces the active subscription on the same connection. To stop receiving notifications entirely, send `{ "action": "unsubscribe" }` or close the socket.

###### Block message (server → client)

After the first `subscribe` is acknowledged, the server sends one **block message** per processed block, in strictly increasing order of `block`:

```json
{
   "type": "block",
   "block": 1500005,
   "blockTime": "2026-05-11T13:00:05Z",
   "changes": [
      {
         "did": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
         "trust": {
            "trusted":          true,
            "evaluatedAtTime":  "2026-05-11T13:00:05Z",
            "evaluatedAtBlock": 1500005,
            "expiresAtTime":    "2026-05-12T13:00:05Z",
            "corporationId":    "verana1rw7w9hm0zd7e4jcxsm955nu8l5ju0wtkpssxe5"
         },
         "corporation":    true,
         "participations": true,
         "ecsCredentials": true,
         "presentations":  false,
         "services":       false,
         "ecosystems":     true
      }
   ]
}
```

Semantics:

- `block` — Height of the just-processed block.
- `blockTime` — Wall-clock time the block was committed (ISO 8601).
- `changes[]` — One entry per DID whose subscribed-to state changed at this block. Empty when no subscribed change occurred — the message still acts as a heartbeat.
- `changes[].did` — The DID this envelope refers to.
- `changes[].trust` — Present iff `trust` is in the subscription **and** any trust-core field changed at this block. Carries the new core values inline, with the same shape as the trust-core fields in the [resolution response schema](#resolution-response-schema).
- `changes[].<channel>` — `true` iff the channel is in the subscription **and** changed at this block; `false` otherwise. Clients fetch the new state by calling `/vt/v1/resolve` with `At-Block-Height: <block>`.

###### Block production as ping

Block messages are emitted **for every processed block**, even when `changes[]` is empty. Block production is the heartbeat: a connection that does not deliver a block message within the expected block-time window is presumed broken, and the client SHOULD reconnect and catch up via [`listChanges`](#idx-vt-qry-2).

A subscriber detects a connection-level loss by observing a gap (`block > previousBlock + 1`) in the sequence of received block messages.

###### Backpressure

A subscriber that fails to drain its receive buffer within an indexer-defined window MAY have its connection closed with WebSocket close code `1011` (server error / overloaded). The client SHOULD reconnect and resume via `listChanges`.

##### `listChanges`

**Spec tag:** `IDX-VT-QRY-2` <a id="idx-vt-qry-2"></a>

After a disconnection — or whenever the subscriber detects a gap in the WebSocket sequence — `listChanges` returns the same change envelopes as the WebSocket but compressed: it skips blocks with no subscribed changes, so the client never has to walk every block height.

Request:

```http
GET /vt/v1/changes
  ?fromBlock=<int>
  [&dids=<comma-separated DIDs>]
  [&channels=<comma-separated channel names>]
  [&includeParticipantCounts=true|false]
  [&includeIssuedCredentials=true|false]
  [&includeVerifiedCredentials=true|false]
  [&limit=<int>]
```

`limit` defaults to `100` and MUST NOT exceed `1000`. When `dids` is omitted, the call subscribes-by-query to every indexed DID (same wildcard semantics as the WS `subscribe` with no `dids[]`).

Response:

```json
{
   "currentBlock":   1500300,
   "fromBlock":      1500005,
   "blocks": [
      {
         "block":     1500005,
         "blockTime": "2026-05-11T13:00:05Z",
         "changes":   [ /* same shape as `changes[]` in WS block messages */ ]
      },
      {
         "block":     1500012,
         "blockTime": "2026-05-11T13:01:05Z",
         "changes":   [ /* … */ ]
      }
   ],
   "nextFromBlock":  1500050
}
```

- `currentBlock` — Latest block the indexer has processed at the time of the response.
- `blocks[]` — Up to `limit` consecutive blocks in increasing order that contain at least one change matching the filters. **Blocks with no subscribed changes are omitted entirely.**
- `nextFromBlock` — Smallest block height strictly greater than the last returned block (or strictly greater than `fromBlock` if `blocks` is empty) for which the indexer **knows** further changes exist. `null` when the response has reached `currentBlock`.

Catch-up loop:

```
last_seen = client_last_seen_block
while true:
  r = GET /vt/v1/changes?fromBlock=last_seen+1&...
  apply(r.blocks)
  if r.blocks:
    last_seen = r.blocks[-1].block
  if r.nextFromBlock is null:
    break
  last_seen = max(last_seen, r.nextFromBlock - 1)
```

The `nextFromBlock` cursor lets the client jump over arbitrarily long change-free ranges without making one HTTP call per block.

##### `listIndexedDids`

**Spec tag:** `IDX-VT-QRY-3` <a id="idx-vt-qry-3"></a>

A client that starts with an empty mirror needs a way to enumerate the universe of DIDs the indexer tracks at a frozen snapshot block, then resolve each via `/vt/v1/resolve` to populate its initial state.

Request:

```http
GET /vt/v1/dids
  [?cursor=<opaque string>]
  [&limit=<int>]
At-Block-Height: <int>
```

The snapshot block is selected via the `At-Block-Height` HTTP request header per [Conventions](#at-block-height-header); when omitted, the latest indexed block is used. `limit` defaults to `1000` and MUST NOT exceed `10000`.

Response:

```json
{
   "atBlock": 1500004,
   "dids": [
      "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
      "did:webvh:QmZ8Y3xRkH2pV4qTw9nL7sFmJg6cN5dB1aWxKvE3uPyT8r:corp.acme.example",
      "did:web:ecosystem.eu-passport.example"
   ],
   "nextCursor": "eyJvZmZzZXQiOjEwMDB9"
}
```

- `atBlock` — Echo of the resolved snapshot block (the value of `At-Block-Height` if provided, otherwise the latest indexed block at evaluation time). The "DID universe" at block `B` is the set of DIDs the indexer can resolve at `B`: every Corporation `did`, every Ecosystem `did`, the Corporation-side DID of every Participant entry that is in scope (per the resolver's [participation states](#example-resolution-response)), and any DID previously evaluated by the resolver that the indexer is still tracking.
- `dids[]` — Page of indexed DIDs in stable sort order across pages.
- `nextCursor` — Opaque pagination cursor; `null` (or absent) on the last page.

##### Bootstrap pattern

The recommended initial-sync sequence for a client with an empty mirror:

1. **Connect** to `WS /vt/v1/subscribe`. Read the `ready` message and capture `B = ready.block`.
2. **Subscribe** with the desired `dids` / `channels`. Buffer all incoming block messages **without applying them** until step 5.
3. **Enumerate** the DID universe at block `B - 1` by calling `GET /vt/v1/dids` with header `At-Block-Height: B-1` and paginating through `nextCursor`.
4. **Resolve** each enumerated DID by calling `POST /vt/v1/resolve` with header `At-Block-Height: B-1` and the response selectors the client cares about. Persist the resulting state as the snapshot at block `B - 1`.
5. **Apply** the buffered WebSocket block messages in order (starting at block `B`), then continue applying live block messages as they arrive.

Because the snapshot is taken at the immutable past block `B - 1` and the WebSocket delivers from `B` onwards, no events are lost or double-counted.

##### Resume pattern

After a temporary disconnection, a client with a non-empty mirror resumes by:

1. Recording `last_seen_block` of the most recently applied WebSocket block message.
2. Reconnecting to `WS /vt/v1/subscribe` and re-subscribing as before. Buffer incoming block messages.
3. Running the [`listChanges`](#idx-vt-qry-2) catch-up loop from `fromBlock = last_seen_block + 1` until either `nextFromBlock` is `null` or it has reached the smallest block held in the WebSocket buffer.
4. Applying the buffered WebSocket block messages in order, deduplicated by `block` against anything already applied from `listChanges`.

#### Trust Registry Query Protocol v2 methods

The Verana indexer implements the [Trust Registry Query Protocol v2](https://trustoverip.github.io/tswg-trust-registry-query-protocol/) (TRQP v2.0) so any relying party can ask, in a registry-agnostic way, two complementary questions about a Verana corporation, ecosystem, or schema:

1. **Authorization** — *"Is this `entity_id` authorized by this `authority_id` for this `action` on this `resource`?"*
2. **Recognition** — *"Does this `authority_id` recognize that other authority `entity_id` to be authoritative for this `action` on this `resource`?"*

In Verana v4 both `authority_id` and `entity_id` are normal DIDs — corporations and ecosystems each carry a `did` and a governance framework (CGF and EGF respectively) — so the protocol is fully DID-native.

Both endpoints are pure query views over on-chain VPR state; they are PUBLIC and do not mutate state.

##### Verana TRQP profile

The Verana profile of TRQP v2 is identified by the profile version `verana-trqp/spec-v4`. It freezes the action vocabulary, resource grammar, context extensions, and trigger semantics for both endpoints, summarised below and detailed in the subsections that follow.

| Slot | Value |
| --- | --- |
| Profile version | `verana-trqp/spec-v4` |
| Authorization actions | `issue`, `verify`, `grant_issue`, `grant_verify`, `govern` |
| Recognition actions | same as authorization (action-invariant in v4) |
| Authorization resource grammar | VPR schema URI (`vpr:verana:<network>/cs/v1/js/<n>`) |
| Recognition resource grammar | VPR schema URI |
| Authorization trigger | `Participant.role = role_of(action)` AND `state = "ACTIVE"` |
| Recognition trigger | `Ecosystem.did = entity_id` AND the Corporation referenced by `Ecosystem.corporationId` has `did = authority_id`, AND not archived |
| Recognition scope (v4) | corporation DID → ecosystem DID |
| Context extension | `session_id` (string), precedence `session_id` > `time` |
| Active states | `ACTIVE` |

Request and response payloads use the upstream ToIP TSWG schemas verbatim (see the per-direction subsections below for the canonical URLs). The Verana profile narrows their *interpretation*: it freezes `action` to a closed enum, `resource` to the VPR schema URI grammar, and constrains `authority_id` / `entity_id` to Verana corporation or ecosystem DIDs (see scope rules per endpoint). It also registers `context.session_id` (string) as a profile extension permitted by the upstream `context.additionalProperties` clause, and reserves a top-level `verana` object on responses for VPR-state breadcrumbs (opaque to non-Verana consumers; conformant because upstream does not set `additionalProperties: false`).

The full machine-readable Verana TRQP profile descriptor — including the action → `Participant.role` map, regex patterns, trigger semantics, scope rules, error messages, and discovery URLs — is published at [`schemas/v4/vt/trqp-profile.json`](./schemas/v4/vt/trqp-profile.json) (`$id`: `https://verana.io/schemas/v4/trqp/profile.json`).

Profile discovery. TRQP v2.0 does not standardise a profile-discovery mechanism, but per TRQP v2.0 §Identifiers/`authority_id` and §Conformance the **ecosystem governance framework** — of which this profile forms part — MUST be discoverable via the authority's identifier. Verana implements that requirement as follows:

- A Verana corporation or ecosystem MAY advertise a `TRQPEndpoint` service entry in its DID Document, pointing at the indexer's `/trqp/v2/` base path.
- The indexer MUST serve the profile descriptor at `/trqp/v2/profile` with `Content-Type: application/json`; the body is byte-identical to [`schemas/v4/vt/trqp-profile.json`](./schemas/v4/vt/trqp-profile.json).
- The action vocabulary, resource grammar, trigger semantics, and scope rules in the descriptor MUST match the table above; the descriptor is the canonical machine-readable form, this table is its prose summary.

##### `trqpAuthorize`

**Spec tag:** `IDX-TRQP-QRY-1` <a id="idx-trqp-qry-1"></a>

`POST /trqp/v2/authorization`

Direction: ecosystem → corporation. Derived from `Participant` entries.

###### Action vocabulary

| `action` | Verana `Participant.role` | Wire-level meaning |
| --- | --- | --- |
| `issue` | `ISSUER` | corporation may issue credentials of `resource` schema in `authority` ecosystem |
| `verify` | `VERIFIER` | corporation may verify credentials of `resource` schema |
| `grant_issue` | `ISSUER_GRANTOR` | corporation may grant `issue` to others for `resource` schema |
| `grant_verify` | `VERIFIER_GRANTOR` | corporation may grant `verify` to others for `resource` schema |
| `govern` | `ECOSYSTEM` | corporation holds root governance for the `resource` schema in the `authority` ecosystem |

###### Derivation

TRQP authorization is conceptually a DID-based predicate: `(authority DID, entity DID, action, resource URI, time) → boolean`. The query inputs `E` and `V` are DIDs and `R` is a VPR schema URI; the result is a boolean (plus optional breadcrumbs). Any internal translation from DID to stable Corporation/Ecosystem id, or from URI to stable schema id, is an implementation detail of the indexer; it is not exposed on the TRQP wire.

```
For a query (authority=E, entity=V, action=A, resource=R, time=T):
  active_rows = Participant entries where
                  the Participant's controlling Ecosystem has did = E
                AND the Participant's controlling Corporation has did = V
                AND role       = role_of(A)
                AND schema.uri = R
                AND state      = "ACTIVE"
                AND validAt(T)
  authorized = active_rows is non-empty
```

###### Authorization request schema

Authorization requests use the upstream ToIP TSWG schema [`trqp_authorization_request.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_authorization_request.schema.json) (`$id`: `trqp-authorization-request`) verbatim. Verana-specific narrowing of `action`, `resource`, `authority_id`, `entity_id`, and `context` is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json).

###### Authorization response schema

Authorization responses use the upstream ToIP TSWG schema [`trqp_authorization_response.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_authorization_response.schema.json) (`$id`: `trqp-authorization-response`) verbatim. The Verana profile additionally permits a top-level `verana` object whose shape is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json); the upstream schema does not set `additionalProperties: false`, so this extension is conformant.

###### Example authorization request

*"Does the EU-Passport ecosystem authorize Acme Corp to `issue` schema 42?"*

```json
POST /trqp/v2/authorization
{
   "authority_id": "did:webvh:Qm…:ecosystem.eu-passport.example",
   "entity_id":    "did:webvh:Qm…:corp.acme.example",
   "action":       "issue",
   "resource":     "vpr:verana:vna-mainnet-1/cs/v1/js/42",
   "context":      { "time": "2026-05-11T13:00:00Z" }
}
```

###### Example authorization response

```json
{
   "authority_id":   "did:webvh:Qm…:ecosystem.eu-passport.example",
   "entity_id":      "did:webvh:Qm…:corp.acme.example",
   "action":         "issue",
   "resource":       "vpr:verana:vna-mainnet-1/cs/v1/js/42",
   "authorized":     true,
   "time_requested": "2026-05-11T13:00:00Z",
   "time_evaluated": "2026-05-11T13:00:00Z",
   "verana": {
      "participant_state": "ACTIVE",
      "since":             "2026-04-12T08:00:00Z",
      "deposit":           "10000000uvna"
   }
}
```

##### `trqpRecognize`

**Spec tag:** `IDX-TRQP-QRY-2` <a id="idx-trqp-qry-2"></a>

`POST /trqp/v2/recognition`

Direction: Corporation → Ecosystem. Derived from `Ecosystem` entries — specifically the controlling-Corporation reference each Ecosystem carries (VPR-level `Ecosystem.corporation` group field; surfaced in the graph as `Ecosystem.corporationId`). TRQP itself remains DID-only at the wire level — the `authority_id` (Corporation DID) and `entity_id` (Ecosystem DID) inputs are translated to internal stable ids only inside the indexer when evaluating the predicate. Per-Participant-entry recognition (e.g. ECOSYSTEM-role recognition for individual Credential Schemas, Ecosystem-to-Ecosystem federation, Corporation-to-Corporation peer recognition) is **out of scope for v4**.

###### Action vocabulary

Recognition reuses the authorization action enum (`issue`, `verify`, `grant_issue`, `grant_verify`, `govern`). In v4 the boolean answer is **action-invariant**: a Corporation that controls an Ecosystem is acknowledging that Ecosystem's framework as authoritative for every action governed within the Ecosystem's scope. The `action` argument is preserved on the wire for TRQP conformance and forward compatibility with future per-action recognition semantics.

###### Derivation

TRQP recognition is conceptually a DID-based predicate: `(authority DID, entity DID, action, resource URI, time) → boolean`. The query inputs `V` and `E` are DIDs and `R` is a VPR schema URI; the result is a boolean (plus optional breadcrumbs). Any internal translation from DID to stable Corporation/Ecosystem id, or from URI to stable schema id, is an implementation detail of the indexer; it is not exposed on the TRQP wire.

```
For a query (authority=V, entity=E, action=A, resource=R, time=T):
  ecosystem_row = Ecosystem entry where
                    did = E
                  AND its controlling Corporation has did = V
                  AND archived IS NULL
                  AND validAt(T)
  schema_row    = CredentialSchema entry where
                    uri = R
                  AND schema is owned by ecosystem_row
                  AND validAt(T)
  recognized = (ecosystem_row is non-empty) AND (schema_row is non-empty)
```

In words: V recognizes E for resource R iff (a) V is the Corporation that controls E, AND (b) R is a Credential Schema governed by E.

###### Recognition request schema

Recognition requests use the upstream ToIP TSWG schema [`trqp_recognition_request.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_recognition_request.schema.json) (`$id`: `trqp-recognition-request`) verbatim. Verana-specific narrowing is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json).

###### Recognition response schema

Recognition responses use the upstream ToIP TSWG schema [`trqp_recognition_response.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_recognition_response.schema.json) (`$id`: `trqp-recognition-response`) verbatim. The Verana profile additionally permits a top-level `verana` object whose shape is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json).

###### Example recognition request

*"Does Acme Corp recognize EU-Passport to be authoritative to `issue` schema 42?"*

```json
POST /trqp/v2/recognition
{
   "authority_id": "did:webvh:Qm…:corp.acme.example",
   "entity_id":    "did:webvh:Qm…:ecosystem.eu-passport.example",
   "action":       "issue",
   "resource":     "vpr:verana:vna-mainnet-1/cs/v1/js/42",
   "context":      { "time": "2026-05-11T13:00:00Z" }
}
```

###### Example recognition response

```json
{
   "authority_id":   "did:webvh:Qm…:corp.acme.example",
   "entity_id":      "did:webvh:Qm…:ecosystem.eu-passport.example",
   "action":         "issue",
   "resource":       "vpr:verana:vna-mainnet-1/cs/v1/js/42",
   "recognized":     true,
   "time_requested": "2026-05-11T13:00:00Z",
   "time_evaluated": "2026-05-11T13:00:00Z",
   "verana": {
      "ecosystem_active_egf_version": 7,
      "controlling_since":            "2026-03-01T00:00:00Z"
   }
}
```

###### Out-of-scope queries

If `authority_id` is not the DID of an active Corporation entry, or `entity_id` is not the DID of an active Ecosystem entry, the endpoint MUST return `recognized: false` with an explanatory `message`:

```json
{
   "authority_id":   "<echo>",
   "entity_id":      "<echo>",
   "action":         "<echo>",
   "resource":       "<echo>",
   "recognized":     false,
   "time_evaluated": "2026-05-11T13:00:00Z",
   "message":        "out of v4 recognition scope (corporation → ecosystem only)"
}
```

##### Context: `session_id` extension

Both endpoints accept an optional `context.session_id` extension to bind the answer to a specific [VPR `MOD-PERM-MSG-10`] participant session. When supplied:

> Note: `session_id` is needed in most cases for issuance and verification.

- `session_id` takes precedence over `time`.
- The resolver verifies that `time` (if also given) falls inside the session's validity window; if outside, the answer is `authorized: false` (or `recognized: false`) with `message: "session out of window"`.
- If the session does not exist, the answer is `false` with `message: "session not found"`.

When `session_id` is omitted, the answer is point-in-time per the standard `time` argument; if both are omitted, the answer is computed against the latest block.
