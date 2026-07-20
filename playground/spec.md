# Verana Playground — Website Specification

**Status:** DRAFT 0.1 · 2026-07-16
**Site:** `https://playground.testnet.verana.network`
**Companions:** [user-wallet guideline](./guidelines/user-wallet-integration.md) · [cloud-wallet guideline](./guidelines/cloud-wallet-integration.md) · [shared reference](./README.md)

Source of truth for protocol facts: [Verifiable Trust spec v4](https://verana-labs.github.io/verifiable-trust-spec/) and [VPR spec v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/). Where this spec and those disagree, they win.

---

## 1. Purpose

An interactive website with two jobs:

1. **Understand and test the Verana concepts** — Sovereign Ecosystems, Verifiable Identity, Discovery — through guided journeys that execute **real operations on the Verana testnet** (nothing simulated).
2. **Showcase third-party wallet integrations** — user wallets and cloud wallets integrated per the guidelines, presented uniformly, provable live.

**Audiences**, in priority order: wallet developers / integrators; ecosystem builders (organizations, governments, certification bodies); evaluators and community (FIDES / GDC / UNFOLD); curious visitors.

## 2. Principles

- **Live, not simulated.** Every journey step performs a real testnet interaction (trust resolution, indexer query, chain transaction) and links its on-chain evidence (block, tx, entry) to the explorer. Where verana.io simulates (Query Console), the playground executes.
- **Bring your own wallet.** Every user-facing step is completable with **any listed user wallet** via QR code / deep link. The playground never requires a specific vendor's wallet; Hologram Messaging is the *reference* wallet, one tile among peers.
- **Same information, same way.** The site's own trust renderings implement the [Proof-of-Trust presentation pattern](./guidelines/user-wallet-integration.md#5-proof-of-trust-presentation-uw-pot) — the playground is itself the reference implementation of the pattern it asks integrators to follow.
- **One fictional universe.** The cast continues verana.io's worked examples: **Acme Corp** (organization + its Customer-Support AI Agent), the **AI Assurance Ecosystem (demo)** with accredited **CertBody A/B/C (demo)** issuers, and one deliberately failing actor, **Umbra Corp (demo)**. All demo entities are labeled `(demo)`; ISO-referencing credentials are always "ISO/IEC 42001-**style** (demo)". [DECISION: confirm names.]
- **Low barrier.** Browsing requires no account. Doing requires only an anonymous **playground session** (ephemeral, cookie/localStorage-scoped). Chain fees are invisible to visitors (§6.3).
- **Stay in lane.** Not the network frontend (org/ecosystem management → `app.testnet.verana.network`), not documentation (→ `docs.verana.io`), not marketing (→ `verana.io`). The playground teaches, proves, and showcases.

## 3. Architecture

| Component | What it is | Notes |
| --- | --- | --- |
| **Playground web** | Next.js site (verana.io stack family: App Router, Tailwind, TypeScript) | Static + server routes; reuses verana.io component recipes (PoT card, explorer widgets) |
| **Scenario backend** | Thin API in the playground web app | Orchestrates journeys: session state, pooled-account transactions, QR payload generation, webhooks from demo services |
| **Demo ecosystem services** | vs-agent instances: AI Assurance root, CertBody issuer(s), Acme demo agent, Umbra untrusted service, unauthorized issuer/verifier | Standing services; §6.1. Deployed like other testnet VSs (k8s) |
| **Onboarding portal** | The flow from [CW-ECS-1]: delivers ECS credentials to cloud-wallet integrators (DIDComm or hosted portal) | [DECISION: part of playground web vs. separate service] |
| **Integration registry** | `integrations/` directory in a public repo — one folder per integration: `integration.yaml` + logo + screenshots | PRs from integrators; CI validates schema; site builds tiles from it. [DECISION: host in `verana-labs/verana-playground` app repo] |
| **Upstream** | Resolver, indexer, chain API/RPC, faucet, `app.testnet` explorer links | Public testnet instances (see [README](./README.md#testnet-endpoints)) |

Non-functional: same conventions as the other verana-labs sites — open source (Apache-2.0 code / CC BY-SA 4.0 text), light+dark themes, WCAG-AA, consent-gated analytics, no accounts/PII beyond the anonymous session, English first (i18n-ready strings).

## 4. Information architecture

**Header nav:** `Learn` (journeys) · `Wallets` (showcase) · `Integrate` · `About` — plus a persistent **network chip** (`TESTNET · block N · resolver OK`) and the faucet link. One repeated CTA: **“Integrate your wallet”**.

```
/                     Home
/learn                Journey index (the triad)
/learn/ecosystems     Journey 1 — Build a trust ecosystem
/learn/identity       Journey 2 — Verify first, then connect
/learn/discovery      Journey 3 — Find who you can trust
/wallets              Wallet showcase (tiles)
/wallets/<slug>       Integration detail page
/integrate            Integrator hub (guidelines + quickstart + PoT UI kit)
/about                What is real, who runs it, links (incl. FIDES use-case page)
```

## 5. Pages

### 5.1 Home `/`

- **Hero** — "Try the open trust layer. Live." One paragraph (real testnet, any wallet, verify first), two buttons: *Start the tour* (→ `/learn/identity`, the strongest first experience) and *Integrate your wallet* (→ `/integrate`).
- **Live counters** (from indexer/registry): integrated wallets · trust resolutions run via the playground · sandbox ecosystems created. Counters are real or absent — never faked.
- **The triad** — three journey cards (same 1-2-3 sequencing idiom as verana.io).
- **The wallet wall** — logo strip of every listed integration → `/wallets`. This is the collaboration surface; it must be the most visually prominent block after the hero.
- **The reference loop** — a 4-step visual of the AI Assurance loop (ecosystem → credentials → PoT in *your* wallet → discovery) with *Run it now*.
- **Footer** — standard family footer + award-window banner (§8).

### 5.2 Journeys `/learn/*`

Common journey mechanics:

- A journey is a numbered sequence of steps; each step = one explanation card + one **live action** + one **evidence link** (explorer/resolver output). Progress is session-scoped.
- Steps that involve a wallet render a **QR code** (DIDComm OOB invitation or OID4VC request per the wallet's track) and, beside it, the **expected wallet rendering** — the reference PoT card in the state the wallet should show. Teaching the pattern and demonstrating conformance are the same act.
- Every journey ends with a **recap card**: what happened on chain / in the registry, with links, and "go deeper" pointers (docs, specs, `app.testnet`).

**Journey 1 — Build a trust ecosystem** `/learn/ecosystems`

1. **Inspect** the AI Assurance Ecosystem (demo): live view of its governance framework entry, credential schema ("Certified AI Management — ISO/IEC 42001-style (demo)"), and participant tree (root → CertBodies → services), read from the indexer.
2. **Create** your own sandbox ecosystem: pick a name; the playground executes the chain transactions (pooled accounts, §6.3); your session becomes its controller.
3. **Define** a credential schema from a template (clone the ISO-42001-style schema; ISO-9001-style variant available — reusability made visible).
4. **Accredit** a demo issuer into your tree (playground-mediated onboarding process).
5. **See it exist**: your ecosystem in the live registry list and in `app.testnet` — same links any third party would use.

**Journey 2 — Verify first, then connect** `/learn/identity` *(the flagship; also the user-wallet acceptance path [UW-TEST])*

1. **Resolve** Acme's Customer-Support AI Agent (demo): full PoT card — TRUSTED, ECS-Org, ECS-Service, ISO-42001-style credential, trust chain. (No wallet needed yet — the site resolves.)
2. **Connect with your wallet**: QR → your wallet resolves and shows the same PoT → accept → connected. Wallet picker lists every showcase wallet supporting the step, with per-wallet deep links.
3. **Meet Umbra Corp (demo)**: resolve/connect to the untrusted service → red verdict with failure reasons. Failures are content.
4. **Credential offer, authorized**: CertBody B issues you a demo credential — wallet shows the Q2 pass verdict.
5. **Credential offer, unauthorized**: Umbra offers the same schema — wallet shows the Q2 fail verdict, accept blocked/demoted.
6. **Presentation request, authorized / unauthorized**: the Q3 pair, same structure.
7. Recap: "your wallet just refused two rogue actors, with proof."

**Journey 3 — Find who you can trust** `/learn/discovery`

1. **Query live**: "services holding a Certified-AI-Management (demo) credential" — real indexer/graph query (the verana.io Query Console example, now executing).
2. **Scope and filter**: by ecosystem, schema, credential — including entities created in Journey 1 sessions.
3. **Resolve from results**: click a result → PoT card. Discovery → verification in one motion.
4. Recap: how agents will do this over API/MCP (link out to docs; MCP surface is roadmap).

### 5.3 Wallet showcase `/wallets` and `/wallets/<slug>`

- **Tile grid** built from the integration registry. Filters: kind (user/cloud) · track (native/bridge, +sidecar for cloud) · license.
- **Tile anatomy (uniform, fixed order):** logo · name · organization · kind chip · track chip · license chip · "AI Assurance loop ✓" badge (acceptance test passed) · actions: *Try it* (deep-link into Journey 2 step 2 with this wallet preselected) · *Video* · *Repo*.
- **Detail page:** the tile data + the integration's acceptance-test recording, screenshots of **its** PoT rendering, `integration.yaml` provenance (PR link), and the org's blurb.
- **The money shot:** a horizontal strip on `/wallets` showing **the same resolution of the same DID rendered by every integrated user wallet** — one screenshot per wallet, same five blocks visible. This strip is the single image used in award submissions and social posts.

### 5.4 Integrator hub `/integrate`

- Renders both guidelines (single source: this repo — no forked copies).
- **Quickstart ("integrate in a day"):** the [WL] config block, the one resolver call, the PoT UI kit (exportable components + state iconography + wording strings from §7 of the user-wallet guideline), the acceptance test, and *Submit your `integration.yaml` PR*.
- Standing offer: office hours / Discord channel for integrators. [TODO: channel link.]

### 5.5 About `/about`

What is real (testnet, real transactions) vs fictional (all `(demo)` entities); trademark disclaimer (ISO-style); who operates it (Verana Foundation in formation, stewarded by 2060 OÜ) and the demo-service operators; links: verana.io · docs · specs · `app.testnet` · **the FIDES use-case page** · UNFOLD marketplace entry; privacy/terms/cookies (family pattern).

## 6. Demo environment (normative for the playground operators)

### 6.1 Standing demo services

| Service | Role | State |
| --- | --- | --- |
| AI Assurance Ecosystem (demo) | Ecosystem root; controls the ISO-42001-style schema | TRUSTED |
| CertBody A/B/C (demo) | Accredited issuers of the demo credential | TRUSTED; ISSUER participant entries |
| Acme Corp — Customer-Support AI Agent (demo) | The trusted target: ECS-Org + ECS-Service + ISO-42001-style credential; authorized verifier of the demo credential | TRUSTED |
| Umbra Corp (demo) | The refusal path: broken/absent credentials; offers and requests without authorization | UNTRUSTED by construction |

All standing services run vs-agent (or conformant equivalents), are monitored, and their trust state is asserted by CI: **a standing service in the wrong trust state is a paging incident** — the playground's credibility is its live truth.

### 6.2 Sessions & sandbox hygiene

Anonymous session id (localStorage); sandbox entities (Journey 1 ecosystems, schemas, accreditations) are tagged with the session, auto-archived after **14 days** [DECISION], and created under rate limits (per-session and per-IP). No personal data is collected for sessions.

### 6.3 Fees & accounts

Visitors never handle keys or VNA: the scenario backend executes chain transactions from a **pooled set of playground accounts**, refilled from the faucet. The faucet chatbot remains linked for users who *want* to hold testnet VNA. (Trust-fee business models — Participant Sessions — are out of scope; see the cloud guideline deferral.)

## 7. Out of scope (this revision)

- ECS-UserAgent issuance/presentation; Participant Sessions / trust-fee settlement (deferred in the guidelines).
- Mainnet anything; token/price content (family-wide rule).
- User accounts, profiles, or persistence beyond the anonymous session.
- Ecosystem *management* UX (→ `app.testnet.verana.network`); tutorials/API reference (→ docs); a general demo-builder ("create your own scenario") — later.

## 8. Publication & award surface

- **FIDES:** the playground is the living evidence of the *"One trust layer, many wallets"* use case (Verana org) — see [`submission/README.md`](./submission/README.md). During the award window (submission → Sept 2), Home and About carry a discreet banner: "We're candidates for the Global Digital Trust Awards — support the use case" → the FIDES use-case page. Every wallet tile links its org's FIDES catalog entry when it exists.
- **UNFOLD:** the playground's OID4VC-capable demo issuer/verifier get listed in the EUDIW Unfold marketplace; the playground `/about` links back.
- **Badges:** listed integrations may use "Runs on the Verana open trust layer" (README terms).

## 9. Milestones

| # | Milestone | Target |
| --- | --- | --- |
| M1 | This spec + guidelines reviewed/approved | Jul 20 |
| M2 | Demo environment live (§6.1 services TRUSTED, monitored) | Jul 31 |
| M3 | Site MVP: Home + Journey 2 + Journey 3 + Wallet showcase with ≥ 3 wallets (Hologram, Paradym, Talao) + `/integrate` | Aug 8 |
| M4 | FIDES submission + catalog entries + campaign wave 1 | ~Aug 10 |
| M5 | Journey 1 (sandbox ecosystems) + remaining wallet integrations | Aug 20 |
| M6 | Award window ops (finalists Aug 24, voting → Sept 2, GDC Sept 1–3) | Sept |

## 10. Consolidated open items

1. Demo-entity naming (§2) — confirm Acme / CertBody / Umbra / "AI Assurance Ecosystem (demo)".
2. Testnet ECS Ecosystem DID (healthy) — blocks M2 ([README TODO](./README.md)).
3. Onboarding portal placement (§3) — in-app vs separate service.
4. Integration-registry repo (§3) — recommend `verana-labs/verana-playground`.
5. Sandbox retention (§6.2) — 14 days proposed.
6. [UW-POT-2] hard-block vs warn — inherited from the user-wallet guideline.
7. Integrator support channel (§5.4).
