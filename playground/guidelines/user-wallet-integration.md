# Verana Integration Guideline — User Wallets

**Status:** DRAFT 0.1 · 2026-07-16
**Audience:** developers of open-source **user wallets** (mobile or web software operated by a person: identity wallets, DIDComm messengers, agentic browsers).
**Goal:** every user wallet integrates Verana **the same way** and presents trust information **the same way**.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14).

Normative background: [Verifiable Trust spec v4](https://verana-labs.github.io/verifiable-trust-spec/) (esp. [TR], [VUA-REQ], [VUA-CONN-VS], [CIT], [PRT], [WL]) and the [VPR spec v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/). Shared endpoints and configuration: see the [playground README](../README.md).

---

## 1. What the integration does

A Verana-integrated user wallet answers three questions for its user, at the right moments, using the **Trust Resolver**:

| # | Question | When it is asked | Resolver query |
| --- | --- | --- | --- |
| **Q1** | Is this service a **trusted Verifiable Service**, and who operates it? | On every new connection to a service | `GET /v1/trust/resolve?did=…` |
| **Q2** | Is this service **authorized to issue** this credential (schema, ecosystem)? | On every credential offer | issuer-permission check for the offered schema |
| **Q3** | Is this service **authorized to verify** this credential (schema, ecosystem)? | On every presentation request | verifier-permission check for the requested schema |

Everything else in this guideline is the uniform way to ask these questions and display the answers.

## 2. Integration tracks

| Requirement | Track N — Native (DIDComm) | Track B — Bridge (OID4VC / DIIP) |
| --- | --- | --- |
| Trust resolution (Q1/Q2/Q3) | MUST | MUST |
| Proof-of-Trust presentation (§5) | MUST | MUST |
| DIDComm connections | MUST | N/A |
| OID4VCI / OID4VP flows | MAY | MUST (existing stack, unchanged) |

> **Deferred:** ECS-UserAgent issuance and presentation ([VUA-REQ]) are intentionally **out of scope of this revision** — the issuance infrastructure is not yet generally available. A later revision will add them; wallets integrated under this revision are not full-VT VUAs and are not presented as such.

Track B exists so that **DIIP/EUDI-style wallets keep their stack**: OpenID4VCI, OpenID4VP, SD-JWT VC, `did:web`/`did:jwk` identification of issuers and verifiers. The integration adds trust resolution and the Proof-of-Trust UI around the existing consent screens — nothing else changes.

## 3. Configuration [UW-CFG]

- **[UW-CFG-1]** The wallet MUST maintain a list of VPR networks (endpoints for resolver, indexer, RPC) and a list of trusted ECS Ecosystem DIDs, per [WL-VPR] and [WL-ECS]. Use the shared testnet configuration from the [README](../README.md).
- **[UW-CFG-2]** The wallet MUST label non-production networks. Any trust status obtained from a network whose `production` flag is `false` MUST be visibly marked (e.g. a `TESTNET` chip on the Proof-of-Trust).
- **[UW-CFG-3]** The wallet MAY use the public resolver or a self-hosted instance. The resolver in use SHOULD be shown in an about/diagnostics screen.

## 4. Trust resolution [UW-RES]

### When to resolve

- **[UW-RES-1] On connection.** When the user initiates or accepts a connection to a service (DIDComm OOB invitation, deep link, or any flow that yields a service DID), the wallet MUST resolve the service DID (Q1) **before** the connection is used ([VUA-CONN-VS]).
- **[UW-RES-2] On credential offer.** When a service offers a credential, the wallet MUST verify (Q2) that the offering service is an **authorized issuer of that credential schema in its ecosystem** at the current time, **before** presenting the accept action to the user ([CIT-3]).
- **[UW-RES-3] On presentation request.** When a service requests a credential presentation, the wallet MUST verify (Q3) that the requesting service is an **authorized verifier of that credential schema in its ecosystem**, **before** presenting the share action to the user ([PRT-3]).
- **[UW-RES-4] Track B hook points.** In OID4VCI, Q1+Q2 run when the credential offer is received, against the issuer's DID. In OID4VP, Q1+Q3 run when the authorization request is received, against the verifier's DID (e.g. `client_id` with a DID scheme). The Proof-of-Trust is rendered **inside** the existing consent screen, above the fold, before the user can accept.
- **[UW-RES-9] Resolvable peers only.** Trust resolution requires the issuer/verifier DID to resolve to a **DID Document that presents credentials** (`did:web`, `did:webvh`). A peer identified by a key-only method (`did:key`, `did:jwk` — permitted by DIIP but unable to present credentials) has no verifiable trust chain and MUST be rendered `UNTRUSTED`, with the reason stated ("this issuer/verifier cannot present verifiable trust credentials").

### How to handle results

- **[UW-RES-5]** The wallet MUST derive one of four states: `RESOLVING`, `TRUSTED`, `UNTRUSTED`, `UNVERIFIED` (resolver unreachable, timeout, or malformed response). There is no fifth state.
- **[UW-RES-6]** `UNVERIFIED` MUST NOT be presented as either trusted or untrusted; it is "could not verify" and MUST offer a retry.
- **[UW-RES-7]** Results MAY be cached until the `expiresAt` returned by the resolver, and MUST be re-resolved after it. A cached result MUST show its evaluation time.
- **[UW-RES-8]** If a previously `TRUSTED` peer resolves to `UNTRUSTED` (or a Q2/Q3 check fails) on a later interaction, the wallet MUST re-surface the Proof-of-Trust and require fresh user acknowledgment; it MUST NOT silently continue on a stale acceptance.

## 5. Proof-of-Trust presentation [UW-POT]

This section is the "**always show information the same way**" contract. The reference rendering is the Proof-of-Trust card on [verana.io/identity](https://verana.io/identity); the playground provides exportable UI assets.

### Anatomy — five blocks, in this order

1. **Status band** — the trust verdict:
   - `TRUSTED` → a **green check / shield** and the word "Trusted".
   - `UNTRUSTED` → a **red cross / warning** and the word "Untrusted". Never hidden, never softened to a neutral icon.
   - `UNVERIFIED` → a **gray question / warning** and "Could not verify", with a retry affordance.
   - Plus: the service DID (truncated middle, copyable) and the evaluation time or block.
2. **Service** — from the **ECS-Service** credential claims: name, type, logo, description. If absent: "No ECS-Service credential presented."
3. **Operated by** — from the **ECS-Organization** (or **ECS-Persona**) credential claims: legal name, country (flag), registry id, address (org) / name, country (persona). If absent: "No ECS-Organization or ECS-Persona credential presented."
4. **Other credentials** — **every additional credential presented by the service or its operator** (e.g. an ISO/IEC 42001-style AI-management credential, an ISO 9001-style credential, a sector accreditation): credential name/schema, issuer, and the ecosystem it belongs to. Each entry carries its own valid/invalid mark.
5. **Trust chain / failures** — collapsible detail: per credential, `issuer → presenter` with the verification result; and, when `UNTRUSTED`, the list of **failed credentials with their error reasons** as a first-class block (failures teach verify-first; they are content, not an edge case).

### Interaction rules

- **[UW-POT-1]** On **first contact** with a service, the wallet MUST display the Proof-of-Trust and obtain an explicit user action (accept / cancel) **before** any message, credential exchange, or session bootstrap.
- **[UW-POT-2]** On a **credential offer**, the consent screen MUST show the status band plus the Q2 verdict in words: "✅ *Acme CertBody* is an authorized issuer of *Certified AI Management (demo)* in *AI Assurance Ecosystem*" — or the red equivalent. If Q2 fails, the accept action MUST be disabled or demoted behind an explicit "accept anyway (unsafe)" step. [DECISION: hard-block vs. warn-and-allow — default in this draft: **hard-block on testnet playground scenarios**.]
- **[UW-POT-3]** On a **presentation request**, same as [UW-POT-2] with the Q3 verdict: "✅ *…* is an authorized verifier of *…* in *…*". A failed Q3 MUST NOT default to sharing.
- **[UW-POT-4]** All claims displayed in blocks 2–4 MUST come from **verified** credentials only. Claims from failed credentials MUST NOT be rendered as facts (they may appear inside the failures block, clearly marked).
- **[UW-POT-5]** The wallet MUST NOT invent trust signals: no stars, scores, or "verified" wording beyond what resolution returned. (Trust-score display from deposits is a future, resolver-provided field.)
- **[UW-POT-6]** Wallets keep their own look & feel (colors, typography, layout) — the block order, the state semantics, the wording patterns above, and the green-check / red-cross / gray-question iconography are the invariants.

## 6. Acceptance test [UW-TEST]

To be listed on the playground, record one uncut run of the **AI Assurance loop** (see [README](../README.md)):

1. Connect to the playground's demo AI agent → Proof-of-Trust renders `TRUSTED` with ECS-Org + ECS-Service + the ISO-42001-style credential (blocks 1–4).
2. Connect to the playground's **untrusted** demo service → `UNTRUSTED` renders with failure reasons; connection is not silently established.
3. Accept a credential offer from an **authorized** issuer (Q2 pass shown), then receive an offer from an **unauthorized** one (Q2 fail shown, accept blocked/demoted).
4. Receive a presentation request from an **authorized** verifier (Q3 pass shown), then from an **unauthorized** one (Q3 fail shown, share blocked/demoted).

Submit the recording with your `integration.yaml` (see [README — Getting listed](../README.md#getting-listed-on-the-playground)).

## 7. References

- Verifiable Trust spec v4 — [TR], [VUA-CONN-VS], [CIT], [PRT], [WL]
- VPR spec v4 — Participants
- Trust Resolver API — `https://resolver.testnet.verana.network/docs` (REST + ToIP TRQP)
- DIIP v5 — `https://fidescommunity.github.io/DIIP/` (Track B target profile)
- Reference Proof-of-Trust rendering — `https://verana.io/identity`
