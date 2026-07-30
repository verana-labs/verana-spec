# The Vesta Use Case — Playground Specification

**Status:** DRAFT 0.6 · 2026-07-30 — reorganized to match the implementation: four chapter routes with a persistent stepper, the five-need journey, interactive diagrams with TrustCards, and the deployment inventory.
**Companions:** [playground spec](../spec.md) · [integration guidelines](../guidelines/) · [Verifiable Trust spec (v3)](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) · [VPR spec (v3)](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html) · demo scripts draft: [`examples.md`](./examples.md)

---

## 1. Purpose

The playground's flagship use case: **learn with Vesta how to make an organization verifiable and trusted**. A fictional company with a problem everyone recognizes — impostors trading on its name — proves its identity, makes its services verifiable, turns its certification into proof, and ends up governing trust for its own partner network. Business-first: chapter 1 contains no protocol vocabulary; mechanics live in collapsible layers.

**Audience:** normal people first; technical readers get their depth in "Reproduce it" and "Under the hood".

## 2. The cast

| Name | Role |
|---|---|
| **Vesta Appliances** | Protagonist: household-appliance maker, Geneva, ~200 employees, 120 independent repair partners. Brand kit: logo, tagline, product/factory/CEO imagery (generated, in-repo). |
| **Elena Vasquez** (CEO) · **Marc Keller** (CTO) | The voices: Elena states the problem (end of ch.1); Marc states the solution and drives the journey. |
| **Helvetia Trust Services (demo)** | Accredited ECS-Organization issuer: runs the KYB and issues Vesta's (and every demo org's) Organization credential. |
| **Verana ECS Ecosystem** | The identity-card trust registry: ECS-Organization, ECS-Service, ECS-Badge (exists on testnet). |
| **ISO Certification Ecosystem (demo)** · **NormaCert (demo)** | Demo certification registry and its accredited issuer; NormaCert certified Vesta since 2003 and issues the ISO 9001 (demo) credential with no re-identification. |
| **Vesta Repair Network** · **Vesta Iberia / Vesta Nordics (demo)** | Vesta's own ecosystem (issuance governed, verification open) and its two subsidiary issuers of the **Authorized Repairer** credential. |
| **Zenith Repairs (demo)** | Genuine partner: verifiable org, holds Authorized Repairer (issued by Vesta Iberia), issues ECS-Badges to its technicians. |
| **Umbra Repairs (demo)** | The impostor: a DID with no credentials; every check ends red. |

## 3. Information architecture (as implemented)

- **Four chapter routes** with a **persistent stepper** (sticky under the site nav, all widths; done = check, current = gradient, upcoming = outline) and a prev/**Continue** footer per chapter:
  1. `/usecases/vesta` — **Meet Vesta Appliances**
  2. `/usecases/vesta/solution` — **The solution: become verifiable**
  3. `/usecases/vesta/journey` — **Marc's journey**
  4. `/usecases/vesta/demos` — **Run the demos**
- Legacy single-page anchors (`#section-N`, `#need-N`) are forwarded to the chapter routes client-side.
- **Design system ("The Mix")**: light `#fcfcff` surface, glass panels for diagrams, gradient CTAs/circles, photo frames, status LED in the network chip; chapter heroes use the playground gradient. Copy rules: no em-dashes, no glyph symbols (icon components only).

### Chapter 1 — Meet Vesta Appliances *(marketing article; no DIDs, no protocol)*

Brand header (logo, tagline, meta chips, ISO 9001 seal since 2003) · numbered "1 · The Company" heading, then subsections: **The product line** (unbranded lineup photo) · **The factory** · **The certified repair network** (hub-and-spoke diagram, green "Vesta Certified Repair Company" paper badges, closing line: online, anyone can print one) · **Online services** (ownership diagram: Agentic Support, Employee badges, Staff & partner portal) · **The problems, and what they cost the brand** (Online: fake support, password pain incl. partner account churn/shared logins, paperwork · On-site: the impostor-van photo) with the root-cause banner · **The word of the CEO** (portrait; ends "That has to change.").

### Chapter 2 — The solution: become verifiable

CTO quote card (Marc Keller, portrait): *"Today, verifiable credential open source software exists for user and cloud wallets, and there is Verana, a public trust infrastructure. We have everything we need to make Vesta and its partner network a network of verifiable organizations, providing verifiable services."* Then:
- **What Marc needs** — five-checkpoint checklist; each chip deep-links to the matching journey subsection.
- **Let's build on Verana** — the three verana.io pillars + facts strip (public, decentralized; any ecosystem self-creates; any organization joins or creates its own).
- **The ecosystems Vesta wants to join** — Verana ECS Ecosystem (recognized KYB, certified Organization credential) and ISO Certification (demo); each card: HOLDER role badge, did:webvh (placeholder), "Open in Verana" link.
- **The ecosystems Vesta wants to build** — Vesta Repair Network card (ECOSYSTEM role badge; issuance governed: Vesta and its subsidiaries; verification open).

### Chapter 3 — Marc's journey *(five subsections = the checklist, numbered 3.1–3.5)*

Checkpoint strip on top (five stations). Sub-steps are unnumbered blocks (story · optional points/DID display · diagram · Reproduce it · Under the hood). Scene stages `3.0` (baseline world) to `3.8`:

- **3.1 Vesta Organization identity** — Marc deploys the **Business Wallet** (vs-agent; generated DID shown, link to vs-agent home; solo "Unverifiable Organization" diagram) · **KYB with an accredited issuer**: Helvetia chosen, KYB over DIDComm, credential received (trio diagram: Vesta / ECS / Helvetia).
- **3.2 Service identity** — any service needs a controller organization and an ECS-Service credential; Vesta **self-accredits as ECS-Service issuer** and self-issues (trio diagram + ECS-Service pill + TRUSTED; Vesta earns its green check).
- **3.3 Vesta employee badges** — Vesta self-accredits as **ECS-Badge issuer** (issuer accreditation only) and issues badges for digital *and* physical access · a **dedicated verifiable login service** (own Business Wallet; ECS-Service issued by the anchor — inheriting ECS-Org from the parent per the Verifiable Trust spec; **VERIFIER ECS-Badge** accreditation, accepted issuer pinned to the anchor DID; Bluetooth/NFC/QR at the door, wallet permitting). Diagram: trio + the login service turning verifiable.
- **3.4 ISO 9001 credential** — NormaCert, recently accredited in the ISO Certification Ecosystem (demo), instantly issues ISO 9001 to Vesta's Organization DID (identified by its Organization credential; no paperwork). Diagram: + ISO ecosystem + NormaCert.
- **3.5 Vesta's own rules for its network** — the **Vesta Repair Network**: registry + Authorized Repairer schema; subsidiaries **Vesta Iberia** and **Vesta Nordics** accredited as issuers; Iberia onboards Zenith by its ECS-Org (diagram: 3.4 cast + network + subsidiaries + Zenith) · **Authorized Repairer login and at the front door**: Zenith issues ECS-Badges to technicians; the Vesta portal grants access to badges whose issuer presents Authorized Repairer; at the door the customer scans the badge and sees the Vesta seal (focused badge-flow diagram + technician photo).

### Chapter 4 — Run the demos *(placeholders until the cast ships; source: examples.md)*

Amber standing rule (always verify the certified Organization in the Proof-of-Trust first) · **Obtain an ECS-Badge** (from Vesta / from Zenith / from a non-authorized org → red) · **Log in with the badge** (Vesta-issued → employee; issuer presents Authorized Repairer → partner employee; else denied) · **Search the directory of Authorized Repairers** (all holders · AND ISO 9001). Closing teaser: **Being found** (Trust Graph, pending) + spec link.

## 4. The diagram system (as implemented)

One master scene graph, fixed positions; elements declare `appears`/`until`/tone- and label-by-stage; per-stage **focused views** (`only` + cropped viewBox) for intimate moments; changed stages pulse with "New in this step" captions. **Verifiable participants show a green check before their name** (measured text width, consistent gap). **Clicking any participant opens the TrustCard** (chain design): DID row → Service check → Operated-by check (with *inherited from parent* chip for delegated services) → Verana-branded TRUSTED verdict (only when both verify; UNVERIFIABLE otherwise) → collapsed "Also presents" (inherited ISO 9001 on delegated services) and "Accreditations" (ISSUER/VERIFIER role chips). Impostors show the red "nothing can be proven" card.

## 5. Deployment inventory — what must exist, per organization

Everything below is a **separate vs-agent (Business Wallet) instance per participant** (decided 2026-07-28; not a reuse of the verana-demos ACME cast). Status: ✔ exists · ◐ partial · ☐ to build.

### Platform (Verana testnet)

| Item | Status | Notes |
|---|---|---|
| Verana testnet (chain, app, resolver, faucet, indexer) | ✔ | app/resolver/idx/rpc/api/faucet-vs.testnet.verana.network |
| Verana ECS Ecosystem trust registry | ✔ | on testnet; card DID still a placeholder in the UI — wire the real did:webvh |
| ECS schemas: Organization, Service, Persona, UserAgent | ✔ | v3 |
| **ECS-Badge** schema | ✔ | created 2026-07 (AnonCreds/DIDComm first; Hologram first) |
| verana-demos ACME cast | ✔ | currently stands in for live TrustCards; retire from this use case once the Vesta cast ships |
| Trust Graph / directory query (chapter 4, demo 3) | ☐ | needs indexer query or interim registry query |

### Helvetia Trust Services (demo) — accredited ECS-Org issuer

| Item | Status | Notes |
|---|---|---|
| Business Wallet (vs-agent) + did:webvh | ☐ | `helvetia-trust.demos.testnet.verana.network` (placeholder in UI) |
| ECS-Organization (own) + self-issued ECS-Service | ☐ | org credential from a bootstrap/peer issuer |
| ISSUER accreditation on ECS-Organization (ECS tree) | ☐ | via join or bootstrap grant |
| KYB issuance flow (DIDComm) | ☐ | issues ECS-Org to Vesta, subsidiaries, Zenith |

### ISO Certification Ecosystem (demo) + NormaCert (demo)

| Item | Status | Notes |
|---|---|---|
| ISO trust registry + EGF + **ISO 9001 (demo)** schema | ☐ | "ISO 9001-style (demo)" wording rule applies |
| Registry operator service (vs-agent, ECS-Org + ECS-Service) | ☐ | ecosystems are verifiable services too |
| NormaCert vs-agent + ECS-Org + ECS-Service | ☐ | `normacert.demos…` |
| NormaCert ISSUER accreditation on ISO 9001 | ☐ | under the ISO registry |
| Instant issuance flow to Vesta's org DID | ☐ | identification by ECS-Org presentation |

### Vesta Appliances — anchor + login service + Repair Network

| Item | Status | Notes |
|---|---|---|
| Anchor Business Wallet + did:webvh | ☐ | `vesta-anchor.demos…`; replaces UI placeholders (hero card, 3.1 DID display) |
| ECS-Organization (Helvetia) · self-accredited ISSUER + self-issued ECS-Service | ☐ | 3.1 / 3.2 |
| ISSUER accreditation ECS-Badge + employee badge issuance (demo offer) | ☐ | 3.3 / demo 1 |
| **Login service** vs-agent (2nd instance) | ☐ | delegated ECS-Service issued by the anchor; VERIFIER ECS-Badge; policy: issuer = anchor DID **or** issuer presents Authorized Repairer; login demo endpoint (demo 2) |
| **Vesta Repair Network** trust registry + EGF + **Authorized Repairer** schema + root permission | ☐ | issuance governed (Vesta + subsidiaries), verification OPEN |
| Registry service presents Vesta's ECS-Org + ECS-Service | ☐ | `repair-network.vesta.example` placeholder |

### Subsidiaries, partner, impostor, people

| Item | Status | Notes |
|---|---|---|
| Vesta Iberia + Vesta Nordics: vs-agents, ECS-Org (Helvetia), ECS-Service, ISSUER Authorized Repairer | ☐ | Iberia issues to Zenith |
| Zenith Repairs: vs-agent anchor, ECS-Org, ECS-Service, HOLDER Authorized Repairer, ISSUER ECS-Badge + technician badges | ☐ | badge offer for demo 1; scanned badge for the door demo |
| Umbra Repairs: vs-agent with DID and **no credentials** + unauthorized badge offer | ☐ | the refusal paths (demo 1 red case) |
| Personal wallets: Hologram (badge + login demos) | ✔ | more integrated wallets as their badge loops land |

## 6. Open items

1. ~~Location / format / cast~~ — resolved through 0.5; **0.6: four chapter routes** with stepper (this document).
2. Deploy the inventory above (§5) and replace every `QmPLACEHOLDER` DID and "Open in Verana" TODO link with real values; then retire the verana-demos stand-in note on live cards.
3. Chapter 4 demos: wire QR/deep links to the real offers/login/search once the cast is live.
4. Vesta brand kit refresh from generated assets if a designed kit arrives (open since 0.5).
5. "Being found" chapter (Trust Graph) once discovery is queryable.
