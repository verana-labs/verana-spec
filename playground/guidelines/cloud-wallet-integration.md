# Verana Integration Guideline — Cloud Wallets

**Status:** DRAFT 0.1 · 2026-07-16
**Audience:** developers and operators of open-source **cloud wallets** — organizational / enterprise wallets and agent frameworks that host services, issue and verify credentials on behalf of an organization (e.g. credo-ts, ACA-Py, walt.id, Veramo, Identus, vs-agent).
**Goal:** every cloud wallet integrates Verana **the same way**, and publishes trust artifacts so that any integrated user wallet renders **the same Proof-of-Trust** for the services it hosts.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14).

Normative background: [Verifiable Trust spec v4](https://verana-labs.github.io/verifiable-trust-spec/versions/v4/) (esp. [VS-REQ], [VS-SVC], [VT-ECS-CRED], [CIB], [PRB], [VS-CONN-*], [TR]) and the [VPR spec v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/versions/v4/). Shared endpoints and configuration: see the [playground README](../README.md).

---

## 1. What the integration does

A Verana-integrated cloud wallet makes each service it hosts a **verifiable, accountable actor**:

1. The service is identified by a **resolvable DID** whose DID Document declares its endpoints and presents its credentials.
2. The service (and the organization behind it) holds **ECS credentials** — ECS-Service, plus ECS-Organization or ECS-Persona — so anyone can verify *what it is* and *who operates it* before connecting.
3. The service attaches **domain credentials** (e.g. an ISO 9001-style credential) from the ecosystems it participates in.
4. The service **verifies its peers** and only issues or requests presentations when **authorized** to do so in the relevant ecosystem.

The result, seen from any integrated user wallet: the uniform Proof-of-Trust — green check, ECS-Org, ECS-Service, and every other credential the org or service presents.

## 2. Integration patterns

| Pattern | What it is | Reach |
| --- | --- | --- |
| **A — Native** | Implement the Verifiable Trust behaviors directly in your stack (DIDComm, Linked VPs, trust resolution, VPR operations). | Full **Verifiable Service** conformance. |
| **B — Sidecar** *(recommended fast path)* | Run [`vs-agent`](https://github.com/verana-labs/vs-agent) next to your stack. It owns the service DID, DID Document, DIDComm channel, Linked VPs, and VPR transactions; your stack keeps its business logic and existing APIs. | Full **Verifiable Service** conformance with days-not-months effort. |
| **C — Bridge** | OID4VC-only stacks: publish a resolvable DID (`did:web`/`did:webvh`) with Linked VPs for the ECS credentials, and call the Trust Resolver for peer checks. **No DIDComm endpoint required.** | **Verified service identity** level — sufficient for the playground. (Full *Verifiable Service* conformance per the VT spec [VS-SVC-2] additionally requires DIDComm; optional here.) |

All three patterns share the requirements below; the DIDComm-conditional ones say so explicitly.

## 3. Service identity [CW-ID]

- **[CW-ID-1]** Each hosted service — including every **issuer** and **verifier** — MUST be identified by its own DID, **resolvable to a DID Document that can declare service endpoints and Linked Verifiable Presentations**. `did:webvh` is RECOMMENDED; `did:web` is accepted on the playground.
  > **Eligibility consequence:** cloud-wallet integration is limited to stacks that support such a resolvable DID method for the issuers/verifiers they host. Key-only methods (`did:key`, `did:jwk`) resolve to a bare key and cannot present credentials — they do not qualify, even where profiles like DIIP otherwise allow them.
- **[CW-ID-2]** A `DIDCommMessaging` service endpoint is required **only if** the service accepts DIDComm connections (serving Track N user wallets, or agent-to-agent DIDComm traffic). An issuer or verifier that interacts exclusively over OpenID4VC needs **no** DIDComm endpoint. *(For reference: full Verifiable Service conformance per the VT spec [VS-SVC-2] mandates DIDComm; the playground does not.)*
- **[CW-ID-3]** The DID Document MAY declare additional endpoints — `MCP`, `A2A`, `LinkedDomains` (website), or any other ([VS-SVC-3]). Peers will only consume them after trust resolution succeeds; where a DIDComm channel exists, authentication material for other endpoints SHOULD be obtained over it ([VS-SVC-7]).
- **[CW-ID-4]** Credentials MUST be presented as **Linked Verifiable Presentations** using the standard fragments, so resolvers and wallets find them deterministically ([VT-ECS-CRED]):
  - `#vpr-schemas-service-vtc-vp` → the ECS-Service credential
  - `#vpr-schemas-org-vtc-vp` → the ECS-Organization credential (or the persona fragment for ECS-Persona)
  - additional domain credentials per [VT-CRED-W3C-LINKED-VP]

## 4. ECS onboarding [CW-ECS]

- **[CW-ECS-1]** The organization MUST obtain an **ECS-Organization** (or **ECS-Persona**) credential, and each hosted service an **ECS-Service** credential, from an authorized issuer of the ECS Ecosystem. Two acquisition paths:
  - **Out-of-band** — complete the onboarding process and receive the signed credential out-of-band (e.g. via the playground's hosted onboarding portal), then publish it as a Linked VP. No protocol implementation required.
  - **In-band** — implement the [**Verifiable Trust Flow Protocol** (`vt-flow`)](../../v4/vt-flow-protocol/spec.md): the DIDComm superprotocol that orchestrates onboarding and credential acquisition between Applicant and Validator (the vs-agent sidecar implements it already — patterns A/B).

  [TODO: link the playground onboarding service once live.]
- **[CW-ECS-2]** Claim quality is a display contract — these values are what every user wallet renders on the Proof-of-Trust:
  - `name` — the real, public-facing name (org ≤ 512 chars, service ≤ 512 chars);
  - `logoUri` + `logoDigestSri` — a square PNG/JPEG/SVG that renders at 40 px, with a valid SRI digest;
  - org: `registryId`, `address`, `countryCode` (ISO 3166-1 alpha-2) — accurate and verifiable;
  - service: `type`, `description` (≤ 4096 chars), `minimumAgeRequired`, terms & privacy URIs with SRI digests.
- **[CW-ECS-3]** After publishing or changing Linked VPs, the cloud wallet MUST trigger re-resolution (`MsgTriggerResolver`, exposed by vs-agent and the playground) and MUST verify that the public resolver returns `trustStatus: TRUSTED` for the service DID before advertising it.
- **[CW-ECS-4]** On credential revocation or expiry, the cloud wallet MUST update the DID Document (remove the stale linked-vp) and trigger re-resolution — a service that keeps presenting a revoked credential will resolve `UNTRUSTED`.

## 5. Domain credentials [CW-DOM]

- **[CW-DOM-1]** A service MAY hold any number of additional Verifiable Trust credentials from ecosystems it joins (playground reference: the **ISO 9001-style demo credential** from the ISO Certification Ecosystem (demo)).
- **[CW-DOM-2]** Each domain credential MUST be published as a Linked VP on the service (or organization) DID Document so user wallets can display it in the "Other credentials" block.
- **[CW-DOM-3]** The onboarding process for a domain credential runs against the issuing ecosystem's participant tree (application, validation, fees per the VPR spec), with the same acquisition paths as [CW-ECS-1] (out-of-band, or in-band via `vt-flow`). The playground automates this for the demo ecosystem.

## 6. Verifying peers [CW-PEER]

- **[CW-PEER-1]** Before connecting to another service (A2A, MCP, DIDComm), the cloud wallet MUST trust-resolve the peer service DID and proceed only on `TRUSTED` ([VS-CONN-VS], [VS-SVC-4/5]). Pattern C stacks perform this via the public Trust Resolver API at minimum.

> **Deferred:** requesting and verifying the **ECS-UserAgent** credential of inbound user agents ([VS-CONN-VUA]) is intentionally **out of scope of this revision** — the issuance infrastructure is not yet generally available. A later revision will add it.

## 7. Issuing and verifying under authorization [CW-OPS]

The mirror of the user-wallet rules: a cloud wallet only exercises roles it holds.

- **[CW-OPS-1] Issue only when authorized.** Before offering a credential of a schema, the cloud wallet MUST hold an active **ISSUER participant** entry for that schema in its ecosystem ([CIB-3]). Wallets on the other end check this (their Q2); an unauthorized offer will be rejected and displayed as a red warning to the end user.
- **[CW-OPS-2] Verify only when authorized.** Before requesting a presentation, the cloud wallet MUST hold an active **VERIFIER participant** entry for that schema ([PRB-3]); peers check this (their Q3).
- **[CW-OPS-3]** The cloud wallet SHOULD expose its own trust state in its admin surface: current resolver status per hosted service, held participant entries and their expiries, and the outcome of the last re-resolution.

> **Deferred:** **Participant Sessions** (per-issuance / per-verification session records and trust-fee settlement on the VPR, *Create or Update Participant Session*) are intentionally **out of scope of this revision** — integrations do not create sessions or settle trust fees. A later revision will add them when the pay-per-issuance / pay-per-verification business models are activated on the playground.

## 8. Acceptance test [CW-TEST]

To be listed on the playground, record one uncut run of the **ISO Certification loop** from the hosting side:

1. Register a demo organization + one hosted AI-agent service; obtain ECS-Org + ECS-Service via the playground onboarding.
2. Obtain the ISO-9001-style demo credential from the demo certification body; publish all Linked VPs.
3. Show the public resolver returning `TRUSTED` for the service DID, and the playground reference user wallet rendering the full Proof-of-Trust (green check, ECS-Org, ECS-Service, ISO-9001-style credential).
4. Accept a connection from an integrated user wallet.
5. Issue one demo credential to the user wallet as an authorized issuer, and run one presentation request as an authorized verifier — then demonstrate the refusal path (attempt without authorization → peer wallet shows the red verdict).

Submit the recording with your `integration.yaml` (see [README — Getting listed](../README.md#getting-listed-on-the-playground)).

## 9. References

- Verifiable Trust spec v4 — [VS-REQ], [VS-SVC], [VT-ECS-CRED], [CIB], [PRB], [VS-CONN-VS], [TR]
- VPR spec v4 — Corporations, Ecosystems, Credential Schemas, Participants
- [`vs-agent`](https://github.com/verana-labs/vs-agent) — reference implementation & sidecar; spec in [`v4/vs-agent/spec.md`](../../v4/vs-agent/spec.md)
- Trust Resolver API — `https://resolver.testnet.verana.network/docs` (REST + ToIP TRQP)
- Organization-as-trust-anchor pattern — [2060-io/hologram-verifiable-services](https://github.com/2060-io/hologram-verifiable-services)
