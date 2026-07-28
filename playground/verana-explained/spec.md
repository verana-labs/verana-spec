# Verana Explained — Playground Specification

**Status:** DRAFT 0.5 · 2026-07-28 — complete look-and-feel rework: **one single page**, business-first; §1 is a marketing-style company article (no DIDs, no protocol diagram); the technical scene graph only starts at §4.
**Companions:** [playground spec](../spec.md) · [integration guidelines](../guidelines/) · [Verifiable Trust spec (v3)](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) · [VPR spec (v3)](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html)

---

## 1. Purpose

A playground that **explains the basics of Verana** through one continuous story a non-technical reader can follow: a fictional company with a problem everyone recognizes — impostors trading on its name — discovers Verana, joins the ecosystems it needs, makes its services verifiable, and ends up governing trust for its own partner network.

The story **starts from the business, not the technology**: §1 reads like a company page on a marketing website. Protocol mechanics appear progressively and stay in collapsible layers.

**Audience:** normal people first — customers, business owners, evaluators. No prior SSI knowledge assumed. Technical readers get their depth in the "Reproduce it" and "Under the hood" layers.

## 2. The cast

| Name | Role in the story |
|---|---|
| **Vesta Appliances** | The protagonist: a household-appliance manufacturer (washing machines, ovens), ~200 employees, selling worldwide, with a network of independent repair partners. Has a logo, a tagline, a company profile — presented like a real brand. |
| Vesta's online services | Customer **Agentic Support** (AI support chatbot) · **employee badge** service · **staff & partner portal login** — ordinary services in §1, verifiable services by §4. |
| **Zenith Repairs (demo)** | A genuine independent repair company — becomes Vesta's first credentialed **Authorized Repairer**. |
| **Umbra Repairs (demo)** | The villain: a fake "Vesta-authorized" repair outfit scamming customers. Fails verification in §5. |
| **Verana ECS Ecosystem** | The root "identity card" trust ecosystem: recognized KYB services by accredited issuers: ECS-Organization (who you are), ECS-Service (what this service is), ECS-Badge. |
| **ISO Certification Ecosystem (demo)** | Fictional certification ecosystem governing an **ISO 9001** credential, issued by accredited certification bodies. |
| **Vesta Repair Network** | The ecosystem Vesta itself creates in §5, with one credential schema: **Authorized Repairer** (issuance governed, verification open). |

> **Demo cast note:** for this playground we **create separate vs-agent instances for every participant of the story** — the Vesta anchor and its three services, the KYB issuer, the certification body, Zenith Repairs, Umbra Repairs. A dedicated cast, not a reuse of the existing verana-demos (ACME-branded) services; until the Vesta cast is deployed, the verana-demos anchor stands in for live cards. See open items.

## 3. Format & look-and-feel

- **Everything on one single page**: `/usecases/vesta`, five sections with anchors (`#section-1` … `#section-5`), a closing "Being found" teaser, and a sticky/linked table of chapters from the home page cards.
- **The page changes register as it progresses** — that is the design:
  - **§1 is a marketing-style article** — company logo, profile, article prose, a **business services diagram** (the company card above, connectors down to one card per service: ownership at a glance), and an attractive **problems grid**. **No DIDs, no protocol diagram, no Verana vocabulary.** It must feel like a page from Vesta's own website / a business magazine profile.
  - **§2 is Elena's solution: pillar cards + ecosystem choice cards.
  - **§3–§5 are the technical build** — sub-steps with the progressive **scene graph**, which **starts at §3 pre-populated with the business world** (Vesta, its three gray services, the customer with the "?", the red impostors) so the first technical stage transforms a world the reader already knows. DIDs appear only from §3.1.
- Sub-steps (§3–§5 only) carry a chip — **story** / **watch** (Vesta does it; every service shown MUST link the GitHub repository of the software that runs it) / **hands-on** (the visitor does it with their own wallet) — and up to four layers: story · diagram stage · **Reproduce it** (optional numbered recipe; frontend flow: ecosystem → credential schema → Participants → permission tree → Join under the chosen branch) · **Under the hood** (optional collapsible; v3 message names).
- Scene-graph mechanics: one master graph, fixed positions; elements declare the stage at which they **appear, change tone/label, or leave** (gray unprovable services turn verified; the customer's "?" resolves; the fake support line turns ✗ red; full-circle verdicts in §5). New/changed elements pulse, with a "New in x.y" caption.
- Artifacts are **real testnet artifacts** wherever possible; screenshots only where liveness adds nothing.
- Sections end with a state line ("what Vesta now has") where it helps the narrative.

## 4. Section 1 — Meet Vesta Appliances *(marketing article)*

**Look:** company page. Ordered subsections:

1. **Brand header** — logo mark, name, tagline ("Quality home appliances since 1985"), meta chips (HQ, ~200 employees, 40+ countries, 120 repair partners), and the **ISO 9001 certification seal** ("ISO 9001 certified · since 2003").
2. **The product line** — product promise copy ("machines that last — and get repaired, not replaced") + unbranded product lineup image.
3. **The factory** — manufacturing/heritage copy + assembly-line image.
4. **The certified repair network** — hub-and-spoke business diagram: Vesta (logo) at the center ("trains · audits · certifies"), the independent repair companies around it (Zenith Repairs among them), **each carrying the green "Vesta Certified Repair Company" badge** — the real-world paper certification (training, yearly audits, signed contract). Closing line bridges to the problems: the badge lives on van doors and PDF certificates — online, anyone can print one.
5. **Online services** — ownership diagram: the Vesta company card on top, connectors down to three service cards — **Agentic Support** · **Employee badges** · **Staff & partner portal**. The visual states the ownership: *all of this is Vesta's*.
6. **The problems — and what they cost the brand**, in two groups, each with a consequence line:
   - **Online**: fake support lines · password pain · paperwork, again and again. *Consequence: refund scams run in Vesta's name; the brand takes the blame.*
   - **On-site**: fake "authorized" repairers — illustrated by the impostor-van photo (unmarked van with a **printed Vesta panel**). *Consequence: customers scammed at their own front door; honest certified partners lose the work; Vesta blamed either way.*
   - Root-cause banner: **Online or at the front door, Vesta's word looks exactly like the scammers' word. Nothing can be proven.**
7. **The word of the CEO** — closes the section: *"Our machines earn trust in people's homes every day. Yet online, we can't prove a support chat is really ours — and at the front door, we can't prove a technician is really one of our certified partners. **That has to change.**"* (Elena Vasquez, CEO) — the segue into Section 2.

No DIDs, no protocol vocabulary anywhere in Section 1.

## 5. Section 2 — The solution: become verifiable *(CTO quote + pillar cards + choice cards)*

The section opens on a **CTO quote card** (Marc Keller, CTO, Vesta Appliances — portrait slot like the CEO's): *"Today, verifiable credential open source software exists for user and cloud wallets, and there is Verana, a public trust infrastructure. We have everything we need to make Vesta and its partner network a network of verifiable organizations, providing verifiable services."*

Two subsections:

### Subsection 1 — What Marc needs *(mission checklist)*

Intro: *To make every organization and every service verifiable, Marc's list is short:* — five checklist cards (empty checkbox squares, to-do style), each with a clickable chip pointing to the section that fulfills it:

1. **Verifiable identities for organizations** — provable "who we are", checkable by anyone, no paperwork. *(→ Section 3 · ECS-Organization)*
2. **Verifiable identities for services** — every service proves what it is and who operates it. *(→ Section 4 · ECS-Service)*
3. **Credentials people can hold** — badges in a wallet: passwordless login, and proof at the customer's door. *(→ Section 4 · ECS-Badge)*
4. **Certifications as proof, not PDFs** — ISO 9001 travels with Vesta's identity. *(→ Section 3 · ISO 9001)*
5. **Vesta's own rules for its network** — only Vesta says who is an Authorized Repairer, revocable. *(→ Section 5 · Vesta Repair Network)*

Bridge line (violet strip): *All of this needs wallets to hold and check the proofs (they exist, open source, for people and for organizations) and one neutral, public place where every proof anchors. That place is Verana.*

The checklist doubles as a map of Sections 3–5. Optional later extension: re-show it with items ticked at the end of each fulfilling section.

### Subsection 2 — Let's build on Verana

Intro line: *Verana is a public infrastructure that generalizes the use of verifiable credentials, and provides out of the box:* — followed by the three Verana pillars, exactly as on [verana.io](https://verana.io):

- **Trust Ecosystems** — sovereign ecosystems: build ecosystems that issue and verify any credential, with your own schemas, governance framework, participants, and business model, or join an existing one.
- **Verifiable Trust** — verifiable identity: identify any service and the organization or person that controls it, and verify it before you connect. *Verify first. Then connect.*
- **The Trust Graph** — discovery: find services and ecosystems by the credentials they hold, ranked by trust.

Emphasis strip: **Verana is public, decentralized infrastructure. Any ecosystem can self-create. Any organization can join the ecosystems it is interested in as a participant, or create its own.** No gatekeeper; no single company decides who is trustworthy.

### Subsection 3 — The ecosystems Vesta wants to join

Two choice cards, each carrying a **role badge: "Vesta joins as HOLDER"** (Vesta holds the credentials these ecosystems govern), the ecosystem`s **did:webvh DID** (placeholder until the demo cast is deployed), and an **"Open in Verana" link** (deep link to the trust-registry page in the app, to be connected):

- **Verana ECS Ecosystem — the identity card.** A trust ecosystem that governs the essential credential schemas; its accredited issuers provide **recognized KYB services** and issue the **certified ECS-Organization credential** to verified organizations; services carry ECS-Service credentials. **Why Vesta joins:** one KYB with a recognized issuer and its identity becomes provable everywhere; this is what turns the check green.
- **ISO Certification Ecosystem (demo).** Accredited certification bodies issue ISO 9001 credentials to organizations' verified identities. **Why Vesta joins:** today the certificate is a PDF nobody can verify; as a credential it becomes proof that customers and partners see on every Vesta service.

### Subsection 4 — The ecosystems Vesta wants to build

Intro: *One need remains: no existing ecosystem can answer "who is an authorized Vesta repairer". Only Vesta can. So Vesta will build its own.* One card, mirroring the choice cards but with the **role badge "Vesta operates as ECOSYSTEM"**:

- **Vesta Repair Network — the Authorized Repairer credential.** Vesta's own trust ecosystem, one credential schema: Authorized Repairer; issuance governed (only Vesta issues), verification open (anyone checks). The paper Vesta Certified Repair Company badge from Section 1 becomes verifiable, revocable proof. **Why Vesta builds it:** brand protection as a structural property — real partners green, impostors red, rogue partners revocable. Chip: → Section 5.

## 6. Section 3 — Joining the ecosystems *(watch; scene graph starts here, pre-populated with the business world)*

### 3.1 Vesta gets its digital identity *(watch)*

Vesta deploys a **vs-agent** — a small cloud-wallet service — as its **Organization anchor**. A **DID** is born: the identifier everything else attaches to. It proves nothing yet; it is the empty identity card.

> **Under the hood** — the vs-agent generates the DID (`did:webvh` recommended) and publishes its DID Document with a `DIDCommMessaging` endpoint at `https://<host>/.well-known/did.json`. The anchor will hold and present Vesta's credentials as Linked Verifiable Presentations.

*Reproduce:* deploy a vs-agent ([verana-labs/vs-agent](https://github.com/verana-labs/vs-agent)); check `/.well-known/did.json`; resolve at the public resolver → `UNTRUSTED` — the starting line.

### 3.2 Joining ECS: proving who they are — once *(watch)*

Vesta joins the ECS Ecosystem on the **Organization schema** and passes **Know-Your-Business once**, over DIDComm, with an accredited issuer. The issuer verifies the company and issues the **ECS-Organization credential** to Vesta's DID.

> **Under the hood** — app flow: ECS Ecosystem → Organization schema → **Participants** → permission tree → **Join** under an active Issuer branch (that issuer becomes the validator). `Start Permission VP` (HOLDER, `PENDING`) → DIDComm evidence session → `Set Permission VP to Validated` → credential issued and published as Linked VP (`#vpr-schemas-org-vtc-vp`).

### 3.3 Joining ISO Certification: the certificate becomes proof *(watch)*

The shortcut that shows the model's power: **the certification body never asks Vesta to prove who it is again.** Vesta presents the ECS-Organization credential on its DID (the KYB from 3.2, reused), the body runs its certification checks, and issues **ISO 9001 directly to Vesta's Organization DID**.

> **Under the hood** — HOLDER permission on the ISO 9001 schema, certification body as validator — same tree-join flow, different registry. Identification by ECS-Org presentation over DIDComm: **reusable organizational identity** — the ECS layer is the KYB other ecosystems build on.

*What Vesta now has:* a DID with two proven credentials — who it is, and that it is certified. But its services are still gray.

## 7. Section 4 — Making the services verifiable *(watch + hands-on)*

### 4.1 The anchor turns green *(watch)*

Vesta registers as an issuer of the **ECS-Service schema** and self-issues the Service credential on its anchor — valid because the same DID already presents the proven ECS-Organization. Resolve the DID now: **TRUSTED**. The trust card (live embed) is the exact card every integrated wallet shows.

> **Under the hood** — ISSUER permission on ECS-Service per the schema's permission-management mode; self-issue via the vs-agent Admin API; publish `#vpr-schemas-service-vtc-vp`. Self-issuance is valid because the same DID presents ECS-Org.

### 4.2 Rolling it out: support, badges, login *(hands-on)*

Each real service becomes its own Verifiable Service — its own vs-agent and DID, with an **ECS-Service credential issued by the anchor**. The gray cards from §1 turn verified — and the visitor joins in:

- **Agentic Support** — install the **Hologram App**, scan the QR, review the Proof-of-Trust (green check · Service · Operated by Vesta), then chat. The fake support line from §1 can't produce that card: it shows **red**.
- **Employee badge** — pick an integrated open-source wallet, receive an **ECS-Badge** (AnonCreds/DIDComm for now; Hologram first). The wallet first verifies the issuer is trusted **and** authorized to issue ECS-Badge (Q1+Q2).
- **Passwordless login** — the portal requests the badge; the wallet verifies the verifier (Q1+Q3), then presents. No password ever existed.

And because the ISO 9001 credential lives on the Organization DID, it **surfaces on every service's card at once**.

> **Under the hood** — delegated pattern: each service DID presents an ECS-Service credential issued by the anchor; trust chains resolve through the anchor's ECS-Org. ISSUER + VERIFIER permissions on ECS-Badge. Wallet rules: [UW-RES-2/3] + [UW-POT-2/3].

*What Vesta now has:* three verifiable services with badge login; the certification travels everywhere. Fake support and password phishing are dead; the paperwork problem is dying. One villain remains.

## 8. Section 5 — Vesta creates its own ecosystem *(story + watch + hands-on)*

### 5.1 Why: the last problem standing *(story)*

Umbra Repairs is still ringing doorbells — because "who is an authorized Vesta repairer" is a question only Vesta can answer. In Verana, an organization that consumed trust can also produce it: **any organization can create its own ecosystem**.

### 5.2 The Vesta Repair Network *(watch)*

Vesta publishes a one-page governance framework and creates its ecosystem with a single credential schema: **Authorized Repairer** — **issuance governed** (only Vesta issues), **verification open** (anyone checks). Then Vesta onboards **Zenith Repairs** — itself a verifiable organization (it went through its own §3–4; the pattern replicates) — identifying it by the ECS-Org credential on its DID, and issues **Authorized Repairer to Zenith's organization DID**.

> **Under the hood** — Create New Trust Registry (+ EGF document) → Create New Credential Schema (issuer mode `ECOSYSTEM`, verifier mode `OPEN`) → Create Root Permission. Zenith joins the tree as HOLDER under Vesta's root; validation by ECS-Org presentation; Linked VP on Zenith's anchor. Extension: Zenith can in turn issue **technician badges** to its employees — the technician at your door proves they're from an authorized repairer.

### 5.3 Full circle — anyone can tell *(hands-on)*

The §1 picture returns, with verdicts. Resolve Zenith's service: **green** — ECS-Org, ECS-Service, Authorized Repairer, chain verified to the Vesta Repair Network. Resolve Umbra Repairs, still claiming: **red** — no credential Vesta ever issued exists for its DID. **Brand impersonation fails structurally.** If a partner goes rogue, Vesta revokes; re-resolution drops the credential from every card.

## 9. Closing teaser — Being found *(pending)*

A short closing block (not a full section): everything Vesta published is public, resolvable, indexable. The Trust Graph turns that into discovery — only verified trust results are indexed; people, search engines, and AI agents find services by what they prove ("ISO 9001-certified manufacturers", "authorized Vesta repairers"). Full walkthrough ships later.

## 10. Open items

1. ~~Location~~ — **resolved (0.5): one single page** `/explained` with section anchors; home cards deep-link to anchors.
2. ~~Watch-only v1 vs. do-it-yourself mode~~ — **resolved (§3): hybrid** — story / watch (with mandatory source-repo links) / hands-on chips.
3. The demo anchor and services: standing testnet services (kept `TRUSTED`, monitored like the [playground demo services](../spec.md#6-shared-machinery)) vs. artifacts replayed from recordings. Proposed: standing services, shared with the playground's demo cast. [DECISION]
4. ~~ECS-Badge schema~~ — **created** in the ECS ecosystem; §5.2 and the per-wallet playground template are unblocked (AnonCreds/DIDComm first, Hologram first).
5. ~~Demo-cast unification~~ — **resolved: unified on the ISO Certification Ecosystem (demo) / ISO 9001**.
6. ~~Story cast~~ — **resolved (0.4): Vesta Appliances** · **Zenith Repairs (demo)** (needs its own standing anchor) · **Umbra Repairs (demo)** · credential **Authorized Repairer**.
7. **Deploy the Vesta demo cast**: separate vs-agent instances for every story participant — Vesta anchor + Agentic Support + badge service + portal login, KYB issuer, ISO certification body, Zenith Repairs (own anchor), Umbra Repairs (untrusted). Dedicated to this playground; not a reuse/rebrand of the verana-demos ACME cast. Until deployed, the verana-demos anchor stands in for live cards. [ACTION]
8. Vesta brand kit for the playground: logo mark, tagline, service icons — first version generated in-app (SVG); replace with designed assets later. [ACTION]
