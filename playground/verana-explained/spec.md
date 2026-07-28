# Verana Explained — Playground Specification

**Status:** DRAFT 0.4 · 2026-07-28 — restructured: business-first story, six chapters, cast renamed (ACME Corp → **Vesta Appliances**).
**Companions:** [playground spec](../spec.md) · [integration guidelines](../guidelines/) · [Verifiable Trust spec (v3)](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) · [VPR spec (v3)](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html)

---

## 1. Purpose

A playground that **explains the basics of Verana** through one continuous story a non-technical reader can follow: a fictional company with a problem everyone recognizes — impostors trading on its name — discovers Verana, joins it, and ends up governing trust for its own partner network.

The story must **start from the business, not the technology**: who the company is, what it runs, what hurts, why Verana — and only then, how. All protocol mechanics live in collapsible layers for readers who want them.

Where the [Verana Playground](../spec.md) is a hands-on surface for testing concepts and showcasing wallet integrations, *Verana Explained* is the **narrative on-ramp**.

**Audience:** normal people first — customers, business owners, evaluators. No prior SSI knowledge assumed. Technical readers get their depth in the "Reproduce it" and "Under the hood" layers.

## 2. The cast

| Name | Role in the story |
|---|---|
| **Vesta Appliances** | The protagonist: a household-appliance manufacturer (washing machines, ovens), ~200 employees, selling worldwide, with a network of independent repair partners. |
| Vesta's online services | Customer **support chat** · **employee badge** service · **staff & partner portal login** — ordinary services in Chapter 1, verifiable services by Chapter 4. |
| **Zenith Repairs (demo)** | A genuine independent repair company — becomes Vesta's first credentialed **Authorized Repairer**. |
| **Umbra Repairs (demo)** | The villain: a fake "Vesta-authorized" repair outfit scamming customers. Fails verification in Chapter 5. |
| **ECS Ecosystem** | The root "identity card" ecosystem: ECS-Organization (who you are), ECS-Service (what this service is), ECS-Badge. |
| **ISO Certification Ecosystem (demo)** | Fictional certification ecosystem governing an **ISO 9001** credential, issued by accredited certification bodies. |
| **Vesta Repair Network** | The ecosystem Vesta itself creates in Chapter 5, with one credential schema: **Authorized Repairer** (issuance governed, verification open). |

> **Demo cast note:** for this playground we **create separate vs-agent instances for every participant of the story** — the Vesta anchor and its three services, the KYB issuer, the certification body, Zenith Repairs, Umbra Repairs. A dedicated cast, not a reuse of the existing verana-demos (ACME-branded) services; until the Vesta cast is deployed, the verana-demos anchor stands in for live cards. See open items.

## 3. Format

- One linear story told in **six chapters**. Each chapter is a **separate page** (`/explained/chapter-N`, with `/explained` as the index of chapter cards). Chapters 1–3 are context (business situation, motivation, choices); Chapters 4–5 are action; Chapter 6 is the outlook.
- Each sub-step has up to four layers:
  1. **The story** — what happens, in plain language (2–4 sentences). This layer must be readable by someone who has never heard of DIDs or credentials.
  2. **The progressive diagram** — one master Vesta scene graph (verana.io/ecosystems visual grammar, playground palette) with **fixed positions**, re-rendered at every sub-step. Elements declare the stage at which they appear (and may change tone or disappear at a later stage — e.g. gray "unverifiable" services turning verified, the customer's "?" resolving). New elements are highlighted (pulse + "New in x.y" caption). The Chapter 1 "today" picture — gray services, red impostors, a customer who cannot tell — **returns in 5.3 with the verdicts in place**: the full-circle payoff.
  3. **Reproduce it** *(optional; action chapters only)* — a numbered recipe with the real clicks/commands: deploy a vs-agent, open the Verana app, then the current frontend join flow — **ecosystem → credential schema → Participants → permission tree → Join** on the branch to join under (that branch becomes the validator).
  4. **Under the hood** *(optional)* — a collapsible box mapping the story to the real mechanics (v3 message names: Start Permission VP, Set Permission VP to Validated, Create Root Permission…), linking to the specs.
- Sub-steps carry a chip: **story** (context, just read) · **watch** (Vesta does it; every service shown MUST link the GitHub repository of the software that runs it) · **hands-on** (the visitor does it with their own wallet).
- Artifacts are **real testnet artifacts** wherever possible (live registry entries, a resolvable demo DID); screenshots only where liveness adds nothing.
- Every chapter ends with the state so far ("what Vesta now has").

## 4. Chapter 1 — Meet Vesta Appliances *(story)*

### 1.1 The company

Vesta Appliances has made washing machines and ovens for forty years. It sells worldwide through resellers, employs ~200 people, and relies on a network of independent repair companies to service machines in customers' homes.

*Diagram:* Vesta at the center, plain and gray — no checks, no proofs. Just a company.

### 1.2 What Vesta runs online

Like any company, Vesta runs online services: a **customer support chat**, an **employee badge** system, and a **staff & partner portal**. They work — but nothing about them can be *proven*. They are names on a screen.

*Diagram:* the three services attach to Vesta, all gray. A customer node connects to support.

### 1.3 The problems

- Customers googling "Vesta support" land on **fake support lines**; impostor accounts on social media "help" with refunds — and harvest card numbers.
- Vans labeled "Vesta-authorized repair" that Vesta has never heard of ring doorbells. Customers get scammed; **Vesta gets blamed**.
- Portal passwords are phished and reset endlessly; the support team drowns.
- Every marketplace, bank, and certifier asks Vesta for the **same company documents, again and again**.
- The root cause of all four: online, **Vesta's word looks exactly like the scammers' word**. There is no way to prove anything.

*Diagram:* red dashed impostors appear — **Fake support line**, **Umbra Repairs** ("claims: Vesta-authorized") — and the customer node gains a **?**: *which one is real? Nobody can tell.*

*What Vesta has:* a real business, real services — and no way to prove any of it.

## 5. Chapter 2 — Why Verana *(story)*

### 2.1 What if services could prove who runs them?

What if, before you connect to anything — a support chat, a repair company, a login page — your wallet could **check who really operates it**, and show a green check only when there is proof? Not a claim, not a logo: a verification that scammers cannot fake. That is what Verana makes possible: **trust before contact**.

*Diagram:* a wallet appears next to the customer, with a dashed "checks before connecting" edge toward the services — the *idea*, previewed.

### 2.2 Verana in one picture

Three concepts carry the whole system:

- **Ecosystems** — communities that set the rules: *who* may issue *which* proofs, and how. Public, governed, on a public registry (the VPR).
- **Credentials** — the proofs themselves: "this is organization X", "this service belongs to X", "X is ISO 9001-certified". Issued once, verifiable everywhere.
- **Wallets** — where verification happens: every integrated wallet checks the same public registry and shows the same verdict, the same way.

Open source, public, no gatekeeper — no single company decides who is trustworthy.

### 2.3 Vesta's decision

Vesta decides to join, with a three-part plan: **prove** (become verifiable, so customers can tell real from fake) → **certify** (attach its ISO 9001 certification so it travels everywhere Vesta acts) → **govern** (later: control who counts as an authorized repairer).

*Diagram:* the plan pinned to Vesta: *prove → certify → govern*.

## 6. Chapter 3 — Choosing ecosystems *(story)*

### 3.1 The ECS Ecosystem — the identity card

Every verifiable organization starts here. The ECS Ecosystem governs the **essential credentials**: **ECS-Organization** (*who you are* — legal name, country, registry id, verified once by an accredited issuer) and **ECS-Service** (*what this service is* — name, type, description). Together they are what turns the check **green**. Why Vesta joins: without this, nothing else can be proven.

*Diagram:* the ECS Ecosystem node appears (violet) — "proves who you are & what your services are".

### 3.2 The ISO Certification Ecosystem (demo)

Vesta is ISO 9001-certified — today that is a **PDF nobody can verify**. In the ISO Certification Ecosystem (a demo, not the real ISO), accredited certification bodies issue **ISO 9001 credentials** to organizations' verified identities. Why Vesta joins: the certificate becomes a proof customers and business partners see on every Vesta service, verified.

*Diagram:* the ISO Certification Ecosystem node appears (violet).

### 3.3 The gap — and the foreshadowing

No ecosystem anywhere governs "who is an authorized Vesta repairer" — only Vesta can know that. The repair-fraud problem from 1.3 has no existing ecosystem to join. **Vesta will have to create its own.** (Chapter 5.)

*Diagram:* a red pill near Umbra: *"authorized repairers? — no proof exists"*.

## 7. Chapter 4 — Joining, in practice *(watch + hands-on)*

### 4.1 Vesta gets its digital identity *(watch)*

Vesta deploys a **vs-agent** — a small cloud-wallet service — as its **Organization anchor**. A **DID** is born: the identifier everything else attaches to. At this point it proves nothing; it is the empty identity card.

> **Under the hood** — the vs-agent generates the DID (`did:webvh` recommended) and publishes its DID Document with a `DIDCommMessaging` endpoint at `https://<host>/.well-known/did.json`. The anchor will hold and present Vesta's credentials as Linked Verifiable Presentations.

*Reproduce:* deploy a vs-agent ([verana-labs/vs-agent](https://github.com/verana-labs/vs-agent); the verana-demos organization-vs is a working template); check `/.well-known/did.json`; resolve the DID at the public resolver → `UNTRUSTED` — the starting line.

### 4.2 Proving who they are — once *(watch)*

Vesta joins the ECS Ecosystem on the **Organization schema** and passes **Know-Your-Business once**, over DIDComm, with an accredited issuer. The issuer verifies the company and issues the **ECS-Organization credential** to Vesta's DID. The anchor finally has a name that is proven, not claimed.

> **Under the hood** — in the Verana app: ECS Ecosystem → Organization schema → **Participants** → permission tree → **Join** under an active Issuer branch (that issuer becomes the validator). `Start Permission VP` creates the HOLDER permission (`PENDING`); evidence over a DIDComm session; `Set Permission VP to Validated`; credential issued and published as Linked VP (`#vpr-schemas-org-vtc-vp`).

### 4.3 Describing the service — the check turns green *(watch)*

Vesta registers as an issuer of the **ECS-Service schema** and self-issues the Service credential on its anchor (valid because the same DID presents the proven ECS-Organization). Resolve the DID now: **TRUSTED**. The trust card — the same card every integrated wallet shows — has its green check, the Service block, and the Operated-by block.

*Live artifact:* the standing anchor's trust card, resolved on page load.

> **Under the hood** — ISSUER permission on ECS-Service (per the schema's permission-management mode), self-issue via the vs-agent Admin API, publish `#vpr-schemas-service-vtc-vp`. Self-issuance is valid because the same DID presents ECS-Org — every service traces to an accountable organization.

### 4.4 Rolling it out: support, badges, login *(hands-on)*

Each real service becomes its own Verifiable Service — own vs-agent, own DID, **ECS-Service issued by the anchor** (this is why 4.3 registered Vesta as an ECS-Service issuer):

- **Support chat** — *you*: install the **Hologram App**, scan the QR, review the Proof-of-Trust (green check · Service · Operated by Vesta), then chat. The fake support line from 1.3 can't produce that card: it shows **red**.
- **Employee badge** — Vesta's badge service issues **ECS-Badge** credentials (AnonCreds/DIDComm for now; OpenID4VC when available). *You*: pick an integrated open-source wallet (wallet chooser), receive a badge. Your wallet first verifies the issuer is trusted **and** authorized to issue ECS-Badge (Q1+Q2).
- **Passwordless login** — the portal requests presentation of the badge. Your wallet verifies the verifier is trusted **and** authorized to request ECS-Badge (Q1+Q3), then presents. No password ever existed; phishing for credentials fails structurally.

> **Under the hood** — delegated ECS-Service pattern: each service DID presents an ECS-Service credential issued by the anchor; trust chains resolve through the anchor's ECS-Org. Vesta holds ISSUER and VERIFIER permissions on the ECS-Badge schema. Wallet rules: [UW-RES-2/3] + [UW-POT-2/3] from the [user-wallet guideline](../guidelines/user-wallet-integration.md).

### 4.5 The certification credential *(watch)*

Vesta executes its Chapter 3 choice: it joins the ISO Certification Ecosystem, and here is the shortcut that shows the model's power — **the certification body never asks Vesta to prove who it is again.** Vesta presents the ECS-Organization credential on its DID (the KYB from 4.2, reused), the body runs its certification checks, and issues **ISO 9001 directly to Vesta's Organization DID**. Instantly, the credential surfaces on **every** Vesta service's trust card.

> **Under the hood** — HOLDER permission on the ISO 9001 schema, certification body as validator; identification by ECS-Org presentation over DIDComm (**reusable organizational identity** — the ECS layer is the KYB other ecosystems build on); Linked VP on the anchor; org-level credentials surface on all services' cards ([UW-POT] block 4).

*What Vesta now has:* a proven identity · three verifiable services with badge login · a certification that travels everywhere it acts. Two of the four Chapter 1 problems are dead (fake support, password phishing); the paperwork problem is dying (KYB once). One villain remains.

## 8. Chapter 5 — Vesta's own ecosystem *(watch + hands-on)*

### 5.1 Why: the last problem standing *(story)*

Umbra Repairs is still out there, ringing doorbells. No existing ecosystem can say who a genuine Vesta repairer is — **only Vesta can**. In Verana, an organization that consumed trust can also *produce* it: Vesta becomes a governance authority.

### 5.2 The Vesta Repair Network *(watch)*

Vesta publishes a one-page **governance framework** (who qualifies as a repairer, obligations, revocation) and creates its ecosystem with a single credential schema: **Authorized Repairer**. The design choice that matters: **issuance is governed** (only Vesta issues) — **verification is open** (anyone checks, no permission needed).

Then Vesta onboards **Zenith Repairs** — itself a verifiable organization (it went through its own Chapter 4; the pattern replicates, that is the point). Vesta identifies Zenith by the **ECS-Org credential on its DID** — the reusable-KYB shortcut again, with Vesta now on the issuer side — and issues **Authorized Repairer to Zenith's organization DID**. The credential surfaces on Zenith's services next to its own ECS credentials.

> **Under the hood** — Create New Trust Registry (+ EGF document) → Create New Credential Schema (issuer mode `ECOSYSTEM`, verifier mode `OPEN`) → Create Root Permission. Zenith joins the tree as HOLDER under Vesta's root; validation by ECS-Org presentation; Linked VP on Zenith's anchor. Extension (one line in the story): Zenith can in turn issue **technician badges** to its own employees — so the technician at your door proves they are from an authorized repairer.

### 5.3 Full circle — anyone can tell *(hands-on)*

The Chapter 1 picture returns, with verdicts. *You*: resolve Zenith's service with your wallet — **green**: ECS-Org, ECS-Service, **Authorized Repairer** (issued by Vesta Appliances, chain verified to the Vesta Repair Network). Then Umbra Repairs, which still *claims* to be authorized — **red verdict**: no credential Vesta ever issued exists for its DID, and the claim cannot be forged. **Brand impersonation fails structurally.** And if a partner goes rogue, Vesta revokes — re-resolution drops the credential from every card.

*What Vesta now has* — the full circle: proven identity · verifiable services · portable certification · **its own governed trust ecosystem** protecting its brand, its partners, and its customers. What Vesta consumed, Vesta now provides.

## 9. Chapter 6 — Being found *(pending — to be redacted later)*

Not part of this revision; will be defined once Chapters 1–5 are validated. Summary for orientation:

Everything Vesta published — the ECS credentials, the ISO 9001 certification, the Authorized Repairer credentials — lives in DID Documents and the public registry, so it can be **indexed**. The indexer crawls; the resolver verifies; **only verified trust results enter the Trust Graph**. Anyone — a person, a search engine, an AI agent over API/MCP — then **discovers by proof, not keywords**: "ISO 9001-certified manufacturers", "authorized Vesta repairers" — with every result carrying verifiable provenance. The visitor will run those queries live and find Vesta's services and Zenith exactly where their credentials put them.

## 10. Open items

1. Location of this playground: standalone section of the main playground site vs. its own page tree. [DECISION]
2. ~~Watch-only v1 vs. do-it-yourself mode~~ — **resolved (§3): hybrid** — story chips: story / watch (with mandatory source-repo links) / hands-on (Hologram App for chat; an integrated open-source user wallet for badge + login).
3. The demo anchor and services: standing testnet services (kept `TRUSTED`, monitored like the [playground demo services](../spec.md#6-shared-machinery)) vs. artifacts replayed from recordings. Proposed: standing services, shared with the playground's demo cast. [DECISION]
4. ~~ECS-Badge schema~~ — **created** in the ECS ecosystem; 4.4 and the per-wallet playground template are unblocked (AnonCreds/DIDComm first, Hologram first).
5. ~~Demo-cast unification~~ — **resolved: unified on the ISO Certification Ecosystem (demo) / ISO 9001** across this story, the [playground spec](../spec.md), the guidelines, and the submission kit.
6. ~~Story cast~~ — **resolved (0.4): Vesta Appliances** (protagonist) · **Zenith Repairs (demo)** (authorized partner — needs its own standing anchor in the demo environment) · **Umbra Repairs (demo)** (fake repairer) · credential renamed **Authorized Repairer**.
7. **Deploy the Vesta demo cast**: separate vs-agent instances for every story participant — Vesta anchor + support chat + badge service + portal login, KYB issuer, ISO certification body, Zenith Repairs (own anchor), Umbra Repairs (untrusted). Dedicated to this playground; not a reuse/rebrand of the verana-demos ACME cast. Until deployed, the verana-demos anchor stands in for live cards. [ACTION]
