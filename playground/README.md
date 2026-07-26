# Verana Playground

**Status:** DRAFT 0.1 · 2026-07-16
**Site:** `https://playground.testnet.verana.network` (target)

The Verana Playground is an interactive website for:

1. **Understanding and testing the Verana concepts** — Sovereign Ecosystems, Verifiable Identity, and Discovery — through the step-by-step **Verana Explained** story (watch-only for organization-side steps, hands-on for end-user steps), running against the Verana testnet.
2. **Showcasing integrations of Verana in third-party wallets** — open-source **user wallets** and **cloud wallets** — where every integration follows the same pattern, gets an identical per-wallet playground page, and presents trust information the same way.

**Protocol version:** v4 is not fully published yet — the playground targets **v3**, which is what runs on testnet today. These documents keep v4 terminology where concepts are equivalent (v3 **Trust Registry** = v4 *Ecosystem*; v3 **Permission** = v4 *Participant*). Sources of truth for now: [Verifiable Trust spec v3](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) and [VPR spec v3](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html); v4 drafts: [VT v4](https://verana-labs.github.io/verifiable-trust-spec/versions/v4/) · [VPR v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/versions/v4/).

> **ECS-Badge on v3:** created — the schema has been **added to the ECS ecosystem**. Badge flows run over **AnonCreds / DIDComm** for now, with **Hologram Messaging as the initial user wallet**; OpenID4VC/OpenID4VP issuance & presentation will be enabled when available.

## Documents

| Document | Purpose |
| --- | --- |
| [`spec.md`](./spec.md) | The playground website specification: what-is-Verana intro, Verana Explained step cards, per-wallet playground templates (user + cloud), shared machinery, milestones. |
| [`verana-explained/spec.md`](./verana-explained/spec.md) | *Verana Explained* — the narrative on-ramp: ACME Corp's story, step by step — anchor & verification (1) · services, badges & credential login (2) · ISO 9001 via reusable KYB (3) · its own Partner Ecosystem (4) · Discovery (5, pending). Hybrid watch-only / hands-on format. |
| [`guidelines/user-wallet-integration.md`](./guidelines/user-wallet-integration.md) | Integration guideline for **user wallets** (mobile / web wallets operated by a person). Includes the normative **Proof-of-Trust presentation pattern** so every wallet shows trust the same way. |
| [`guidelines/cloud-wallet-integration.md`](./guidelines/cloud-wallet-integration.md) | Integration guideline for **cloud wallets** (organizational / enterprise wallets and agent frameworks hosting services). |
| [`submission/README.md`](./submission/README.md) | Publication kit: FIDES use-case dossiers (Verana + 2060), catalog-entry checklist, collaborator roster, campaign calendar, UNFOLD. |

## The reference scenario

All integrations are validated against one end-to-end loop, the **ISO Certification loop**:

1. A fictional **ISO Certification Ecosystem** registers on the Verana Public Registry (VPR): it publishes its governance framework, defines an *ISO 9001-style* quality-management credential schema (demo), and accredits fictional certification bodies through its participant tree.
2. An organization operates a **cloud wallet** hosting its AI agent as a **Verifiable Service**: the organization holds **ECS-Organization**, the agent holds **ECS-Service**, and the organization obtains the **ISO-9001-style credential** from an accredited certification body. All credentials are published as Linked Verifiable Presentations in the agent's DID Document.
3. A person opens any integrated **user wallet** and connects to the agent. Before the first interaction, the wallet trust-resolves the agent's DID and renders the **Proof-of-Trust**: ECS-Organization + ECS-Service + the ISO-9001-style credential, verified recursively up to the ecosystem root.
4. The agent is discoverable in the **Trust Graph** by the credentials it holds.

> **Trademark note:** the playground issues *demo* credentials from *fictional* certification bodies. Public copy MUST describe the credential as an "ISO 9001-**style** quality-management credential (demo)" and MUST NOT imply any real certification.

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
kind: user-wallet          # user-wallet | cloud-wallet
repo: https://github.com/animo/paradym-wallet
license: Apache-2.0        # OSI-approved license required
track: bridge              # native | bridge (+ sidecar for cloud)
scenarios: [iso-certification-loop]
demo_video: https://…
download: https://…/paradym.apk   # mobile user wallet: direct APK download; cloud wallet: URL of the hosted instance / product page
contact: …
logo: ./logo.svg
```

Requirements: the product is **open source** (OSI license), the acceptance scenario passes (see each guideline's test section), the wallet is **obtainable from its tile** — a mobile user wallet MUST provide a direct **APK download link** (store links MAY complement it), a cloud wallet MUST provide a **URL** — and the descriptor + a screen recording are submitted by PR. Listed organizations may use the **"Runs on the Verana open trust layer"** badge.

## License

Same as the repository. Guideline text CC BY-SA 4.0 intended on publication.
