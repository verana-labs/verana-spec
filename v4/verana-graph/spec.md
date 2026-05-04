# Verana Graph v4 Specification

**Latest Draft:** spec v4-draft1

## Abstract

The Verifiable Trust ecosystem publishes its trust topology across many places: DID Documents expose Linked Verifiable Presentations, a Verifiable Public Registry (VPR) records permissions and credential schemas, and trust-resolution clients (such as [verana-indexer](https://github.com/verana-labs/verana-indexer)) compute and cache per-DID `TrustResult`s on demand. Each of these systems answers a narrow question: *"is this specific DID trusted right now?"* None of them answers *"show me every trusted service operated by organization X"* or *"list every Verifiable Service in country DE that exposes an MCP endpoint."*

**Verana Graph** is the conformant implementation of the DID Indexing role anticipated by §2.4 of the VPR specification. It consumes trust-resolution events, distills them into a structured graph of DIDs and their relationships, and exposes the graph through a GraphQL API tailored to discovery use cases for Verifiable User Agents (VUAs), search engines, and analytics.

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
~ A distinct entity in the [[ref: trust graph]]. One of `Did`, `TrustRegistry`, `CredentialSchema`, `Credential`, `ServiceEndpoint`, or `Permission`.

[[def: trust graph edge, edge]]:
~ A directed relationship between two [[ref: nodes]], labelled with a relation type (see [TG-MODEL]).

[[def: trust-resolution event, resolution event]]:
~ A single observation of a DID's trust status at a given block height, carrying the full verified credential set and permission chains. Delivered to Verana Graph via the webhook contract defined in [TG-INGEST].

[[def: architecture pattern, pattern]]:
~ The deployment shape of a [[ref: Verifiable Service]] as defined by [VS-REQ-3] and [VS-REQ-4] of the Verifiable Trust Specification. **Pattern A** denotes self-issuance (the VS is its own ORG/PERSONA); **Pattern B** denotes delegated issuance (a separate ORG/PERSONA DID issues the VS's Service Credential).

## Introduction

### What Verana Graph Is

A persistent, queryable index of the Verifiable Trust ecosystem that:

- **Ingests** trust-resolution events from conformant upstream resolvers via a well-defined webhook contract.
- **Normalizes** those events into a graph of DIDs, credentials, permissions, schemas, and service endpoints.
- **Exposes** the graph via a GraphQL API supporting common discovery queries.
- **Expires** stale data automatically, inheriting the TTL of each upstream resolution event.

### What Verana Graph Is Not

- Not a trust resolver — it does **not** perform verre resolution itself.
- Not an authoritative source — every row is derivable from the VPR and the DID Documents it references.
- Not a write-side system — there is no API to add, modify, or remove graph entries except via the webhook from a trust-resolution source.
- Not a credential wallet or presenter — it does not hold, issue, or re-present credentials.
- Not an on-chain observer — it depends on an upstream indexer+resolver pair for its data feed.

### Relationship to VPR §2.4 (DID Indexing)

The [VPR Specification §2.4](https://verana-labs.github.io/verifiable-trust-vpr-spec/#did-indexing) explicitly anticipates the role Verana Graph fills:

> *The Permission registry can be used by crawlers to index the metadata associated with verifiable services. Search engines can iterate over the permissions, and index VSs by resolving the service identifier (at the moment a DID, that could be extended in the future), verify if service is a verifiable service, and in such a case extracting their verifiable metadata, such as linked-vp presented credentials.*
>
> *The index is particularly important for verifiable user agents, such as social browsers, CDN enabled browsers… However, it can also be leveraged by traditional, form-based search engines, which may return simple links for accessing VSs.*

Verana Graph is the reference implementation of this index. The division of labor is:

- **verana-indexer** tails the chain and emits affected-DID events per block and performs verre trust resolution on each affected DID, producing a `TrustResult`.
- **verana-graph** consumes each resulting `TrustResult` and maintains the searchable graph.

## Architecture

```
                   ┌─────────────────────┐
                   │  VPR                │ (on-chain state)
                   └──────────┬──────────┘
                              ▼
                   ┌─────────────────────┐
                   │  verana-indexer     │ (block stream → affected DIDs)
                   └──────────┬──────────┘
                              ▼
                   ┌─────────────────────┐
                   │  verana-resolver    │ (verre trust resolution)
                   │                     │
                   │  runVerrePass       │
                   │       │             │
                   │       ├─► Postgres  │ (trust_results cache)
                   │       └─► webhook ──┼──┐
                   └─────────────────────┘  │
                                            ▼
                                ┌────────────────────────┐
                                │  verana-graph          │
                                │  ┌──────────────────┐  │
                                │  │ POST /v1/ingest/ │  │
                                │  │   trust-result   │  │
                                │  └────────┬─────────┘  │
                                │           ▼            │
                                │  ┌──────────────────┐  │
                                │  │ Postgres         │  │
                                │  │ (graph schema)   │  │
                                │  └────────┬─────────┘  │
                                │           ▼            │
                                │  ┌──────────────────┐  │
                                │  │ POST /v1/graphql │  │
                                │  └──────────────────┘  │
                                └────────────────────────┘
```

### Design Principles

- **Source of truth lies upstream.** The VPR and DID Documents are authoritative. The graph is an *index* — destroying and rebuilding it MUST be equivalent to a sequence of re-ingestions.
- **Expiration binds to the trust-resolution TTL.** A row's freshness lifetime is the `expiresAt` asserted by the webhook payload. No independent TTL logic in the graph.
- **Last observation wins.** Repeated webhooks for the same DID overwrite earlier observations. History is explicitly out of scope for v0.1 (see [Open Questions](#open-questions)).
- **Graph is strongly typed.** ECS credentials surface with dedicated columns for their canonical attributes (`registryId`, `countryCode`, `name`, etc.). Non-ECS credentials fall back to generic JSONB storage.
- **Trust status gates visibility.** Only DIDs with `trustStatus ∈ {TRUSTED, PARTIAL}` are surfaced by default GraphQL queries. UNTRUSTED webhooks trigger cleanup, not retention.

## Normative Requirements

### [TG-MODEL] Data Model Requirements

- **[TG-MODEL-1]** A Verana Graph implementation MUST expose six node types: `Did`, `TrustRegistry`, `CredentialSchema`, `Credential`, `ServiceEndpoint`, and `Permission`.
- **[TG-MODEL-2]** A Verana Graph implementation MUST expose at least the following edge types between nodes: `ISSUED_CREDENTIAL`, `OPERATES_SERVICE`, `GOVERNS_SCHEMA`, `MEMBER_OF_ECOSYSTEM`, `DECLARES_VTJSC`, `EXPOSES_ENDPOINT`. Additional edge types MAY be exposed.
- **[TG-MODEL-3]** Every node MUST carry a last-observation timestamp (`last_seen_at`) and an expiration timestamp (`expires_at`) derived from the `TrustResult.expiresAt` of the webhook payload that last refreshed it.
- **[TG-MODEL-4]** Every `Did` node MUST record its most recent `trustStatus` and, if applicable per [VS-REQ], its `architecturePattern` (`A` or `B`).

### [TG-PAT] Architecture Pattern Detection

- **[TG-PAT-1]** For a `Did` node that presents a credential conforming to `[VT-ECS-SERVICE-CRED-W3C]`, the implementation MUST compute `architecturePattern` as follows:
  - **Pattern A** when the Service Credential's `issuer` DID equals the `Did` node's DID (self-issued per [VS-REQ-3]).
  - **Pattern B** when the Service Credential's `issuer` DID differs from the `Did` node's DID (delegated per [VS-REQ-4]).
- **[TG-PAT-2]** In Pattern B, the implementation MUST emit an `OPERATES_SERVICE` edge from the issuer DID to the service DID, and MUST mark the issuer DID's role set as including `ORGANIZATION` or `PERSONA` according to which ECS credential the issuer DID Document presents.
- **[TG-PAT-3]** In Pattern A, the implementation MUST NOT emit an `OPERATES_SERVICE` edge. The service DID's own `Did` node carries the ORG/PERSONA role.

### [TG-ING] Ingestion Requirements

- **[TG-ING-1]** A Verana Graph implementation MUST expose a webhook endpoint at `POST /v1/ingest/trust-result` that accepts a JSON body conforming to the `TrustResult` schema defined in [[ref: verana-indexer's `TrustResult` type]]. See [TG-INGEST] for the payload schema.
- **[TG-ING-2]** The endpoint MUST be idempotent: repeated invocations with the same `(did, evaluatedAtBlock)` tuple MUST yield the same graph state.
- **[TG-ING-3]** On receipt of a `TrustResult` with `trustStatus ∈ {TRUSTED, PARTIAL}`, the implementation MUST upsert the corresponding `Did` node with `expires_at = payload.expiresAt` and MUST upsert every referenced `Credential`, `CredentialSchema`, `TrustRegistry`, `ServiceEndpoint`, and incidental `Did` node surfaced in the payload's `credentials[]`, `validPresentations[]`, and `permissionChain[]`.
- **[TG-ING-4]** On receipt of a `TrustResult` with `trustStatus == UNTRUSTED` for a DID that has existing graph entries, the implementation MUST mark the DID node's `last_trust_status = 'UNTRUSTED'` and MUST hide it from default GraphQL queries. Associated edges MAY be retained for audit purposes.
- **[TG-ING-5]** The implementation SHOULD complete ingestion within a reasonable bound (RECOMMENDED: 2 seconds at p99) to allow the upstream indexer to report webhook success without retry.
- **[TG-ING-6]** The implementation MUST expire rows whose `expires_at < NOW()` from default GraphQL query results.

### [TG-QRY] Query Requirements

- **[TG-QRY-1]** A Verana Graph implementation MUST expose a GraphQL endpoint at `POST /v1/graphql` and a GET introspection endpoint at `GET /v1/graphql/schema`.
- **[TG-QRY-2]** The schema MUST conform to the canonical schema defined in [TG-GRAPHQL].
- **[TG-QRY-3]** All GraphQL queries MUST filter out DIDs, credentials, and edges whose `expires_at < NOW()` by default. Explicit inclusion of expired rows MAY be supported via a per-query flag.
- **[TG-QRY-4]** The GraphQL schema MUST support additive evolution: new fields and types MAY be added without bumping the API version. Breaking changes MUST bump the path prefix (`/v2/graphql`, …).

### [TG-SEARCH] Search Requirements

- **[TG-SEARCH-1]** A Verana Graph implementation MUST expose a free-text search query that returns services (DIDs holding a TRUSTED `ECS-SERVICE` credential). The query MUST consider matches against `ECS-SERVICE`, `ECS-ORG`, and `ECS-PERSONA` credential attributes.
- **[TG-SEARCH-2]** A service S held by DID-X MUST be returned when EITHER:
  - any TRUSTED ECS credential (`ECS-SERVICE`, `ECS-ORG`, or `ECS-PERSONA`) held by DID-X matches the query text, OR
  - any TRUSTED `ECS-ORG` or `ECS-PERSONA` credential held by S's issuer DID (the Pattern B parent) matches the query text.

  *Trust propagation note:* per [TG-SEARCH-1] and [TG-SEARCH-6], S only appears when DID-X is currently TRUSTED. In Pattern B this transitively requires S's issuer DID to be currently TRUSTED — an UNTRUSTED parent makes its child VS UNTRUSTED per [VS-REQ-4] of the Verifiable Trust Specification, and the upstream resolver MUST have already filtered such services out. The graph therefore performs no extra issuer-trust check at search time; it relies on this upstream invariant. As a consequence, a service whose parent ORG/PERSONA was never independently resolved cannot be TRUSTED, will not appear in search, and need not be matched on the parent's name.
- **[TG-SEARCH-3]** Each result MUST include a `badges` array. The implementation MUST include:
  - `ORGANIZATION` iff DID-X itself holds a currently-valid TRUSTED `ECS-ORG` credential (Pattern A).
  - `PERSONA` iff DID-X itself holds a currently-valid TRUSTED `ECS-PERSONA` credential (Pattern A).
  - `TRUST_REGISTRY` iff there exists a currently-valid `TrustRegistry` row whose `ecosystem_did` equals DID-X.
  Implementations MAY add additional badge values; the defined values MUST retain these semantics. In particular, a Pattern B service MUST NOT earn an `ORGANIZATION` badge from its parent organization alone — the badge reflects only self-presented ECS credentials.
- **[TG-SEARCH-4]** Multi-word queries MUST be treated as conjunction: every word MUST appear in a matched attribution. Phrase queries delimited by double quotes SHOULD be treated as adjacency (the words appearing in order, next to each other).
- **[TG-SEARCH-5]** Prefix, substring, and typo-tolerant matching (for example via `pg_trgm` trigram similarity) is RECOMMENDED. A minimal implementation MAY support only whole-word matching via PostgreSQL full-text search (`tsvector` + `websearch_to_tsquery`).
- **[TG-SEARCH-6]** Results MUST be filtered by [TG-QRY-3]: expired credentials, expired DID observations, and DIDs with `trust_status = 'UNTRUSTED'` MUST NOT contribute matches or populate badges. A DID with `trust_status = 'PARTIAL'` contributes only those of its credentials whose own result is `VALID`.
- **[TG-SEARCH-7]** When a DID holds multiple currently-valid ECS credentials of the same `ecs_type` (e.g., two `ECS-ORG` credentials issued under different trust registries), the implementation MAY select any one of them as the representative for:
  - badge predicate evaluation in [TG-SEARCH-3];
  - population of `Did.organization` and `Did.persona` in the GraphQL schema;
  - the `Service.provider.organization` / `Service.provider.persona` chain on Pattern B results.

  The selection SHOULD be deterministic given the same inputs. RECOMMENDED tie-breaker: the credential with the most recent `issued_at`; on ties, the lexicographically-smallest credential `id`. Implementations MAY surface only the chosen representative; they MAY also expose the alternates via an explicit field, but this is not required for v0.1.

### [TG-SEC] Security Requirements

- **[TG-SEC-1]** The webhook ingestion endpoint is unauthenticated. Operators MUST restrict its reachability via network-level controls (private network, Kubernetes `NetworkPolicy`, firewall rules, or equivalent) so that only the upstream indexer can deliver to it. Public exposure is NOT RECOMMENDED. Because the graph's contents are independently verifiable against the VPR, a forged webhook produces, at worst, transient stale rows that are corrected on the next genuine resolution event.

::: note
The graph stores only information that is already publicly verifiable: DID Documents, VPR entries, and credentials presented as Linked Verifiable Presentations. The GraphQL query surface is therefore unauthenticated by design — it is, in effect, a search index over public data — and there is no special handling required for logging of webhook payloads.
:::

## Data Model

### Node Types

#### `Did`

The central node representing any DID observed by the graph — VSs, organizations, personas, user agents, and ecosystems.

| Field | Type | Notes |
|---|---|---|
| `did` | `string` (PK) | The DID URI. |
| `first_seen_at` | `timestamp` | When the graph first observed this DID. |
| `last_seen_at` | `timestamp` | When the last webhook touched this DID. |
| `expires_at` | `timestamp` | From the webhook payload's `TrustResult.expiresAt`. |
| `last_trust_status` | `enum` | `TRUSTED` \| `PARTIAL` \| `UNTRUSTED`. |
| `roles[]` | `enum[]` | Any of `SERVICE`, `ORGANIZATION`, `PERSONA`, `ECOSYSTEM`, `ISSUER_GRANTOR`, `ISSUER`, `VERIFIER_GRANTOR`, `VERIFIER`. Accumulated across observations. |
| `architecture_pattern` | `enum` | `A` \| `B` \| `null`. Only set when the DID presents an ECS-SERVICE credential. |

#### `TrustRegistry`

A VPR trust registry. Conceptually 1:1 with an Ecosystem DID, but modeled separately so registry metadata (language, active version) can be queried independently.

| Field | Type | Notes |
|---|---|---|
| `tr_id` | `string` (PK) | The VPR trust registry identifier. |
| `ecosystem_did` | `string` (FK → `dids.did`) | The Ecosystem DID controlling this TR. |
| `controller` | `string` | Per VPR `TrustRegistry.controller`. |
| `language` | `string` | BCP 47 language tag. |
| `active_version` | `int` | Active governance framework version. |
| `last_seen_at`, `expires_at` | `timestamp` | Per [TG-MODEL-3]. |

#### `CredentialSchema`

A VPR credential schema entry. Keyed by `(tr_id, schema_id)`.

| Field | Type | Notes |
|---|---|---|
| `tr_id`, `schema_id` | `string, int` (composite PK) | |
| `ecs_type` | `enum` | `ECS-SERVICE` \| `ECS-ORG` \| `ECS-PERSONA` \| `ECS-UA` \| `null` for non-ECS. |
| `json_schema_url` | `string` | URL of the `VT-JSON-SCHEMA-CRED-W3C` declaration. |
| `digest_sri` | `string` | SRI of the schema document. |
| `issuer_onboarding_mode` | `enum` | `OPEN` \| `ECOSYSTEM_VALIDATION_PROCESS` \| `GRANTOR_VALIDATION_PROCESS`. |
| `verifier_onboarding_mode` | `enum` | Same. |
| `holder_onboarding_mode` | `enum` | `ISSUER_VALIDATION_PROCESS` \| `PERMISSIONLESS`. |
| `last_seen_at`, `expires_at` | `timestamp` | |

#### `Credential`

An observed Verifiable Trust Credential. Covers both W3C VTCs (`format = 'W3C_VTC'`) and Ecosystem-issued VTJSCs (`format = 'W3C_VTJSC'`). AnonCreds credentials (e.g., ECS-UA) are out of scope for v0.1.

| Field | Type | Notes |
|---|---|---|
| `id` | `string` (PK) | Credential ID (DID URL or `urn:uuid:…`). |
| `holder_did` | `string` (FK → `dids.did`) | From `credentialSubject.id`. |
| `issuer_did` | `string` (FK → `dids.did`) | From `issuer`. |
| `tr_id`, `schema_id` | `string, int` (FK → `credential_schemas`) | Nullable for non-VPR schemas. |
| `ecs_type` | `enum` | Denormalized from schema for query performance. |
| `format` | `enum` | `W3C_VTC` \| `W3C_VTJSC`. |
| `vp_url` | `string` | `serviceEndpoint` of the linked-vp that carried this credential. |
| `vp_service_id` | `string` | The DID URL fragment identifying the VP in the holder's DID Document. |
| `issued_at` | `timestamp` | |
| `valid_until` | `timestamp` | |
| `digest_sri` | `string` | |
| **ECS-SERVICE extension** | | Stored as dedicated columns when `ecs_type = 'ECS-SERVICE'`: |
| `svc_name`, `svc_type`, `svc_description`, `svc_description_format`, `svc_minimum_age_required`, `svc_terms_and_conditions`, `svc_terms_and_conditions_digest_sri`, `svc_privacy_policy`, `svc_privacy_policy_digest_sri` | (various) | Per [ECS-SERVICE] |
| **ECS-ORG extension** | | When `ecs_type = 'ECS-ORG'`: |
| `org_name`, `org_registry_id`, `org_registry_uri`, `org_address`, `org_country_code`, `org_legal_jurisdiction`, `org_organization_kind`, `org_lei` | (various) | Per [ECS-ORG] |
| **ECS-PERSONA extension** | | When `ecs_type = 'ECS-PERSONA'`: |
| `persona_name`, `persona_description`, `persona_description_format`, `persona_controller_country_code`, `persona_controller_jurisdiction` | (various) | Per [ECS-PERSONA] |
| `claims_raw` | `jsonb` | Fallback storage of the full `credentialSubject` object for forward-compat. |
| `last_seen_at`, `expires_at` | `timestamp` | |

#### `ServiceEndpoint`

A non-`LinkedVerifiablePresentation` service entry in a DID Document (DIDComm, MCP, A2A, LinkedDomains, or any custom type). Keyed by `(did, service_id)`.

| Field | Type | Notes |
|---|---|---|
| `did` | `string` (FK → `dids.did`) | |
| `service_id` | `string` | The `#fragment` of the DID service entry. |
| `service_type` | `string` | `DIDCommMessaging` \| `MCP` \| `A2A` \| `LinkedDomains` \| ecosystem-defined. |
| `service_endpoint_uri` | `string` | |
| `service_endpoint_raw` | `jsonb` | Full `serviceEndpoint` object (DIDComm has a composite shape). |
| `last_seen_at`, `expires_at` | `timestamp` | |

**Source dependency:** Populating `ServiceEndpoint` requires the upstream resolver to expose non-LinkedVP service entries in its `TrustResult`. See [Upstream Dependencies](#upstream-dependencies).

#### `Permission` (v0.2, non-normative for v0.1)

A row mirrored from the VPR `Permission` registry. Included here for completeness; implementations MAY omit in v0.1.

### Edge Types

Edges are stored in a single `did_relations` table with a `relation_type` discriminator. All edges carry `observed_at`, `last_seen_at`, and `expires_at`.

| `relation_type` | `from_did` | `to_did` | Payload source | Emitted by |
|---|---|---|---|---|
| `ISSUED_CREDENTIAL` | issuer | holder | `credentials[].issuer` / `credentials[].holder` | One per credential in `TrustResult.credentials` |
| `OPERATES_SERVICE` | provider ORG/PERSONA | VS | `service.issuer !== did` detection | One per Pattern B resolution |
| `GOVERNS_SCHEMA` | ecosystem | schema | `TrustRegistry.ecosystem_did` → schema | One per schema observed |
| `MEMBER_OF_ECOSYSTEM` | participant | ecosystem | Terminal of `permissionChain[]` | One per unique (participant, ecosystem) pair |
| `DECLARES_VTJSC` | ecosystem | VTJSC credential | `credentials[].format === 'W3C_VTJSC'` + issuer is an ECOSYSTEM DID | One per VTJSC |
| `EXPOSES_ENDPOINT` | did | service endpoint | DID Document non-LinkedVP service entries | One per endpoint |

## Storage Schema

Postgres DDL. All timestamps are `TIMESTAMPTZ`. All DIDs are `TEXT` (variable length; max 2048 chars per ECS schemas).

```sql
-- Node: Did
CREATE TABLE dids (
  did                   TEXT PRIMARY KEY,
  first_seen_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at            TIMESTAMPTZ,
  last_trust_status     TEXT CHECK (last_trust_status IN ('TRUSTED','PARTIAL','UNTRUSTED')),
  roles                 TEXT[] NOT NULL DEFAULT '{}',
  architecture_pattern  TEXT CHECK (architecture_pattern IN ('A','B'))
);
CREATE INDEX dids_trust_status_idx     ON dids(last_trust_status);
CREATE INDEX dids_roles_gin_idx        ON dids USING gin (roles);
CREATE INDEX dids_architecture_idx     ON dids(architecture_pattern);
CREATE INDEX dids_expires_at_idx       ON dids(expires_at);

-- Node: TrustRegistry
CREATE TABLE trust_registries (
  tr_id          TEXT PRIMARY KEY,
  ecosystem_did  TEXT NOT NULL REFERENCES dids(did),
  controller     TEXT,
  language       TEXT,
  active_version INT,
  last_seen_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at     TIMESTAMPTZ
);

-- Node: CredentialSchema
CREATE TABLE credential_schemas (
  tr_id                     TEXT NOT NULL,
  schema_id                 BIGINT NOT NULL,
  ecosystem_did             TEXT NOT NULL REFERENCES dids(did),
  ecs_type                  TEXT CHECK (ecs_type IN ('ECS-SERVICE','ECS-ORG','ECS-PERSONA','ECS-UA')),
  json_schema_url           TEXT,
  digest_sri                TEXT,
  issuer_onboarding_mode    TEXT,
  verifier_onboarding_mode  TEXT,
  holder_onboarding_mode    TEXT,
  last_seen_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at                TIMESTAMPTZ,
  PRIMARY KEY (tr_id, schema_id),
  FOREIGN KEY (tr_id) REFERENCES trust_registries(tr_id)
);
CREATE INDEX credential_schemas_ecs_type_idx ON credential_schemas(ecs_type);

-- Node: Credential
CREATE TABLE credentials (
  id                             TEXT PRIMARY KEY,
  holder_did                     TEXT NOT NULL REFERENCES dids(did),
  issuer_did                     TEXT NOT NULL REFERENCES dids(did),
  tr_id                          TEXT,
  schema_id                      BIGINT,
  ecs_type                       TEXT,
  format                         TEXT NOT NULL CHECK (format IN ('W3C_VTC','W3C_VTJSC')),
  vp_url                         TEXT,
  vp_service_id                  TEXT,
  issued_at                      TIMESTAMPTZ,
  valid_until                    TIMESTAMPTZ,
  digest_sri                     TEXT,
  -- ECS-SERVICE columns
  svc_name                       TEXT,
  svc_type                       TEXT,
  svc_description                TEXT,
  svc_description_format         TEXT,
  svc_minimum_age_required       SMALLINT,
  svc_terms_and_conditions       TEXT,
  svc_terms_and_conditions_digest_sri TEXT,
  svc_privacy_policy             TEXT,
  svc_privacy_policy_digest_sri  TEXT,
  -- ECS-ORG columns
  org_name                       TEXT,
  org_registry_id                TEXT,
  org_registry_uri               TEXT,
  org_address                    TEXT,
  org_country_code               CHAR(2),
  org_legal_jurisdiction         TEXT,
  org_organization_kind          TEXT,
  org_lei                        CHAR(20),
  -- ECS-PERSONA columns
  persona_name                   TEXT,
  persona_description            TEXT,
  persona_description_format     TEXT,
  persona_controller_country_code CHAR(2),
  persona_controller_jurisdiction TEXT,
  -- Fallback
  claims_raw                     JSONB NOT NULL,
  last_seen_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at                     TIMESTAMPTZ,
  FOREIGN KEY (tr_id, schema_id) REFERENCES credential_schemas(tr_id, schema_id)
);
CREATE INDEX credentials_holder_idx            ON credentials(holder_did);
CREATE INDEX credentials_issuer_idx            ON credentials(issuer_did);
CREATE INDEX credentials_schema_idx            ON credentials(tr_id, schema_id);
CREATE INDEX credentials_ecs_type_idx          ON credentials(ecs_type);
CREATE INDEX credentials_org_registry_id_idx   ON credentials(org_registry_id)         WHERE ecs_type = 'ECS-ORG';
CREATE INDEX credentials_org_country_code_idx  ON credentials(org_country_code)        WHERE ecs_type = 'ECS-ORG';
CREATE INDEX credentials_org_lei_idx           ON credentials(org_lei)                 WHERE ecs_type = 'ECS-ORG' AND org_lei IS NOT NULL;
CREATE INDEX credentials_svc_name_trgm_idx     ON credentials USING gin (svc_name gin_trgm_ops) WHERE ecs_type = 'ECS-SERVICE';
CREATE INDEX credentials_expires_at_idx        ON credentials(expires_at);

-- Node: ServiceEndpoint
CREATE TABLE service_endpoints (
  did                    TEXT NOT NULL REFERENCES dids(did),
  service_id             TEXT NOT NULL,
  service_type           TEXT NOT NULL,
  service_endpoint_uri   TEXT,
  service_endpoint_raw   JSONB,
  last_seen_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at             TIMESTAMPTZ,
  PRIMARY KEY (did, service_id)
);
CREATE INDEX service_endpoints_type_idx ON service_endpoints(service_type);
CREATE INDEX service_endpoints_did_idx  ON service_endpoints(did);

-- Search attributions
-- Denormalized searchable text, one row per (DID, ECS credential held by that DID).
-- Rebuilt on every webhook ingestion for the affected DIDs (delete-then-insert
-- keyed on `did`). Powers [TG-SEARCH]; the search join follows:
--   matched DID  →  services where service.holder_did = matched OR service.issuer_did = matched.
-- This single rule covers Pattern A (holder match) and Pattern B (issuer match
-- on the parent ORG/PERSONA).
CREATE TABLE did_search_attributions (
  did                    TEXT NOT NULL REFERENCES dids(did) ON DELETE CASCADE,
  source_credential_id   TEXT NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
  source_ecs_type        TEXT NOT NULL CHECK (source_ecs_type IN ('ECS-SERVICE','ECS-ORG','ECS-PERSONA')),
  text                   TEXT NOT NULL,
  text_tsv               TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED,
  last_seen_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at             TIMESTAMPTZ,
  PRIMARY KEY (did, source_credential_id)
);
CREATE INDEX did_search_attributions_tsv_idx  ON did_search_attributions USING gin (text_tsv);
CREATE INDEX did_search_attributions_trgm_idx ON did_search_attributions USING gin (text gin_trgm_ops);
CREATE INDEX did_search_attributions_exp_idx  ON did_search_attributions(expires_at);

-- Edges
CREATE TABLE did_relations (
  id              BIGSERIAL PRIMARY KEY,
  from_did        TEXT NOT NULL REFERENCES dids(did),
  to_did          TEXT NOT NULL REFERENCES dids(did),
  relation_type   TEXT NOT NULL CHECK (relation_type IN (
                    'ISSUED_CREDENTIAL','OPERATES_SERVICE','GOVERNS_SCHEMA',
                    'MEMBER_OF_ECOSYSTEM','DECLARES_VTJSC','EXPOSES_ENDPOINT')),
  credential_id   TEXT REFERENCES credentials(id),
  metadata        JSONB,
  observed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at      TIMESTAMPTZ,
  UNIQUE (from_did, to_did, relation_type, COALESCE(credential_id, ''))
);
CREATE INDEX did_relations_from_idx ON did_relations(from_did, relation_type);
CREATE INDEX did_relations_to_idx   ON did_relations(to_did,   relation_type);
CREATE INDEX did_relations_cred_idx ON did_relations(credential_id);

-- Extensions required
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## [TG-INGEST] Webhook Contract

### Endpoint

```http
POST /v1/ingest/trust-result
Content-Type: application/json
```

The endpoint is unauthenticated. Operators MUST restrict reachability at the network layer (see [TG-SEC-1]).

### Payload Schema

The request body is the exact JSON of a verana-resolver `TrustResult` with `detail=full`. Canonical fields:

```json
{
  "did": "did:webvh:Qm…:github-agent.vs.hologram.zone",
  "trustStatus": "TRUSTED",
  "production": true,
  "evaluatedAt": "2026-04-29T05:00:00.000Z",
  "evaluatedAtBlock": 123456,
  "expiresAt": "2026-04-29T06:00:00.000Z",
  "credentials": [
    {
      "ecsType": "ECS-SERVICE",
      "id": "urn:uuid:...",
      "result": "VALID",
      "issuedBy": "did:webvh:...",
      "presentedBy": "did:webvh:...",
      "claims": { "name": "...", "type": "...", "...": "..." },
      "permissionChain": [
        { "permissionType": "ISSUER", "did": "did:webvh:...", "organizationName": "...", "trustDeposit": "100" },
        { "permissionType": "ECOSYSTEM", "did": "did:webvh:..." }
      ]
    }
  ],
  "validPresentations": [
    {
      "id": "https://.../service-vtc-vp.json",
      "serviceId": "did:webvh:...#vpr-schemas-service-c-vp",
      "credentialIds": ["urn:uuid:..."],
      "presentationType": "vtc"
    }
  ],
  "invalidPresentations": [],
  "failedCredentials": [],
  "dereferenceErrors": [],
  "serviceEndpoints": [
    { "id": "...#didcomm",       "type": "DIDCommMessaging", "serviceEndpoint": { "uri": "...", "accept": ["didcomm/v2"] } },
    { "id": "...#mcp",           "type": "MCP",              "serviceEndpoint": "https://.../mcp" },
    { "id": "...#website",       "type": "LinkedDomains",    "serviceEndpoint": "https://..." }
  ]
}
```

**Note:** The `serviceEndpoints[]` field is NEW and depends on an upstream resolver change. See [Upstream Dependencies](#upstream-dependencies).

### Response

| Status | When |
|---|---|
| `200 OK` | Ingestion succeeded and graph is updated. |
| `202 Accepted` | Request accepted for asynchronous processing (implementation-defined). |
| `400 Bad Request` | Payload failed schema validation. Body: `{ "error": "...", "details": [...] }`. |
| `409 Conflict` | Duplicate `(did, evaluatedAtBlock)` already fully ingested. RECOMMENDED treated as success by the sender. |
| `500 Internal Server Error` | Unexpected failure. Sender SHOULD retry. |

### Retry Policy (sender side)

- At-least-once delivery with exponential backoff.
- RECOMMENDED: 3 retries with delays of 1s, 5s, 30s.
- After exhaustion, the event is dropped — the graph will re-ingest on the next resolution of the same DID.

### Idempotency

The pair `(did, evaluatedAtBlock)` is the canonical idempotency key. Implementations MUST accept repeated deliveries of the same key without producing duplicate rows or inconsistent graph states.

## [TG-GRAPHQL] GraphQL Contract

Endpoint: `POST /v1/graphql` (JSON body `{ query, variables }`).
Schema introspection: `GET /v1/graphql/schema` returns the current SDL.

### Canonical Schema (v0.1)

```graphql
scalar DateTime
scalar JSON

enum TrustStatus { TRUSTED PARTIAL UNTRUSTED }
enum ArchitecturePattern { A B }
enum DidRole { SERVICE ORGANIZATION PERSONA ECOSYSTEM ISSUER_GRANTOR ISSUER VERIFIER_GRANTOR VERIFIER }
enum EcsType { ECS_SERVICE ECS_ORG ECS_PERSONA }
enum CredentialFormat { W3C_VTC W3C_VTJSC }
enum ServiceBadge { ORGANIZATION PERSONA TRUST_REGISTRY }

type Query {
  did(did: ID!): Did
  dids(filter: DidFilter, limit: Int = 50, offset: Int = 0): [Did!]!

  organizationByRegistryId(registryId: String!, countryCode: String): Did
  organizationByLei(lei: String!): Did

  service(did: ID!): Service
  servicesBySchema(trId: String!, schemaId: Int!, limit: Int = 50, offset: Int = 0): [Service!]!
  servicesByOrganizationRegistryId(registryId: String!): [Service!]!
  servicesByCountryCode(countryCode: String!, limit: Int = 50): [Service!]!
  searchServices(text: String!, filter: SearchServicesFilter, limit: Int = 20, offset: Int = 0): SearchServicesPage!

  credentialSchema(trId: String!, schemaId: Int!): CredentialSchema
  trustRegistry(trId: String!): TrustRegistry
  ecosystem(did: ID!): Did
}

input DidFilter {
  trustStatus: [TrustStatus!]
  roles: [DidRole!]
  architecturePattern: ArchitecturePattern
  hasEndpointType: String
  countryCode: String
}

input SearchServicesFilter {
  countryCode: String        # filters on ECS-ORG.country_code / ECS-PERSONA.controller_country_code
  endpointType: String       # filters services that expose at least one endpoint of this type
  ecsServiceType: String     # filters on ECS-SERVICE.type
  includeBadges: [ServiceBadge!]  # if set, result MUST carry ALL listed badges
}

type Did {
  did: ID!
  trustStatus: TrustStatus
  roles: [DidRole!]!
  architecturePattern: ArchitecturePattern
  firstSeenAt: DateTime!
  lastSeenAt: DateTime!
  expiresAt: DateTime

  service: Service                    # ECS-SERVICE credential presented by this DID
  organization: Organization          # ECS-ORG credential presented by this DID
  persona: Persona                    # ECS-PERSONA credential presented by this DID

  presentedCredentials: [Credential!]!
  issuedCredentials: [Credential!]!
  serviceEndpoints: [ServiceEndpoint!]!

  # Edges
  issuers: [Did!]!                    # DIDs that have issued a credential to this DID
  provider: Did                       # Pattern B: ORG/PERSONA DID that issued our SERVICE credential
  servicesProvided: [Service!]!       # Pattern B: services whose SERVICE credential this DID issued
  ecosystem: Did                      # Terminal of permission chain
}

interface Credential {
  id: ID!
  holder: Did!
  issuer: Did!
  format: CredentialFormat!
  schema: CredentialSchema
  ecsType: EcsType
  issuedAt: DateTime
  validUntil: DateTime
  claimsRaw: JSON!
  vpUrl: String
  vpServiceId: String
}

type Service implements Credential {
  id: ID!
  holder: Did!
  issuer: Did!
  format: CredentialFormat!
  schema: CredentialSchema
  ecsType: EcsType
  issuedAt: DateTime
  validUntil: DateTime
  claimsRaw: JSON!
  vpUrl: String
  vpServiceId: String

  # ECS-SERVICE columns
  name: String!
  type: String!
  description: String
  descriptionFormat: String
  minimumAgeRequired: Int
  termsAndConditions: String
  privacyPolicy: String

  provider: Did!                      # holder in Pattern A, external DID in Pattern B
  endpoints: [ServiceEndpoint!]!      # consumable endpoints on the holder DID
}

type Organization implements Credential {
  id: ID!
  holder: Did!
  issuer: Did!
  format: CredentialFormat!
  schema: CredentialSchema
  ecsType: EcsType
  issuedAt: DateTime
  validUntil: DateTime
  claimsRaw: JSON!
  vpUrl: String
  vpServiceId: String

  # ECS-ORG columns
  name: String!
  registryId: String!
  registryUri: String
  address: String!
  countryCode: String!
  legalJurisdiction: String
  organizationKind: String
  lei: String

  servicesProvided: [Service!]!       # Pattern B convenience
}

type Persona implements Credential {
  id: ID!
  holder: Did!
  issuer: Did!
  format: CredentialFormat!
  schema: CredentialSchema
  ecsType: EcsType
  issuedAt: DateTime
  validUntil: DateTime
  claimsRaw: JSON!
  vpUrl: String
  vpServiceId: String

  # ECS-PERSONA columns
  name: String!
  description: String
  descriptionFormat: String
  controllerCountryCode: String!
  controllerJurisdiction: String
}

type CredentialSchema {
  trId: String!
  schemaId: Int!
  ecosystem: Did!
  ecsType: EcsType
  jsonSchemaUrl: String
  digestSri: String
  issuerOnboardingMode: String
  verifierOnboardingMode: String
  holderOnboardingMode: String

  # Derived
  credentials(limit: Int = 50): [Credential!]!
  issuers: [Did!]!                    # DIDs that have issued credentials under this schema
}

type ServiceEndpoint {
  did: Did!
  serviceId: String!
  serviceType: String!
  serviceEndpointUri: String
  serviceEndpointRaw: JSON
}

type TrustRegistry {
  trId: String!
  ecosystem: Did!
  controller: String
  language: String
  activeVersion: Int
  schemas: [CredentialSchema!]!
}

# ─── Search ────────────────────────────────────────────────────────────────

type SearchServicesPage {
  results: [ServiceSearchResult!]!
  totalCount: Int!
}

type ServiceSearchResult {
  service: Service!
  pattern: ArchitecturePattern!      # A (self-issued) | B (delegated)
  badges: [ServiceBadge!]!           # per [TG-SEARCH-3]
  matchedOn: [SearchMatch!]!         # which DID / credential / field triggered the match
  rank: Float!                       # opaque, monotonic; higher = better match
}

type SearchMatch {
  did: Did!                          # DID whose attribution matched (= service holder in Pattern A; = parent ORG/PERSONA in Pattern B)
  ecsType: EcsType!                  # ECS_SERVICE | ECS_ORG | ECS_PERSONA
  field: String!                     # e.g. "svc_name", "org_name", "persona_description"
  excerpt: String                    # ts_headline-style snippet with the matched span highlighted
}
```

### Example Queries

**"Search-engine UX: free-text query returns ranked services with badges":**

```graphql
query SearchServices {
  searchServices(text: "plumber berlin", limit: 10) {
    totalCount
    results {
      rank
      pattern               # A or B
      badges                # [ORGANIZATION, PERSONA, TRUST_REGISTRY]
      service {
        name
        type
        description
        holder { did, trustStatus }
        provider {          # In Pattern B this is the parent ORG/PERSONA;
          did               # in Pattern A this equals holder.
          organization { name, countryCode }
          persona          { name, controllerCountryCode }
        }
        endpoints { serviceType, serviceEndpointUri }
      }
      matchedOn {            # Explainability: why did this service match?
        did                  # ← may differ from service.holder in Pattern B
        ecsType              # ECS_SERVICE | ECS_ORG | ECS_PERSONA
        field                # "svc_name" | "org_name" | "persona_description" | …
        excerpt              # "<b>Plumber</b> Booking in <b>Berlin</b>"
      }
    }
  }
}
```

*Interpretation of results:*

- A result with `pattern: A, badges: [ORGANIZATION]` → the service DID self-presents an ECS-ORG; the service is operated by an organization that is itself the service.
- A result with `pattern: B, badges: []` → the service DID is a pure VS; its `provider.organization.name` identifies the parent (who holds the ORG credential, and whose name may have been what actually matched the query).
- A result with `badges: [TRUST_REGISTRY, ORGANIZATION]` → the service DID is also an Ecosystem DID running a Trust Registry (edge case, e.g. an issuance portal operated by the ecosystem itself).

**"Services of organization with registryId ABC-123":**

```graphql
query ServicesByOrg {
  organizationByRegistryId(registryId: "ABC-123") {
    did
    organization {
      name
      countryCode
      legalJurisdiction
    }
    servicesProvided {
      holder { did, trustStatus }
      name
      type
      description
      endpoints { serviceType, serviceEndpointUri }
    }
  }
}
```

**"Services presenting a credential of schema `vpr:verana:vna-testnet-1/cs/v1/js/168`":**

```graphql
query ServicesBySchema {
  servicesBySchema(trId: "vpr:verana:vna-testnet-1", schemaId: 168) {
    holder { did }
    name
    type
    provider {
      did
      organization { name, countryCode }
    }
    schema { trId, schemaId, ecsType }
  }
}
```

**"All trusted services in country DE that expose an MCP endpoint":**

```graphql
query TrustedDEMcpServices {
  dids(filter: { trustStatus: [TRUSTED], hasEndpointType: "MCP", countryCode: "DE" }) {
    did
    service { name, type, description }
    serviceEndpoints(filter: { serviceType: "MCP" }) { serviceEndpointUri }
  }
}
```

**"Full trust path for a DID (who vouches for it?)":**

```graphql
query TrustPath {
  did(did: "did:webvh:Qm…:github-agent.vs.hologram.zone") {
    trustStatus
    architecturePattern
    organization { name }
    provider { did, organization { name } }
    ecosystem { did, organization { name } }
  }
}
```

## Operations

### Bootstrapping

On cold start, verana-graph has no entries. Three non-exclusive options:

1. **On-demand** (RECOMMENDED v0.1) — new DIDs arrive naturally via the webhook as the upstream resolver performs its next pass. No cold-start procedure required; the graph stabilizes over one resolver-pass cycle.
2. **Backfill endpoint** — verana-resolver exposes `POST /v1/admin/backfill-graph` which iterates its `trust_results` table and re-emits webhooks. RECOMMENDED for v0.2.
3. **Replay log** — persist inbound webhook payloads to disk; allow graph rebuild by replay. Out of scope for v0.1.

### Expiration

- Every `dids`, `credentials`, `service_endpoints`, and `did_relations` row carries an `expires_at` sourced from the webhook's `TrustResult.expiresAt`.
- Default GraphQL resolvers filter `WHERE expires_at > NOW()`.
- A background janitor MAY hard-delete rows where `expires_at < NOW() - interval '7 days'` to keep the graph compact. Non-normative.

### Observability

Implementations SHOULD expose Prometheus metrics at `GET /metrics`:

- `verana_graph_webhook_received_total{status}` — counter
- `verana_graph_webhook_processing_duration_seconds` — histogram
- `verana_graph_graphql_queries_total{operation}` — counter
- `verana_graph_graphql_query_duration_seconds` — histogram
- `verana_graph_rows{table}` — gauge
- `verana_graph_expired_rows{table}` — gauge

Health probe: `GET /health` returning `{ "status": "ok", "postgres": "connected", "webhookLastSeen": "..." }`.

### Deployment

- Container-based (Docker). A published image at `ghcr.io/verana-labs/verana-graph:vX.Y.Z` is RECOMMENDED.
- Helm chart at `charts/verana-graph` following the same conventions as verana-resolver.
- Required environment:
  - `DATABASE_URL` — Postgres connection string.
  - `PORT` — default `3400`.
- Optional: `LOG_LEVEL`, `METRICS_ENABLED`, `GRAPHQL_MAX_DEPTH`, `GRAPHQL_MAX_COMPLEXITY`.

## Upstream Dependencies

Verana Graph depends on upstream systems to perform the following additions. These are tracked as separate issues in their respective repositories:

| Dependency | Owner | Status | Why needed |
|---|---|---|---|
| Surface `serviceEndpoints[]` on `TrustResult` | verana-resolver | TBD | `ServiceEndpoint` node population ([TG-MODEL-1]) |
| Emit webhook on each completed `TrustResult` | verana-resolver | TBD | Primary ingestion mechanism ([TG-ING-1]) |
| Expose webhook retry queue with DLQ | verana-resolver | Nice-to-have | Graph availability under resolver-side flakiness |
| Backfill endpoint for graph cold-start | verana-resolver | v0.2 | Bootstrapping (see [Operations](#operations)) |

## Tech Stack

Implementations are free to choose their tech stack. The reference implementation uses:

- **Language:** TypeScript 5.x on Node.js 20.x
- **Web framework:** Fastify 4.x (matches verana-resolver)
- **GraphQL:** Mercurius (Fastify-native, GraphQL Yoga compatible)
- **Database:** PostgreSQL 15+
- **Schema migrations:** Umzug or Kysely migrator
- **Query builder / ORM:** Kysely (lightweight, type-safe, pg native)
- **Observability:** Pino logging, prom-client metrics
- **Container:** Debian slim base, non-root user
- **Deployment:** Helm chart; Kubernetes via verana-deploy conventions

## Security Considerations

1. **Network isolation of the ingest endpoint** — per [TG-SEC-1], `/v1/ingest/trust-result` MUST NOT be exposed to the public internet. Co-locate verana-graph and the upstream indexer on a private network, or restrict ingress to the indexer's pod / IP via `NetworkPolicy` or firewall rules.
2. **Rate limiting** — RECOMMENDED on `/v1/graphql` (per-client IP) for operational stability under abusive load. Not a confidentiality control; the data is public.
3. **Query complexity** — GraphQL queries SHOULD be bounded by max depth and max complexity for operational stability (implementation-defined; defaults RECOMMENDED: depth 10, complexity 1000).
4. **DID squatting resistance** — the graph does not authenticate holders of DIDs; it reflects what the upstream resolver verified. Trust in the graph's contents derives entirely from trust in the upstream indexer.

## Out of Scope (v0.1)

- AnonCreds credentials (including `ECS-UA`). See [Verifiable Trust Spec §VT-ECS-UA-CRED-ANON].
- GraphQL subscriptions / live updates.
- Multi-tenant deployments.
- Mutations via GraphQL (writes are webhook-only).
- Full permission-tree mirroring from VPR (only per-credential `permissionChain[]` is ingested).
- Historical time-series (retention is last-observation only, capped by TTL).
- Authentication on GraphQL queries (PoC allows anonymous reads).
- Per-tenant / per-ecosystem access control.

## Open Questions

These are deliberately unresolved in v0.1 and scheduled for later drafts:

1. **History and time-series.** Should the graph record every observation rather than last-only? If yes, schema changes in v0.2.
2. **Ecosystem isolation.** When multiple ecosystems coexist, should the graph expose per-ecosystem views? How do unrelated ecosystems interact via shared DIDs?
3. **Trust-path rendering.** Should the graph compute and cache full trust paths (did → ecosystem) as materialized views? Query complexity concern.
4. **Authoritative mirror of VPR.** At what point does v0.2 absorb VPR `Permission` rows as first-class data, rather than only what shows up in a credential's `permissionChain[]`?
5. **AnonCreds.** Feasibility and value of indexing AnonCreds-based ECS-UA issuance lineage (without identifying instances).
6. **Trust signals beyond VS-REQ.** Should the graph expose aggregate signals such as "number of services provided by this ORG"? Governance question.
7. **Decentralization of the index.** Can the same graph be built by multiple independent operators and its contents cross-checked? Governance question.

## References

- **[Verifiable Trust Specification](https://verana-labs.github.io/verifiable-trust-spec/)** — normative source for VS-REQ, ECS schemas, TR, architecture patterns.
- **[VPR Specification](https://verana-labs.github.io/verifiable-trust-vpr-spec/)** — normative source for TrustRegistry, CredentialSchema, Permission, DID Indexing.
- **[verana-resolver](https://github.com/verana-labs/verana-resolver)** — reference implementation of the upstream trust-resolution service.
- **[verana-indexer](https://github.com/verana-labs/verana-indexer)** — reference implementation of the VPR state indexer.
- **[Docs: architecture patterns](https://docs.verana.io/docs/next/use/verifiable-service-builders/overview#architecture-patterns)** — non-normative narrative of Patterns A and B.
