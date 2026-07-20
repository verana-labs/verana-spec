# Publication & Award Submission Kit

**Status:** DRAFT 0.1 · 2026-07-16
**Owners:** Verana (org on FIDES) — primary; 2060 (org on FIDES) — supporting lane.
**Targets:** FIDES Ecosystem Explorer + **Global Digital Trust Awards — Collaboration Award 2026** (winners announced Sept 3, GDC26 Geneva); FIDES Community Awards (Sept 15, Utrecht); EUDIW Unfold Playground.

## 1. Hard dates

| Date | Event | Our action |
| --- | --- | --- |
| ~Aug 10 | — | Use cases + all catalog entries published; playground MVP live; campaign wave 1 (likes) |
| Aug 20 | FIDES Community Awards eligibility cutoff | Everything published, incl. 2060 business-wallet entry |
| Aug 21 | FIDES CA finalists | Wave 2 comms |
| Aug 24 | **GDTA finalists (10/category)** | Voting opens — wave 3 comms |
| Sept 2 | GDTA community voting closes | Final push ends |
| Sept 1–3 | **GDC26 Geneva** (winners Sept 3) | On-site presence, live playground demo |
| Sept 15 | FIDES Community Event, Utrecht | Winners; business-wallets demo |

Likes (submission period) select finalists; votes (Aug 24 → Sept 2, one per signed-in user per category) + expert jury (50/50) pick winners. **All engagement must be real people** — employees, partners, and the communities of every listed wallet vendor; no multi-accounting (detectable, disqualifying, reputationally fatal with FIDES).

## 2. Verana use case (primary — Collaboration Award)

**Working title:** *One trust layer, many wallets — the Verana Playground*
**Submitted by:** Verana org · **URL evidence:** `https://playground.testnet.verana.network` + demo video + the "same PoT, N wallets" strip (spec §5.3).

**Narrative (draft, ~150 words for the form):**

> Independent wallet stacks — DIDComm-native (Hologram), OID4VC/DIIP (Paradym, Talao, …), MOSIP Inji, and open-source cloud wallets — issue, hold, and verify credentials against one open, neutral trust registry: the Verana testnet. A fictional ISO Certification Ecosystem accredits certification bodies that issue an ISO 9001-style credential (demo) to the organization operating an AI agent. When a person connects with **any** integrated wallet, the wallet trust-resolves the agent **before** the first message and renders the same Proof-of-Trust: the organization (ECS-Org), the service (ECS-Service), and its certification — verified recursively to the ecosystem root. Unauthorized issuers and verifiers are refused, with proof. Every integration follows one published open guideline, so any wallet can join the same way. Live on a public playground; every claim reproducible.

**Criteria mapping (Collaboration Award):**

| Criterion | Evidence |
| --- | --- |
| Multi-stakeholder collaboration | N independent orgs' products integrated (roster §4); named collaborators with consent |
| Cross-border / cross-ecosystem interoperability | DIDComm + OID4VC/DIIP + MOSIP stacks on one trust layer; UNFOLD marketplace listing; TRQP interface |
| Ecosystem growth & participation | Wallet showcase open by PR; FIDES catalog entries for every artifact; sandbox ecosystems anyone can create |
| Open standards & reusability | W3C VC/DID, DIDComm, OpenID4VC, SD-JWT VC, TRQP; guidelines published CC BY-SA; schema templates cloneable |
| Knowledge sharing & community engagement | The playground itself (journeys), integrator hub, FIDES track participation (Agentic eCommerce), plugfests |
| Contribution to broader ecosystem | The trust-registry answer to DIIP's open trust-establishment question; open-source everything |

**Form checklist:** title · summary · full description · images (PoT strip, journey screenshots) · video (≤3 min, the ISO Certification loop uncut) · links (playground, guidelines, specs, repos) · linked Explorer entries (§4) · standards used · organizations involved.

## 3. 2060 use case (supporting lane)

**Working title:** *Hologram Agentic AI — verifiable agents, chatbots and a DIDComm browser* · **Submitted by:** 2060 org · **Targets:** Innovation Award (FIDES CA); feeds the Agentic eCommerce track.
Outline: Hologram AI Agent + VUA + Messaging; agents authenticate humans and other agents via credentials over DIDComm; every agent is a Verifiable Service on Verana (the trust layer the primary use case demonstrates). Cross-links the Verana use case; deliberately does not compete in Collaboration.
**Plus catalog assets:** Hologram Messaging → *Personal Wallets*; **vs-agent / Hologram cloud → *Business Wallets* by Aug 20** (Best Business Wallet 2026 eligibility).

## 4. Catalog entries checklist

| Explorer catalog | Entry | Org | Status |
| --- | --- | --- | --- |
| Organizations | Verana (Foundation, in formation) | Verana | ☐ |
| Organizations | 2060 | 2060 | ✅ created |
| Use cases | One trust layer, many wallets | Verana | ☐ |
| Use cases | Hologram Agentic AI | 2060 | ☐ |
| Personal wallets | Hologram Messaging | 2060 | ☐ |
| Business wallets | vs-agent (Hologram cloud wallet) | 2060 | ☐ |
| Credential types | ECS-Service · ECS-Organization · ECS-Persona (+ ISO 9001 (demo)) | Verana | ☐ |
| Issuers | CertBody demo issuers · ECS onboarding issuer | Verana | ☐ |
| Relying parties | Acme demo agent (verifier) · Inji Verify | Verana | ☐ |
| *(per integrated wallet)* | vendor's own wallet entry — ask each vendor to create/claim theirs | vendor | ☐ |

## 5. Collaborator roster & consent

Rule: **every organization with ≥1 open-source product integrated is named** — after a heads-up message and a yes. Each named org receives a kit: its playground tile URL, the "Runs on the Verana open trust layer" badge, two ready-to-post texts (submission day, voting day), and the like/vote links.

Candidates (verify license + integration status at submission time): Animo (Paradym, credo-ts) · Talao · MOSIP (Inji) · 2060 (Hologram) · OWF (Bifold, ACA-Py, credo-ts) · walt.id · Sphereon · Impierce (UniMe) · DIF (Veramo) · LF Decentralized Trust (Identus) · Findy Agency · [extend as integrations land]. Constraint reminder: cloud stacks must support `did:web`/`did:webvh` for hosted issuers/verifiers ([CW-ID-1]).

## 6. Campaign calendar (real-people engagement)

| Wave | When | Action |
| --- | --- | --- |
| 0 | now | Harmen call (track + award logistics); UNFOLD form; vendor heads-up messages begin |
| 1 | submission day (~Aug 10) | Blogs (verana.io + foundation), LinkedIn/X posts, vendor kits go out, Discord/communities ask for **likes** |
| 2 | Aug 21 / Aug 24 | Finalist announcements relayed; switch CTA from likes to **votes**; vendor second post |
| 3 | Aug 25 → Sept 2 | Weekly reminders; GDC26 demo prep; partner reshares |
| 4 | Sept 3 / Sept 15 | Outcome comms either way — the playground and integrations are the durable asset |

## 7. UNFOLD (parallel, not award-gated)

Submit France Identité participation form (link in `integration-sandbox/unfold/README.md`) → list the playground's OID4VC demo issuer + verifier in the Unfold marketplace → attend the next interop event. Purpose: the cross-border proof point cited in §2, and the EUDI-side relationship.
