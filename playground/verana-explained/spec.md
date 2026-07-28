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
| Vesta's online services | Customer **support chat** · **employee badge** service · **staff & partner portal login** — ordinary services in §1, verifiable services by §5. |
| **Zenith Repairs (demo)** | A genuine independent repair company — becomes Vesta's first credentialed **Authorized Repairer**. |
| **Umbra Repairs (demo)** | The villain: a fake "Vesta-authorized" repair outfit scamming customers. Fails verification in §6. |
| **ECS Ecosystem** | The root "identity card" ecosystem: ECS-Organization (who you are), ECS-Service (what this service is), ECS-Badge. |
| **ISO Certification Ecosystem (demo)** | Fictional certification ecosystem governing an **ISO 9001** credential, issued by accredited certification bodies. |
| **Vesta Repair Network** | The ecosystem Vesta itself creates in §6, with one credential schema: **Authorized Repairer** (issuance governed, verification open). |

> **Demo cast note:** for this playground we **create separate vs-agent instances for every participant of the story** — the Vesta anchor and its three services, the KYB issuer, the certification body, Zenith Repairs, Umbra Repairs. A dedicated cast, not a reuse of the existing verana-demos (ACME-branded) services; until the Vesta cast is deployed, the verana-demos anchor stands in for live cards. See open items.

## 3. Format & look-and-feel

- **Everything on one single page**: `/explained`, six sections with anchors (`#section-1` … `#section-6`), a closing "Being found" teaser, and a sticky/linked table of chapters from the home page cards.
- **The page changes register as it progresses** — that is the design:
  - **§1 is a marketing-style article** — company logo, profile, article prose, a **business services diagram** (the company card above, connectors down to one card per service: ownership at a glance), and an attractive **problems grid**. **No DIDs, no protocol diagram, no Verana vocabulary.** It must feel like a page from Vesta's own website / a business magazine profile.
  - **§2–§3 are short, visual, card-based** — the three verana.io pillars, then the ecosystem choices.
  - **§4–§6 are the technical build** — sub-steps with the progressive **scene graph**, which **starts at §4 pre-populated with the business world** (Vesta, its three gray services, the customer with the "?", the red impostors) so the first technical stage transforms a world the reader already knows. DIDs appear only from §4.1.
- Sub-steps (§4–§6 only) carry a chip — **story** / **watch** (Vesta does it; every service shown MUST link the GitHub repository of the software that runs it) / **hands-on** (the visitor does it with their own wallet) — and up to four layers: story · diagram stage · **Reproduce it** (optional numbered recipe; frontend flow: ecosystem → credential schema → Participants → permission tree → Join under the chosen branch) · **Under the hood** (optional collapsible; v3 message names).
- Scene-graph mechanics: one master graph, fixed positions; elements declare the stage at which they **appear, change tone/label, or leave** (gray unprovable services turn verified; the customer's "?" resolves; the fake support line turns ✗ red; full-circle verdicts in §6). New/changed elements pulse, with a "New in x.y" caption.
- Artifacts are **real testnet artifacts** wherever possible; screenshots only where liveness adds nothing.
- Sections end with a state line ("what Vesta now has") where it helps the narrative.

## 4. Section 1 — Meet Vesta Appliances *(marketing article)*

**Look:** company page. Logo mark + wordmark, tagline ("Quality home appliances since 1985"), meta chips (HQ, ~200 employees, worldwide resellers, independent repair partners). Two or three short article paragraphs:

Vesta Appliances has made washing machines and ovens for forty years. It sells worldwide through resellers and relies on a network of independent repair companies to service machines in customers' homes.

**The services (business diagram, not protocol):** the Vesta company card on top; connectors down to three service cards — **Support chat** (help with your machine), **Employee badges** (company IDs for staff), **Staff & partner portal** (orders, manuals, warranty claims). The visual states the ownership: *all of this is Vesta's*.

**The certified repair network (business diagram, not protocol):** a hub-and-spoke visual — Vesta (logo) at the center ("trains · audits · certifies"), the independent repair companies around it (Zenith Repairs among them), **each carrying the amber "Vesta Certified Repair Company" badge** — the real-world paper certification (training, yearly audits, signed contract). Closing line bridges to the problems: the badge lives on van doors and PDF certificates — online, anyone can print one.

**The problems (grid of four + root-cause banner):**

1. **Fake support lines** — customers googling "Vesta support" land on scammers; impostor accounts "help" with refunds and harvest card numbers.
2. **Fake "authorized" repairers** — vans Vesta has never heard of ring doorbells; customers get scammed, Vesta gets blamed.
3. **Password pain** — portal passwords phished and reset endlessly; the support team drowns.
4. **Paperwork, again and again** — every marketplace, bank, and certifier asks for the same company documents.

Banner: **Online, Vesta's word looks exactly like the scammers' word. Nothing can be proven.**

## 5. Section 2 — Why Verana *(short, pillar cards)*

The three Verana pillars, exactly as on [verana.io](https://verana.io):

- **Trust Ecosystems** — sovereign ecosystems: build ecosystems that issue and verify any credential, with your own schemas, governance framework, participants, and business model — or join an existing one.
- **Verifiable Trust** — verifiable identity: identify any service and the organization or person that controls it, and verify it before you connect. *Verify first. Then connect.*
- **The Trust Graph** — discovery: find services and ecosystems by the credentials they hold, ranked by trust.

Emphasis strip (the facts that matter to Vesta): **Verana is public, decentralized infrastructure. Any ecosystem can self-create. Any organization can join the ecosystems it is interested in as a participant — or create its own.** No gatekeeper; no single company decides who is trustworthy.

## 6. Section 3 — The ecosystems Vesta wants to join *(choice cards)*

Two choice cards + one dashed teaser:

- **ECS Ecosystem — the identity card.** Governs the essential credentials: ECS-Organization (who you are — verified once by an accredited issuer) and ECS-Service (what each service is). **Why Vesta joins:** this is what turns the check green; without it, nothing else can be proven.
- **ISO Certification Ecosystem (demo).** Accredited certification bodies issue ISO 9001 credentials to organizations' verified identities. **Why Vesta joins:** today the certificate is a PDF nobody can verify; as a credential it becomes proof that customers and partners see on every Vesta service.
- *(dashed teaser)* **Authorized repairers? No ecosystem governs that — only Vesta can. §6.**

## 7. Section 4 — Joining the ecosystems *(watch; scene graph starts here, pre-populated with the business world)*

### 4.1 Vesta gets its digital identity *(watch)*

Vesta deploys a **vs-agent** — a small cloud-wallet service — as its **Organization anchor**. A **DID** is born: the identifier everything else attaches to. It proves nothing yet; it is the empty identity card.

> **Under the hood** — the vs-agent generates the DID (`did:webvh` recommended) and publishes its DID Document with a `DIDCommMessaging` endpoint at `https://<host>/.well-known/did.json`. The anchor will hold and present Vesta's credentials as Linked Verifiable Presentations.

*Reproduce:* deploy a vs-agent ([verana-labs/vs-agent](https://github.com/verana-labs/vs-agent)); check `/.well-known/did.json`; resolve at the public resolver → `UNTRUSTED` — the starting line.

### 4.2 Joining ECS: proving who they are — once *(watch)*

Vesta joins the ECS Ecosystem on the **Organization schema** and passes **Know-Your-Business once**, over DIDComm, with an accredited issuer. The issuer verifies the company and issues the **ECS-Organization credential** to Vesta's DID.

> **Under the hood** — app flow: ECS Ecosystem → Organization schema → **Participants** → permission tree → **Join** under an active Issuer branch (that issuer becomes the validator). `Start Permission VP` (HOLDER, `PENDING`) → DIDComm evidence session → `Set Permission VP to Validated` → credential issued and published as Linked VP (`#vpr-schemas-org-vtc-vp`).

### 4.3 Joining ISO Certification: the certificate becomes proof *(watch)*

The shortcut that shows the model's power: **the certification body never asks Vesta to prove who it is again.** Vesta presents the ECS-Organization credential on its DID (the KYB from 4.2, reused), the body runs its certification checks, and issues **ISO 9001 directly to Vesta's Organization DID**.

> **Under the hood** — HOLDER permission on the ISO 9001 schema, certification body as validator — same tree-join flow, different registry. Identification by ECS-Org presentation over DIDComm: **reusable organizational identity** — the ECS layer is the KYB other ecosystems build on.

*What Vesta now has:* a DID with two proven credentials — who it is, and that it is certified. But its services are still gray.

## 8. Section 5 — Making the services verifiable *(watch + hands-on)*

### 5.1 The anchor turns green *(watch)*

Vesta registers as an issuer of the **ECS-Service schema** and self-issues the Service credential on its anchor — valid because the same DID already presents the proven ECS-Organization. Resolve the DID now: **TRUSTED**. The trust card (live embed) is the exact card every integrated wallet shows.

> **Under the hood** — ISSUER permission on ECS-Service per the schema's permission-management mode; self-issue via the vs-agent Admin API; publish `#vpr-schemas-service-vtc-vp`. Self-issuance is valid because the same DID presents ECS-Org.

### 5.2 Rolling it out: support, badges, login *(hands-on)*

Each real service becomes its own Verifiable Service — its own vs-agent and DID, with an **ECS-Service credential issued by the anchor**. The gray cards from §1 turn verified — and the visitor joins in:

- **Support chat** — install the **Hologram App**, scan the QR, review the Proof-of-Trust (green check · Service · Operated by Vesta), then chat. The fake support line from §1 can't produce that card: it shows **red**.
- **Employee badge** — pick an integrated open-source wallet, receive an **ECS-Badge** (AnonCreds/DIDComm for now; Hologram first). The wallet first verifies the issuer is trusted **and** authorized to issue ECS-Badge (Q1+Q2).
- **Passwordless login** — the portal requests the badge; the wallet verifies the verifier (Q1+Q3), then presents. No password ever existed.

And because the ISO 9001 credential lives on the Organization DID, it **surfaces on every service's card at once**.

> **Under the hood** — delegated pattern: each service DID presents an ECS-Service credential issued by the anchor; trust chains resolve through the anchor's ECS-Org. ISSUER + VERIFIER permissions on ECS-Badge. Wallet rules: [UW-RES-2/3] + [UW-POT-2/3].

*What Vesta now has:* three verifiable services with badge login; the certification travels everywhere. Fake support and password phishing are dead; the paperwork problem is dying. One villain remains.

## 9. Section 6 — Vesta creates its own ecosystem *(story + watch + hands-on)*

### 6.1 Why: the last problem standing *(story)*

Umbra Repairs is still ringing doorbells — because "who is an authorized Vesta repairer" is a question only Vesta can answer. In Verana, an organization that consumed trust can also produce it: **any organization can create its own ecosystem**.

### 6.2 The Vesta Repair Network *(watch)*

Vesta publishes a one-page governance framework and creates its ecosystem with a single credential schema: **Authorized Repairer** — **issuance governed** (only Vesta issues), **verification open** (anyone checks). Then Vesta onboards **Zenith Repairs** — itself a verifiable organization (it went through its own §4–5; the pattern replicates) — identifying it by the ECS-Org credential on its DID, and issues **Authorized Repairer to Zenith's organization DID**.

> **Under the hood** — Create New Trust Registry (+ EGF document) → Create New Credential Schema (issuer mode `ECOSYSTEM`, verifier mode `OPEN`) → Create Root Permission. Zenith joins the tree as HOLDER under Vesta's root; validation by ECS-Org presentation; Linked VP on Zenith's anchor. Extension: Zenith can in turn issue **technician badges** to its employees — the technician at your door proves they're from an authorized repairer.

### 6.3 Full circle — anyone can tell *(hands-on)*

The §1 picture returns, with verdicts. Resolve Zenith's service: **green** — ECS-Org, ECS-Service, Authorized Repairer, chain verified to the Vesta Repair Network. Resolve Umbra Repairs, still claiming: **red** — no credential Vesta ever issued exists for its DID. **Brand impersonation fails structurally.** If a partner goes rogue, Vesta revokes; re-resolution drops the credential from every card.

## 10. Closing teaser — Being found *(pending)*

A short closing block (not a full section): everything Vesta published is public, resolvable, indexable. The Trust Graph turns that into discovery — only verified trust results are indexed; people, search engines, and AI agents find services by what they prove ("ISO 9001-certified manufacturers", "authorized Vesta repairers"). Full walkthrough ships later.

## 11. Open items

1. ~~Location~~ — **resolved (0.5): one single page** `/explained` with section anchors; home cards deep-link to anchors.
2. ~~Watch-only v1 vs. do-it-yourself mode~~ — **resolved (§3): hybrid** — story / watch (with mandatory source-repo links) / hands-on chips.
3. The demo anchor and services: standing testnet services (kept `TRUSTED`, monitored like the [playground demo services](../spec.md#6-shared-machinery)) vs. artifacts replayed from recordings. Proposed: standing services, shared with the playground's demo cast. [DECISION]
4. ~~ECS-Badge schema~~ — **created** in the ECS ecosystem; §5.2 and the per-wallet playground template are unblocked (AnonCreds/DIDComm first, Hologram first).
5. ~~Demo-cast unification~~ — **resolved: unified on the ISO Certification Ecosystem (demo) / ISO 9001**.
6. ~~Story cast~~ — **resolved (0.4): Vesta Appliances** · **Zenith Repairs (demo)** (needs its own standing anchor) · **Umbra Repairs (demo)** · credential **Authorized Repairer**.
7. **Deploy the Vesta demo cast**: separate vs-agent instances for every story participant — Vesta anchor + support chat + badge service + portal login, KYB issuer, ISO certification body, Zenith Repairs (own anchor), Umbra Repairs (untrusted). Dedicated to this playground; not a reuse/rebrand of the verana-demos ACME cast. Until deployed, the verana-demos anchor stands in for live cards. [ACTION]
8. Vesta brand kit for the playground: logo mark, tagline, service icons — first version generated in-app (SVG); replace with designed assets later. [ACTION]
