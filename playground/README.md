# Verana Playground

**Status:** DRAFT 0.2 (shared demo cast) · 2026-07-30
**Site:** `https://playground.testnet.verana.network` (target)

The Verana Playground is an interactive website for:

1. **Understanding and testing the Verana concepts** — Sovereign Ecosystems, Verifiable Identity, and Discovery — through the step-by-step **Verana Explained** story (watch-only for organization-side steps, hands-on for end-user steps), running against the Verana testnet.
2. **Showcasing integrations of Verana in third-party wallets** — open-source **personal wallets** and **business wallets** — where every integration follows the same pattern, gets an identical per-wallet playground page, and presents trust information the same way.

**Protocol version:** v4 is not fully published yet — the playground targets **v3**, which is what runs on testnet today. These documents keep v4 terminology where concepts are equivalent (v3 **Trust Registry** = v4 *Ecosystem*; v3 **Permission** = v4 *Participant*). Sources of truth for now: [Verifiable Trust spec v3](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) and [VPR spec v3](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html); v4 drafts: [VT v4](https://verana-labs.github.io/verifiable-trust-spec/versions/v4/) · [VPR v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/versions/v4/).

> **ECS-Badge on v3:** created — the schema has been **added to the ECS ecosystem**. Badge flows run over **AnonCreds / DIDComm** for now, with **Hologram Messaging as the initial personal wallet**; OpenID4VC/OpenID4VP issuance & presentation will be enabled when available. (ECS-Badge is the **story** credential of `/usecases/vesta`; the personal-wallet playground pages use the **DemoCredential** of the Playground Ecosystem (demo) — see [the reference scenario](#the-reference-scenario).)

## Documents

| Document | Purpose |
| --- | --- |
| [`spec.md`](./spec.md) | The playground website specification: what-is-Verana intro, Verana Explained step cards, per-wallet playground templates (user + cloud), shared machinery, milestones. |
| [`verana-explained/spec.md`](./verana-explained/spec.md) | *Verana Explained* — the narrative on-ramp: the **Vesta Appliances** story in six chapters — the business & its impostor problem (1) · why Verana (2) · choosing ecosystems (3) · joining in practice (4) · the Vesta Repair Network, Zenith ✓ / Umbra ✗ (5) · being found (6, pending). Story / watch / hands-on format. |
| [`guidelines/personal-wallet-integration.md`](./guidelines/personal-wallet-integration.md) | Integration guideline for **personal wallets** (mobile / web wallets operated by a person). Includes the normative **Proof-of-Trust presentation pattern** so every wallet shows trust the same way. |
| [`guidelines/business-wallet-integration.md`](./guidelines/business-wallet-integration.md) | Integration guideline for **business wallets** (organizational / enterprise wallets and agent frameworks hosting services). |
| [`submission/README.md`](./submission/README.md) | Publication kit: FIDES use-case dossiers (Verana + 2060), catalog-entry checklist, collaborator roster, campaign calendar, UNFOLD. |

## The reference scenario

All **personal-wallet** integrations are validated against one shared cast — the **Playground demo cast** — and its six **DemoCredential scenarios**. Every personal-wallet playground page runs the same logic against the same services; only the wallet changes.

**The cast.** The **Playground Organization (demo)** — a corporation created on testnet for all demo services of the personal-wallet and business-wallet playgrounds — controls an anchor Verifiable Service, **Playground Demo**, which owns the **Playground Ecosystem (demo)** and defines its single **DemoCredential** schema (minimal claims: `name`, `demoId`; issued instantly, no evidence step). The demo services run `veranalabs/vs-agent:v1.12.0-oidc4vc.2` and serve the DemoCredential over **both rails**: AnonCreds/DIDComm (Track N — Hologram Messaging) and OpenID4VCI/OpenID4VP (Track B wallets). The ecosystem is deliberately reusable by other playground sections. Five standing demo services run against it:

| Service (slug) | Trust state (Q1) | DemoCredential accreditation |
| --- | --- | --- |
| `demo-issuer-accredited` | TRUSTED | ISSUER |
| `demo-issuer-unaccredited` | TRUSTED | none |
| `demo-verifier-accredited` | TRUSTED | VERIFIER |
| `demo-verifier-unaccredited` | TRUSTED | none |
| `demo-untrusted` | UNTRUSTED | n/a — no ECS credentials; used in both the issuer and verifier trios |

**The loop.** A person installs the wallet's **modified APK** (the Verana-integrated, testnet-configured build, downloaded from the wallet's playground page) — or its **standard build** when Verana support is built in (descriptor `verana_builtin: true`, e.g. Hologram Messaging) — then runs the six scenarios: the three issuer demos (Q2 pass · Q2 fail · Q1 fail) and the three verifier demos (Q3 pass · Q3 fail · Q1 fail), presenting the DemoCredential received from the accredited issuer. The wallet renders each verdict per the [personal-wallet guideline](./guidelines/personal-wallet-integration.md); the recorded run is the [PW-TEST] acceptance evidence and the source of the page's screen captures.

> **Business-wallet note:** the business-wallet acceptance loop ([BW-TEST]) still references the earlier *ISO Certification* scenario until the §5 template is aligned with the shared cast (see [spec §5](./spec.md#5-the-business-wallet-playground-identical-template)). Where ISO-style demo credentials appear, public copy MUST describe them as "ISO 9001-**style** quality-management credential (demo)" and MUST NOT imply any real certification.

## Shared reference

### Testnet endpoints

| Component | Endpoint |
| --- | --- |
| Chain RPC | `https://rpc.testnet.verana.network` |
| Chain API (LCD) | `https://api.testnet.verana.network` |
| Indexer | `https://idx.testnet.verana.network` |
| **Trust Resolver** | `https://resolver.testnet.verana.network` ([API docs](https://resolver.testnet.verana.network/docs)) |
| Network frontend | `https://app.testnet.verana.network` |
| Faucet (Hologram chatbot VS) | `https://faucet-vs.testnet.verana.network` |
| MOSIP playground | `https://playground.mosip.testnet.verana.network` |

### Network configuration ([WL] whitelists)

Per the Verifiable Trust spec ([WL-VPR], [WL-ECS]), integrated wallets maintain a list of VPRs and a list of trusted ECS Ecosystem DIDs:

```json
{
  "verifiablePublicRegistries": [
    {
      "id": "vna-testnet-1",
      "scheme": "vpr:verana:vna-testnet-1",
      "api": ["https://idx.testnet.verana.network"],
      "rpc": ["https://rpc.testnet.verana.network"],
      "resolver": ["https://resolver.testnet.verana.network"],
      "version": "1",
      "production": false
    }
  ],
  "ecsEcosystems": [
    {
      "did": "did:webvh:QmPXNqN9qj5eeFviA7d1ToPUPiN8KZcn2QwSWFjZXx4dZS:organization-vs.main.demos.testnet.verana.network",
      "vpr": "vna-testnet-1"
    }
  ]
}
```

> The ecosystem DID above is the demo organization anchor from [`verana-labs/verana-demos`](https://github.com/verana-labs/verana-demos) (`organization-vs`), resolved from its public DID Document.

### Trust Resolution API (summary)

Both guidelines rely on the public Trust Resolver:

```
GET {RESOLVER_URL}/v1/trust/resolve?did={did}&detail=summary|full
```

Response (abridged):

```json
{
  "did": "did:webvh:…",
  "trustStatus": "TRUSTED | UNTRUSTED",
  "production": false,
  "evaluatedAt": "…", "evaluatedAtBlock": 123456, "expiresAt": "…",
  "credentials": [
    {
      "ecsType": "ECS-SERVICE | ECS-ORG | ECS-PERSONA | …",
      "claims": { "name": "…", "…": "…" },
      "issuedBy": "did:…", "presentedBy": "did:…",
      "result": "VALID", "permissionChain": [ "…" ]
    }
  ],
  "failedCredentials": [ { "id": "…", "error": "…", "errorCode": "…" } ]
}
```

The resolver also exposes a **ToIP TRQP** interface for trust-registry queries. Wallets MAY self-host the resolver and indexer (both open source) instead of using the public instances.

### Integration tracks

| Track | For | In one line |
| --- | --- | --- |
| **Track N — Native** | DIDComm-capable wallets/agents | Native Verifiable Trust integration: DIDComm bootstrap, trust resolution before connect. |
| **Track B — Bridge** | OID4VC (DIIP/EUDI-style) wallets and stacks | Keep your existing OpenID4VCI/OpenID4VP + SD-JWT VC flows; add Verana trust resolution of issuer/verifier DIDs (resolvable methods only: `did:web`/`did:webvh`) before consent, and render the Proof-of-Trust. |
| **Sidecar pattern** (cloud) | Any backend stack | Run [`vs-agent`](https://github.com/verana-labs/vs-agent) alongside your stack; it handles DIDs, DIDComm, Linked VPs, and VPR operations while your stack keeps its business logic. |

### Getting listed on the playground

Each integration appears in the Home wallet lists and gets its **own playground page** (identical template — [spec §4/§5](./spec.md)), all generated from a machine-readable descriptor submitted by PR to [`verana-labs/playground`](https://github.com/verana-labs/playground):

```yaml
# integration.yaml
name: Paradym Wallet
organization: Animo Solutions
kind: personal-wallet          # personal-wallet | business-wallet
repo: https://github.com/animo/paradym-wallet
license: Apache-2.0        # OSI-approved license required
track: bridge              # native | bridge (+ sidecar for cloud)
scenarios: [iso-certification-loop]
demo_video: https://…
download: https://…/paradym.apk   # mobile personal wallet: direct APK download; business wallet: URL of the hosted instance / product page
contact: …
logo: ./logo.svg
```

Requirements: the product is **open source** (OSI license), the acceptance scenario passes (see each guideline's test section), the wallet is **obtainable from its tile** — a mobile personal wallet MUST provide a direct **APK download link** (store links MAY complement it), a business wallet MUST provide a **URL** — and the descriptor + a screen recording are submitted by PR. Listed organizations may use the **"Runs on the Verana open trust layer"** badge.

## License

Same as the repository. Guideline text CC BY-SA 4.0 intended on publication.
