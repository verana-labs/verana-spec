# The Verandia Use Case — Playground Specification

**Status:** DRAFT 0.1 · 2026-08-11 — initial story, cast, schemas, demos, and deployment inventory.
**Companions:** [playground spec](../spec.md) · [Vesta use case](../verana-explained/spec.md) · [integration guidelines](../guidelines/) · [Verifiable Trust spec (v3)](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) · [VPR spec (v3)](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html)

---

## 1. Purpose

The playground's second use case: **learn with the Republic of Verandia how a democracy deploys verifiable identity for citizens and businesses**. Where Vesta is a company producing trust for its brand and partner network, Verandia is the public-sector mirror: a state that issues a **Digital Verifiable Identity Card** to its citizens (eIDAS 2 compatible), a **Digital Verifiable Business ID** to its companies, and a **Proof of Legal Representation** binding people to the companies they act for — and then lets both public entities and private companies authenticate anyone, passwordless and fail-closed.

Two lessons Verandia adds over Vesta:

1. **Personal identity credentials at national scale** — the credential in the wallet IS the ID card, on the eIDAS-2-compatible rail (OpenID4VC SD-JWT) as well as AnonCreds/DIDComm.
2. **Governed verification** — the eIDAS 2 relying-party-registration story made concrete: a service must hold a VERIFIER permission before any wallet will share a Citizen ID with it. Q3, fail-closed, is the star of this story.

**Audience:** normal people first; technical readers get their depth in "Reproduce it" and "Under the hood" — same layering as Vesta.

## 2. The cast

| Name | Role |
|---|---|
| **Republic of Verandia** | Protagonist: a small democracy going digital. Brand kit: flag, coat of arms, institution imagery (generated, in-repo). |
| **Ines Duarte** (Prime Minister) · **Milo Kovar** (Digital Minister) | The voices: the PM states the problem (end of ch.1); the Digital Minister states the solution and drives the journey (the Marc role). |
| **National Business Registry (demo)** | The company register, and the keystone of the build: becomes an **accredited ECS-Organization issuer** under the Verana ECS Ecosystem (the Helvetia role, but a government registry — KYB is a lookup, because the issuer IS the source of truth), and operates its own **Legal Representation** trust registry. |
| **National Civil Registry (demo)** | Operates the **Verandia Citizen ID** trust registry and issues the Citizen ID (issuance governed, verification governed). |
| **Tax Buro (demo)** | Public entity relying party: authorized VERIFIER of the Citizen ID; accepts Legal Representation for company tax spaces. Hosts the login demo. |
| **Meridian Bank (demo)** | Private-sector relying party: obtains its ECS-Organization from the Business Registry, publishes verifiable services (online banking), and **registers as relying party** (VERIFIER on Citizen ID) — KYC in one scan; corporate account access via Legal Representation. |
| **QuickCash Loans (demo)** | The counter-example: a perfectly **verifiable** organization (ECS-Org, ECS-Service) that holds **no VERIFIER permission** on the Citizen ID — wallets refuse to share (Q3). Trust is not authorization. |
| **Aria Solano (demo)** | A citizen: receives her Citizen ID, files her taxes, opens a bank account — no passwords, no paperwork. |
| **Tomás Ferreira (demo)** | Managing director of **Solaris Bakery (demo)**: identifies with his Citizen ID and receives a **Legal Representative** credential; accesses the bakery's tax space and bank account. Solaris Bakery itself is a claims-only entity (no agent) in 0.1. |
| **Helvetia Trust Services (demo)** | Reused from the Vesta cast: bootstraps the Business Registry's own ECS-Organization. Cross-story continuity. |
| **Verana ECS Ecosystem** | The shared identity-card trust registry (exists on testnet). Verandia **joins** it for Business IDs — with the explicit design note that it could have built a custom ecosystem instead, but interop wins: Verandian companies are trusted everywhere, not just in Verandia. |

## 3. Information architecture

Mirrors Vesta: **four chapter routes** with the persistent stepper and prev/Continue footers, same design system, same copy rules (no em-dashes, no glyph symbols in rendered site copy):

1. `/usecases/verandia` — **Meet the Republic of Verandia**
2. `/usecases/verandia/solution` — **The solution: a verifiable Republic**
3. `/usecases/verandia/journey` — **The Minister's journey**
4. `/usecases/verandia/demos` — **Run the demos**

### Chapter 1 — Meet the Republic of Verandia *(civic article; no DIDs, no protocol)*

State header (coat of arms, motto, meta chips: population, institutions, "e-government since 2009") · **The Republic** (flag/landscape imagery) · **The institutions** (ownership diagram: Civil Registry, Business Registry, Tax Buro — the state owns and operates all three) · **Digital services today** (tax portal with passwords, citizen portal, company register selling PDF extracts) · **The problems, and what they cost the Republic**:

- **Online:** fake "tax refund" portals phishing citizens in the Republic's name · password pain across every government portal (resets, shared credentials, help-desk load) · identity theft: anyone can claim to be anyone · companies prove their existence with **PDF extracts anyone can edit**.
- **At the counter and at the bank:** every bank and notary re-runs the same KYC on the same companies, over and over · "who may sign for this company?" is answered with notarized paper and faxes · citizens queue at offices to prove facts the state already knows.

Root-cause banner: *online, the Republic's word looks exactly like the scammers' word — nothing can be proven.* · **The word of the Prime Minister** (portrait; Ines Duarte, ends "That has to change.").

### Chapter 2 — The solution: a verifiable Republic

Digital Minister quote card (Milo Kovar, portrait): *"Open source wallets exist — for citizens and for organizations. Verana is public trust infrastructure. We have everything we need to give every citizen a verifiable ID card, every company a verifiable Business ID, and every service a way to check both — without building a single silo."* Then:

- **What the Minister needs** — five-checkpoint checklist; each chip deep-links to the matching journey subsection:
  1. **Verifiable institutions** — the Republic itself must be provable before it can vouch for anyone.
  2. **A Citizen ID citizens actually hold** — the national ID card as a verifiable credential in any compatible wallet, eIDAS 2 compatible.
  3. **Verifiable Business IDs** — companies prove who they are with a credential, not a PDF.
  4. **Proof of legal representation** — a personal credential binding a person to the company they may act for, revocable the day it ends.
  5. **Passwordless, fail-closed authentication** — public entities and companies verify citizens, and only **authorized** verifiers ever see the data.
- **Let's build on Verana** — the three pillars + facts strip (public, decentralized; any ecosystem self-creates; no gatekeeper — a state uses the same open infrastructure as everyone else).
- **The ecosystems Verandia wants to join** — the **Verana ECS Ecosystem** (HOLDER + ISSUER roles): Business IDs are plain **ECS-Organization** credentials, issued by the National Business Registry once accredited. Design note, stated in the story: *Verandia could run Business IDs in a custom ecosystem, but joining the shared ECS ecosystem means a Verandian company's credential is recognized by every Verana-aware wallet and service worldwide — interop wins.*
- **The ecosystems Verandia wants to build** — two cards (ECOSYSTEM role badges):
  - **Verandia Citizen ID** (National Civil Registry) — issuance governed (only the Civil Registry issues), **verification governed** (relying parties must register — the eIDAS 2 relying-party analog).
  - **Verandia Legal Representation** (National Business Registry) — issuance governed (only the Business Registry issues), verification OPEN (anyone may check who represents a company — that is the register's public function).

### Chapter 3 — The Minister's journey *(five subsections = the checklist, numbered 3.1–3.5)*

Checkpoint strip on top. Sub-steps follow the Vesta block pattern (story · optional points/DID display · diagram · Reproduce it · Under the hood). Scene stages `3.0` (baseline world: gray institutions, citizens with the "?", red fake tax-refund portal) to `3.8`:

- **3.1 Verifiable institutions** — the Business Registry deploys its **Business Wallet** (vs-agent; generated DID shown; solo diagram) · gets its own **ECS-Organization** from Helvetia Trust Services (demo) + self-issued ECS-Service → the first green check of the Republic · then is **accredited as ECS-Organization ISSUER** in the Verana ECS Ecosystem (the join-vs-build note lives here). From now on, the state's own register issues Business IDs.
- **3.2 The Citizen ID** — the Civil Registry becomes verifiable (**ECS-Org issued by the Business Registry — the Republic dogfoods its own register**) and creates the **Verandia Citizen ID** trust registry + schema (issuance ECOSYSTEM, verification ECOSYSTEM) · **citizens receive their Citizen IDs**: Aria walks into a registry office (or uses her existing eID) and the credential lands in the wallet of her choice — story states explicitly that **any of the integrated personal wallets can be customized for Verandia** (the EUDI-reference fork and Authbound are the precedent; the SD-JWT rail is the eIDAS-2-compatible one). Diagram: registries + citizen wallet nodes (the Vesta-3.4 employees pattern).
- **3.3 Verifiable Business IDs** — **Meridian Bank** applies; the Business Registry looks itself up (KYB = a lookup) and issues the bank its ECS-Organization; the bank self-issues ECS-Service and **publishes its online-banking service** under its DID → TRUSTED. The anti-phishing payoff: your bank can finally prove it is your bank, before you type a password. Solaris Bakery and every other Verandian company follow the same path.
- **3.4 Proof of legal representation** — the Business Registry creates the **Legal Representation** trust registry + schema · **Tomás identifies with his Citizen ID** over the session (reusable identity — the NormaCert moment of this story) and receives his **Legal Representative** credential: company name, registry id, his role, validity. Revocable the day he leaves the bakery.
- **3.5 Passwordless, fail-closed authentication** — the **Tax Buro** becomes verifiable (ECS-Org from the Business Registry) and registers as **VERIFIER on the Citizen ID**; its portal grants a personal tax space on a Citizen ID presentation, and a **company tax space** when a Legal Representative credential is presented alongside · **Meridian Bank registers as relying party** (VERIFIER on Citizen ID): account opening becomes **KYC in one scan**, and corporate account access rides the same Legal Representative credential — the same two credentials working at a public entity and a private company · **the counter-example:** QuickCash Loans, a verifiable organization with no VERIFIER permission, requests a Citizen ID presentation — every compliant wallet shows "trusted, but not authorized to request this credential" and refuses to share (Q3); the fake tax-refund portal fails Q1 outright. Diagram: full cast with green checks, QuickCash red-crossed on the verification edge.

### Chapter 4 — Run the demos *(placeholders until the cast ships)*

Amber standing rule (always verify the certified Organization in the Proof-of-Trust first) · wallet chooser (reused component; carries the "any integrated wallet can be customized for Verandia" message) · then:

1. **Get your Verandia Citizen ID** — live offer minted by the Civil Registry agent; green Proof-of-Trust (certified institution, authorized issuer). SD-JWT for OID4VC wallets (the eIDAS-compatible rail), AnonCreds for Hologram. Demo claims: a generated citizen identity (per-scan identifier, e.g. `VD-XXXXXXXX`). Red issuance paths are the six-scenario page's job and are not duplicated here.
2. **Get a Proof of Legal Representation** — live offer minted by the Business Registry agent with the Tomás Ferreira / Solaris Bakery demo claims. Note in copy: in the real flow the applicant first identifies with their Citizen ID; the demo mints directly.
3. **Log in to the Tax Buro** — portal-window demo (PortalLoginDemo pattern). Outcomes: Citizen ID issued by the Civil Registry → *personal tax space, welcome citizen* · Legal Representative credential issued by the Business Registry → *company tax space, welcome + company name* · anything else → *access denied*.
4. **Open an account at Meridian Bank** — the KYC-in-one-scan demo: present your Citizen ID → account opened, claims shown; present your Legal Representative credential → corporate account access with the company name.
5. **The over-asking verifier** — QuickCash Loans mints a real Citizen ID presentation request; your wallet trust-resolves it, finds no VERIFIER authorization, and blocks the share. Your data never leaves.
6. **Search the Directory of Verandia** — Trust Graph teaser (demo-coming chips): *all verified Verandian businesses* (ECS-Org issued by the National Business Registry) · *all services accepting the Verandia Citizen ID* (authorized verifiers) · *who legally represents company X*.

Closing teaser: **Being found in Verandia** — everything the Republic and its companies published is public, resolvable, and indexable; the Trust Graph turns it into a national service directory nobody has to maintain by hand. Ships when discovery is queryable.

## 4. Schemas

Both are **personal credentials** (the ECS-Badge pattern: AnonCreds/DIDComm first, OID4VC SD-JWT alongside; never published as Linked VPs).

### Verandia Citizen ID *(Civil Registry ecosystem)*

eIDAS-2-PID-inspired claim set (kept modest for the demo):

| Claim | Type | Notes |
|---|---|---|
| `familyName` · `givenName` | string | mandatory |
| `birthDate` | dateint (`YYYYMMDD`) | enables age predicates over AnonCreds |
| `personalIdentifier` | string | `VD-` prefixed, unique per citizen (random per scan in the demo) |
| `nationality` | string | `VD` |
| `portrait` | data URI | the ID photo (generated avatar in the demo) |
| `issuingAuthority` | string | "National Civil Registry (demo)" |

Modes: issuance **ECOSYSTEM** (only the Civil Registry) · verification **ECOSYSTEM** (relying parties register — Tax Buro, Meridian Bank hold VERIFIER permissions; QuickCash does not).

### Legal Representative *(Business Registry ecosystem)*

| Claim | Type | Notes |
|---|---|---|
| `companyName` | string | "Solaris Bakery (demo)" |
| `companyRegistryId` | string | Verandia register number |
| `representativeName` | string | must match the Citizen ID presented at issuance |
| `role` | string | e.g. `managing-director` |
| `powers` | string | e.g. `full` / `banking` / `tax` |
| `validUntil` | dateint | optional |

Modes: issuance **ECOSYSTEM** (only the Business Registry) · verification **OPEN** (the register's public function).

## 5. Deployment inventory — what must exist, per organization

Same rules as the Vesta cast: **one vs-agent (Business Wallet) per participant**, hosts on `*.verandia.playground.testnet.verana.network`, provisioned by `verandia-*` CI/CD workflows cloned from the `vesta-*` pattern (shared `common.sh`, per-org `config.env`, schema JSONs, Admin-API scripts). Status: ✔ exists · ◐ partial · ☐ to build.

> **v3 constraint — no DIDComm between verifiable services.** Every org-to-org exchange (Helvetia → Business Registry, Business Registry → Civil Registry / Tax Buro / Meridian Bank / QuickCash) is provisioned by CI/CD driving the agents' Admin APIs. DIDComm and OID4VC are used only between **Personal Wallets and services** (Citizen ID and Legal Representative issuance, login presentations) at runtime.

### Platform (Verana testnet)

| Item | Status | Notes |
|---|---|---|
| Verana testnet (chain, app, resolver, faucet, indexer) | ✔ | shared with the Vesta cast |
| Verana ECS Ecosystem trust registry + ECS-Organization schema | ✔ | on testnet |
| Helvetia Trust Services (demo) — bootstrap ECS-Org issuer | ◐ | from the Vesta cast; reused for the Business Registry's own ECS-Org |
| Trust Graph / directory query (chapter 4, demo 6) | ☐ | teaser until discovery is queryable |

### National Business Registry (demo) — the keystone

| Item | Status | Notes |
|---|---|---|
| vs-agent + did:webvh | ☐ | `business-registry.verandia.playground.testnet.verana.network` |
| ECS-Organization (Helvetia) + self-issued ECS-Service | ☐ | 3.1 |
| **ISSUER accreditation on ECS-Organization** (ECS tree) | ☐ | requires the ECS-ecosystem accreditation step (`ECS_ECOSYSTEM_MNEMONIC`, the `vesta-02` pattern) |
| Issues ECS-Org to: Civil Registry, Tax Buro, Meridian Bank, QuickCash | ☐ | CI/CD, Admin APIs |
| **Legal Representation** trust registry + EGF + schema + root permission | ☐ | issuance ECOSYSTEM, verification OPEN |
| Legal Representative issuance (demo offer, both rails) | ☐ | demo 2 |

### National Civil Registry (demo)

| Item | Status | Notes |
|---|---|---|
| vs-agent + did:webvh | ☐ | `civil-registry.verandia.playground.testnet.verana.network` |
| ECS-Organization (Business Registry) + self-issued ECS-Service | ☐ | the dogfooding step, 3.2 |
| **Verandia Citizen ID** trust registry + EGF + schema + root permission | ☐ | issuance ECOSYSTEM, verification ECOSYSTEM |
| ISSUER on Citizen ID + issuance flow (demo offer, both rails) | ☐ | demo 1; AnonCreds cred-def + OID4VC SD-JWT config (the ECS-Badge dual-rail precedent) |
| VERIFIER permissions granted to: Tax Buro, Meridian Bank | ☐ | the relying-party registrations; deliberately **not** QuickCash |

### Tax Buro (demo)

| Item | Status | Notes |
|---|---|---|
| vs-agent + did:webvh + ECS creds (ECS-Org from the Business Registry) | ☐ | `tax-buro.verandia.playground.testnet.verana.network` |
| VERIFIER on Citizen ID (granted by the Civil Registry) | ☐ | 3.5 |
| Login-demo endpoints (both rails): Citizen ID request + Legal Representative request | ☐ | demo 3; decision policy: issuer = Civil Registry DID → citizen · Legal Rep issuer = Business Registry DID → company space + company name · else denied |

### Meridian Bank (demo)

| Item | Status | Notes |
|---|---|---|
| vs-agent + did:webvh + ECS creds (ECS-Org from the Business Registry) | ☐ | `meridian-bank.verandia.playground.testnet.verana.network` |
| Published online-banking service under its DID (live Proof-of-Trust on the page) | ☐ | 3.3 |
| VERIFIER on Citizen ID (relying-party registration) | ☐ | 3.5 / demo 4 (KYC in one scan) |
| Corporate-access flow on Legal Representative presentations | ☐ | demo 4 |

### QuickCash Loans (demo) — the counter-example

| Item | Status | Notes |
|---|---|---|
| vs-agent + did:webvh + ECS creds (ECS-Org from the Business Registry) | ☐ | `quickcash.verandia.playground.testnet.verana.network` — genuinely verifiable |
| Citizen ID presentation-request minting, with **no VERIFIER permission** | ☐ | demo 5: the wallet-side Q3 refusal |

### People (demo claims, no agents)

| Item | Status | Notes |
|---|---|---|
| Aria Solano — citizen demo claims (generated identity + avatar) | ☐ | demo 1 |
| Tomás Ferreira / Solaris Bakery — Legal Representative demo claims | ☐ | demo 2; Solaris Bakery is claims-only in 0.1 (see open item 5) |

## 6. Open items

1. **Deploy the inventory** (§5) and record the real did:webvh values, trust registry ids, and schema ids; wire "Open in Verana" links.
2. **Playground implementation prerequisites** (verana-labs/playground): generalize `StoryDiagram` / `Stepper` / `ChapterFooter` / `LegacyHash` over a scene-graph and chapters parameter (currently Vesta-hardwired); extract the portal-login demo into a configurable component; add `verandia` cast + claims modules + `/api/tax-login`; nav, home card, sitemap, about-page fictional-entities list.
3. **Brand kit**: flag, coat of arms, PM and Minister portraits, institution and bank imagery, citizen avatar (generated, same pipeline as Vesta's).
4. **Citizen identification at issuance**: the story says "registry office or existing eID"; decide whether the demo copy references an eSignet-style bootstrap (the MOSIP-showcase precedent) or stays abstract.
5. **Solaris Bakery**: claims-only in 0.1. Optionally promote it to a sixth agent later (own ECS-Org, own published service) to show a represented company acting online.
6. **Directory of Verandia**: wire live queries when the Trust Graph ships; consider an interim indexer query (participants of the Citizen ID schema tree = the public relying-party register — itself a nice transparency story).
7. **eIDAS 2 mapping sidebar**: consider a collapsible "For eIDAS readers" box mapping Citizen ID ≈ PID, relying-party registration ≈ VERIFIER permissions, Legal Representative ≈ attestation of attributes, wallet plurality ≈ the integrated-wallet chooser.
