# Verana Explained — Playground Specification

**Status:** DRAFT 0.3 · 2026-07-16 — Steps 1–4 redacted.
**Companions:** [playground spec](../spec.md) · [integration guidelines](../guidelines/) · [Verifiable Trust spec v4](https://verana-labs.github.io/verifiable-trust-spec/) · [VPR spec v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/)

---

## 1. Purpose

A playground that **explains the basics of Verana** through one continuous story: a fictional corporation, **ACME Corp**, creates itself in Verana and becomes a verified, resolvable participant of the trust layer.

Where the [Verana Playground](../spec.md) is a hands-on surface for testing concepts and showcasing wallet integrations, *Verana Explained* is the **narrative on-ramp**: a visitor follows ACME step by step and, at each step, sees both the plain-language story and what actually happened on the network.

**Audience:** first-time visitors, ecosystem-builder prospects, evaluators. No prior SSI knowledge assumed.

## 2. Format

- One linear story, told in **steps**. Each step is a page (or scroll section) with three layers:
  1. **The story** — what ACME does, in plain language (2–4 sentences per sub-step).
  2. **What you see** — the concrete artifact: a screenshot or live embed (Verana frontend view, DIDComm exchange, registry entry, trust card).
  3. **Under the hood** — a collapsible box mapping the story to the real mechanics (spec message names, DID Document fragments), linking to the specs.
- Artifacts are **real testnet artifacts** wherever possible (live registry entries, a resolvable ACME demo DID); screenshots only where liveness adds nothing.
- **Format: hybrid.**
  - **Organization-side steps are watch-only** (v1): deployments, corporation creation, onboarding processes — the visitor watches ACME do it. Every service shown MUST link the **GitHub repository of the software that runs it** (vs-agent, chatbot, issuer, login service): watch-only never means closed — the visitor can always jump to the source.
  - **End-user-side steps are hands-on**: the visitor is instructed to download the **Hologram App** to chat with the customer-support service (Step 2.1), and **one of the integrated open-source user wallets (their choice)** to receive the ECS-Badge (Step 2.2) and log in with it (Step 2.3).
- Every step ends with the ACME state so far ("what ACME now has").

## 3. The story — Step 1: ACME Corp creates itself in Verana

### 1.1 Create the Organization anchor

ACME deploys a **Verifiable Service** using the [vs-agent](https://github.com/verana-labs/vs-agent): its **Organization anchor**. Deploying the vs-agent creates a **DID** for ACME — the identity everything else attaches to.

*What you see:* the vs-agent coming online; the fresh DID (`did:webvh:…acme…`) and its DID Document.

> **Under the hood** — the vs-agent generates the DID (`did:webvh` recommended) and publishes its DID Document with a `DIDCommMessaging` service endpoint. This anchor will hold and present ACME's credentials as Linked Verifiable Presentations ([VT-ECS-CRED]).

### 1.2 Become a corporation and get verified as an Organization

ACME connects to the **Verana frontend** (`app.testnet.verana.network`), creates itself as a **Corporation**, and **joins the ECS Ecosystem**: it selects the **Organization credential schema** from the ecosystem and starts an **onboarding process** with an **Issuer** of the Organization schema to verify its business.

ACME provides its DID and the required documentation (KYB / KYC) so the issuer can verify the company and its representative. When the issuer has verified the company, it sets the onboarding process to **validated** and **issues the Verifiable Credential representing the Organization** to the DID of ACME's Verifiable Service anchor.

*What you see:* the corporation entry in the frontend; the onboarding process moving `PENDING → VALIDATED`; the DIDComm exchange where documents are provided; the ECS-Organization credential landing on the anchor DID.

> **Under the hood** — creating the Corporation registers a `Corporation` entry on the VPR (its on-chain identity and governance anchor). Starting the onboarding creates a `HOLDER` participant entry on the Organization schema, with the chosen issuer as validator (`MsgStartParticipantOP`, state `PENDING`). Evidence is exchanged over a DIDComm session with the issuer's Verifiable Service. On approval the issuer submits `MsgSetParticipantOPToValidated`, then issues the **ECS-Organization** credential to ACME's anchor DID; the anchor publishes it as a Linked VP (`#vpr-schemas-org-vtc-vp`).

### 1.3 Self-issue the Service credential

ACME now registers itself as an **Issuer of the ECS-Service schema** and **self-issues its Service credential** to its anchor: the anchor is not just an organization — it is a verifiable *service* of that organization.

*What you see:* the issuer registration on the Service schema; the self-issued ECS-Service credential appearing on the anchor DID.

> **Under the hood** — ACME obtains an `ISSUER` participant entry on the ECS-Service schema, then issues the **ECS-Service** credential to its own DID and publishes it (`#vpr-schemas-service-vtc-vp`). Self-issuance is valid precisely because the same DID also presents the ECS-Organization credential ([VS-REQ-3]): every service traces to an accountable organization. The anchor triggers re-resolution (`MsgTriggerResolver`) so the public resolver picks up the new state.

### 1.4 ACME is verified

**ACME Corp is now verified, and its DID is verifiable and resolvable by anyone.**

*What you see:* the **trust card** — the same Proof-of-Trust card as on [verana.io](https://verana.io/identity) and in the [presentation pattern](../guidelines/user-wallet-integration.md#5-proof-of-trust-presentation-uw-pot):

- ✅ **Trusted** — the DID, evaluated live against the public registry
- **Service** — ACME's anchor service (name, logo, description) from ECS-Service
- **Operated by** — ACME Corp (legal name, country, registry id) from ECS-Organization
- **Trust chain** — each credential's issuer, verified recursively up to the ECS Ecosystem root

*What ACME now has:* a resolvable DID · a Corporation entry · a verified ECS-Organization credential · a self-issued ECS-Service credential · `TRUSTED` status from the public resolver — the anchor from which everything in the next steps grows.

## 4. The story — Step 2: ACME deploys its services

One organization, many services: each real-world service ACME runs becomes its own **Verifiable Service** — its own vs-agent, its own DID — with an **ECS-Service credential issued by the Organization anchor**. This is why ACME registered as an ECS-Service issuer in Step 1.3: the anchor now identifies everything the company operates.

### 2.1 Customer support service (Hologram Chatbot)

ACME deploys its customer-support chatbot as a Verifiable Service: a new vs-agent, a new DID, and an **ECS-Service credential issued by the Org anchor**. Anyone who connects can verify, before the first message, that this chatbot really is ACME's.

*What you see:* the new service DID; its trust card (Trusted · service: Customer Support · operated by: ACME Corp); the service's source repository link.
*What you do:* download the **Hologram App** (App Store / Play Store links provided), connect to the chatbot, review the Proof-of-Trust it shows, accept — and chat.

> **Under the hood** — the delegated pattern ([VS-REQ-4]): the chatbot's DID presents an ECS-Service credential whose **issuer** is the anchor DID; the anchor presents ECS-Organization; trust resolution walks that chain, so the chatbot is provably bound to the accountable organization. Linked VP `#vpr-schemas-service-vtc-vp` on the chatbot DID; `MsgTriggerResolver` → `TRUSTED`.

### 2.2 Employee badge issuer (OpenID4VC)

ACME deploys a **badge issuer service** — a new vs-agent, a new DID, ECS-Service issued by the Org — to issue **company badges (ECS-Badge)** to its employees over **OpenID4VC**.

An employee receives their badge in **one of the open-source user wallets integrated with Verana — the user chooses which**. Before accepting, the wallet verifies two things: that the issuer service is **trusted** (Q1), and that it is **accredited to issue ECS-Badge credentials** (Q2).

*What you see:* the badge issuer's service DID, trust card, and source repository link.
*What you do:* pick a wallet in the **wallet chooser** (every integrated wallet from the [showcase](../spec.md#53-wallet-showcase-wallets-and-walletsslug), with download instructions), scan the QR, review the consent screen — the Proof-of-Trust plus the issuer verdict ("✅ ACME Badge Service is an authorized issuer of ECS-Badge") — and receive the badge in your wallet.

> **Under the hood** — ACME holds an `ISSUER` participant entry on the ECS-Badge schema; issuance runs over OpenID4VCI (the wallet's bridge track); the wallet applies [UW-RES-2] + [UW-POT-2] from the [user-wallet guideline](../guidelines/user-wallet-integration.md). [TODO: confirm the ECS-Badge schema is available in the testnet ECS Ecosystem.]

### 2.3 Login with a verifiable credential (IAM)

ACME deploys a **login service for its IAM solution**: instead of passwords, it **requests presentation of the Badge credential**. Before sharing, the employee's wallet verifies that the verifier service is **trusted** (Q1) and **accredited to request presentation of ECS-Badge credentials** (Q3). The employee logs in with their badge.

*What you see:* the login service's DID, trust card, and source repository link.
*What you do:* open ACME's login page, scan the QR with the **same wallet holding your badge**, review the consent screen — the Proof-of-Trust plus the verifier verdict — share the badge, and land in the signed-in IAM session.

> **Under the hood** — a third vs-agent + DID + delegated ECS-Service; ACME holds a `VERIFIER` participant entry on the ECS-Badge schema; the request runs over OpenID4VP; the wallet applies [UW-RES-3] + [UW-POT-3]. A rogue verifier without the participant entry gets the red verdict — phishing for credentials fails structurally.

*What ACME now has:* the anchor plus three services — support, badge issuance, credential login — each with its own DID, each resolvable, each provably ACME's; employees holding badges they use to log in.

## 5. The story — Step 3: ACME gets certified (ISO 9001)

ACME joins the fictional **ISO Certification Ecosystem (demo)**: it selects an accredited **issuer of the ISO 9001 credential** from that ecosystem and executes the onboarding.

Here is the shortcut that shows the power of the model: **the issuer does not ask ACME to prove who it is again.** ACME simply presents the **ECS-Organization credential on its DID** — the KYB already done in Step 1 — and the issuer, after its certification checks, issues the **ISO 9001 credential directly to ACME's Organization DID**.

**Now, every time a user connects to any of ACME's services, or exchanges a credential with them, they see — in addition to the ECS-Org and ECS-Service — the ISO 9001 credential: the company is provably ISO 9001-certified, everywhere it acts.**

*What you see:* the onboarding with no document upload (identity carried by the ECS-Org presentation); the ISO 9001 credential on the Organization DID; the **enriched trust card** on the chatbot, the badge issuer, and the login service — same card as before, now with the ISO 9001 credential in the "Other credentials" block.

> **Under the hood** — a `HOLDER` onboarding on the ISO 9001 schema with the certification body as validator; identification by presenting ECS-Organization over the DIDComm session (**reusable organizational identity** — the ECS layer is the KYB other ecosystems build on); the credential is published as a Linked VP on the anchor DID. Because every ACME service's trust chain resolves through the anchor, org-level credentials surface on **all** of its services' Proof-of-Trust cards ([UW-POT] block 4).

*What ACME now has:* everything from Steps 1–2, plus a domain credential that travels with the organization across every service it operates.

## 6. The story — Step 4: ACME creates its own ecosystem

So far ACME has *joined* ecosystems others govern. But ACME has a trust problem of its own: **who is a genuine ACME partner?** Fake resellers and unauthorized repair shops trade on its name every day. So ACME creates the **ACME Partner Ecosystem** — and becomes a governance authority itself.

### 4.1 Design the partner program

ACME connects to the Verana frontend and **creates its ecosystem**: it publishes the partner program's **governance framework** (who qualifies, obligations, revocation rules) and defines one credential schema — **ACME Authorized Partner**. It configures the permissions deliberately: **issuance is governed** (only ACME can issue), **verification is open** (anyone — a customer's wallet, another business — can check a partner claim, no permission needed).

*What you see:* the new ecosystem entry in the live registry, its governance framework document, and the schema with its permission modes side by side — one governed, one open.

> **Under the hood** — the frontend creates an `Ecosystem` entry (with its governance-framework version and document) and a `CredentialSchema` for the partner credential; ACME creates the schema's root `ECOSYSTEM` participant entry and grants itself the `ISSUER` role. Permission modes are per-schema, per-role — the range from fully open to fully governed the [playground](../spec.md) demonstrates in Journey 1.

### 4.2 Onboard a partner

**Zenith Repairs (demo)**, an independent repair company, wants in. Zenith is already a Verana-verified organization — it went through its own Step 1 with its own anchor and ECS-Organization credential (the pattern replicates; that is the point). Zenith starts the onboarding with ACME; **ACME identifies Zenith by the ECS-Org credential on its DID** — no paperwork exchange — checks its partner criteria, and issues the **ACME Authorized Partner** credential to Zenith's DID. Zenith attaches it to its service.

*What you see:* Zenith's onboarding `PENDING → VALIDATED`; the partner credential landing on Zenith's DID; Zenith's enriched trust card.

> **Under the hood** — a `HOLDER` onboarding on the partner schema with ACME as validator (`MsgStartParticipantOP` → DIDComm evidence session → `MsgSetParticipantOPToValidated`); identification by ECS-Org presentation — the same reusable-KYB shortcut as Step 3, now with ACME on the *issuer* side of it. The credential is published as a Linked VP on Zenith's anchor.

### 4.3 Anyone can verify a partner claim

The payoff, in the visitor's own hands.

*What you do:* with the wallet from Step 2, connect to Zenith's service — the Proof-of-Trust shows Zenith's **ECS-Org + ECS-Service + ACME Authorized Partner** (issued by ACME Corp, chain verified). Then try **Umbra Corp (demo)**, which *claims* on its website to be an ACME partner — its card shows no such credential, and its claim fails verification: **the red verdict. Brand impersonation fails structurally.**

*What you see (discovery):* a live Trust Graph query — "services holding an ACME Authorized Partner credential" — returning exactly the genuine partners, with Zenith in the list.

> **Under the hood** — verification is open on this schema, so any wallet checks a partner claim without asking anyone's permission; only issuance is gated. Revocation works too: if ACME revokes Zenith's credential, re-resolution drops it from Zenith's card and from the query results.

*What ACME now has* — the full circle: a verified organization (Step 1) · verified services with badge-based login (Step 2) · an ISO 9001 certification that travels everywhere it acts (Step 3) · and now **its own governed trust ecosystem**, protecting its brand and its customers. Every step used the same primitives: DIDs, credential schemas, participant trees, trust resolution. What ACME consumed, ACME now provides.

## 7. Next steps — to be defined

Further steps, if any, to be defined.

## 8. Open items

1. Location of this playground: standalone section of the main playground site vs. its own page tree. [DECISION]
2. ~~Watch-only v1 vs. do-it-yourself mode~~ — **resolved (§2): hybrid** — watch-only for organization-side steps (with mandatory source-repo links), hands-on for end-user steps (Hologram App for chat; an integrated open-source user wallet for badge + login).
3. The ACME demo anchor and services: standing testnet services (kept `TRUSTED`, monitored like the [playground demo services](../spec.md#6-demo-environment-normative-for-the-playground-operators)) vs. artifacts replayed from recordings. Proposed: standing services, shared with the playground's demo cast. [DECISION]
4. **ECS-Badge schema** availability in the testnet ECS Ecosystem — blocks Steps 2.2/2.3. [TODO]
5. **Demo-cast unification** — this story uses the ISO Certification Ecosystem (demo) / ISO 9001 (matching the verana.io worked example); the [playground spec](../spec.md) demo environment uses the AI Assurance Ecosystem / ISO-42001-style credential (the award scenario). Decide: host both ecosystems in the shared demo environment, or unify on one. [DECISION]
6. Step 4 cast: **Zenith Repairs (demo)** as the onboarded partner; Umbra Corp doubles as the fake-partner claimant. [DECISION: confirm names — Zenith needs its own standing anchor in the demo environment.]
