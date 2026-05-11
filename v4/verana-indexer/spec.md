# Indexer v4 Specification

**Latest Draft:** spec v4-draft1

## Abstract

## About this Document

In order to fully understand the concepts developed in this document, you should have some basic knowledge of DID, DIDComm, AnonCreds, the Verifiable Trust model, and the [ToIP stack](https://www.trustoverip.org/toip-model/). All terms used in this specification are defined in the [Terminology](#terminology) section.

## Conformance

As well as sections marked as non-normative, all authoring guidelines, diagrams, examples, and notes in this specification are non-normative. Everything else in this specification is normative.

The key words MAY, MUST, MUST NOT, OPTIONAL, RECOMMENDED, REQUIRED, SHOULD, and SHOULD NOT in this document are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) [RFC2119](https://w3c.github.io/vc-data-model/#bib-rfc2119) [RFC8174](https://w3c.github.io/vc-data-model/#bib-rfc8174) when, and only when, they appear in all capitals, as shown here.

## Terminology

- **AnonCreds** — Anonymous Credentials, a privacy-preserving verifiable credential format supporting selective disclosure and unlinkability.
- **decentralized identifier (DID, DIDs)** — A decentralized identifier, as specified in [DID-CORE](https://www.w3.org/TR/did-core/).
- **DIDComm** — A peer-to-peer messaging protocol built on DIDs, as specified by the [DIDComm Messaging Specification](https://identity.foundation/didcomm-messaging/spec/).
- **Verifiable Public Registry (VPR, VPRs)** — A decentralized registry used to publish and resolve trust-related resources (credential schemas, trust registries, governance frameworks, etc.), as specified by the [Verifiable Trust VPR specification](https://github.com/verana-labs/verifiable-trust-vpr-spec).
- **Verifiable Service (Verifiable Services)** — A service that identifies its operator, purpose, and governance context through verifiable credentials, as defined in the [Verifiable Trust specification](https://github.com/verana-labs/verifiable-trust-spec).
- **Verifiable Trust** — The open, decentralized trust layer specified at [verana-labs/verifiable-trust-spec](https://github.com/verana-labs/verifiable-trust-spec).
- **VS Agent** — The runtime component specified by this document, which hosts a Verifiable Service and exposes a REST API and event model to backend implementations.
- **VTJSC, Verifiable Trust JSON Schema Credential** — A W3C `JsonSchemaCredential` issued by an Ecosystem DID that references a `CredentialSchema` entry in a Verifiable Public Registry, cryptographically binding that schema to the Ecosystem that controls the Trust Registry in which the schema is defined. Specified in [VT-JSON-SCHEMA-CRED-W3C](https://github.com/verana-labs/verifiable-trust-spec/blob/main/spec.md#vt-json-schema-cred-w3c-verifiable-trust-json-schema-credential) of the Verifiable Trust Specification.
- **W3C Verifiable Credentials Data Model (W3C VC Data Model)** — The W3C Recommendation defining a standard data model for verifiable credentials, as specified in [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model/).


## Trust Resolution

## API

### DID Resolver

The DID Resolver answers two complementary questions about a DID at a chosen point in time:

1. **Is the DID a Verifiable Service?** — Reflected in the boolean `trusted` field of the response.

   Per [[VS-REQ]], a DID qualifies as a **Verifiable Service** only if:
   - **[VS-REQ-2]** It presents a valid Service Credential (`ECS-SERVICE` VTC).
   - **[VS-REQ-3]** If the issuer of the Service Credential **is the VS itself** (self-issued), the VS MUST also present exactly one `ECS-ORG` or `ECS-PERSONA` credential.
   - **[VS-REQ-4]** If the issuer of the Service Credential **is another DID**, the DID Document of that issuer MUST present exactly one `ECS-ORG` or `ECS-PERSONA` credential.

   This ensures every VS is ultimately bound to a legally or naturally accountable entity — either directly (the VS identifies itself) or indirectly (the issuer of its Service Credential identifies itself). A DID that satisfies these requirements is returned with `trusted: true`; otherwise `trusted: false`.

2. **What contextual data does the indexer have on this DID?** — Opt-in sections selected via the request payload. Each section is suppressed by default and is only computed and returned when its selector is set:

   - **`corporation`** — DID, controller, deposit, and slash history of the on-chain Corporation entry associated with the DID being resolved. The Corporation `did` is the entity-level identifier under the [VPR Corporation model](https://github.com/verana-labs/verifiable-trust-vpr-spec); the `controller` is the Cosmos SDK group policy address that controls the Corporation entry (1:1 with the underlying group); the `deposit` is the trust deposit currently bonded by the Corporation.
   - **`participations`** — Trust registries and schemas the DID participates in, filterable by state (`ACTIVE`, `FUTURE`, `INACTIVE`, `EXPIRED`, `REVOKED`, `SLASHED`, `REPAID`); defaults to `ACTIVE` when no filter is given.
   - **`ecsCredentials`** — The full ECS credentials extracted from the DID's linked-VPs, with their `credentialSubject` claims.
   - **`services`** — Non-`LinkedVerifiablePresentation` service entries from the DID Document (DIDComm, MCP, A2A, LinkedDomains, …), surfaced verbatim.
   - **`presentations`** — Per-VP credential-ID summaries (`vtcCredentialIds[]`); sub-flags additionally surface unresolvable and invalid credential IDs per VP.
   - **`ecosystems`** — Aggregate metrics for the ecosystems (and their underlying trust registries) the DID participates in. Sub-flags control whether archived ecosystems (and their archived embedded schemas) are included.

The response always carries the core fields (`did`, `trusted`, `evaluatedAt`, `evaluatedAtBlock`, `expiresAt`, `vsOperator`); every other section is gated by its selector. The full payload contract is normatively defined by the [Resolution request schema](#resolution-request-schema) and [Resolution response schema](#resolution-response-schema) below.

The point-in-time is controlled by `atTime` (ISO 8601 datetime) or `atBlock` (block height); the two are mutually exclusive and default to the latest block when neither is provided.

> **Recursive resolution.** To obtain full details about any participant DID surfaced in the response (an issuer, an ecosystem, a permission grantor, …), call this same method on that DID.

| Module | Method Name | Relative REST API path | Type | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| DID Resolver | `resolveDid` | `/dr/v1/resolve` | Query | [[VS-REQ-2]], [[VS-REQ-3]], [[VS-REQ-4]] | PUBLIC |

#### Resolution request schema

The normative JSON Schema for the resolution request is published alongside this document at [`resolver-schemas/request.schema.json`](./resolver-schemas/request.schema.json). It defines the `did` parameter, the optional point-in-time selectors (`atTime` / `atBlock`, mutually exclusive), and the response-shaping selectors (`corporation`, `participations`, `ecsCredentials`, `services`, `presentations`, `ecosystems`).

#### Resolution response schema

The normative JSON Schema for the resolution response is published alongside this document at [`resolver-schemas/response.schema.json`](./resolver-schemas/response.schema.json). It defines the always-present core fields (`did`, `trusted`, `evaluatedAt`, `evaluatedAtBlock`, `expiresAt`, `vsOperator`) and every optional section returned when the corresponding request selector is set.

#### Example resolution request

The following is a **maximum** request that asks for every optional section the resolver can return. Any top-level selector below MAY be omitted, in which case that section is excluded from the response. The response always includes the core fields (`did`, `trusted`, `evaluatedAt`, `evaluatedAtBlock`, `expiresAt`, `vsOperator`).

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
      "schemas": {
         "includeArchived": true
      }
   }
}
```

Selector semantics:

- **`atTime` / `atBlock`** — Optional point-in-time. Mutually exclusive; when neither is provided the resolver evaluates against the latest block. `atTime` is an ISO 8601 datetime; `atBlock` is an integer block height.
- **`corporation`** — `true` to include the `corporation` object (DID, controller, deposit, slash history). Omit or set `false` to exclude.
- **`participations`** — Omit to exclude. When present, `states[]` filters which participation states are returned. Defaults to `["ACTIVE"]` when `participations` is provided without `states`. Valid values: `ACTIVE, FUTURE, INACTIVE, EXPIRED, REVOKED, SLASHED, REPAID`.
- **`ecsCredentials`** — `true` to include the full ECS credentials with subject claims. Omit or `false` to exclude.
- **`services`** — `true` to include `services[]`, the non-LinkedVerifiablePresentation service entries from the DID Document (e.g. DIDComm, MCP, LinkedDomains). Omit or `false` to exclude.
- **`presentations`** — Omit to exclude. When present, each entry always carries `vtcCredentialIds[]` plus `id` / `serviceId`. The two sub-flags additionally enable `unresolvableCredentialIds[]` and `invalidCredentialIds[]` per entry; both default to `false`.
- **`ecosystems`** — Omit to exclude. `includeArchived` (default `false`) controls whether archived ecosystems appear in the top-level array. The nested `schemas` object controls embedded schemas: omit `schemas` entirely to suppress them, or set `schemas.includeArchived` (default `false`) to also surface archived schemas.

#### Example resolution response

participation states: REPAID, SLASHED, REVOKED, EXPIRED, ACTIVE, FUTURE, INACTIVE
participation roles: HOLDER, ISSUER, VERIFIER, ISSUER_GRANTOR, VERIFIER_GRANTOR, ECOSYSTEM

```json
{
   "did":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
   "trusted":true,
   "evaluatedAt":"2026-05-06T17:00:00.000Z",
   "evaluatedAtBlock":1500000,
   "expiresAt":"2026-05-07T17:00:00.000Z",
   "vsOperator":"verana19kpereglz3jw690kjys3lnulx2r06p99l5u6sz",
   "corporation":{
      "did":"did:webvh:QmZ8Y3xRkH2pV4qTw9nL7sFmJg6cN5dB1aWxKvE3uPyT8r:corp.acme.example",
      "controller":"verana1rw7w9hm0zd7e4jcxsm955nu8l5ju0wtkpssxe5",
      "deposit":"40000000uvna",
      "lastSlashedAt":"2026-01-01T03:00:00.000Z",
      "slashedEvents":1,
      "slashedValue":"1000000uvna"
   },
   "participations":[
      {
         "ecosystem":"did:web:ecosystem1",
         "role":"ISSUER",
         "state": "ACTIVE",
         "schema":{
            "id":1234,
            "type":"JsonSchema",
            "uri":"vpr:verana:vna-testnet-1/cs/v1/js/1234",
            "digestSRI":"sha384-…"
         },
         "weight":"10000000uvna",
         "issuedCredentials":2345,
         "participants":{
            "HOLDER":75
         }
      },
      {
         "ecosystem":"did:web:ecosystem2",
         "role":"VERIFIER",
         "state": "ACTIVE",
         "schema":{
            "id":5678,
            "type":"JsonSchema",
            "uri":"vpr:verana:vna-testnet-1/cs/v1/js/5678",
            "digestSRI":"sha384-…"
         },
         "weight":"5000000uvna",
         "verifiedCredentials":500
      },
      {
         "ecosystem":"did:web:ecosystem3",
         "role":"ISSUER_GRANTOR",
         "state": "REPAID",
         "schema":{
            "id":9012,
            "type":"JsonSchema",
            "uri":"vpr:verana:vna-testnet-1/cs/v1/js/9012",
            "digestSRI":"sha384-…"
         },
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
         "issuer":"did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
         "ecosystem":"did:webvh:QmcTCdA8z7cs7BwCKyrrJrTTmvff3wmxSn7WUZtP2iAM7T:ecs-trust-registry.testnet.verana.network",
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
         "issuer":"did:webvh:QmcTCdA8z7cs7BwCKyrrJrTTmvff3wmxSn7WUZtP2iAM7T:ecs-trust-registry.testnet.verana.network",
         "ecosystem":"did:webvh:QmcTCdA8z7cs7BwCKyrrJrTTmvff3wmxSn7WUZtP2iAM7T:ecs-trust-registry.testnet.verana.network",
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
         "vtcCredentialIds":[
            "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#cc5c398f-bc64-45df-9482-9cb583cce197",
            "urn:uuid:22222222-aaaa-bbbb-cccc-222222222222",
            "urn:uuid:33333333-aaaa-bbbb-cccc-333333333333"
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
         "archived":false,
         "schemas":[
            {
               "id":223,
               "type":"JsonSchema",
               "uri":"vpr:verana:vna-testnet-1/cs/v1/js/223",
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
| Recognition trigger | `Ecosystem.did = entity_id` AND `Ecosystem.corporation.did = authority_id` AND not archived |
| Recognition scope (v4) | corporation DID → ecosystem DID |
| Context extension | `session_id` (string), precedence `session_id` > `time` |
| Active states | `ACTIVE` |

Request and response payloads use the upstream ToIP TSWG schemas verbatim (see the per-direction subsections below for the canonical URLs). The Verana profile narrows their *interpretation*: it freezes `action` to a closed enum, `resource` to the VPR schema URI grammar, and constrains `authority_id` / `entity_id` to Verana corporation or ecosystem DIDs (see scope rules per endpoint). It also registers `context.session_id` (string) as a profile extension permitted by the upstream `context.additionalProperties` clause, and reserves a top-level `verana` object on responses for VPR-state breadcrumbs (opaque to non-Verana consumers; conformant because upstream does not set `additionalProperties: false`).

The full machine-readable Verana TRQP profile descriptor — including the action → `Participant.role` map, regex patterns, trigger semantics, scope rules, error messages, and discovery URLs — is published at [`trqp-profile.json`](./trqp-profile.json) (`$id`: `https://verana.io/schemas/v4/trqp/profile.json`).

Profile discovery. TRQP v2.0 does not standardise a profile-discovery mechanism, but per TRQP v2.0 §Identifiers/`authority_id` and §Conformance the **ecosystem governance framework** — of which this profile forms part — MUST be discoverable via the authority's identifier. Verana implements that requirement as follows:

- A Verana corporation or ecosystem MAY advertise a `TRQPEndpoint` service entry in its DID Document, pointing at the indexer's `/trqp/v2/` base path.
- The indexer MUST serve the profile descriptor at `/trqp/v2/profile` with `Content-Type: application/json`; the body is byte-identical to [`trqp-profile.json`](./trqp-profile.json).
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

```
For a query (authority=E, entity=V, action=A, resource=R, time=T):
  active_rows = Participant entries where
                  ecosystem  = E
                AND corporation = V
                AND role       = role_of(A)
                AND schema.uri = R
                AND state      = "ACTIVE"
                AND validAt(T)
  authorized = active_rows is non-empty
```

##### Authorization request schema

Authorization requests use the upstream ToIP TSWG schema [`trqp_authorization_request.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_authorization_request.schema.json) (`$id`: `trqp-authorization-request`) verbatim. Verana-specific narrowing of `action`, `resource`, `authority_id`, `entity_id`, and `context` is described by the [Verana TRQP profile descriptor](./trqp-profile.json).

##### Authorization response schema

Authorization responses use the upstream ToIP TSWG schema [`trqp_authorization_response.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_authorization_response.schema.json) (`$id`: `trqp-authorization-response`) verbatim. The Verana profile additionally permits a top-level `verana` object whose shape is described by the [Verana TRQP profile descriptor](./trqp-profile.json); the upstream schema does not set `additionalProperties: false`, so this extension is conformant.

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

Direction: corporation → ecosystem. Derived from `Ecosystem` entries — specifically the `Ecosystem.corporation` controller field. Per-Participant-entry recognition (e.g. ECOSYSTEM-role recognition for individual schemas, ecosystem-to-ecosystem federation, corp-to-corp peer recognition) is **out of scope for v4**.

##### Action vocabulary

Recognition reuses the authorization action enum (`issue`, `verify`, `grant_issue`, `grant_verify`, `govern`). In v4 the boolean answer is **action-invariant**: a corporation that controls an ecosystem is acknowledging that ecosystem's framework as authoritative for every action governed within the ecosystem's scope. The `action` argument is preserved on the wire for TRQP conformance and forward compatibility with future per-action recognition semantics.

##### Derivation

```
For a query (authority=V, entity=E, action=A, resource=R, time=T):
  ecosystem_row = Ecosystem entry where
                    did              = E
                  AND corporation.did = V
                  AND archived IS NULL
                  AND validAt(T)
  schema_row    = CredentialSchema entry where
                    uri      = R
                  AND ecosystem = ecosystem_row
                  AND validAt(T)
  recognized = (ecosystem_row is non-empty) AND (schema_row is non-empty)
```

In words: V recognizes E for resource R iff (a) V is the corporation that controls E, AND (b) R is a schema governed by E.

##### Recognition request schema

Recognition requests use the upstream ToIP TSWG schema [`trqp_recognition_request.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_recognition_request.schema.json) (`$id`: `trqp-recognition-request`) verbatim. Verana-specific narrowing is described by the [Verana TRQP profile descriptor](./trqp-profile.json).

##### Recognition response schema

Recognition responses use the upstream ToIP TSWG schema [`trqp_recognition_response.schema.json`](https://trustoverip.github.io/tswg-trust-registry-protocol/approved/schema/trqp_recognition_response.schema.json) (`$id`: `trqp-recognition-response`) verbatim. The Verana profile additionally permits a top-level `verana` object whose shape is described by the [Verana TRQP profile descriptor](./trqp-profile.json).

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

