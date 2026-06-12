# VS Agent v4 Specification

**Latest Draft:** spec v4-draft3

## Abstract

The **VS Agent** is a container that provides the full stack required to operate a Verifiable Service. It bundles, in a single deployable unit:

- **Decentralized identity** — a resolvable DID whose DID Document is signed by the agent's keys and attested by `LinkedVerifiablePresentation` entries wrapping W3C Verifiable Credentials Data Model credentials that establish the operator, purpose, and governance context of the service.
- **DIDComm stack** — a full DIDComm implementation for establishing secure agent-to-agent communication channels with any other DIDComm-compatible peer.
- **Service endpoint declaration** — publishing one or more concrete service endpoints (DIDComm messaging, MCP, A2A, HTTP / website, and similar) in the agent's DID Document under a single resolvable DID.
- **Service bootstrap over DIDComm** — an initial exchange over the DIDComm channel through which peers obtain the credentials, access tokens, or configuration needed to consume any of the declared service endpoints.

By combining these components, the VS Agent allows backends to expose identified, verifiable, and governance-aware services without implementing DID resolution, credential lifecycle management, DIDComm encryption, or trust-layer integration themselves. The VS Agent is intentionally service-shape-agnostic: conversational chatbots integrated with messaging applications such as the [Hologram Messaging App](https://hologram.chat) are one of several deployment patterns, alongside MCP tool servers, A2A agents, and plain HTTP APIs.

This document specifies the normative behavior of a VS Agent implementation: its container configuration and bootstrap, its DID Document management, its credential acquisition and issuance flows, its indexer subscription and event model, its administration API, and its conformance to the Verifiable Trust specification.

## About this Document

In order to fully understand the concepts developed in this document, you should have some basic knowledge of DID, DIDComm, AnonCreds, the Verifiable Trust model, and the [ToIP stack](https://www.trustoverip.org/toip-model/). All terms used in this specification are defined in the [Terminology](#terminology) section.

## Conformance

As well as sections marked as non-normative, all authoring guidelines, diagrams, examples, and notes in this specification are non-normative. Everything else in this specification is normative.

The key words MAY, MUST, MUST NOT, OPTIONAL, RECOMMENDED, REQUIRED, SHOULD, and SHOULD NOT in this document are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) [RFC2119](https://w3c.github.io/vc-data-model/#bib-rfc2119) [RFC8174](https://w3c.github.io/vc-data-model/#bib-rfc8174) when, and only when, they appear in all capitals, as shown here.

## Terminology

- **AnonCreds** — Anonymous Credentials, a privacy-preserving verifiable credential format supporting selective disclosure and unlinkability.
- **decentralized identifier (DID, DIDs)** — A decentralized identifier, as specified in [DID-CORE](https://www.w3.org/TR/did-core/).
- **DIDComm** — A peer-to-peer messaging protocol built on DIDs, as specified by the [DIDComm Messaging Specification](https://identity.foundation/didcomm-messaging/spec/).
- **Verifiable Public Registry (VPR, VPRs)** — A decentralized registry used to publish and resolve trust-related resources (Corporations, Ecosystems, Credential Schemas, Participants, Governance Frameworks, etc.), as specified by the [Verifiable Trust VPR specification](https://github.com/verana-labs/verifiable-trust-vpr-spec).
- **Verifiable Service (Verifiable Services)** — A service that identifies its operator, purpose, and governance context through verifiable credentials, as defined in the [Verifiable Trust specification](https://github.com/verana-labs/verifiable-trust-spec).
- **Verifiable Trust** — The open, decentralized trust layer specified at [verana-labs/verifiable-trust-spec](https://github.com/verana-labs/verifiable-trust-spec).
- **VS Agent** — The runtime component specified by this document, which hosts a Verifiable Service and exposes a REST API and event model to backend implementations.
- **VTJSC, Verifiable Trust JSON Schema Credential** — A W3C `JsonSchemaCredential` issued by an Ecosystem DID that references a `CredentialSchema` entry in a Verifiable Public Registry, cryptographically binding that schema to the Ecosystem in which it is defined. Specified in [VT-JSON-SCHEMA-CRED-W3C](https://github.com/verana-labs/verifiable-trust-spec/blob/main/spec.md#vt-json-schema-cred-w3c-verifiable-trust-json-schema-credential) of the Verifiable Trust Specification.
- **W3C Verifiable Credentials Data Model (W3C VC Data Model)** — The W3C Recommendation defining a standard data model for verifiable credentials, as specified in [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model/).

## Verifiable Trust Integration

### Introduction

*This section is not normative.*

Resources created in a VPR (like the Verana ledger) are linked to DIDs that represent VS Agents. For this reason, a VS Agent MUST receive notifications of changes in the ledger that are directly or indirectly linked to its DID, and update its state accordingly.

**Examples:**

- **Ecosystem schema addition** — A new `CredentialSchema` is created in an Ecosystem. The VS Agent whose DID is the Ecosystem's `did` is notified and automatically generates the corresponding VTJSC, publishing it as a `LinkedVerifiablePresentation` in its DID Document.
- **Onboarding process lifecycle** — An applicant initiates an Onboarding Process to obtain a HOLDER `Participant` entry from an ISSUER for a given Credential Schema. The applicant creates the on-chain `Participant` entry (with `op_state = PENDING`) on the Verana ledger. The VS Agents of both applicant and validator (ISSUER) are notified and begin a userland onboarding flow over DIDComm. As the on-chain `Participant` state changes, the respective VS Agents receive further notifications and execute follow-up tasks (e.g., continuing the DIDComm exchange, issuing the credential).

```mermaid
flowchart LR
    VPR["Verana Ledger<br/>(VPR)"]
    IDX["Indexer<br/>(WebSocket)"]
    VS["VS Agent<br/>(Ecosystem Controller)"]
    DID["DID Document"]

    VPR -- "new CredentialSchema<br/>created in Ecosystem" --> IDX
    IDX -- "notification" --> VS
    VS -- "generate VTJSC +<br/>publish linked VP" --> DID
```

*Figure 1a — Ecosystem schema addition. A new `CredentialSchema` is created on-chain; the Indexer notifies the owning VS Agent (the Ecosystem controller), which generates the corresponding VTJSC and publishes it in its DID Document.*

```mermaid
flowchart LR
    VPR["Verana Ledger<br/>(VPR)"]
    IDX["Indexer<br/>(WebSocket)"]
    VSA["VS Agent A<br/>(Applicant)"]
    VSB["VS Agent B<br/>(Validator / ISSUER)"]

    VPR -- "Participant event" --> IDX
    IDX -- "Participant change notifications" --> VSA
    IDX -- "Participant change notifications" --> VSB
    VSA <-- "DIDComm<br/>(onboarding + issuance)" --> VSB
```

*Figure 1b — Onboarding process lifecycle. The applicant creates a `Participant` entry on-chain; both VS Agents are notified and coordinate over DIDComm. As the on-chain `Participant.op_state` changes, further notifications trigger follow-up tasks.*

Additionally, a Corporation controller needs to remotely query and manage the state of its VS Agents directly from the Verana frontend. To enable this, each VS Agent MUST expose a secure Administration API accessible to Verana accounts that have been granted administrative rights over the agent by the Corporation.

### Corporation and Account Model

#### Corporation

*This section is not normative.*

As defined in the [VPR Specification v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/#corporation):

> A `Corporation` is the VPR-level entity representing an authority that acts in the registry. It carries a DID, a governance framework, and lifecycle attributes, and is anchored on-chain by a `policy_address` account that signs on its behalf. A Corporation may control [[ref: participants]] in zero or more [[ref: ecosystems]] and may itself be the controller of zero or more [[ref: ecosystems]].

A `Corporation` has, among other fields:

- `id` (uint64) — server-assigned, globally unique primary key.
- `policy_address` (account) — globally unique cosmos account that signs Msgs on behalf of the Corporation (typically a Cosmos SDK `group_policy_address`).
- `did` (string) — globally unique DID of the Corporation; the same DID MUST NOT be `Corporation.did` of two distinct Corporation entries.
- `language`, `active_version`.

Resources in the VPR (Ecosystems, Credential Schemas, Participants, Participant Sessions, Trust Deposits, Authorizations, Fee Grants) are owned by a Corporation, not by individual accounts. Individual Verana accounts operate on behalf of a Corporation through delegated authorizations (see [[AUTHZ-CHECK-1]] and [[AUTHZ-CHECK-3]] in the VPR specification).

The `VERANA_CORPORATION_ID` environment variable identifies the Corporation this agent belongs to (by its `id`, uint64). The agent SHOULD resolve the rest of the Corporation entry — `policy_address`, `did`, `active_version` — from the indexer at startup.

#### Agent Account (vs_operator)

*This section is not normative.*

The agent's Verana account, derived from `VERANA_ACCOUNT_MNEMONIC`, acts as the `vs_operator` for on-chain operations. Each `Participant` entry the agent operates on carries a `vs_operator` field (see [[Participant]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#participant)) that MUST equal the agent's account.

#### Agent Account Authorizations

*This section is not normative.*

The `vs_operator` account should have been granted appropriate authorizations by the `VERANA_CORPORATION_ID` Corporation:

recommended:

- **`VSOperatorAuthorization`** (see [[VSOperatorAuthorization]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#vsoperatorauthorization) and [[ParticipantAuthorizationRecord]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#participantauthorizationrecord)): groups one or more `ParticipantAuthorizationRecord` entries, each keyed by `participant_id`, that grant the agent the right to execute, on behalf of the Corporation and in the context of that specific `Participant`, the message types declared in `record.msg_types` (typically `CreateOrUpdateParticipantSession`, `TriggerResolver`, `SetParticipantOPValidated`). See [[AUTHZ-CHECK-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#authz-check-3-vs-operator-authorization-checks).
  - If `record.with_feegrant` is `true` for the relevant `Participant`, the Corporation's `policy_address` covers transaction fees via an on-chain `FeeGrant` and the agent account does not need to be independently funded.
  - If `record.with_feegrant` is `false`, the agent account MUST have sufficient balance to pay transaction fees.

> If no `VSOperatorAuthorization` record exists for a `Participant`, the VS Agent MUST have VNA balance in its `vs_operator` account to cover transaction and trust fees, and the Corporation `policy_address` MUST co-sign every message that targets that `Participant`.

### [VSA-VTI-CFG] Configuration

#### [VSA-VTI-CFG-ENV] Container Environment Variables

The following environment variables MUST be provided when the VS Agent container is started.

##### [VSA-VTI-CFG-ENV-ID] Identity and Corporation

| Variable | Required | Description |
|---|---|---|
| `VERANA_CORPORATION_ID` | REQUIRED | The VPR `Corporation.id` (uint64) of the Corporation this agent belongs to. All on-chain resources (Ecosystems, Credential Schemas, Participants, Participant Sessions, ...) are owned by this Corporation. The agent SHOULD resolve the Corporation's `policy_address`, `did`, and `active_version` from the indexer at startup. |
| `VERANA_ACCOUNT_MNEMONIC` | REQUIRED | BIP-39 mnemonic used to derive the agent's Verana blockchain account (the agent's `vs_operator`). This account MUST have been granted a `VSOperatorAuthorization` by the `VERANA_CORPORATION_ID` Corporation, with one `ParticipantAuthorizationRecord` per `Participant` it operates under. |

##### [VSA-VTI-CFG-ENV-NET] Network Configuration

| Variable | Required | Description |
|---|---|---|
| `VERANA_RPC_ENDPOINT_URL` | REQUIRED | Verana blockchain RPC endpoint URL (e.g., `https://rpc.testnet.verana.network`). |
| `VERANA_INDEXER_BASE_URL` | REQUIRED | Verana indexer API URL (e.g., `https://idx.testnet.verana.network`). |
| `VERANA_CHAIN_ID` | OPTIONAL | Chain ID. |

##### [VSA-VTI-CFG-ENV-MODE] Agent Configuration Mode

Agent mode depends on whether you want the agent to obtain an ECS-Organization or ECS-Persona credential (standalone): Verifiable Trust VS-REQ-3; or delegated Verifiable Trust VS-REQ-4.

See [comparison between VS-REQ-3 and VS-REQ-4](https://verana-labs.github.io/verifiable-trust-spec/#vs-req-verifiable-service-basic-requirements-and-linked-vps).

| Variable | Required | Description |
|---|---|---|
| `AGENT_MODE` | OPTIONAL | One of `standalone` or `delegated`. Default: `standalone`. See [ECS Standalone Mode](#ecs-standalone-mode). |
| `AGENT_DELEGATED_PARENT_VS_DID` | CONDITIONAL | DID of the parent Verifiable Service to contact for obtaining a Service credential. REQUIRED when `AGENT_MODE` = `delegated`. |

### [VSA-VTI-DIDDOC] DID Document Service Entries

In addition to the `DIDCommMessaging` entry mandated by [[VS-SVC-2]](https://verana-labs.github.io/verifiable-trust-spec/#vs-svc-service-declaration) and the `LinkedVerifiablePresentation` entries produced by the credential-acquisition flows and by [[VSA-VTI-VTJSC] VTJSC Management](#vsa-vti-vtjsc-vtjsc-management), the VS Agent MAY publish a `VsAgentAdminAPI` service entry in its DID Document.

This entry is CONDITIONAL: it is REQUIRED when the agent's [Administration API](#administration-api) is intended to be accessed externally (e.g. by browsers, MCP servers, or other Verifiable Services). When present, it links the agent's DID to the public `https://` origin of the [Administration API](#administration-api), so that external clients can discover that URL directly from the agent's DID Document — removing the need for static `agent_did` → URL configuration in callers such as the [Verana MCP Server](../mcp-server/spec.md).

When present, the entry:

- MUST use `type: "VsAgentAdminAPI"`.
- MUST set `serviceEndpoint` to a single `https://` origin. The value MUST equal the `ADMIN_API_PUBLIC_URL` environment variable verbatim — scheme + host + optional port, no trailing path.
- MAY use any DID-relative fragment as its `id`; consumers MUST locate the entry by `type`, not by fragment.
- MUST be produced and maintained automatically by the agent at every DID Document publication.
- MUST NOT be created, modified, or deleted via the [[VSA-ADM-SE] Service Endpoint Management](#vsa-adm-se-service-endpoint-management) admin methods.

Example fragment of the resulting DID Document:

```json
{
  "service": [
    {
      "id": "did:example:agent#admin-api",
      "type": "VsAgentAdminAPI",
      "serviceEndpoint": "https://admin.agent.example.com"
    }
  ]
}
```


### [VSA-VTI-NOTIF] Notifications

The agent MUST maintain a permanent WebSocket connection to the VPR indexer's [`IDX-INDEXER-SUB-1` Subscribe Indexer Events](../verana-indexer/spec.md#idx-indexer-sub-1-subscribe-indexer-events) endpoint:

```text
WS {VERANA_INDEXER_BASE_URL}/v4/indexer/subscribe
```

After receiving the indexer's `ready` message, the agent MUST send a `subscribe` control message scoped to its own DID:

```json
{
   "action": "subscribe",
   "dids":   ["{agent DID}"]
}
```

An agent that wants the broader corp-scoped view (its own Participant entry plus every other resource owned by its Corporation — sibling Participants, controlled Ecosystems, embedded sub-entities — plus every Participant the Corporation validates one hop down the tree) MAY instead send `{ "action": "subscribe", "corporationId": <Participant.corporation_id> }` per [`IDX-INDEXER-SUB-1`](../verana-indexer/spec.md#idx-indexer-sub-1-subscribe-indexer-events). The default scope is the agent's own DID.

The indexer then streams one block envelope per processed block, in strictly increasing `block` order. Each envelope carries `{ type: "block", block, blockTime, events[] }`; each entry of `events[]` is an [`IndexerTransactionEvent`](../verana-indexer/spec.md#idx-indexer-qry-6-list-indexer-events) — `type: "indexer-event"`, `event_type` (Cosmos action name, e.g. `StartParticipantOP`), `did`, `block_height`, `tx_hash`, `timestamp`, and `payload: { module, action, message_type, tx_index, message_index, sender, related_dids[], entity_type, entity_id }` — in `(payload.tx_index, payload.message_index)` order. An envelope with `events[]: []` carries no work but still serves as a per-block heartbeat for gap detection.

The indexer tracks all on-chain entities where the agent's DID is `Corporation.did`, `Ecosystem.did`, or `Participant.did` — transitively covering the embedded `CredentialSchema`, `GovernanceFrameworkVersion`, `ParticipantSession`, `VSOperatorAuthorization`, and `FeeGrant` entries that reference those parents — and emits an event whenever any of those entities is created or modified by a transaction.

**Catch-up and resume:** The WebSocket stream does not deliver historical events on connect. The agent MUST persist the highest `block_height` it has fully processed and, on (re)connect, MUST first call [`GET /v4/indexer/events?dids=<agent DID>&after_block_height=<last_seen_block>`](../verana-indexer/spec.md#idx-indexer-qry-6-list-indexer-events) (or `?corporation_id=<Participant.corporation_id>` if the agent uses the corp-scoped subscription) to drain any missed events to exhaustion **before** processing new WebSocket messages. Events that have already been processed (same `tx_hash` + `message_index`) MUST be discarded as idempotent duplicates.

If the WebSocket connection is lost, the agent MUST reconnect with exponential backoff and re-apply the catch-up pattern above.

The following tables list all VPR transactions that produce an `IndexerTransactionEvent` for the subscribed agent's DID, grouped by the role the agent plays in each event. The `event_type` column matches the `IndexerTransactionEvent.event_type` field.

Each notification must be associated with a specific handler interface in the VS Agent. A default implementation will be provided to handle the most important notifications. Developers can implement their own handlers to override VS Agent default handlers (or provide an implementation for notifications not handled by the default implementation).

Other `event_type` values not listed below COULD be received and SHOULD be ignored.

> Independently from the indexer event stream above, the agent MAY also subscribe to the [Verifiable Trust Resolver subscription](../verana-indexer/spec.md#idx-vt-sub-1-subscribe-changes) at `WS {VERANA_INDEXER_BASE_URL}/v4/verifiable-trust/subscribe` to receive aggregated trust-resolution change envelopes about its DID (e.g., when its `trusted` boolean flips). The two streams are complementary: `/v4/indexer/subscribe` is the source of truth for on-chain transactions; `/v4/verifiable-trust/subscribe` is a derived, debounced view of the resolver state.

#### [VSA-VTI-NOTIF-CO] Corporation Notifications

These notifications are emitted when the agent's DID is the `did` of a `Corporation` entry (`Corporation.did = agent DID`). Per the per-Corporation `did` uniqueness invariant, at most one Corporation entry exists for the agent's DID.

| `event_type` | Description | Default Handler Implementation |
| --- | --- | --- |
| `CreateNewCorporation` [[MOD-CO-MSG-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-co-msg-1-create-new-corporation) | A new Corporation has been created with the agent's DID. | N/A. |
| `UpdateCorporation` [[MOD-CO-MSG-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-co-msg-2-update-corporation) | The Corporation has been updated (DID rotation, language, etc.). | If `Corporation.did` rotation moves the binding away from this agent's DID **and** the agent uses the per-DID subscription scope (`dids: [agent DID]`), the agent SHOULD log a warning and stop processing further events on the previous DID. Agents using the corp-scoped subscription (`corporationId: <Participant.corporation_id>`) are unaffected by `Corporation.did` rotation since the subscription scope is keyed on the stable `Corporation.id`, not on its DID. |
| `AddGovernanceFrameworkDocument` [[MOD-GF-MSG-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-gf-msg-1-add-governance-framework-document) | A Governance Framework Document has been added to the Corporation's CGF. | N/A. |
| `IncreaseActiveGovernanceFrameworkVersion` [[MOD-GF-MSG-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-gf-msg-2-increase-active-governance-framework-version) | The Corporation's active CGF version has been incremented. | N/A. |

#### [VSA-VTI-NOTIF-ES] Ecosystem Controller Notifications

These notifications are emitted when objects in an Ecosystem controlled by the agent's DID (`Ecosystem.did = agent DID`) are created or modified. A single DID MAY be the `did` of several Ecosystem entries.

| `event_type` | Description | Default Handler Implementation |
| --- | --- | --- |
| `CreateNewEcosystem` [[MOD-ES-MSG-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-es-msg-1-create-new-ecosystem) | A new Ecosystem has been created with the agent's DID. | N/A. |
| `UpdateEcosystem` [[MOD-ES-MSG-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-es-msg-2-update-ecosystem) | The Ecosystem has been updated. | N/A. |
| `ArchiveEcosystem` [[MOD-ES-MSG-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-es-msg-3-archive-ecosystem) | The Ecosystem has been archived or unarchived. | N/A. |
| `AddGovernanceFrameworkDocument` [[MOD-GF-MSG-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-gf-msg-1-add-governance-framework-document) | A Governance Framework Document has been added to the Ecosystem's EGF. | N/A. |
| `IncreaseActiveGovernanceFrameworkVersion` [[MOD-GF-MSG-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-gf-msg-2-increase-active-governance-framework-version) | The Ecosystem's active EGF version has been incremented. | N/A. |
| `CreateNewCredentialSchema` [[MOD-CS-MSG-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-msg-1-create-new-credential-schema) | A new Credential Schema has been created in an Ecosystem the agent controls. | Trigger automatic VTJSC publication (see [VTJSC Management](#vsa-vti-vtjsc-vtjsc-management)). |
| `UpdateCredentialSchema` [[MOD-CS-MSG-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-msg-2-update-credential-schema) | A Credential Schema has been updated (e.g., onboarding validity periods). | N/A. |
| `ArchiveCredentialSchema` [[MOD-CS-MSG-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-msg-3-archive-credential-schema) | A Credential Schema has been archived or unarchived. | N/A. |

#### [VSA-VTI-NOTIF-PP] Participant Notifications

These notifications are emitted when a `Participant` entry whose `did` equals the agent's DID is created or transitions state, and when an event affecting such a `Participant` is emitted toward an upstream/downstream `Participant`. All notifications are sent both to the **Applicant** (the `Participant` whose `did` matches the agent's DID) and to the **Validator** (the upstream `Participant` referenced by `applicant_participant.validator_participant_id`, if its `did` also matches the agent's DID for the validator's own subscription).

| `event_type` | Description | Default Handler Implementation |
| --- | --- | --- |
| `StartParticipantOP` [[MOD-PP-MSG-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-1-start-participant-op) | An applicant has started a new Onboarding Process targeting a validator `Participant` of this agent. | For Validator: N/A. For Applicant: Progress the credential acquisition flow (see [new onboarding process](#vsa-vti-flow-op-new-new-onboarding-process)). |
| `RenewParticipantOP` [[MOD-PP-MSG-2]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-2-renew-participant-op) | An applicant has renewed an existing Onboarding Process. | For Validator: N/A. For Applicant: Progress the credential acquisition flow (see [renew onboarding process](#vsa-vti-flow-op-renew-renew-onboarding-process)). |
| `SetParticipantOPValidated` [[MOD-PP-MSG-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-3-set-participant-op-to-validated) | Validator has set the agent's `Participant.op_state` to `VALIDATED`. | For Validator: Progress the credential acquisition flow (see [new onboarding process](#vsa-vti-flow-op-new-new-onboarding-process)). For Applicant: N/A. |
| `CreateRootParticipant` [[MOD-PP-MSG-7]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-7-create-root-participant) | A root `Participant` (no validator parent) has been created with the agent's DID. | N/A. |
| `SetParticipantEffectiveUntil` [[MOD-PP-MSG-8]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-8-set-participant-effective-until) | Validator or ancestor has set or adjusted the agent's `Participant.effective_until`. | N/A. |
| `RevokeParticipant` [[MOD-PP-MSG-9]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-9-revoke-participant) | Validator, ancestor, or Ecosystem controller has revoked the agent's `Participant` entry. | Remove the corresponding linked VP from the DID Document (if any) and delete the credential from the credential store (HOLDER `Participant` only). For non-HOLDER `Participant`, terminate every in-flight downstream flow it serves as Validator for (see [Revoke Participant / Slash Participant Trust Deposit](#vsa-vti-flow-op-revoke-revoke-participant--slash-participant-trust-deposit)). |
| `SlashParticipantTrustDeposit` [[MOD-PP-MSG-12]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-12-slash-participant-trust-deposit) | Validator, ancestor, or Ecosystem controller has slashed the agent's `Participant.deposit`. | Same as `RevokeParticipant`: clean up linked VP / credential / downstream flow state. |
| `RepayParticipantSlashedTrustDeposit` [[MOD-PP-MSG-13]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-13-repay-participant-slashed-trust-deposit) | The agent's slashed trust deposit has been repaid (confirmation of own tx). | N/A. |
| `CancelParticipantOPLastRequest` [[MOD-PP-MSG-6]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-6-cancel-participant-op-last-request) | An applicant has cancelled a pending Onboarding Process. | Clean up the associated flow state (see [Cancel OP Last Request](#vsa-vti-flow-op-cancel-cancel-op-last-request)). |
| `SelfCreateParticipant` [[MOD-PP-MSG-14]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-14-self-create-participant) | The agent's `Participant` entry has been self-created on-chain (OPEN onboarding mode). | Record the resulting `participant_id` for later use (see [Participant Self Creation](#vsa-vti-flow-self-participant-self-creation)). |
| `TriggerResolver` [[MOD-PP-MSG-15]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-15-trigger-resolver) | A trust-resolution refresh has been triggered for the agent's `Participant` entry. | N/A (off-chain consumers may react). |

#### [VSA-VTI-NOTIF-AUTH] Authorization Notifications

These notifications are emitted whenever a `VSOperatorAuthorization` whose `vs_operator` is the agent's `vs_operator` account is created, modified, or revoked, **and** the affected `ParticipantAuthorizationRecord` references a `Participant` whose `did` is the agent's DID. They reach the agent through the same DID-scoped indexer subscription via the parent `Participant` event (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)).

| `event_type` | Description | Default Handler Implementation |
| --- | --- | --- |
| `GrantVSOperatorAuthorization` [[MOD-DE-MSG-5]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-de-msg-5-grant-vs-operator-authorization) | The Corporation has granted the agent's `vs_operator` one or more `ParticipantAuthorizationRecord` entries within a `VSOperatorAuthorization`. | Refresh the cached `VSOperatorAuthorization`; `CreateOrUpdateParticipantSession`, `TriggerResolver`, and `SetParticipantOPValidated` MAY now be signed for the newly authorized `Participant` entries. |
| `RevokeVSOperatorAuthorization` [[MOD-DE-MSG-6]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-de-msg-6-revoke-vs-operator-authorization) | One or more of the agent's `ParticipantAuthorizationRecord` entries have been revoked. The parent `VSOperatorAuthorization` is deleted when its last record is removed. | Invalidate the cached records. Stop signing `CreateOrUpdateParticipantSession`, `TriggerResolver`, and `SetParticipantOPValidated` for the affected `Participant` entries until a new authorization is granted. |
| `UpdateVSOperatorAuthorizationExpiration` [[MOD-DE-MSG-9]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-de-msg-9-update-vs-operator-authorization-expiration) | A `ParticipantAuthorizationRecord.expiration` has been updated. | Refresh the cached record; recompute remaining feegrant validity if `record.with_feegrant` is true. |

### [VSA-VTI-BOOT] Bootstrap Sequence

When the VS Agent starts, it SHOULD execute the following steps in order:

1. **Validate configuration**: All REQUIRED environment variables MUST be present and well-formed. If any variable is missing or invalid, the agent MUST fail with a descriptive error.

2. **Derive Verana account**: Derive the blockchain account from `VERANA_ACCOUNT_MNEMONIC` and store the derived address as the agent's `vs_operator` account.

3. **Start DIDComm message processor**: Enable DIDComm for outgoing messages.

4. **Catch up missed events**: Call [`GET {VERANA_INDEXER_BASE_URL}/v4/indexer/events?dids=<agent DID>&after_block_height=<last_seen_block>`](../verana-indexer/spec.md#idx-indexer-qry-6-list-indexer-events) (or `?corporation_id=<VERANA_CORPORATION_ID>` if the agent uses the corp-scoped subscription per [[VSA-VTI-NOTIF]](#vsa-vti-notif-notifications)), paginating to exhaustion, where `last_seen_block` is the highest block height the agent has fully processed in its persistent state (0 on first start). Process each `IndexerTransactionEvent` returned, then advance `last_seen_block` to the highest `block_height` observed.

5. **Connect to indexer WebSocket**: Establish a persistent WebSocket connection to [`WS {VERANA_INDEXER_BASE_URL}/v4/indexer/subscribe`](../verana-indexer/spec.md#idx-indexer-sub-1-subscribe-indexer-events) for real-time awareness of on-chain changes (see [Notifications](#vsa-vti-notif-notifications)). After receiving the indexer's `ready` message, send `{ "action": "subscribe", "dids": ["<agent DID>"] }`. The indexer then streams one block envelope per processed block; process each envelope's `events[]` entries (each an `IndexerTransactionEvent`) in `(payload.tx_index, payload.message_index)` order. Any event with `block_height <= last_seen_block` MUST be discarded as a duplicate. These actions may trigger outgoing DIDComm messages.

6. **Start processing the queued incoming DIDComm messages**.

> If no `VSOperatorAuthorization` has been granted to this VS Agent AND the account balance of `vs_operator` is equal to 0, a warning SHOULD be printed in the log.

### [VSA-VTI-VTJSC] VTJSC Management

Each Verifiable Trust Ecosystem publishes one or more `CredentialSchema` entries within its Ecosystem (`Ecosystem.id`). For each such schema, the Ecosystem controller (the VS Agent whose DID is `Ecosystem.did`) MUST attach to its own DID Document a corresponding VTJSC — a JSON Schema Credential that binds the on-chain schema definition to the controlling Ecosystem DID (see [VT-JSON-SCHEMA-CRED-W3C](https://verana-labs.github.io/verifiable-trust-spec/#vt-json-schema-cred-w3c-verifiable-trust-json-schema-credential) and [VT-ECOSYSTEM-DIDDOC](https://verana-labs.github.io/verifiable-trust-spec/#vt-ecosystem-diddoc-ecosystem-did-document)).

The VS Agent takes care of the full VTJSC lifecycle automatically. The flow is entirely driven by on-chain events — no Applicant, no Validator, and no DIDComm session is involved.

```mermaid
sequenceDiagram
    participant EC as Ecosystem Controller
    participant VPR as VPR (Chain)
    participant Agent as Agent (Ecosystem Controller)

    EC->>VPR: 1. CreateNewCredentialSchema
    VPR->>Agent: 2. CreateNewCredentialSchema notification (via Indexer)
    Note over Agent: 3. generate VTJSC, wrap in VP,<br/>publish as LinkedVerifiablePresentation<br/>in DID Document
    Note over Agent: 4. serve VP at the service endpoint
```

**Step-by-step**:

1. The Ecosystem controller submits a [`CreateNewCredentialSchema` (MOD-CS-MSG-1)](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-msg-1-create-new-credential-schema) transaction on-chain, referencing the Ecosystem (`Ecosystem.id`) controlled by the agent's DID. `CredentialSchema` entries in the VPR are immutable once created, so this event is a one-off trigger per schema.

2. The VPR indexer emits a `CreateNewCredentialSchema` event (see [Ecosystem Controller Notifications](#vsa-vti-notif-es-ecosystem-controller-notifications)) to the Ecosystem controller — i.e., the agent.

3. The agent MUST automatically produce and publish the corresponding VTJSC:
   - Generate a VTJSC conforming to [VT-JSON-SCHEMA-CRED-W3C], whose `credentialSubject.jsonSchema.$ref` points to the on-chain `CredentialSchema` entry and whose `credentialSubject.digestSRI` carries the SRI digest of the referenced JSON schema content. The VTJSC is signed with the Ecosystem's DID key.
   - Wrap the VTJSC in a Verifiable Presentation signed by the same Ecosystem DID.
   - Add a `LinkedVerifiablePresentation` service entry to the Ecosystem's DID Document, with a fragment that starts with `#vpr-schemas-` and ends with `-vtjsc-vp`, as required by [VT-ECOSYSTEM-DIDDOC].

4. The agent MUST serve the VP at its declared `serviceEndpoint` so that any wallet, issuer, or verifier resolving the Ecosystem DID can retrieve and verify the VTJSC.

> Because `CredentialSchema` entries in the VPR are **immutable**, the agent never has to update an existing VTJSC — it only generates a new one whenever a new schema is created in an Ecosystem it controls.

### Participant and Credential Acquisition Logic

*This section is non normative.*

Ecosystems are created in a VPR and define one or more `CredentialSchema` entries. Credential Schemas have different onboarding modes (`issuer_onboarding_mode`, `verifier_onboarding_mode`, `holder_onboarding_mode`). These modes define how applicants onboard the ecosystem, and have a direct effect on the workflows used.

Onboarding modes are [defined here](https://verana-labs.github.io/verifiable-trust-vpr-spec/#credential-schemas-and-participants).

#### ECS Participants and Credentials

*This section is non normative.*

To be a Verifiable Service, an agent MUST obtain `Participant` entries (HOLDER and/or ISSUER) and the corresponding ECS credentials from a trusted ECS Ecosystem. The vs-agent implements two modes, as specified in the Verifiable Trust spec. They are configured via the `AGENT_MODE` env variable.

> For ECS-Organization, ECS-Persona, and ECS-Service credential schemas, `holder_onboarding_mode` is always set to `ISSUER_ONBOARDING_PROCESS`. See [[VT-ECS-JSON-SCHEMA-VPR-CONFIG]](https://verana-labs.github.io/verifiable-trust-spec/#vt-ecs-json-schema-vpr-config-essential-schema-vpr-configuration).

##### ECS Standalone Mode

In standalone mode:

1. Applicant starts a [new onboarding process flow](#vsa-vti-flow-op-new-new-onboarding-process) to obtain an **ECS-Organization** or **ECS-Persona** HOLDER `Participant` and its corresponding credential via DIDComm from an authorized ISSUER registered under a trusted ECS Ecosystem.
2. Applicant starts a [new onboarding process flow](#vsa-vti-flow-op-new-new-onboarding-process) to obtain an ISSUER `Participant` for the **Service** credential schema from the same trusted ECS Ecosystem.

> As defined in [[VS-CONN-VS]](https://verana-labs.github.io/verifiable-trust-spec/#vs-conn-vs-requirements-for-a-vs-to-accept-a-connection-from-another-service), a validator agent CAN accept connections from a not-yet-verifiable agent if and only if the purpose of the connection is the issuance of [VT-ECS-ORG-CRED-W3C], [VT-ECS-PERSONA-CRED-W3C], or [VT-ECS-SERVICE-CRED-W3C] credentials.

##### ECS Delegated Mode

In delegated mode, the agent contacts the parent VS specified by `AGENT_DELEGATED_PARENT_VS_DID` to obtain its Service credential:

1. Applicant starts a [new onboarding process flow](#vsa-vti-flow-op-new-new-onboarding-process) to obtain a HOLDER `Participant` and its corresponding **Service credential** from the parent VS via DIDComm.

The parent VS (`AGENT_DELEGATED_PARENT_VS_DID`) MUST already hold an ISSUER `Participant` for the Service schema and MUST be a Verifiable Service. If the agent cannot reach the parent VS, or the parent VS rejects the request, or the parent agent IS NOT verifiable, the agent MUST fail with a descriptive error.

#### Logic for Other Participants and Credentials

*This section is non normative.*

To obtain a `Participant` entry and/or credential from a specific issuer of a `CredentialSchema` `cs` in a specific Ecosystem, the flow to choose depends on:

- the Credential Schema configuration (`issuer_onboarding_mode`, `verifier_onboarding_mode`, `holder_onboarding_mode`).
- the `role` of the `Participant` the Applicant will request.

**Important**: refer to [Credential Schemas and Participants](https://verana-labs.github.io/verifiable-trust-vpr-spec/#credential-schemas-and-participants) in the VPR spec.

The flows described in the next section provide a list of possible Applicant/Validator combinations for which they are relevant.

### Participant and Credential Acquisition Flows

*This section is non normative.*

In all flows below, actors represented as Applicant and Validator can be: an agent, or any operator of a corporation that has been granted (authorized) the execution of the corresponding VPR Messages.

> Applicant is always the peer that initiates a connection to a Validator.

#### [VSA-VTI-FLOW-OP] Onboarding Processes

Possible Applicant/Validator combinations:

| Applicant `role` | Validator `role` | Schema Mode Condition |
|---|---|---|
| ISSUER_GRANTOR | ECOSYSTEM | `issuer_onboarding_mode` = `GRANTOR_ONBOARDING_PROCESS` |
| VERIFIER_GRANTOR | ECOSYSTEM | `verifier_onboarding_mode` = `GRANTOR_ONBOARDING_PROCESS` |
| ISSUER | ISSUER_GRANTOR | `issuer_onboarding_mode` = `GRANTOR_ONBOARDING_PROCESS` |
| ISSUER | ECOSYSTEM | `issuer_onboarding_mode` = `ECOSYSTEM_ONBOARDING_PROCESS` |
| VERIFIER | VERIFIER_GRANTOR | `verifier_onboarding_mode` = `GRANTOR_ONBOARDING_PROCESS` |
| VERIFIER | ECOSYSTEM | `verifier_onboarding_mode` = `ECOSYSTEM_ONBOARDING_PROCESS` |
| HOLDER | ISSUER | `holder_onboarding_mode` = `ISSUER_ONBOARDING_PROCESS` |

##### [VSA-VTI-FLOW-OP-NEW] New Onboarding Process

```mermaid
sequenceDiagram

    participant VPR as VPR (Chain)
    participant Validator as Agent (Validator)

    Applicant Operator->>VPR: 1. StartParticipantOP
    VPR-->>Applicant Agent: participant_id (op_state=PENDING)
    Applicant Agent->>Validator: 2. DIDComm connect
    Applicant Agent->>Validator: 3. OR: participant_id, participant_session_id,<br/>cred. claims, proofs, ...
    Validator-->>Applicant Agent: 4. (optional) out-of-band info collection
    Validator->>VPR: 5. SetParticipantOPValidated

    Note over Applicant Agent,Validator: All steps below are optional

    Note over Validator: 6. Generate credential<br/>(sign + compute digest)
    Validator->>VPR: 7. CreateOrUpdateParticipantSession
    Validator->>Applicant Agent: 6. Credential offer, applicant requests
    Note over Validator: Sign credential<br/>+ compute digest
    Validator->>VPR: 7. CreateOrUpdateParticipantSession
    Validator->>Applicant Agent: 8. Deliver signed credential
    Applicant Agent->>VPR: 9. Verify validator + digest
    Applicant Agent->>Validator: 10. Accept Credential
    Note over Applicant Agent: 11. Store credential
    Note over Applicant Agent: 12. (optional) VP in DID Doc
    Applicant Agent->>VPR: 13. (optional) TriggerResolver
```

**Step-by-step**:

1. The applicant submits `StartParticipantOP` on-chain, referencing the validator's `validator_participant_id` and all other required attributes as specified in [[MOD-PP-MSG-1] Start Participant OP](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-1-start-participant-op). This creates a `Participant` entry with `op_state=PENDING` and returns its `id` (`participant_id`). The VS Agent is notified.

2. The agent connects to the validator via DIDComm (see [DIDComm Protocol Binding](#vsa-vti-flow-didcomm-didcomm-protocol-binding)). The validator MUST verify that the connecting agent is compliant with [[VS-CONN-VS]](https://verana-labs.github.io/verifiable-trust-spec/#vs-conn-vs-requirements-for-a-vs-to-accept-a-connection-from-another-service) before accepting the connection.

3. The applicant sends an **OR (Onboarding Request)** message containing the following (to be used later for `CreateOrUpdateParticipantSession`):
   - `participant_id`: The applicant `Participant.id`.
   - `participant_session_id`: A UUID for the `ParticipantSession`.

   The applicant MAY also include credential claims (if the flow should issue a credential) and supporting proofs, if already available. The validator MUST either accept the information and proceed, or refuse it with an error code and descriptive error message. If refused, the applicant MAY retry with corrected information.

> Note: this onboarding request must be executed when a new onboarding process is started or if an existing onboarding process is renewed.

4. If the validator requires additional information to generate the credential (e.g., missing claims or proofs), the validator MAY send a link to the applicant for an out-of-DIDComm flow (such as a web form or portal) to collect the missing data.

5. After validation, the validator calls `SetParticipantOPValidated` ([[MOD-PP-MSG-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-3-set-participant-op-to-validated)) on-chain, changing `op_state` to `VALIDATED`. The VS Agent is notified.

All steps below are optional and executed only if the validator issues a credential.

6. The validator generates and signs the credential, and computes the digest.

7. The **validator** calls `CreateOrUpdateParticipantSession` ([[MOD-PP-MSG-10]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-10-create-or-update-participant-session)) on-chain (see [Agent Account Authorizations](#agent-account-authorizations)). The credential MUST NOT be delivered until this transaction succeeds.

8. The validator delivers the signed credential to the applicant via the existing DIDComm session.

9. The applicant MUST verify the received credential before accepting it:
   - Verify the validator is authorized by the ecosystem to issue credentials for this schema (`validator_participant.role` is `ISSUER` and the `Participant` is active).
   - Recompute the credential's digest and verify it matches the digest recorded on-chain in the `ParticipantSession` updated in step 7.
   - If either check fails, the applicant MUST reject the credential and log the error.

10. The applicant sends a **CRED_ACCEPT** message to the validator, confirming that the credential has been verified and accepted.

11. The applicant stores the credential in its credential store.

12. **Optionally**, the applicant links the credential as a `LinkedVerifiablePresentation` in its DID Document per [[VT-CRED-W3C-LINKED-VP]](https://verana-labs.github.io/verifiable-trust-spec/#vt-cred-w3c-linked-vp-w3c-vtc-linked-vp). This is required for ECS credentials but optional for other credential types.

13. **Optionally**, the applicant calls `TriggerResolver` ([[MOD-PP-MSG-15]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-15-trigger-resolver)) on-chain to refresh its Verifiable Service resolution state. The applicant SHOULD call `TriggerResolver` when:
    - it has just become a Verifiable Service by newly complying with [[VS-REQ]](https://verana-labs.github.io/verifiable-trust-spec/#vs-req-verifiable-service-basic-requirements-and-linked-vps); or
    - it has added or removed a `LinkedVerifiablePresentation` entry in its DID Document.

##### [VSA-VTI-FLOW-OP-RENEW] Renew Onboarding Process

This flow is used when the Applicant wants to extend the validity of an existing `Participant` whose `op_state` is `VALIDATED`, by re-running an Onboarding Process with the same Validator.

```mermaid
sequenceDiagram
    participant VPR as VPR (Chain)
    participant Validator as Agent (Validator)

    Applicant Operator->>VPR: 1. RenewParticipantOP(participant_id)
    VPR-->>Applicant Agent: op_state=PENDING
    Applicant Agent->>Validator: 2. DIDComm (re)connect
    Applicant Agent->>Validator: 3. OR: participant_id, participant_session_id,<br/>updated claims, proofs
    Validator-->>Applicant Agent: 4. (optional) out-of-band info collection
    Validator->>VPR: 5. SetParticipantOPValidated
    Note over VPR: op_exp += validity_period

    Note over Applicant Agent,Validator: ... credential offer / accept / store / update VP ...<br/>(same as New Onboarding Process steps 6–12)
```

**Preconditions**:

- `applicant_participant.op_state` MUST be `VALIDATED`. Renewal cannot be initiated while a previous request is still `PENDING` — the Applicant MUST first cancel the pending request (see [Cancel OP Last Request](#vsa-vti-flow-op-cancel-cancel-op-last-request)).
- The `Participant` cannot be slashed, repaid, or revoked.
- `applicant_participant.validator_participant_id` MUST still be an [active Participant](https://verana-labs.github.io/verifiable-trust-vpr-spec/#term:active-participant). If the Validator's `Participant` is no longer active, the Applicant MUST start a [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) with another Validator instead.
- Renewal MUST NOT change `validation_fees`, `issuance_fees`, `verification_fees`, `issuance_fee_discount`, or `verification_fee_discount`. To change any of these, the Applicant MUST start a [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process).

**Step-by-step**:

1. The Applicant submits `RenewParticipantOP` on-chain referencing its own `participant_id`, as specified in [[MOD-PP-MSG-2] Renew Participant OP](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-2-renew-participant-op). On success, `op_state` returns to `PENDING`, and the corresponding validation trust deposit and (if any) validation fees are re-escrowed.

2. The Applicant connects to the same Validator via DIDComm (see [DIDComm Protocol Binding](#vsa-vti-flow-didcomm-didcomm-protocol-binding)). If a DIDComm session was kept open from the previous flow, that session SHOULD be reused. The Validator MUST verify that the connecting agent is compliant with [[VS-CONN-VS]](https://verana-labs.github.io/verifiable-trust-spec/#vs-conn-vs-requirements-for-a-vs-to-accept-a-connection-from-another-service) before accepting the connection.

3. The Applicant sends an **OR (Onboarding Request)** message containing `participant_id` and (RECOMMENDED) a fresh `participant_session_id`. The Applicant MAY include updated credential claims and supporting proofs. The Validator MUST recognise that `participant_id` corresponds to a renewal (its previous flow was `COMPLETED`) and reuse / update the associated flow state rather than create a new one.

4. If the Validator requires fresh information for the renewal (e.g., re-confirming identity, updated documentation), it MAY send an `OOB_LINK` to the Applicant for an out-of-DIDComm flow.

5. After validation, the Validator calls `SetParticipantOPValidated` on-chain. For a renewal, the VPR enforces that `validation_fees`, `issuance_fees`, `verification_fees`, and fee discounts MUST equal the values originally agreed; any modification will be rejected on-chain. On success, `op_state` returns to `VALIDATED` and `op_exp` is extended by the schema-defined `validity_period`.

Steps 6–13 are identical to those of [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) and are executed only if the Validator chooses to issue an updated credential as part of the renewal. If a credential is delivered:

- The Applicant MUST replace the previously stored credential with the updated one in its credential store and delete any previously created linked-VP linked to the old credential.
- **Optionally**, the Applicant creates the corresponding `LinkedVerifiablePresentation` entry in its DID Document.
- **Optionally**, the Applicant calls `TriggerResolver` on-chain to refresh its Verifiable Service resolution state. The Applicant SHOULD call `TriggerResolver` when:
  - it has just become a Verifiable Service by newly complying with [[VS-REQ]](https://verana-labs.github.io/verifiable-trust-spec/#vs-req-verifiable-service-basic-requirements-and-linked-vps); or
  - it has added or removed a `LinkedVerifiablePresentation` entry in its DID Document.

##### [VSA-VTI-FLOW-OP-CANCEL] Cancel OP Last Request

This flow describes what happens when the Applicant cancels the in-flight Onboarding Request (either a `StartParticipantOP` or a `RenewParticipantOP`) before the Validator has set `op_state` to `VALIDATED`. On-chain cancellation is exclusively driven by the [`CancelParticipantOPLastRequest`](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-6-cancel-participant-op-last-request) message and is only valid when `applicant_participant.op_state` is `PENDING`.

```mermaid
sequenceDiagram
    participant VPR as VPR (Chain)
    participant Validator as Agent (Validator)

    Applicant Operator->>VPR: 1. CancelParticipantOPLastRequest(participant_id)
    Note over VPR: op_current_fees refunded<br/>op_current_deposit released<br/>op_state = TERMINATED<br/>(or VALIDATED if op_exp != null)
    VPR->>Validator: 2. CancelParticipantOPLastRequest event (via Indexer)
    VPR->>Applicant Agent: 3. own-tx confirmation (via Indexer)
    Applicant Agent-->>Validator: 4. (optional) informational message over DIDComm
    Applicant Agent-->>Validator: 5. (if TERMINATED) close DIDComm session
```

**Preconditions**:

- `applicant_participant.op_state` MUST be `PENDING`.
- `applicant_participant.deposit` MUST NOT be in a slashed-and-unrepaid state.

**On-chain effect** (executed atomically by [[MOD-PP-MSG-6]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-6-cancel-participant-op-last-request)):

- If `applicant_participant.op_exp` is `null` (the `Participant` was never validated — i.e., the cancellation targets a `StartParticipantOP`): `op_state` is set to `TERMINATED`.
- If `applicant_participant.op_exp` is not `null` (the `Participant` had previously been `VALIDATED` — i.e., the cancellation targets a `RenewParticipantOP`): `op_state` is restored to `VALIDATED` and the previous validation result still stands.
- Escrowed `op_current_fees` are refunded to the Applicant's `corporation`.
- `op_current_deposit` is removed from the Applicant's trust deposit.

**Applicant behaviour**:

1. Submit `CancelParticipantOPLastRequest` on-chain referencing `participant_id`.
2. On confirmation, the Applicant receives a `CancelParticipantOPLastRequest` notification for its own transaction (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)). The handler updates local Flow State based on the resulting on-chain `op_state`:
   - **`TERMINATED`** (cancelled a `StartParticipantOP`): set Connection State to `TERMINATED` and Flow State to `TERMINATED_BY_APPLICANT`. The Applicant MAY send a final `ERROR` (or otherwise informational) message to the Validator over DIDComm before closing the session.
   - **`VALIDATED`** (cancelled a `RenewParticipantOP`): keep Connection State as `ESTABLISHED` and Flow State as `COMPLETED`. The DIDComm session SHOULD remain open for future Validator updates (revocation notices, credential refresh, etc.).
3. Clean up any local resources associated with the cancelled request (pending `OOB_LINK` URLs, draft claim data, etc.).

**Validator behaviour**:

1. The Validator receives the `CancelParticipantOPLastRequest` notification from the indexer for an `applicant_participant_id` matching one of its in-flight flows (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)).
2. The Validator MUST stop any pending validation work for this flow:
   - Abort off-chain validation tasks.
   - Invalidate any outstanding `OOB_LINK` URL.
   - Discard any pre-generated credential that has not yet been delivered.
3. Update local Flow State based on the resulting on-chain `op_state`:
   - **`TERMINATED`**: set Connection State to `TERMINATED` and Flow State to `TERMINATED_BY_APPLICANT`. The Validator MAY close the DIDComm session.
   - **`VALIDATED`**: keep Connection State as `ESTABLISHED` and Flow State as `COMPLETED`. No further action toward the Applicant is required; the previous credential (if any) remains valid.

> There is no dedicated DIDComm message for cancellation. Both peers learn about it via the on-chain `CancelParticipantOPLastRequest` notification delivered by the indexer. Any DIDComm message exchanged between the peers after cancellation is informational only.

##### [VSA-VTI-FLOW-OP-REVOKE] Revoke Participant / Slash Participant Trust Deposit

Possible Applicant/Validator combinations: All.

`RevokeParticipant` ([[MOD-PP-MSG-9]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-9-revoke-participant)) and `SlashParticipantTrustDeposit` ([[MOD-PP-MSG-12]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-12-slash-participant-trust-deposit)) cause an existing `Participant` entry `p1` to become permanently unusable. Both messages are handled identically by VS Agents — `p1` can no longer be used as the basis for any flow, and any in-flight flow that depends on `p1` MUST be terminated.

The two messages differ only on-chain:

| Aspect | RevokeParticipant | SlashParticipantTrustDeposit |
| --- | --- | --- |
| On-chain state change | `p1.revoked = now` | `p1.slashed = now`; `slashed_deposit += amount`; trust deposit burned |
| Authorized initiators | ancestor validator, grantee `corporation`, or Ecosystem controller | ancestor validator or Ecosystem controller (NOT the grantee) |
| `Participant` must be active | yes | no — MAY be applied to expired or revoked Participants |
| VS Operator Authorization (ISSUER / VERIFIER only) | revoked | revoked |

When `p1` is revoked or slashed, an indexer event (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)) is delivered to:

- the **Applicant of `p1`** (the grantee whose `Participant` has been revoked); and
- the **Validator of `p1`** (the validator that originally issued `p1`, plus every ancestor validator and the Ecosystem controller).

```mermaid
sequenceDiagram
    participant VPR as VPR (Chain)
    participant Validator as Agent (Validator of p1)
    participant Applicant as Agent (Applicant of p1)
    participant Downstream as Agent (Downstream Applicant)

    Initiator Operator->>VPR: 1. RevokeParticipant(p1) OR SlashParticipantTrustDeposit(p1, amt)
    Note over VPR: p1 marked revoked / slashed
    VPR->>Validator: 2. Revoke / Slash event (via Indexer)
    VPR->>Applicant: 2. Revoke / Slash event (via Indexer)

    alt p1 is a HOLDER Participant
        Validator-->>Applicant: 3. CRED_STATE_CHANGE over DIDComm
        Note over Applicant: Remove credential's linked-vp (if any) and delete credential from store
    else p1 is NOT a HOLDER Participant
        Note over Applicant: For each in-flight flow where Applicant of p1 acts as Validator (validator_participant_id == p1):
        Applicant-->>Downstream: 3. ERROR over DIDComm (validator Participant revoked)
        Note over Applicant: Terminate flow: Connection State = TERMINATED Flow State = PARTICIPANT_REVOKED / PARTICIPANT_SLASHED
    end
```

**Behaviour by `Participant` role**:

- **If `p1` is a HOLDER `Participant`** (the credential issued under `p1` is held by the Applicant of `p1`):
  - The **Validator of `p1`** SHOULD send a `CRED_STATE_CHANGE` message to the Applicant of `p1` over the existing DIDComm session.
  - The **Applicant of `p1`** MUST:
    - remove the corresponding `LinkedVerifiablePresentation` entry from its DID Document if the credential was published as a linked VP;
    - delete the credential from its credential store.

- **If `p1` is NOT a HOLDER `Participant`** (i.e., `p1.role` is `ISSUER`, `VERIFIER`, `ISSUER_GRANTOR`, `VERIFIER_GRANTOR`, or `ECOSYSTEM`):
  - The **Applicant of `p1`** MUST terminate every in-flight flow in which it acts as Validator under `p1` — i.e., every flow whose `validator_participant_id == p1` and whose Flow State is not `COMPLETED`. For each such flow, the Applicant of `p1` MUST:
    - send an `ERROR` DIDComm message to the downstream Applicant indicating that the validator `Participant` has been revoked and the flow cannot continue;
    - set Connection State to `TERMINATED` and Flow State to `PARTICIPANT_REVOKED` (after `RevokeParticipant`) or `PARTICIPANT_SLASHED` (after `SlashParticipantTrustDeposit`);
    - discard any pending out-of-band resources for the flow (`OOB_LINK` URLs, draft credentials, etc.).
  - The Applicant of `p1` MUST NOT cascade-revoke any `Participant` entries or credentials it had previously issued under `p1`. Credentials delivered before the revocation remain valid; their lifecycle is governed independently.

> Revocation and slashing are irreversible from the agent's perspective: a revoked or slashed `Participant` cannot be revived. To resume operating, the corporation MUST obtain a new `Participant` entry via a new onboarding process — and, for slashed Participants, MUST first repay the slashed trust deposit ([[MOD-PP-MSG-13]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-13-repay-participant-slashed-trust-deposit)).

#### [VSA-VTI-FLOW-DI] Credential Direct Issuance

This flow is used when an applicant wants to obtain a credential that can be issued directly without an on-chain onboarding process.

Possible Applicant/Validator combinations:

| Applicant | Validator | Schema Mode Condition |
|---|---|---|
| HOLDER | ISSUER | `holder_onboarding_mode` = `PERMISSIONLESS` |

```mermaid
sequenceDiagram
    participant Applicant as Agent (Applicant)
    participant VPR as VPR (Chain)
    participant Validator as Agent (Validator)

    Applicant->>Validator: 1. DIDComm connect
    Applicant->>Validator: 2. IR: schema_id, cred. claims,<br/>proofs, participant_session_id
    Validator-->>Applicant: 3. (optional) out-of-band info collection
    Note over Validator: 4. Generate credential<br/>(sign + compute digest)
    Validator->>VPR: 5. CreateOrUpdateParticipantSession
    Validator->>Applicant: 6. Credential offer
    Applicant->>VPR: 7. Verify validator + digest
    Applicant->>Validator: 8. Accept Credential
    Note over Applicant: 9. Store credential
    Note over Applicant: 10. (optional) VP in DID Doc
```

**Step-by-step**:

1. The agent connects to the validator via DIDComm. The validator MUST verify that the connecting agent is a Verifiable Service as specified in [[VS-CONN-VS]](https://verana-labs.github.io/verifiable-trust-spec/#vs-conn-vs-requirements-for-a-vs-to-accept-a-connection-from-another-service) before accepting the connection.

2. The applicant sends an **IR (Issuance Request)** message containing the desired credential `schema_id`, along with the following session parameters (to be used later for `CreateOrUpdateParticipantSession`):
   - `participant_session_id`: A UUID for the `ParticipantSession`.

   The applicant MAY also include credential claims and supporting proofs if already available. The validator MUST either accept the information and proceed, or refuse it with an error code and descriptive error message. If refused, the applicant MAY retry with corrected information.

3. If the validator requires additional information to generate the credential (e.g., missing claims or proofs), the validator MAY send a link to the applicant for an out-of-DIDComm flow (such as a web form or portal) to collect the missing data.

4. The validator generates and signs the credential, and computes the digest.

5. The **validator** calls `CreateOrUpdateParticipantSession` ([[MOD-PP-MSG-10]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-10-create-or-update-participant-session)) on-chain (see [Agent Account Authorizations](#agent-account-authorizations)). The credential MUST NOT be delivered until this transaction succeeds.

6. The validator delivers the signed credential to the applicant via the DIDComm session.

7. The applicant MUST verify the received credential before accepting it:
   - Verify the validator is authorized by the ecosystem to issue credentials for this schema (query the VPR via the indexer to confirm the validator has an active ISSUER `Participant` entry).
   - Recompute the credential's digest and verify it matches the digest recorded on-chain in the `ParticipantSession` updated in step 5.
   - If either check fails, the applicant MUST reject the credential and log the error.

8. The applicant sends a **CRED_ACCEPT** message to the validator, confirming that the credential has been verified and accepted.

9. The applicant stores the credential in its credential store.

10. **Optionally**, the applicant links the credential as a `LinkedVerifiablePresentation` in its DID Document per [[VT-CRED-W3C-LINKED-VP]](https://verana-labs.github.io/verifiable-trust-spec/#vt-cred-w3c-linked-vp-w3c-vtc-linked-vp).

11. **Optionally**, the applicant calls `TriggerResolver` on-chain to refresh its Verifiable Service resolution state. The applicant SHOULD call `TriggerResolver` when:
    - it has just become a Verifiable Service by newly complying with [[VS-REQ]](https://verana-labs.github.io/verifiable-trust-spec/#vs-req-verifiable-service-basic-requirements-and-linked-vps); or
    - it has added or removed a `LinkedVerifiablePresentation` entry in its DID Document.

> Note: revocation status of a credential issued without a corresponding HOLDER `Participant` entry must be managed by the validator via a separate revocation list.

#### [VSA-VTI-FLOW-UPD] Validator Updates

Possible Applicant/Validator combinations: All

Validator MAY send update messages to the applicant through the persistent DIDComm session. The following updates are defined:

The validator sends a `CRED_STATE_CHANGE` message when the credential's status changes. Supported states:

- **REVOKED**: The credential has been permanently revoked by the validator. The applicant MUST:
  1. Remove the corresponding `LinkedVerifiablePresentation` from its DID Document (if present).
  2. Delete the credential from the credential store.

> Note: DIDComm connection can be maintained for future updates: a revocation of a credential doesn't imply the end of the flow.

:::warning
A revocation of a credential is distinct from a revocation of a `Participant` entry. When a credential has been revoked, a new one can be requested by re-executing the Credential Direct Issuance flow.
:::

#### [VSA-VTI-FLOW-SELF] Participant Self Creation

This flow is used when a `CredentialSchema`'s onboarding mode for the requested `Participant` role is `OPEN`. The Applicant self-creates its `Participant` entry directly on-chain via [`SelfCreateParticipant`](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-14-self-create-participant); no Validator is involved, no DIDComm session is opened, and no Flow State is maintained on the agent.

Possible cases:

| Applicant `role` | Schema Mode Condition |
|---|---|
| ISSUER | `issuer_onboarding_mode` = `OPEN` |
| VERIFIER | `verifier_onboarding_mode` = `OPEN` |

```mermaid
sequenceDiagram
    participant VPR as VPR (Chain)

    Applicant Operator->>VPR: 1. SelfCreateParticipant<br/>(schema_id, role, ...)
    VPR-->>Applicant Operator: participant_id (active)
    VPR->>Applicant Agent: 2. SelfCreateParticipant own-tx<br/>confirmation (via Indexer)
```

**Step-by-step**:

1. The Applicant submits `SelfCreateParticipant` on-chain referencing the target `schema_id`, the `Participant.role` (ISSUER or VERIFIER), and the other required attributes (DID, `effective_from`, fees, optional `ParticipantAuthorizationRecord` parameters) as specified in [[MOD-PP-MSG-14] Self Create Participant](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-pp-msg-14-self-create-participant). On success, the new `Participant` is immediately active — `op_state = VALIDATED`, no escrow, no Validator.

2. The Applicant receives the `SelfCreateParticipant` event from the indexer for its own transaction (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)) and records the resulting `participant_id` for later use.

> Participant Self Creation does not open a DIDComm session, does not create any Flow State entry, and does not involve a Validator. The corporation MUST nevertheless ensure that its self-created `Participant` complies with the Ecosystem's EGF — an OPEN-mode `Participant` CAN still be revoked or slashed by ecosystem governance (see [Revoke Participant / Slash Participant Trust Deposit](#vsa-vti-flow-op-revoke-revoke-participant--slash-participant-trust-deposit)).

#### [VSA-VTI-FLOW-DIDCOMM] DIDComm Protocol

The wire-level DIDComm protocol for the Onboarding Process and Credential Direct Issuance flows is specified in the [Verifiable Trust Flow Protocol 1.0 (`vt-flow`)](../vt-flow-protocol/spec.md). That document details:

- Message formats, field definitions, and type URIs
- Protocol states (Connection State and Flow State)
- Error codes and the adopted `problem-report` semantics
- Issue Credential V2 subprotocol composition (`~thread.pthid` linking)
- Reconnection semantics
- DIDComm envelope compatibility (v1 / v2)

The following table maps the agent-level message names used in this specification to the `vt-flow` protocol messages:

| Agent-level name | vt-flow message | Sender | Agent-level trigger |
| --- | --- | --- | --- |
| OR (Onboarding Request) | [`validation-request`](../vt-flow-protocol/spec.md#validation-request) | Applicant | After `StartParticipantOP` / `RenewParticipantOP` succeeds on-chain. |
| IR (Issuance Request) | [`issuance-request`](../vt-flow-protocol/spec.md#issuance-request) | Applicant | When initiating a [Credential Direct Issuance](#vsa-vti-flow-di-credential-direct-issuance). |
| OOB_LINK | [`oob-link`](../vt-flow-protocol/spec.md#oob-link) | Validator | When additional out-of-DIDComm information is needed. |
| VALIDATING | [`validating`](../vt-flow-protocol/spec.md#validating) | Validator | When off-chain validation begins. |
| Credential offer / accept | [Issue Credential V2 subprotocol](../vt-flow-protocol/spec.md#subprotocols) | Both | Validator issues `offer-credential`; Applicant verifies and sends `ack`. |
| CRED_STATE_CHANGE | [`credential-state-change`](../vt-flow-protocol/spec.md#credential-state-change) | Validator | Credential status change (e.g., `REVOKED`). See [Validator Updates](#vsa-vti-flow-upd-validator-updates) and [Revoke Participant / Slash Participant Trust Deposit](#vsa-vti-flow-op-revoke-revoke-participant--slash-participant-trust-deposit). |
| ERROR | [`problem-report` (adopted)](../vt-flow-protocol/spec.md#problem-report-adopted) | Either | Protocol error or explicit termination. Error codes are listed in the [protocol spec Error Codes registry](../vt-flow-protocol/spec.md#error-codes). |

#### [VSA-VTI-FLOW-MISC] Additional Considerations

- **Credential update**: At any time, the validator MAY issue an updated credential via a new Issue Credential V2 subprotocol run through the existing DIDComm session. Upon receiving an updated credential, the applicant MUST delete the old credential from the credential store, replace it with the new one, and update the corresponding `LinkedVerifiablePresentation` in its DID Document if the credential was previously linked.
- **Out-of-band requests**: At any time, the validator MAY send an `oob-link` message — for example, to revalidate applicant information, to extend a `Participant`'s lifetime, or to collect additional data before issuing an updated credential.
- **Reconnection**: Per the [vt-flow Reconnection](../vt-flow-protocol/spec.md#reconnection) rules, if the applicant reconnects to the validator after a connection has been closed, it MUST resend a `validation-request` or `issuance-request` with the same `participant_session_id`. The validator MUST identify that the message is related to an existing flow and reassign the flow to the new connection.
- **Onboarding renewal**: When an onboarding process must be renewed, the applicant MUST first execute the required VPR on-chain transaction (`RenewParticipantOP`) and then resend a `validation-request` to the validator to re-trigger validation.

#### [VSA-VTI-FLOW-STATE] Flow State

Each credential acquisition flow has two orthogonal state dimensions that can be queried through the Administration API. The complete state definitions, transitions, and state machine diagrams are specified in the [vt-flow protocol States](../vt-flow-protocol/spec.md#states) section.

- **Connection State**: `NOT_CONNECTED`, `ESTABLISHED`, or `TERMINATED`.
- **Flow State**: Current stage of the credential acquisition flow.

The following table summarises how Flow States relate to agent-level flows:

| Flow State | Role | Agent Flow | Agent-level trigger |
| --- | --- | --- | --- |
| `AWAITING_OP` | Applicant | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | Waiting for `StartParticipantOP` / `RenewParticipantOP` on-chain. |
| `OR_SENT` | Applicant | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | `validation-request` sent to validator. |
| `AWAITING_OR` | Validator | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | `validation-request` expected; last request rejected or not yet received. |
| `IR_SENT` | Applicant | [Credential Direct Issuance](#vsa-vti-flow-di-credential-direct-issuance) | `issuance-request` sent to validator. |
| `AWAITING_IR` | Validator | [Credential Direct Issuance](#vsa-vti-flow-di-credential-direct-issuance) | `issuance-request` expected; last request rejected or not yet received. |
| `OOB_PENDING` | Both | Both | Validator sent `oob-link`; awaiting applicant completion. |
| `VALIDATING` | Both | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | Off-chain validation in progress. |
| `VALIDATED` | Both | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | `SetParticipantOPValidated` on-chain; valid terminal if no credential issued. |
| `CRED_OFFERED` | Both | Both | Issue Credential V2 subprotocol in flight. |
| `COMPLETED` | Both | Both | Credential accepted. Connection remains open for [Validator Updates](#vsa-vti-flow-upd-validator-updates). |
| `CRED_REVOKED` | Both | Both | Credential revoked (see [Validator Updates](#vsa-vti-flow-upd-validator-updates)). |
| `TERMINATED_BY_VALIDATOR` | Both | Both | Validator terminated the flow. |
| `TERMINATED_BY_APPLICANT` | Both | Both | Applicant terminated the flow. |
| `ERROR` | Both | Both | Unrecoverable protocol error. |
| `PARTICIPANT_REVOKED` | Both | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | On-chain `Participant` revoked (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)). |
| `PARTICIPANT_SLASHED` | Both | [New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) | On-chain `Participant` slashed (see [Participant Notifications](#vsa-vti-notif-pp-participant-notifications)). |

For the full state machine diagrams (per-role and post-issuance transitions), see the [vt-flow protocol State Machine Diagrams](../vt-flow-protocol/spec.md#state-machine-diagrams).

## Administration API

The VS Agent MUST expose a secure Administration API that allows authenticated and authorized entities to remotely query and manage the agent's state: for example, from the Verana frontend, or from a backend container connected to agent.

### Authentication and Authorization

#### Listeners

The Admin API can be served through two distinct listeners:

- **Internal listener** — bound to the loopback interface or to a pod-internal address (e.g. a Unix socket or a private container network). Reachable only from inside the agent's pod or deployment. No authentication is performed; trust is established by network reachability.
- **External listener** — bound to a publicly reachable interface at `ADMIN_API_PUBLIC_URL`. Every request MUST be authenticated as a Verana account using a signature challenge (e.g. ADR-036) and authorized per [Authorization](#authorization).

Which listeners are active is controlled by the `ADMIN_API_AUTH_MODE` environment variable, which holds a comma-separated, non-empty list of auth modes. Each mode enables one listener:

| Mode | Listener enabled | Auth on that listener |
|---|---|---|
| `internal` | Internal listener | None — trust is established by network reachability. |
| `corporation` | External listener | Verana-account authentication + per-method authorization (see [Authorization](#authorization)). Requires `ADMIN_API_PUBLIC_URL` to be set. |

Examples: `ADMIN_API_AUTH_MODE=internal`, `ADMIN_API_AUTH_MODE=corporation`, `ADMIN_API_AUTH_MODE=internal,corporation`.

If a mode is not listed, its listener MUST NOT be activated. If `corporation` is not listed, methods declared as INTERNAL-only (see [Authorization](#authorization)) become the only invocable methods; conversely, if `internal` is not listed, those INTERNAL-only methods are unreachable and operators choosing this configuration accept that trade-off.

Future revisions of this specification MAY add additional modes (e.g. an OAuth-backed or mTLS-backed listener). Each new mode declares its own listener and authentication contract; existing modes are unaffected.

#### Authentication

Authentication is enforced **per listener**, not per method:

1. Requests arriving on the **internal listener** are not authenticated. The deployment is responsible for ensuring that this listener is unreachable from outside the trust boundary (pod, deployment, host).
2. Requests arriving on the **external listener** MUST be authenticated using a Verana-account-based mechanism (e.g. ADR-036 signature challenge) before any other check.

#### Authorization

The Admin API does not define a standalone authorization model. Instead, it **reuses the on-chain VPR authorization grants** that the bound Corporation has already issued to operators, and gates each Admin API method on the same VPR `Msg` type that the agent will eventually submit on-chain to fulfil that method's effect. This guarantees that any caller able to drive the agent through the Admin API toward an on-chain outcome is *also* directly authorized by the Corporation to submit that on-chain `Msg`.

Each Admin API method declares which **access modes** can invoke it:

- **INTERNAL** — reachable only via the [internal listener](#listeners). No authentication, no authorization check. Used for methods that are unsafe or meaningless to expose externally (process diagnostics, raw connection management, etc.).
- **CORPORATION** — reachable via either listener. On the internal listener, no authorization check is performed (the caller is already trusted). On the external listener, the authenticated caller MUST hold, from the `VERANA_CORPORATION_ID` Corporation, an authorization whose `msg_types` include the VPR `Msg` type required by the method.

##### Two-layer authorization model

For methods whose effect ultimately involves submitting one or more on-chain VPR `Msg`s, two independent authorizations are checked:

1. **Caller authorization** (off-chain, enforced by the Admin API): the authenticated caller MUST hold a Corporation-issued authorization that includes the method's required VPR `Msg` type.
2. **Agent authorization** (on-chain, enforced by VPR per [[AUTHZ-CHECK-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#authz-check-1-operator-authorization-checks) or [[AUTHZ-CHECK-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#authz-check-3-vs-operator-authorization-checks)): when the agent later submits the on-chain `Msg`, its own `vs_operator` account (see [Agent Account Authorizations](#agent-account-authorizations)) MUST itself hold the required `VSOperatorAuthorization` + `ParticipantAuthorizationRecord` (or, for non-`Participant`-scoped messages, a plain `OperatorAuthorization`).

Both checks MUST succeed for the operation to complete. The agent MUST refuse the API call if (1) fails; the network MUST reject the resulting transaction if (2) fails.

##### Authorization kinds

The VPR defines two authorization grants whose `msg_types` field is reused by the Admin API:

| Authorization grant | VPR check | When to use |
|---|---|---|
| [`OperatorAuthorization`](https://verana-labs.github.io/verifiable-trust-vpr-spec/#operatorauthorization) | [[AUTHZ-CHECK-1]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#authz-check-1-operator-authorization-checks) | For methods that drive **non-`Participant`-scoped** VPR `Msg`s (Corporation, Ecosystem, GovernanceFramework, CredentialSchema management, etc.). |
| [`VSOperatorAuthorization`](https://verana-labs.github.io/verifiable-trust-vpr-spec/#vsoperatorauthorization) + `ParticipantAuthorizationRecord.msg_types` | [[AUTHZ-CHECK-3]](https://verana-labs.github.io/verifiable-trust-vpr-spec/#authz-check-3-vs-operator-authorization-checks) | For methods that drive **`Participant`-scoped** VPR `Msg`s (`StartParticipantOP`, `RenewParticipantOP`, `SetParticipantOPValidated`, `RevokeParticipant`, `CreateOrUpdateParticipantSession`, etc.). The required scope is the specific `Participant` referenced by the method (e.g. via `participant_session_id` or path parameter). |

Each Admin API method MUST declare:

- the **authorization kind** (`OperatorAuthorization` or `VSOperatorAuthorization`),
- the **VPR `Msg` type(s)** that MUST be present in the grant's `msg_types`,
- for `VSOperatorAuthorization`, the **`Participant` scope** identifying which `ParticipantAuthorizationRecord` is consulted.

The VPR `Msg` type identifiers used here are those defined in the [VPR Specification](https://verana-labs.github.io/verifiable-trust-vpr-spec/) (e.g. `SetParticipantOPValidated`, `RevokeParticipant`); this specification does NOT define new ones.

##### Example

`validateFlow` causes the agent to submit `SetParticipantOPValidated` on-chain for a specific `Participant` (the validator's). Therefore:

- **Authz**: `CORPORATION` — `VSOperatorAuthorization` with `msg_types` ⊇ {`SetParticipantOPValidated`}, scoped to the validator `Participant` of the target flow.
- **Caller check**: the authenticated caller MUST be the `vs_operator` of a `VSOperatorAuthorization` whose `ParticipantAuthorizationRecord` for that `Participant` includes `SetParticipantOPValidated` in `msg_types`.
- **Agent check** (later, on submission): the agent's own `vs_operator` account MUST equally hold such authorization. In the typical deployment where the caller is the same operator as the agent's `vs_operator`, both checks resolve against the same `VSOperatorAuthorization` record.

### Container Environment Variables

The following environment variables MUST be provided when the VS Agent container is started.

| Variable | Required | Description |
|---|---|---|
| `ADMIN_API_AUTH_MODE` | REQUIRED | Comma-separated, non-empty list of Admin API auth modes to enable. Currently defined values: `internal`, `corporation`. See [Listeners](#listeners). |
| `ADMIN_API_PUBLIC_URL` | CONDITIONAL | Public `https://` origin (scheme + host + optional port, no trailing path) at which the external listener is exposed. REQUIRED when `ADMIN_API_AUTH_MODE` includes `corporation`; MUST NOT be set otherwise. When set, the agent also publishes a `VsAgentAdminAPI` entry in its DID Document per [[VSA-VTI-DIDDOC]](#vsa-vti-diddoc-did-document-service-entries). |
| `ADMIN_API_CORPORATION_ALLOWED_ACCOUNTS` | OPTIONAL | Comma-separated list of Verana account addresses (the same identifiers that authenticate via [Authentication](#authentication) — e.g. the `operator` / `vs_operator` of an `OperatorAuthorization` / `VSOperatorAuthorization`). When set, the external listener accepts only callers whose authenticated account is in this list, applied **before** the per-method authorization check. The bound Corporation is already fixed by `VERANA_CORPORATION_ID`, so this filter narrows callers within that Corporation's authorized operators. Has no effect when `corporation` is not in `ADMIN_API_AUTH_MODE`. |

### [VSA-ADM-AG] Agent

Methods that expose runtime information about this VS Agent instance.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Agent | `getAgentInfo` | `GET` | `/v1/agent` | [see](#vsa-adm-ag-info-getagentinfo) | INTERNAL |

#### [VSA-ADM-AG-INFO] getAgentInfo

Returns the core configuration and runtime status of this VS Agent instance.

**Inputs**: none.

**Output**:

- `label` — human-readable name of the agent.
- `endpoints` — list of DIDComm service endpoints currently published for this agent.
- `isInitialized` — `true` once the agent has completed its setup.
- `publicDid` — public DID assigned to the agent (when set), e.g. `did:web:agent.example.com`.
- `version` — running application version.

### [VSA-ADM-HE] Health

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Health | `getHealth` | `GET` | `/v1/health` | [see](#vsa-adm-he-get-gethealth) | INTERNAL |

#### [VSA-ADM-HE-GET] getHealth

Liveness/readiness probe for the agent. Returns HTTP `200` when the agent is up.

**Inputs**: none.

**Output**: opaque body indicating health. Implementations MAY include process-level diagnostics.

### [VSA-ADM-CN] Connections

Methods that manage DIDComm connection records held by this agent.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Connections | `listConnections` | `GET` | `/v1/connections` | [see](#vsa-adm-cn-list-listconnections) | INTERNAL |
| Connections | `getConnection` | `GET` | `/v1/connections/{connectionId}` | [see](#vsa-adm-cn-get-getconnection) | INTERNAL |
| Connections | `deleteConnection` | `DELETE` | `/v1/connections/{connectionId}` | [see](#vsa-adm-cn-delete-deleteconnection) | INTERNAL |

#### [VSA-ADM-CN-LIST] listConnections

Returns all connection records, optionally filtered.

**Inputs** (all OPTIONAL query filters):

- `outOfBandId` — filter by Out-of-Band identifier.
- `state` — one of `start`, `invitation-sent`, `invitation-received`, `request-sent`, `request-received`, `response-sent`, `response-received`, `abandoned`, `completed`.
- `role` — `requester` or `responder`.
- `did` — filter by my DID for this connection.
- `theirDid` — filter by the peer's DID.
- `threadId` — filter by DIDComm thread ID.
- `invitationDid` — filter by the invitation DID.
- `didcommVersion` — `v1` or `v2`.
- `mediatorId` — filter by mediator id.

**Output**: array of connection records with at minimum `id`, `state`, `role`, `did`, `theirDid`, `threadId`, `createdAt`, `updatedAt`.

#### [VSA-ADM-CN-GET] getConnection

Retrieves a single connection record by id.

**Path parameters**:

- `connectionId` (REQUIRED) — UUID of the connection.

**Output**: the connection record (same shape as in `listConnections`).

**Errors**:

- `NOT_FOUND` — no connection with the given id.

#### [VSA-ADM-CN-DELETE] deleteConnection

Deletes a connection record. The agent MAY also tear down the underlying DIDComm session.

**Path parameters**:

- `connectionId` (REQUIRED) — UUID of the connection to delete.

**Inputs**: none.

**Output**: empty body (HTTP `204`).

**Errors**:

- `NOT_FOUND` — no connection with the given id.

### [VSA-ADM-IN] Invitations

Methods that create or consume Out-of-Band invitations used to establish DIDComm connections, request presentations, or offer credentials.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Invitations | `createInvitation` | `POST` | `/v1/invitation` | [see](#vsa-adm-in-create-createinvitation) | INTERNAL |
| Invitations | `receiveInvitation` | `POST` | `/v1/invitation/receive` | [see](#vsa-adm-in-receive-receiveinvitation) | INTERNAL |
| Invitations | `createPresentationRequest` | `POST` | `/v1/invitation/presentation-request` | [see](#vsa-adm-in-pres-createpresentationrequest) | INTERNAL |
| Invitations | `createCredentialOffer` | `POST` | `/v1/invitation/credential-offer` | [see](#vsa-adm-in-offer-createcredentialoffer) | INTERNAL |

#### [VSA-ADM-IN-CREATE] createInvitation

Creates a new Out-of-Band connection invitation.

**Inputs** (request body, all OPTIONAL):

- `useLegacyDid` — when the agent's DID is `did:webvh`, force the invitation to advertise the legacy `did:web` form.
- `didCommVersion` — `v1` or `v2`. `v2` requires the agent's `AGENT_DIDCOMM_VERSIONS` to include `v2`. When omitted, the agent infers the version from its configuration.

**Output**:

- `url` — URL-encoded invitation, ready to be rendered as a QR code or sent as a link.

#### [VSA-ADM-IN-RECEIVE] receiveInvitation

Proactively connects to another agent by processing an invitation.

**Inputs** (request body):

- `url` (REQUIRED) — accepts either:
  - an explicit OOB invitation URL (`https://...` or `didcomm://...`); or
  - an implicit invitation DID (`did:webvh:...`, `did:web:...`, etc.). The agent MUST infer the invitation type from the URL scheme.

**Output**:

- `outOfBandId` — identifier of the resulting OOB record.
- `connectionId` — identifier of the initiated connection.

**Errors**:

- `INVALID_INVITATION` — the URL/DID could not be parsed or resolved.

#### [VSA-ADM-IN-PRES] createPresentationRequest

Creates a Presentation Request invitation. Defines the credentials and attributes the holder is asked to present.

**Inputs** (request body):

- `requestedCredentials` (REQUIRED) — array of requested credential descriptors. Each entry references a credential by either `credentialDefinitionId` (AnonCreds) or `jsonSchemaCredentialId` (JSON Schema Credential), and lists the requested `attributes`. If `attributes` is omitted, the agent MUST request every attribute defined by the schema.
- `callbackUrl` (OPTIONAL) — URL the agent calls (HTTP `POST`) when the presentation flow completes. The body contains `ref`, `presentationRequestId`, `status`, and `claims`.
- `ref` (OPTIONAL) — caller-supplied correlation identifier echoed back on the callback.
- `requireNonRevocation` (OPTIONAL, default `false`) — when `true`, the holder MUST provide a non-revocation proof at verification time.
- `useLegacyDid` (OPTIONAL) — see `createInvitation`.
- `didCommVersion` (OPTIONAL) — see `createInvitation`.

**Output**:

- `proofExchangeId` — flow identifier for subsequent tracking.
- `url` — full DIDComm invitation URL.
- `shortUrl` — short URL form suitable for QR codes (when supported).

#### [VSA-ADM-IN-OFFER] createCredentialOffer

Creates an AnonCreds credential offer invitation including a preview of the offered claims.

**Inputs** (request body):

- `credentialDefinitionId` (REQUIRED) — AnonCreds credential definition identifier.
- `claims` (REQUIRED) — array of name/value pairs previewing the credential's attributes.
- `revocationRegistryDefinitionId` (OPTIONAL) — required only for revocable credentials.
- `revocationRegistryIndex` (OPTIONAL) — required only for revocable credentials.
- `useLegacyDid` (OPTIONAL) — see `createInvitation`.
- `didCommVersion` (OPTIONAL) — see `createInvitation`.

**Output**:

- `credentialExchangeId` — flow identifier.
- `url` — full DIDComm invitation URL.
- `shortUrl` — short URL form (when supported).

**Errors**:

- `INVALID_OFFER` — payload validation failed.

### [VSA-ADM-MS] Messaging

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Messaging | `sendMessage` | `POST` | `/v1/message` | [see](#vsa-adm-ms-send-sendmessage) | INTERNAL |

#### [VSA-ADM-MS-SEND] sendMessage

Sends a DIDComm message over an established connection. The set of accepted message `type` values depends on the plugins enabled via `VS_AGENT_PLUGINS` (text, credential-issuance, credential-revocation, identity-proof-request, contextual-menu-update, profile, terminate-connection, etc.).

**Inputs** (request body):

- `type` (REQUIRED) — message type from the agent's enabled plugins.
- `connectionId` (REQUIRED) — target connection.
- `id` (OPTIONAL) — UUID of the message; generated if not provided.
- `threadId` (OPTIONAL) — DIDComm thread ID.
- `timestamp` (OPTIONAL) — ISO-8601 timestamp.
- additional type-specific fields (e.g., `content` for `text`, `credentialDefinitionId` and `claims` for `credential-issuance`, `requestedProofItems` for `identity-proof-request`, etc.).

**Output**:

- `id` — UUID of the submitted message (echoed or generated by the agent).

**Errors**:

- `5xx` — internal error; the response body MUST include a descriptive `error` field.

### [VSA-ADM-CT] Credential Types

Methods that manage AnonCreds credential definitions ("credential types") and their associated revocation registries.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Credential Types | `listCredentialTypes` | `GET` | `/v1/credential-types` | [see](#vsa-adm-ct-list-listcredentialtypes) | INTERNAL |
| Credential Types | `createCredentialType` | `POST` | `/v1/credential-types` | [see](#vsa-adm-ct-create-createcredentialtype) | INTERNAL |
| Credential Types | `deleteCredentialType` | `DELETE` | `/v1/credential-types/{credentialTypeId}` | [see](#vsa-adm-ct-delete-deletecredentialtype) | INTERNAL |
| Credential Types | `exportCredentialType` | `GET` | `/v1/credential-types/export/{credentialTypeId}` | [see](#vsa-adm-ct-export-exportcredentialtype) | INTERNAL |
| Credential Types | `importCredentialType` | `POST` | `/v1/credential-types/import` | [see](#vsa-adm-ct-import-importcredentialtype) | INTERNAL |
| Credential Types | `listRevocationRegistries` | `GET` | `/v1/credential-types/revocation-registry` | [see](#vsa-adm-ct-revlist-listrevocationregistries) | INTERNAL |
| Credential Types | `createRevocationRegistry` | `POST` | `/v1/credential-types/revocation-registry` | [see](#vsa-adm-ct-revcreate-createrevocationregistry) | INTERNAL |
| Credential Types | `deleteRevocationRegistry` | `DELETE` | `/v1/credential-types/revocation-registry/{revocationRegistryDefinitionId}` | [see](#vsa-adm-ct-revdelete-deleterevocationregistry) | INTERNAL |

> Note: the deployed agent currently exposes the revocation-registry endpoints under the camelCased path `/v1/credential-types/revocationRegistry`. The kebab-case form `revocation-registry` is RECOMMENDED for new deployments to stay consistent with the rest of the API; existing deployments MAY continue to expose the camelCased alias.

#### [VSA-ADM-CT-LIST] listCredentialTypes

Returns every credential type known to this agent.

**Inputs**: none.

**Output**: array of credential type records (see `createCredentialType` for fields).

#### [VSA-ADM-CT-CREATE] createCredentialType

Creates a new AnonCreds credential definition, optionally linked to a Verifiable Trust JSON Schema Credential.

**Inputs** (request body):

- `name` — credential type name (REQUIRED if `relatedJsonSchemaCredentialId` is not provided; used together with `version` to identify the credential type).
- `version` — credential type version (REQUIRED if `relatedJsonSchemaCredentialId` is not provided).
- `attributes` (OPTIONAL) — list of schema attribute names. Required when creating a brand-new schema without `relatedJsonSchemaCredentialId`.
- `schemaId` (OPTIONAL) — identifier of an existing AnonCreds schema to bind to.
- `relatedJsonSchemaCredentialId` (OPTIONAL) — Verifiable Trust JSON Schema Credential URL the credential type is based on.
- `issuerDid` (OPTIONAL) — DID of the schema issuer; used when reusing an existing AnonCreds schema from another agent. Requires `relatedJsonSchemaCredentialId`.
- `supportRevocation` (OPTIONAL, default `false`) — when `true`, the credential MAY be revoked.

**Output**: the resulting credential type record.

**Errors**:

- `INVALID_PAYLOAD` — request body fails validation.

#### [VSA-ADM-CT-DELETE] deleteCredentialType

Deletes a credential type and all its associated cryptographic data.

**Path parameters**:

- `credentialTypeId` (REQUIRED) — identifier of the credential definition to delete.

**Inputs** (OPTIONAL query parameter):

- `deleteAssociatedRevocationRegistries` (default `false`) — when `true`, also delete every revocation registry and status list associated with this credential type.

**Output**: empty body.

**Errors**:

- `INVALID_ID` — `credentialTypeId` is malformed.

#### [VSA-ADM-CT-EXPORT] exportCredentialType

Exports a credential type as a portable package suitable for import on another agent.

**Path parameters**:

- `credentialTypeId` (REQUIRED) — identifier of the credential definition to export.

**Output**: a package object containing `id` and `data` fields.

#### [VSA-ADM-CT-IMPORT] importCredentialType

Imports a credential type package previously produced by `exportCredentialType`.

**Inputs** (request body): the credential definition package as returned by `exportCredentialType`.

**Output**: the imported credential type record.

**Errors**:

- `INVALID_PACKAGE` — package payload fails validation.

#### [VSA-ADM-CT-REVLIST] listRevocationRegistries

Returns revocation registry definition IDs known to this agent.

**Inputs** (OPTIONAL query parameter):

- `credentialDefinitionId` — when set, restrict the list to registries bound to that credential definition.

**Output**: array of revocation registry definition identifiers.

#### [VSA-ADM-CT-REVCREATE] createRevocationRegistry

Creates a new revocation registry definition for a revocable credential type.

**Inputs** (request body):

- `credentialDefinitionId` (REQUIRED) — credential definition the registry is bound to.
- `maximumCredentialNumber` (OPTIONAL, default `1000`) — capacity of the registry.

**Output**: the resulting revocation registry definition identifier.

#### [VSA-ADM-CT-REVDELETE] deleteRevocationRegistry

Deletes a revocation registry definition and its associated status list records.

**Path parameters**:

- `revocationRegistryDefinitionId` (REQUIRED) — identifier of the registry to delete. Implementations that still expose the legacy endpoint MAY accept this parameter as a `?revocationRegistryDefinitionId=` query parameter instead.

**Output**: empty body.

**Errors**:

- `INVALID_ID` — `revocationRegistryDefinitionId` is malformed.

### [VSA-ADM-CE] Credential Exchanges

Methods to inspect the credential issuance pipeline.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Credential Exchanges | `listCredentialExchanges` | `GET` | `/v1/credential-exchanges` | [see](#vsa-adm-ce-list-listcredentialexchanges) | INTERNAL |
| Credential Exchanges | `getCredentialExchange` | `GET` | `/v1/credential-exchanges/{credentialExchangeId}` | [see](#vsa-adm-ce-get-getcredentialexchange) | INTERNAL |

#### [VSA-ADM-CE-LIST] listCredentialExchanges

Returns every credential exchange record tracked by the agent.

**Inputs**: none.

**Output**: array of credential exchange records, each containing at minimum `credentialExchangeId`, `state`, `threadId`, `connectionId`, `credentialDefinitionId`, `schemaId`, `claims`, `errorMessage`, `createdAt`, `updatedAt`.

#### [VSA-ADM-CE-GET] getCredentialExchange

Retrieves a single credential exchange record by id.

**Path parameters**:

- `credentialExchangeId` (REQUIRED) — exchange identifier.

**Output**: the credential exchange record.

**Errors**:

- `NOT_FOUND` — no exchange with the given id.

### [VSA-ADM-PR] Presentations

Methods to inspect and clean up presentation (proof) exchanges.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Presentations | `listPresentations` | `GET` | `/v1/presentations` | [see](#vsa-adm-pr-list-listpresentations) | INTERNAL |
| Presentations | `getPresentation` | `GET` | `/v1/presentations/{proofExchangeId}` | [see](#vsa-adm-pr-get-getpresentation) | INTERNAL |
| Presentations | `deletePresentation` | `DELETE` | `/v1/presentations/{proofExchangeId}` | [see](#vsa-adm-pr-delete-deletepresentation) | INTERNAL |

#### [VSA-ADM-PR-LIST] listPresentations

Returns every presentation flow created by the agent.

**Inputs**: none.

**Output**: array of presentation records, each containing at minimum `proofExchangeId`, `state`, `requestedCredentials`, `claims`, `verified`, `threadId`, `updatedAt`.

#### [VSA-ADM-PR-GET] getPresentation

Retrieves a single presentation by `proofExchangeId`.

**Path parameters**:

- `proofExchangeId` (REQUIRED) — presentation flow identifier.

**Output**: the presentation record.

**Errors**:

- `NOT_FOUND` — no presentation with the given id.

#### [VSA-ADM-PR-DELETE] deletePresentation

Deletes a presentation exchange record.

**Path parameters**:

- `proofExchangeId` (REQUIRED) — presentation flow identifier.

**Output**: empty body (HTTP `204`).

**Errors**:

- `NOT_FOUND` — no presentation with the given id.

### [VSA-ADM-QR] QR

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| QR | `getQrCode` | `GET` | `/v1/qr` | [see](#vsa-adm-qr-get-getqrcode) | INTERNAL |

#### [VSA-ADM-QR-GET] getQrCode

Returns a rendered QR-code image for an invitation URL.

**Inputs** (OPTIONAL query parameters):

- `size` — image size in pixels.
- `padding` — padding around the QR.
- `level` — error-correction level (`L`, `M`, `Q`, `H`).
- `bcolor` — background color.
- `fcolor` — foreground color.
- `legacy` — when `true`, render a QR for the legacy `did:web` invitation form.

**Output**: an image response (typically `image/png`).

### [VSA-ADM-VTC] Verifiable Trust Credentials

Methods that issue or revoke Verifiable Trust Credentials (VTCs) on behalf of the agent. Aligned with the [Verifiable Trust Specification](https://verana-labs.github.io/verifiable-trust-spec/).

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Verifiable Trust Credentials | `issueCredential` | `POST` | `/v1/vt/issue-credential` | [see](#vsa-adm-vtc-issue-issuecredential) | INTERNAL |
| Verifiable Trust Credentials | `revokeCredential` | `POST` | `/v1/vt/revoke-credential` | [see](#vsa-adm-vtc-revoke-revokecredential) | INTERNAL |

#### [VSA-ADM-VTC-ISSUE] issueCredential

Issues a Verifiable Trust Credential bound to a JSON Schema Credential. The agent MAY produce either a JSON-LD W3C credential or an AnonCreds credential depending on `format`.

**Inputs** (request body):

- `format` (REQUIRED) — `jsonld` or `anoncreds`.
- `did` (REQUIRED for `jsonld`) — DID of the credential subject (the holder).
- `jsonSchemaCredentialId` (REQUIRED) — URL of the JSON Schema Credential governing the credential structure.
- `claims` (REQUIRED) — credential claims as a flat object of key/value pairs.

**Output**:

- For `jsonld`: the signed W3C Verifiable Credential, ready to be transmitted to the recipient.
- For `anoncreds`: a DIDComm invitation and the associated `credentialExchangeId` for further tracking through the events interface.

#### [VSA-ADM-VTC-REVOKE] revokeCredential

Revokes a previously issued Verifiable Trust Credential. Currently only the AnonCreds format is supported.

**Inputs** (request body):

- `format` (REQUIRED) — `jsonld` or `anoncreds`. Revocation is currently NOT supported for `jsonld` and the agent MUST reject such requests.
- `anoncredsRevocationRegistryDefinitionId` (REQUIRED for `anoncreds`) — revocation registry definition the credential is registered in.
- `anoncredsRevocationRegistryIndex` (REQUIRED for `anoncreds`) — credential index within the registry.

**Output**: confirmation of revocation.

**Errors**:

- `UNSUPPORTED_FORMAT` — caller asked to revoke a `jsonld` credential.

### [VSA-ADM-LVP] Verifiable Trust Linked Verifiable Presentations

Methods that manage stored Verifiable Trust Credentials (VTCs) exposed by the agent as `LinkedVerifiablePresentation` service entries (see [[VS-SVC-6]](https://verana-labs.github.io/verifiable-trust-spec/#vs-svc-service-declaration)).

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Linked Verifiable Presentations | `listLinkedCredentials` | `GET` | `/v1/vt/linked-credentials` | [see](#vsa-adm-lvp-list-listlinkedcredentials) | INTERNAL |
| Linked Verifiable Presentations | `createLinkedCredential` | `POST` | `/v1/vt/linked-credentials` | [see](#vsa-adm-lvp-create-createlinkedcredential) | INTERNAL |
| Linked Verifiable Presentations | `deleteLinkedCredential` | `DELETE` | `/v1/vt/linked-credentials` | [see](#vsa-adm-lvp-delete-deletelinkedcredential) | INTERNAL |

> Note: when the credential lifecycle is managed via Verana VPR events (per [[VSA-VTI-VTJSC] VTJSC Management](#vsa-vti-vtjsc-vtjsc-management)), the create and delete methods MUST be disabled. The agent SHOULD respond with HTTP `409 Conflict` if a caller attempts a managed mutation.

#### [VSA-ADM-LVP-LIST] listLinkedCredentials

Retrieves one or all Verifiable Trust Credentials linked to this agent.

**Inputs** (OPTIONAL query parameters):

- `schemaId` — full URL of a stored credential schema; when set, return only the VTC bound to that schema.
- `limit` (default `10`) — page size.
- `page` (default `1`) — 1-indexed page number.

**Output**: paginated list of Verifiable Trust Credentials.

#### [VSA-ADM-LVP-CREATE] createLinkedCredential

Creates and stores a new Verifiable Trust Credential. The `schemaBaseId` defines the base name used to construct the resulting credential schema URL.

**Inputs** (request body):

- `schemaBaseId` (REQUIRED) — short identifier used to construct the schema URL, e.g. `organization` produces `https://<agent>/vt/schemas-organization-c-vp.json`.
- `credential` (REQUIRED) — the W3C Verifiable Credential payload.

**Output**: confirmation. The resulting schema URL is derived from `schemaBaseId`.

**Errors**:

- `INVALID_CREDENTIAL` — credential payload is malformed or missing required fields.

#### [VSA-ADM-LVP-DELETE] deleteLinkedCredential

Deletes a stored Verifiable Trust Credential identified by its schema URL.

**Inputs** (REQUIRED query parameter):

- `schemaId` — full URL of the VTC to delete.

**Output**: empty body.

**Errors**:

- `NOT_FOUND` — no Verifiable Trust Credential with the given `schemaId`.

### [VSA-ADM-JSC] Verifiable Trust JSON Schema Credentials

Methods that manage Verifiable Trust JSON Schema Credentials (VTJSCs) — credentials by which a Trust Registry binds an on-chain `CredentialSchema` to the Ecosystem DID that governs it. The issuer DID of a VTJSC MUST equal the Ecosystem DID of the Trust Registry that created the referenced `CredentialSchema`.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| JSON Schema Credentials | `listJsonSchemaCredentials` | `GET` | `/v1/vt/json-schema-credentials` | [see](#vsa-adm-jsc-list-listjsonschemacredentials) | INTERNAL |
| JSON Schema Credentials | `createOrUpdateJsonSchemaCredential` | `POST` | `/v1/vt/json-schema-credentials` | [see](#vsa-adm-jsc-create-createorupdatejsonschemacredential) | INTERNAL |
| JSON Schema Credentials | `deleteJsonSchemaCredential` | `DELETE` | `/v1/vt/json-schema-credentials` | [see](#vsa-adm-jsc-delete-deletejsonschemacredential) | INTERNAL |

> Note: when the VTJSC lifecycle is managed via Verana VPR events (see [[VSA-VTI-VTJSC] VTJSC Management](#vsa-vti-vtjsc-vtjsc-management)), the create and delete methods MUST be disabled. The agent SHOULD respond with HTTP `409 Conflict` if a caller attempts a managed mutation.

#### [VSA-ADM-JSC-LIST] listJsonSchemaCredentials

Retrieves one or multiple Verifiable Trust JSON Schema Credentials.

**Inputs** (OPTIONAL query parameters):

- `schemaId` — full URL or identifier of a specific VTJSC.
- `limit` (default `10`) — page size.
- `page` (default `1`) — 1-indexed page number.

**Output**: paginated list of VTJSCs.

#### [VSA-ADM-JSC-CREATE] createOrUpdateJsonSchemaCredential

Creates or updates a VTJSC.

**Inputs** (request body):

- `schemaBaseId` (REQUIRED) — short identifier used to construct the resulting VTJSC URL, e.g. `organization` produces `https://<agent>/vt/schemas-organization-jsc.json`.
- `jsonSchemaRef` (REQUIRED) — VPR URI of the corresponding `CredentialSchema` entry, e.g. `vpr:verana:vna-testnet-1/cs/v1/js/12345678`.

**Output**: confirmation that the VTJSC was created or updated.

**Errors**:

- `INVALID_INPUT` — schema parameters are malformed or missing.
- `ISSUER_MISMATCH` — the agent's DID does not match the Ecosystem DID of the Trust Registry that owns the referenced `CredentialSchema`.

#### [VSA-ADM-JSC-DELETE] deleteJsonSchemaCredential

Deletes a stored VTJSC.

**Inputs** (REQUIRED query parameter):

- `schemaId` — full URL or identifier of the VTJSC to delete.

**Output**: empty body.

**Errors**:

- `NOT_FOUND` — no VTJSC with the given `schemaId`.

### [VSA-ADM-FL] Flow Management

The following methods list and progress credential-acquisition flows handled by the agent (see [[VSA-VTI-FLOW-STATE] Flow State](#vsa-vti-flow-state-flow-state)).

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Flow Management | `listFlows` | `GET` | `/v1/vt/flows` | [see](#vsa-adm-fl-list-listflows) | INTERNAL, CORPORATION (`VSOperatorAuthorization`, msg_types ⊇ any of {`SetParticipantOPValidated`, `StartParticipantOP`, `RenewParticipantOP`}, scope: any `Participant` operated by the agent) |
| Flow Management | `editCredentialClaims` | `PUT` | `/v1/vt/flows/{participant_session_id}/claims` | [see](#vsa-adm-fl-edit-editcredentialclaims) | INTERNAL, CORPORATION (`VSOperatorAuthorization`, msg_types ⊇ {`SetParticipantOPValidated`}, scope: validator `Participant` of the flow) |
| Flow Management | `sendOobLink` | `POST` | `/v1/vt/flows/{participant_session_id}/oob-link` | [see](#vsa-adm-fl-send-sendooblink) | INTERNAL, CORPORATION (`VSOperatorAuthorization`, msg_types ⊇ {`SetParticipantOPValidated`}, scope: validator `Participant` of the flow) |
| Flow Management | `validateFlow` | `POST` | `/v1/vt/flows/{participant_session_id}/validate` | [see](#vsa-adm-fl-validate-validateflow) | INTERNAL, CORPORATION (`VSOperatorAuthorization`, msg_types ⊇ {`SetParticipantOPValidated`}, scope: validator `Participant` of the flow) |
| Flow Management | `revokeCredential` | `POST` | `/v1/vt/flows/{participant_session_id}/revoke-credential` | [see](#vsa-adm-fl-revoke-revokecredential) | INTERNAL, CORPORATION (`VSOperatorAuthorization`, msg_types ⊇ {`RevokeParticipant`}, scope: validator `Participant` of the flow) |

> Note: some VS Agent implementations may not support all actions, or may prefer sending the user to a portal for providing proofs, etc., using the OOB link.

#### [VSA-ADM-FL-LIST] listFlows

Lists and inspects existing credential-acquisition flows handled by the agent.

**Inputs** (all OPTIONAL filters):

- `role` — filter by agent role in the flow: `applicant` or `validator`.
- `connectionState` — one of the Connection State values defined in [Flow State](#vsa-vti-flow-state-flow-state).
- `flowState` — one of the Flow State values defined in [Flow State](#vsa-vti-flow-state-flow-state).
- `peerDID` — DID of the remote peer.
- `participant_id` — applicant or validator `Participant` identifier. If `role` is `applicant`, `participant_id` is the validator `Participant`. If `role` is `validator`, `participant_id` is the applicant `Participant`.
- `schema_id` — credential schema identifier.
- `participant_session_id` — DIDComm session identifier.

**Output**: an array of flow records. Each record MUST include at minimum:

- peer DID;
- the applicable `participant_id`(s);
- `schema_id`;
- `participant_session_id`;
- last-event timestamp;
- submitted credential claims and proofs;
- any outstanding `OOB_LINK` URL;
- once a credential has been generated: the offered credential identifier, its digest, and the on-chain `ParticipantSession` reference.

**Requirements**: none beyond caller authentication and corporation-scoped authorization.

#### [VSA-ADM-FL-EDIT] editCredentialClaims

Creates, modifies, or overrides the credential claims submitted by the applicant for a given flow.

**Path parameters**:

- `participant_session_id` (REQUIRED) — identifier of the target flow.

**Inputs** (request body):

- `claims` (REQUIRED) — replacement or patch set for the credential claims.

**Output**: the updated claim set as stored on the flow.

**Requirements**:

- MUST be called by an account that is the `vs_operator` of a `VSOperatorAuthorization` whose `ParticipantAuthorizationRecord` for the validator `Participant` in scope includes `SetParticipantOPValidated` in `msg_types` (see [Authorization](#authorization)).
- MUST refuse when connection is not in `ESTABLISHED` state.
- MUST refuse when the flow is not `VALIDATING` or `CRED_REVOKED` (see [Flow State](#vsa-vti-flow-state-flow-state)).

**Errors**:

- `NOT_FOUND` — no flow with the given `participant_session_id`.
- `INVALID_STATE` — the flow is not in `VALIDATING` or `CRED_REVOKED` state.

#### [VSA-ADM-FL-SEND] sendOobLink

Sends or resends an `OOB_LINK` DIDComm message to the applicant for out-of-DIDComm information collection (see [[VSA-VTI-FLOW-DIDCOMM] DIDComm Protocol Binding](#vsa-vti-flow-didcomm-didcomm-protocol-binding)).

**Path parameters**:

- `participant_session_id` (REQUIRED) — identifier of the target flow.

**Inputs** (request body):

- `url` (REQUIRED) — the OOB URL to send.
- `message` (OPTIONAL) — descriptive text shown to the applicant.

**Output**: confirmation that the message was dispatched.

**Requirements**:

- MUST be called by an account that is the `vs_operator` of a `VSOperatorAuthorization` whose `ParticipantAuthorizationRecord` for the validator `Participant` in scope includes `SetParticipantOPValidated` in `msg_types` (see [Authorization](#authorization)).
- MUST refuse when the flow's Connection State is not `ESTABLISHED`.

**Errors**:

- `NOT_FOUND` — no flow with the given `participant_session_id`.
- `INVALID_STATE` — the flow's Connection State is not `ESTABLISHED`.

#### [VSA-ADM-FL-VALIDATE] validateFlow

Marks the applicant's documentation as validated for a given flow. When an Onboarding Process is involved, this is independent from the on-chain `SetParticipantOPValidated` transaction and MAY trigger credential issuance (see [[VSA-VTI-FLOW-OP-NEW] New Onboarding Process](#vsa-vti-flow-op-new-new-onboarding-process) steps 6–8).

**Path parameters**:

- `participant_session_id` (REQUIRED) — identifier of the target flow.

**Inputs**: none.

**Output**: the updated flow record.

**Requirements**:

- MUST be called by an account that is the `vs_operator` of a `VSOperatorAuthorization` whose `ParticipantAuthorizationRecord` for the validator `Participant` in scope includes `SetParticipantOPValidated` in `msg_types` (see [Authorization](#authorization)).

**Errors**:

- `NOT_FOUND` — no flow with the given `participant_session_id`.
- `INVALID_STATE` — the flow is not in a state where validation is expected.

#### [VSA-ADM-FL-REVOKE] revokeCredential

Revokes a previously issued credential for a given flow. The agent MUST notify the applicant via a `CRED_STATE_CHANGE` message over DIDComm (see [[VSA-VTI-FLOW-UPD] Validator Updates](#vsa-vti-flow-upd-validator-updates)).

**Path parameters**:

- `participant_session_id` (REQUIRED) — identifier of the target flow.

**Inputs** (request body):

- `reason` (OPTIONAL) — human-readable reason for the revocation.

**Output**: confirmation of revocation.

**Requirements**:

- MUST be called by an account that is the `vs_operator` of a `VSOperatorAuthorization` whose `ParticipantAuthorizationRecord` for the validator `Participant` in scope includes `RevokeParticipant` in `msg_types` (see [Authorization](#authorization)).
- MUST send a `CRED_STATE_CHANGE` DIDComm message to the applicant.

**Errors**:

- `NOT_FOUND` — no flow with the given `participant_session_id`.

> Applicant-side methods — requiring `VSOperatorAuthorization` with `msg_types` containing `StartParticipantOP` and/or `RenewParticipantOP`, scoped to the applicant `Participant` — are to be specified.

### [VSA-ADM-SE] Service Endpoint Management

The following methods manage the **additional consumable** service entries declared in the agent's DID Document — i.e., the entries added under [[VS-SVC-3]](https://verana-labs.github.io/verifiable-trust-spec/#vs-svc-service-declaration), such as `MCP`, `A2A`, `LinkedDomains`, or any other ecosystem-defined consumable type. Note that `VsAgentAdminAPI` entries are auto-managed and MUST NOT be manipulated through these methods.

| Module | Method Name | HTTP Method | Relative REST API path | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |
| Service Endpoint Management | `listServiceEndpoints` | `GET` | `/v1/vt/service-endpoints` | [see](#vsa-adm-se-list-listserviceendpoints) | INTERNAL |
| Service Endpoint Management | `addServiceEndpoint` | `POST` | `/v1/vt/service-endpoints` | [see](#vsa-adm-se-add-addserviceendpoint) | INTERNAL |
| Service Endpoint Management | `updateServiceEndpoint` | `PATCH` | `/v1/vt/service-endpoints/{id}` | [see](#vsa-adm-se-update-updateserviceendpoint) | INTERNAL |
| Service Endpoint Management | `deleteServiceEndpoint` | `DELETE` | `/v1/vt/service-endpoints/{id}` | [see](#vsa-adm-se-delete-deleteserviceendpoint) | INTERNAL |

These methods MUST NOT be used to manipulate:

- `DIDCommMessaging` entries: the mandatory bootstrap channel required by [[VS-SVC-2]](https://verana-labs.github.io/verifiable-trust-spec/#vs-svc-service-declaration) is derived from the agent's container configuration and is maintained automatically by the agent.
- `LinkedVerifiablePresentation` entries: per [[VS-SVC-6]](https://verana-labs.github.io/verifiable-trust-spec/#vs-svc-service-declaration), those are part of the identity layer and are produced and maintained automatically by the agent through [[VSA-VTI-VTJSC] VTJSC Management](#vsa-vti-vtjsc-vtjsc-management) and the credential acquisition flows.
- `VsAgentAdminAPI` entries: per [[VSA-VTI-DIDDOC] DID Document Service Entries](#vsa-vti-diddoc-did-document-service-entries), this entry (when present) is maintained automatically by the agent from `ADMIN_API_PUBLIC_URL`.

For every successful mutation (`addServiceEndpoint`, `updateServiceEndpoint`, `deleteServiceEndpoint`):

- the agent MUST publish the updated DID Document;
- the agent SHOULD call `TriggerResolver` on-chain so the agent's trust-resolution state reflects the change.

#### [VSA-ADM-SE-LIST] listServiceEndpoints

Returns every consumable service entry currently declared in the agent's DID Document.

**Inputs**: none.

**Output**: an array of service entries, each containing:

- `id` — DID-relative URL of the entry (e.g., `did:example:agent#mcp`).
- `type` — service type.
- `serviceEndpoint` — URI string or object as defined in [DID-CORE].

**Requirements**:

- MUST exclude entries whose `type` is `DIDCommMessaging` or `LinkedVerifiablePresentation` (managed automatically by the agent — see preamble).
- MUST exclude entries whose `type` is `VsAgentAdminAPI` (managed automatically by the agent — see preamble).
- MUST reflect the currently published DID Document.

#### [VSA-ADM-SE-DELETE] deleteServiceEndpoint

Removes a consumable service entry from the agent's DID Document.

**Path parameters**:

- `id` (REQUIRED) — identifier of the entry to remove (DID-relative fragment such as `#mcp`, or full DID URL). The value MUST be percent-encoded when placed in the URL path (e.g., `%23mcp` for `#mcp`).

**Inputs**: none.

**Output**: the deleted entry.

**Requirements**:

- MUST refuse if `id` refers to a `DIDCommMessaging`, `LinkedVerifiablePresentation`, or `VsAgentAdminAPI` entry (managed automatically by the agent — see preamble).

**Errors**:

- `NOT_FOUND` — no entry with the given `id`.
- `DIDCOMM_ENTRY` — `id` refers to a `DIDCommMessaging` entry.
- `LINKED_VP_ENTRY` — `id` refers to a `LinkedVerifiablePresentation` entry.
- `ADMIN_API_ENTRY` — `id` refers to a `VsAgentAdminAPI` entry.

#### [VSA-ADM-SE-ADD] addServiceEndpoint

Adds a new consumable service entry to the agent's DID Document.

**Inputs**:

- `type` (REQUIRED) — service type (e.g., `MCP`, `A2A`, `LinkedDomains`). MUST NOT be `DIDCommMessaging`, `LinkedVerifiablePresentation`, or `VsAgentAdminAPI`.
- `serviceEndpoint` (REQUIRED) — URI string or object per [DID-CORE].
- `id` (OPTIONAL) — DID-relative fragment for the new entry. If omitted, the agent MUST generate a unique fragment.

**Output**: the resulting service entry.

**Requirements**:

- MUST refuse `type = DIDCommMessaging`, `type = LinkedVerifiablePresentation`, or `type = VsAgentAdminAPI` (managed automatically by the agent — see preamble).
- MUST refuse if the resulting `id` collides with an existing entry in the DID Document.
- MUST validate the shape of `serviceEndpoint` per [DID-CORE] before publishing.

**Errors**:

- `DUPLICATE_ID` — an entry with the given/derived `id` already exists.
- `INVALID_SERVICE_ENDPOINT` — `serviceEndpoint` does not conform to [DID-CORE].
- `DIDCOMM_ENTRY` — caller attempted to add a `DIDCommMessaging` entry.
- `LINKED_VP_ENTRY` — caller attempted to add a `LinkedVerifiablePresentation` entry.
- `ADMIN_API_ENTRY` — caller attempted to add a `VsAgentAdminAPI` entry.

#### [VSA-ADM-SE-UPDATE] updateServiceEndpoint

Updates the `type` and/or `serviceEndpoint` of an existing consumable service entry in the agent's DID Document.

**Path parameters**:

- `id` (REQUIRED) — identifier of the entry to update. The value MUST be percent-encoded when placed in the URL path (e.g., `%23mcp` for `#mcp`).

**Inputs** (request body):

- `type` (OPTIONAL) — new service type.
- `serviceEndpoint` (OPTIONAL) — new endpoint value.

At least one of `type` or `serviceEndpoint` MUST be provided.

**Output**: the updated service entry.

**Requirements**:

- MUST refuse to update an entry whose existing `type` is `DIDCommMessaging`, `LinkedVerifiablePresentation`, or `VsAgentAdminAPI`, and MUST refuse to change an entry's `type` to `DIDCommMessaging`, `LinkedVerifiablePresentation`, or `VsAgentAdminAPI` (managed automatically by the agent — see preamble).
- MUST validate the new `serviceEndpoint` shape per [DID-CORE] before publishing.

**Errors**:

- `NOT_FOUND` — no entry with the given `id`.
- `DIDCOMM_ENTRY` — `id` refers to a `DIDCommMessaging` entry, or the requested change would produce one.
- `LINKED_VP_ENTRY` — `id` refers to a `LinkedVerifiablePresentation` entry, or the requested change would produce one.
- `ADMIN_API_ENTRY` — `id` refers to a `VsAgentAdminAPI` entry, or the requested change would produce one.
- `INVALID_SERVICE_ENDPOINT` — `serviceEndpoint` does not conform to [DID-CORE].
