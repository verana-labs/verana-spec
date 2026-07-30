# Verana Integration Guideline — Personal Wallets

**Status:** DRAFT 0.2 (shared demo cast) · 2026-07-30
**Audience:** developers of open-source **personal wallets** (mobile or web software operated by a person: identity wallets, DIDComm messengers, agentic browsers).
**Goal:** every personal wallet integrates Verana **the same way** and presents trust information **the same way**.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14).

Normative background: the Verifiable Trust spec ([v3 — current target](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html), [v4 draft](https://verana-labs.github.io/verifiable-trust-spec/versions/v4/) — section tags [TR], [VUA-CONN-VS], [CIT], [PRT], [WL] cited from v4) and the VPR spec ([v3](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html), [v4 draft](https://verana-labs.github.io/verifiable-trust-vpr-spec/versions/v4/)). See the protocol-version note in the [playground README](../README.md), incl. the v3↔v4 vocabulary mapping. Shared endpoints and configuration: same README.

---

## 1. What the integration does

A Verana-integrated personal wallet answers three questions for its user, at the right moments, using the **Trust Resolver**:

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

## 3. Configuration [PW-CFG]

- **[PW-CFG-1]** The wallet MUST maintain a list of VPR networks (endpoints for resolver, indexer, RPC) and a list of trusted ECS Ecosystem DIDs, per [WL-VPR] and [WL-ECS]. Use the shared testnet configuration from the [README](../README.md).
- **[PW-CFG-2]** The wallet MUST label non-production networks. Any trust status obtained from a network whose `production` flag is `false` MUST be visibly marked (e.g. a `TESTNET` chip on the Proof-of-Trust).
- **[PW-CFG-3]** The wallet MAY use the public resolver or a self-hosted instance. The resolver in use SHOULD be shown in an about/diagnostics screen.

## 4. Trust resolution [PW-RES]

### When to resolve

- **[PW-RES-1] On connection.** When the user initiates or accepts a connection to a service (DIDComm OOB invitation, deep link, or any flow that yields a service DID), the wallet MUST resolve the service DID (Q1) **before** the connection is used ([VUA-CONN-VS]).
- **[PW-RES-2] On credential offer.** When a service offers a credential, the wallet MUST verify (Q2) that the offering service is an **authorized issuer of that credential schema in its ecosystem** at the current time, **before** presenting the accept action to the user ([CIT-3]).
- **[PW-RES-3] On presentation request.** When a service requests a credential presentation, the wallet MUST verify (Q3) that the requesting service is an **authorized verifier of that credential schema in its ecosystem**, **before** presenting the share action to the user ([PRT-3]).
- **[PW-RES-4] Track B hook points.** In OID4VCI, Q1+Q2 run when the credential offer is received, against the issuer's DID. In OID4VP, Q1+Q3 run when the authorization request is received, against the verifier's DID (e.g. `client_id` with a DID scheme). The Proof-of-Trust is rendered **inside** the existing consent screen, above the fold, before the user can accept.
- **[PW-RES-9] Resolvable DID methods only.** Only DID methods that are **resolvable** — the DID resolves to a **DID Document** — can be trust-resolved: **no DID Document means no Linked Verifiable Presentations, and no Linked VPs means no verifiable trust.** In practice: `did:web` / `did:webvh`-class methods qualify; key-derived methods (`did:key`, `did:jwk` — permitted by DIIP) yield only a key, so they carry no linked-vp and no trust chain. A peer identified by such a method MUST be rendered `UNTRUSTED`, with the reason stated ("this issuer/verifier cannot present verifiable trust credentials").

### How to handle results

- **[PW-RES-5]** The wallet MUST derive one of four states: `RESOLVING`, `TRUSTED`, `UNTRUSTED`, `UNVERIFIED` (resolver unreachable, timeout, or malformed response). There is no fifth state.
- **[PW-RES-6]** `UNVERIFIED` MUST NOT be presented as either trusted or untrusted; it is "could not verify" and MUST offer a retry.
- **[PW-RES-7]** Results MAY be cached until the `expiresAt` returned by the resolver, and MUST be re-resolved after it. A cached result MUST show its evaluation time.
- **[PW-RES-8]** If a previously `TRUSTED` peer resolves to `UNTRUSTED` (or a Q2/Q3 check fails) on a later interaction, the wallet MUST re-surface the Proof-of-Trust and require fresh user acknowledgment; it MUST NOT silently continue on a stale acceptance.

## 5. Proof-of-Trust presentation [PW-POT]

This section is the "**always show information the same way**" contract. The reference rendering is the Proof-of-Trust card on [verana.io/identity](https://verana.io/identity); the playground provides exportable UI assets.

### Anatomy — five blocks, in this order

1. **Status band** — the trust verdict:
   - `TRUSTED` → a **green check / shield** and the word "Trusted".
   - `UNTRUSTED` → a **red cross / warning** and the word "Untrusted". Never hidden, never softened to a neutral icon.
   - `UNVERIFIED` → a **gray question / warning** and "Could not verify", with a retry affordance.
   - Plus: the service DID (truncated middle, copyable) and the evaluation time or block.
2. **Service** — from the **ECS-Service** credential claims: name, type, logo, description. If absent: "No ECS-Service credential presented."
3. **Operated by** — from the **ECS-Organization** (or **ECS-Persona**) credential claims: legal name, country (flag), registry id, address (org) / name, country (persona). If absent: "No ECS-Organization or ECS-Persona credential presented."
4. **Other credentials** — **every additional credential presented by the service or its operator** (e.g. an ISO 9001-style certification credential, a sector accreditation): credential name/schema, issuer, and the ecosystem it belongs to. Each entry carries its own valid/invalid mark.
5. **Trust chain / failures** — for **each presented credential**, an **expandable detail** showing its full trust chain — `issuer → (optional grantor) → ecosystem` — with the **trust status of every link** (from the resolver's `permissionChain`), plus **icon-based links to the corresponding Verana registry entries**: the ecosystem, the credential schema, and the participant entries involved (opening the public network frontend / explorer view, e.g. `app.testnet.verana.network`). When `UNTRUSTED`, the list of **failed credentials with their error reasons** is a first-class block (failures teach verify-first; they are content, not an edge case).

### Interaction rules

- **[PW-POT-1]** On **first contact** with a service, the wallet MUST display the Proof-of-Trust and obtain an explicit user action (accept / cancel) **before** any message, credential exchange, or session bootstrap.
- **[PW-POT-2]** On a **credential offer**, the consent screen MUST show the status band plus the Q2 verdict in words: "✅ *Accredited Issuer (demo)* is an authorized issuer of *DemoCredential* in *Playground Ecosystem (demo)*" — or the red equivalent. If Q2 fails, the accept action MUST be disabled or demoted behind an explicit "accept anyway (unsafe)" step. [DECISION: hard-block vs. warn-and-allow — default in this draft: **hard-block on testnet playground scenarios**.]
- **[PW-POT-3]** On a **presentation request**, same as [PW-POT-2] with the Q3 verdict: "✅ *…* is an authorized verifier of *…* in *…*". A failed Q3 MUST NOT default to sharing.
- **[PW-POT-4]** All claims displayed in blocks 2–4 MUST come from **verified** credentials only. Claims from failed credentials MUST NOT be rendered as facts (they may appear inside the failures block, clearly marked).
- **[PW-POT-5]** The wallet MUST NOT invent trust signals: no stars, scores, or "verified" wording beyond what resolution returned. (Trust-score display from deposits is a future, resolver-provided field.)
- **[PW-POT-6]** Wallets keep their own look & feel (colors, typography, layout) — the block order, the state semantics, the wording patterns above, and the green-check / red-cross / gray-question iconography are the invariants.

## 6. Acceptance test [PW-TEST]

To be listed on the playground, run the **six DemoCredential scenarios** against the shared Playground demo cast (see [README](../README.md#the-reference-scenario) and [playground spec §4](../spec.md#4-the-personal-wallet-playground-one-page-for-all-wallets)) — the same six cards the single personal-wallets page shows — with **each credential format you claim in your `personal-wallets.yaml` entry** (`anoncreds` over DIDComm and/or `openid4vc-sdjwt` over OpenID4VCI/OpenID4VP):

1. Connect to `demo-issuer-accredited` → Proof-of-Trust renders `TRUSTED` with ECS-Org + ECS-Service (blocks 1–3); accept its **DemoCredential** offer (Q2 pass shown per [PW-POT-2]) and receive the credential.
2. Connect to `demo-issuer-unaccredited` → `TRUSTED` renders, but its DemoCredential offer shows the Q2 **fail** verdict and accept is blocked/demoted.
3. Attempt to connect to `demo-untrusted` → `UNTRUSTED` renders with failure reasons; the connection is not silently established.
4. Connect to `demo-verifier-accredited` → `TRUSTED`; its presentation request shows the Q3 pass verdict per [PW-POT-3]; present the DemoCredential received in step 1.
5. Connect to `demo-verifier-unaccredited` → `TRUSTED`, but its presentation request shows the Q3 **fail** verdict and sharing is blocked/demoted.
6. Attempt the verifier flow against `demo-untrusted` → `UNTRUSTED` again; no request is ever surfaced.

Submission is a PR to [`verana-labs/playground`](https://github.com/verana-labs/playground) with your **`personal-wallets.yaml` entry** (listing the tested `formats`), your **icon** under `wallets/<id>/`, and optional media of the run (recommended as evidence): up to **one screen capture per demo scenario** and a **single video** (its note MUST disclose editing/speed). See [README — Getting listed](../README.md#getting-listed-on-the-playground).

## 7. References

- Verifiable Trust spec v4 — [TR], [VUA-CONN-VS], [CIT], [PRT], [WL]
- VPR spec v4 — Participants
- Trust Resolver API — `https://resolver.testnet.verana.network/docs` (REST + ToIP TRQP)
- DIIP v5 — `https://fidescommunity.github.io/DIIP/` (Track B target profile)
- Reference Proof-of-Trust rendering — `https://verana.io/identity`
