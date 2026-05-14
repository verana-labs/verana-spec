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


## Trust Resolution

## API

### Verifiable Trust Resolver

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

The point-in-time is controlled by `atTime` (ISO 8601 datetime) or `atBlock` (block height); the two are mutually exclusive and default to the latest block when neither is provided.

> **Recursive resolution.** To obtain full details about any other DID surfaced in the response (e.g. an ECS credential's subject at `ecsCredentials[].credentialSubject.id`, or any other DID a consumer chooses to inspect), call this same method on that DID. Note that most cross-entity references are surfaced by stable VPR id rather than DID (e.g. `corporationId`, `ecosystemId`, `credentialSchemaId`, `participantId`, `issuerParticipantId`) and do not need re-resolution — they're already directly joinable.

| Module | Method Name | Relative REST API path | Type | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Verifiable Trust Resolver | `resolve` | `/vt/v1/resolve` | Query | [[VS-REQ-2]], [[VS-REQ-3]], [[VS-REQ-4]] | PUBLIC |

#### Resolution request schema

The normative JSON Schema for the resolution request is published alongside this document at [`schemas/v4/vt/request.schema.json`](./schemas/v4/vt/request.schema.json). It defines the `did` parameter, the optional point-in-time selectors (`atTime` / `atBlock`, mutually exclusive), and the response-shaping selectors (`corporation`, `participations`, `ecsCredentials`, `services`, `presentations`, `ecosystems`).

#### Resolution response schema

The normative JSON Schema for the resolution response is published alongside this document at [`schemas/v4/vt/response.schema.json`](./schemas/v4/vt/response.schema.json). It defines the always-present core fields (`did`, `trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`) and every optional section returned when the corresponding request selector is set.

#### Example resolution request

The following is a **maximum** request that asks for every optional section the resolver can return. Any top-level selector below MAY be omitted, in which case that section is excluded from the response. The response always includes the core fields (`did`, `trusted`, `evaluatedAtTime`, `evaluatedAtBlock`, `expiresAtTime`, `corporationId`).

```json
{
   "did": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
   "atBlock": 1500000,
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

Selector semantics:

- **`atTime` / `atBlock`** — Optional point-in-time. Mutually exclusive; when neither is provided the resolver evaluates against the latest block. `atTime` is an ISO 8601 datetime; `atBlock` is an integer block height.
- **`corporation`** — `true` to include the `corporation` object (the unique Corporation whose `did` equals the resolved DID; carries `id`, `deposit`, slash history, and `cgf`). Omit or set `false` to exclude. The top-level `corporationId` scalar (which equals `corporation.id` whenever the latter is included — by VPR's per-Corporation `did` uniqueness invariant they are necessarily the same Corporation) is **always** returned with the trust-core fields and is not gated by this selector; this selector only controls whether the full Corporation object (`deposit`, slash history, CGF) is also surfaced inline.
- **`participations`** — Omit to exclude. When present, `states[]` filters which participation states are returned. Defaults to `["ACTIVE"]` when `participations` is provided without `states`. Valid values: `ACTIVE, FUTURE, INACTIVE, EXPIRED, REVOKED, SLASHED, REPAID`.
- **`ecsCredentials`** — `true` to include the full ECS credentials with subject claims. Omit or `false` to exclude.
- **`services`** — `true` to include `services[]`, the non-LinkedVerifiablePresentation service entries from the DID Document (e.g. DIDComm, MCP, LinkedDomains). Omit or `false` to exclude.
- **`presentations`** — Omit to exclude. When present, each entry always carries `vtcCredentials[]` (array of `{id, credentialSchemaId, ecosystemId}` per non-ECS VTC carried by the VP) plus the VP's `id` and `serviceId`. The two sub-flags additionally enable `unresolvableCredentialIds[]` and `invalidCredentialIds[]` per entry; both default to `false`.
- **`ecosystems`** — Omit to exclude. `includeArchived` (default `false`) controls whether archived ecosystems appear in the top-level array. The nested `credentialSchemas` object controls embedded Credential Schemas: omit `credentialSchemas` entirely to suppress them, or set `credentialSchemas.includeArchived` (default `false`) to also surface archived Credential Schemas.

#### Example resolution response

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

### Trust Registry Query Protocol v2

The Verana indexer implements the [Trust Registry Query Protocol v2](https://trustoverip.github.io/tswg-trust-registry-query-protocol/) (TRQP v2.0) so any relying party can ask, in a registry-agnostic way, two complementary questions about a Verana corporation, ecosystem, or schema:

1. **Authorization** — *"Is this `entity_id` authorized by this `authority_id` for this `action` on this `resource`?"*
2. **Recognition** — *"Does this `authority_id` recognize that other authority `entity_id` to be authoritative for this `action` on this `resource`?"*

In Verana v4 both `authority_id` and `entity_id` are normal DIDs — corporations and ecosystems each carry a `did` and a governance framework (CGF and EGF respectively) — so the protocol is fully DID-native.

Both endpoints are pure query views over on-chain VPR state; they are PUBLIC and do not mutate state.

| Module | Method Name | Relative REST API path | Type | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| TRQP | `trqpAuthorize` | `/trqp/v2/authorization` | Query | — | PUBLIC |
| TRQP | `trqpRecognize` | `/trqp/v2/recognition`   | Query | — | PUBLIC |

#### Verana TRQP profile

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

#### Authorization

Direction: ecosystem → corporation. Derived from `Participant` entries.

##### Action vocabulary

| `action` | Verana `Participant.role` | Wire-level meaning |
| --- | --- | --- |
| `issue` | `ISSUER` | corporation may issue credentials of `resource` schema in `authority` ecosystem |
| `verify` | `VERIFIER` | corporation may verify credentials of `resource` schema |
| `grant_issue` | `ISSUER_GRANTOR` | corporation may grant `issue` to others for `resource` schema |
| `grant_verify` | `VERIFIER_GRANTOR` | corporation may grant `verify` to others for `resource` schema |
| `govern` | `ECOSYSTEM` | corporation holds root governance for the `resource` schema in the `authority` ecosystem |

##### Derivation

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

##### Authorization request schema

Authorization requests use the upstream ToIP TSWG schema [`trqp_authorization_request.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_authorization_request.schema.json) (`$id`: `trqp-authorization-request`) verbatim. Verana-specific narrowing of `action`, `resource`, `authority_id`, `entity_id`, and `context` is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json).

##### Authorization response schema

Authorization responses use the upstream ToIP TSWG schema [`trqp_authorization_response.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_authorization_response.schema.json) (`$id`: `trqp-authorization-response`) verbatim. The Verana profile additionally permits a top-level `verana` object whose shape is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json); the upstream schema does not set `additionalProperties: false`, so this extension is conformant.

##### Example authorization request

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

##### Example authorization response

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

#### Recognition

Direction: Corporation → Ecosystem. Derived from `Ecosystem` entries — specifically the controlling-Corporation reference each Ecosystem carries (VPR-level `Ecosystem.corporation` group field; surfaced in the graph as `Ecosystem.corporationId`). TRQP itself remains DID-only at the wire level — the `authority_id` (Corporation DID) and `entity_id` (Ecosystem DID) inputs are translated to internal stable ids only inside the indexer when evaluating the predicate. Per-Participant-entry recognition (e.g. ECOSYSTEM-role recognition for individual Credential Schemas, Ecosystem-to-Ecosystem federation, Corporation-to-Corporation peer recognition) is **out of scope for v4**.

##### Action vocabulary

Recognition reuses the authorization action enum (`issue`, `verify`, `grant_issue`, `grant_verify`, `govern`). In v4 the boolean answer is **action-invariant**: a Corporation that controls an Ecosystem is acknowledging that Ecosystem's framework as authoritative for every action governed within the Ecosystem's scope. The `action` argument is preserved on the wire for TRQP conformance and forward compatibility with future per-action recognition semantics.

##### Derivation

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

##### Recognition request schema

Recognition requests use the upstream ToIP TSWG schema [`trqp_recognition_request.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_recognition_request.schema.json) (`$id`: `trqp-recognition-request`) verbatim. Verana-specific narrowing is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json).

##### Recognition response schema

Recognition responses use the upstream ToIP TSWG schema [`trqp_recognition_response.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_recognition_response.schema.json) (`$id`: `trqp-recognition-response`) verbatim. The Verana profile additionally permits a top-level `verana` object whose shape is described by the [Verana TRQP profile descriptor](./schemas/v4/vt/trqp-profile.json).

##### Example recognition request

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

##### Example recognition response

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

##### Out-of-scope queries

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

#### Context: `session_id` extension

Both endpoints accept an optional `context.session_id` extension to bind the answer to a specific [VPR `MOD-PERM-MSG-10`] participant session. When supplied:

> Note: `session_id` is needed in most cases for issuance and verification.

- `session_id` takes precedence over `time`.
- The resolver verifies that `time` (if also given) falls inside the session's validity window; if outside, the answer is `authorized: false` (or `recognized: false`) with `message: "session out of window"`.
- If the session does not exist, the answer is `false` with `message: "session not found"`.

When `session_id` is omitted, the answer is point-in-time per the standard `time` argument; if both are omitted, the answer is computed against the latest block.

### Websocket Subscriptions

The Verifiable Trust Resolver also exposes a real-time event stream so that clients can keep an indexer-backed mirror in sync without polling `/vt/v1/resolve` for every DID on every block.

The stream is organised around three coordinated endpoints. Together they cover live updates (`subscribeChanges`), catch-up after a disconnection (`listChanges`), and bootstrap from an empty mirror (`listIndexedDids`).

| Module | Method Name | Relative REST API path | Type | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Verifiable Trust Resolver | `subscribeChanges` | `/vt/v1/subscribe` | Subscription (WebSocket) | — | PUBLIC |
| Verifiable Trust Resolver | `listChanges` | `/vt/v1/changes` | Query | — | PUBLIC |
| Verifiable Trust Resolver | `listIndexedDids` | `/vt/v1/dids` | Query | — | PUBLIC |

The unit of notification is **(DID, block)**: each time the indexer processes a new block, it re-evaluates trust for every DID whose state may have changed and emits **at most one change envelope per DID per block**, restricted to the channels the subscriber selected.

The normative JSON Schemas for this stream are published alongside this document:

- [`schemas/v4/vt/subscribe.schema.json`](./schemas/v4/vt/subscribe.schema.json) — client → server WebSocket control messages (`subscribe`, `unsubscribe`), including the channel selectors and sub-flags described in the [Channels](#channels) section below.
- [`schemas/v4/vt/changes.schema.json`](./schemas/v4/vt/changes.schema.json) — server-side payloads: the WS `ready` message, the WS `block` message, and the `listChanges` REST response, all sharing the common `ChangeEnvelope` shape.

#### Channels

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

Channel flags carry **change signals**, not full new values — except for `trust`, which is delivered inline because it is small, fixed-shape, and the most frequently consumed. To obtain the new state for any other changed channel, the client calls `/vt/v1/resolve` at `atBlock = <block of the change envelope>`.

#### `subscribeChanges` — WebSocket subscription

The subscriber opens a WebSocket connection to `/vt/v1/subscribe` and sends one or more JSON control messages. The first control message MUST be a `subscribe`.

##### Connect / ready

Immediately after a successful WebSocket upgrade, before any `subscribe` is processed, the server sends a `ready` message:

```json
{
   "type": "ready",
   "block": 1500005,
   "blockTime": "2026-05-11T13:00:05Z"
}
```

`block` is the height of the **next** block that the server will deliver via this WebSocket (i.e. `latestProcessedBlock + 1` at connect time). Clients use `block - 1` as the bootstrap snapshot point — see [Bootstrap pattern](#bootstrap-pattern).

##### Subscribe control message

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

##### Block message (server → client)

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
- `changes[].<channel>` — `true` iff the channel is in the subscription **and** changed at this block; `false` otherwise. Clients fetch the new state by calling `/vt/v1/resolve` at `atBlock = block`.

##### Block production as ping

Block messages are emitted **for every processed block**, even when `changes[]` is empty. Block production is the heartbeat: a connection that does not deliver a block message within the expected block-time window is presumed broken, and the client SHOULD reconnect and catch up via [`listChanges`](#listchanges--catch-up-over-a-block-range).

A subscriber detects a connection-level loss by observing a gap (`block > previousBlock + 1`) in the sequence of received block messages.

##### Backpressure

A subscriber that fails to drain its receive buffer within an indexer-defined window MAY have its connection closed with WebSocket close code `1011` (server error / overloaded). The client SHOULD reconnect and resume via `listChanges`.

#### `listChanges` — catch-up over a block range

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

#### `listIndexedDids` — bootstrap snapshot

A client that starts with an empty mirror needs a way to enumerate the universe of DIDs the indexer tracks at a frozen snapshot block, then resolve each via `/vt/v1/resolve` to populate its initial state.

Request:

```http
GET /vt/v1/dids
  ?atBlock=<int>
  [&cursor=<opaque string>]
  [&limit=<int>]
```

`limit` defaults to `1000` and MUST NOT exceed `10000`.

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

- `atBlock` — Echo of the requested snapshot block. The "DID universe" at block `B` is the set of DIDs the indexer can resolve at `B`: every Corporation `did`, every Ecosystem `did`, the Corporation-side DID of every Participant entry that is in scope (per the resolver's [participation states](#example-resolution-response)), and any DID previously evaluated by the resolver that the indexer is still tracking.
- `dids[]` — Page of indexed DIDs in stable sort order across pages.
- `nextCursor` — Opaque pagination cursor; `null` (or absent) on the last page.

#### Bootstrap pattern

The recommended initial-sync sequence for a client with an empty mirror:

1. **Connect** to `WS /vt/v1/subscribe`. Read the `ready` message and capture `B = ready.block`.
2. **Subscribe** with the desired `dids` / `channels`. Buffer all incoming block messages **without applying them** until step 5.
3. **Enumerate** the DID universe at block `B - 1` by calling `GET /vt/v1/dids?atBlock=B-1` and paginating through `nextCursor`.
4. **Resolve** each enumerated DID by calling `POST /vt/v1/resolve` with `atBlock: B - 1` and the response selectors the client cares about. Persist the resulting state as the snapshot at block `B - 1`.
5. **Apply** the buffered WebSocket block messages in order (starting at block `B`), then continue applying live block messages as they arrive.

Because the snapshot is taken at the immutable past block `B - 1` and the WebSocket delivers from `B` onwards, no events are lost or double-counted.

#### Resume pattern

After a temporary disconnection, a client with a non-empty mirror resumes by:

1. Recording `last_seen_block` of the most recently applied WebSocket block message.
2. Reconnecting to `WS /vt/v1/subscribe` and re-subscribing as before. Buffer incoming block messages.
3. Running the [`listChanges`](#listchanges--catch-up-over-a-block-range) catch-up loop from `fromBlock = last_seen_block + 1` until either `nextFromBlock` is `null` or it has reached the smallest block held in the WebSocket buffer.
4. Applying the buffered WebSocket block messages in order, deduplicated by `block` against anything already applied from `listChanges`.
