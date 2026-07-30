# Verana Playground — Website Specification

**Status:** DRAFT 0.3 (shared demo cast) · 2026-07-30
**Site:** `https://playground.testnet.verana.network`
**Companions:** [verana-explained](./verana-explained/spec.md) · [user-wallet guideline](./guidelines/user-wallet-integration.md) · [cloud-wallet guideline](./guidelines/cloud-wallet-integration.md) · [shared reference](./README.md)

**Protocol version:** v4 is not fully published yet — the playground targets **v3**, which is what runs on testnet today. These documents keep v4 terminology where concepts are equivalent (v3 **Trust Registry** = v4 *Ecosystem*; v3 **Permission** = v4 *Participant*). Sources of truth for now: [Verifiable Trust spec v3](https://verana-labs.github.io/verifiable-trust-spec/index-v3.html) and [VPR spec v3](https://verana-labs.github.io/verifiable-trust-vpr-spec/index-v3.html); v4 drafts: [VT v4](https://verana-labs.github.io/verifiable-trust-spec/versions/v4/) · [VPR v4](https://verana-labs.github.io/verifiable-trust-vpr-spec/versions/v4/).

---

## 1. Purpose

One site, four sections, in this order:

1. **What is Verana** — a short explanation of the infrastructure and what you can do with it.
2. **Learn step by step** — cards linking into the [Verana Explained](./verana-explained/spec.md) story.
3. **User wallets** — the integrated user wallets, each with its own playground page (identical template: a service for issuing, a service for presenting, a download link) + *Add your wallet*.
4. **Cloud wallets** — the integrated cloud wallets, each with its own playground page (identical template: a use case to test) + *Add your wallet*.

Everything runs against the **Verana testnet** — real registry entries, real trust resolution, nothing simulated.

**Design principles (apply to every page):**

- **Clear and visual-oriented** — avoid heavy prose; prefer **diagrams, icons, cards, and live artifacts over text** whenever possible. Each section must communicate at a glance; paragraphs are the fallback, not the default.
- **"Alive" tutorial design language** — the [verana-demos playground](https://github.com/verana-labs/verana-demos) idiom, deliberately distinct from the verana.io website: light surfaces, a vibrant purple-blue **gradient hero** (`#764ba2 → #667eea`), **numbered violet section circles** (guided-tutorial rhythm), white cards with **pastel icon chips** (lucide icons), centered reading flow. The Verana logo mark is shared family DNA; the look is its own.
- **Light-first** — the tutorial personality is light; a night theme is optional future work, not a launch requirement. *(Supersedes the earlier night/light principle.)*

## 2. URL map

```
/                        Home: the four sections (§3)
/usecases/vesta(/…)      The Vesta use case: four chapter routes with a persistent stepper (more use cases later)
/user-wallets/<slug>     Per-user-wallet playground (template §4)
/cloud-wallets/<slug>    Per-cloud-wallet playground (template §5)
/integrate               Add your wallet: guidelines + integration.yaml PR + PoT UI kit
/about                   Who runs it, what is real vs (demo), legal, links
```

Persistent header: logo · What is Verana · **Use Cases submenu** (one entry per use case; currently Vesta Appliances → `/usecases/vesta`) · wallets anchors · network chip (`TESTNET · resolver OK`) · one CTA: **Add your wallet** → `/integrate`.

## 3. Home sections

### 3.1 What is Verana

A short, non-technical block (headline + a few sentences + link row). Content draft:

> **Verana is open, public trust infrastructure — the trust layer of the verifiable internet.**
> On Verana, **ecosystems** define credential schemas, accredit who may **issue** and who may **verify**, and publish their governance on a public registry. **Services and AI agents** become verifiable: identified by a DID, backed by credentials that prove *what they are* and *who operates them*. Anyone — a person's wallet, another service — **verifies first, then connects**: trust is resolved against the public registry and shown as a **Proof-of-Trust** before the first interaction. Credential offers and presentation requests are accepted only from **authorized** issuers and verifiers. And because trust is published, it becomes **discoverable**: find services by what they prove, not what they claim.
>
> **What you can do with it:** make your services and agents verifiable · issue and verify credentials under an ecosystem's governance · build your own trust ecosystem · integrate your wallet.

Link row: [verana.io](https://verana.io) · [docs.verana.io](https://docs.verana.io) · the two specs · `app.testnet.verana.network`.

### 3.2 Learn step by step (→ Verana Explained)

One card per **chapter** of the [Vesta use case](./verana-explained/spec.md), each linking to its chapter route (four routes with a persistent stepper):

| Card | Chapter | Route |
| --- | --- | --- |
| 1 | Meet Vesta Appliances | `/usecases/vesta` |
| 2 | The solution: become verifiable | `/usecases/vesta/solution` |
| 3 | Marc's journey | `/usecases/vesta/journey` |
| 4 | Run the demos | `/usecases/vesta/demos` |

The "Being found" Trust-Graph outlook is a closing teaser on the demos chapter (pending), not a card.

### 3.3 User wallets

- **The list**: one tile per integrated user wallet — logo · name · organization · track chip (native / bridge) · license chip · **Get it** (APK download; web link for a web wallet) · **Open its playground** → `/user-wallets/<slug>`.
- Closing card: **Add your wallet** → `/integrate`.

### 3.4 Cloud wallets

- **The list**: one tile per integrated cloud wallet — logo · name · organization · pattern chip (native / sidecar / bridge) · license chip · **Get it** (URL) · **Open its playground** → `/cloud-wallets/<slug>`.
- Closing card: **Add your wallet** → `/integrate`.

## 4. The user-wallet playground (identical template)

**Every user wallet gets exactly the same playground page** at `/user-wallets/<slug>`, generated from its `integration.yaml` ([README](./README.md#getting-listed-on-the-playground)). Uniformity is the point: **same logic, same services, same six scenarios** — only the wallet (and its captures) changes.

**The shared demo cast.** All user-wallet pages exercise the same standing services, run by the **Playground Organization (demo)** under the **Playground Ecosystem (demo)** and its single **DemoCredential** schema (§6 — the [Playground demo cast](#6-shared-machinery)). Each scenario isolates exactly one of the three questions of the [user-wallet guideline §1](./guidelines/user-wallet-integration.md#1-what-the-integration-does):

| Service (slug) | Trust state (Q1) | DemoCredential accreditation | Teaches |
| --- | --- | --- | --- |
| `demo-issuer-accredited` | TRUSTED | ISSUER | Q2 pass — accept the offer |
| `demo-issuer-unaccredited` | TRUSTED | none | Q2 fail — offer blocked |
| `demo-verifier-accredited` | TRUSTED | VERIFIER | Q3 pass — share the credential |
| `demo-verifier-unaccredited` | TRUSTED | none | Q3 fail — sharing blocked |
| `demo-untrusted` | UNTRUSTED | n/a | Q1 fail — no connection (used in **both** trios) |

Template sections:

1. **Breadcrumb** — `Playground › User wallets › <Wallet>`: each segment clickable (home, the §3.3 list anchor), so the main page is always one tap away.
2. **Header** — logo, name, organization, track/license chips, links: **Download** (APK for a mobile wallet, web link for a web wallet — the `download` field) · repo · demo video.
3. **What you'll test** — the intro that installs the mental model *before any QR*: the three questions a Verana-integrated wallet answers — **Q1** is this service trusted and who operates it (on connect) · **Q2** is it authorized to *issue* this credential (on offer) · **Q3** is it authorized to *verify* it (on presentation request) — rendered as three visual cards (guideline §1 table), plus one line naming the cast: every demo below is a service of the Playground Organization (demo), resolved live against the testnet.
4. **Get the wallet** — the visitor MUST be told to **download the modified APK by clicking the page's link** (the Verana-integrated build, configured for testnet): store builds may not carry the integration; store links MAY complement the APK link, never replace it (for a web wallet: the integrated instance URL).
5. **Issuer demos — three services, three verdicts.** One card per issuer scenario (`demo-issuer-accredited`, `demo-issuer-unaccredited`, `demo-untrusted`). Each card shows: state chips (TRUSTED/UNTRUSTED · accredited/not) · the **expected wallet behavior as a screen capture** (per-wallet, from `integration.yaml`; the generic verdict line per [UW-POT-2] is the fallback until captures are submitted) · a **"Show QR" button** that reveals the QR / deep link and lets the visitor execute the demo · for the trusted services, their live Proof-of-Trust. The accredited card ends with the payoff: the visitor now **holds a DemoCredential**.
6. **Verifier demos — three services, three verdicts.** Same trio shape for Q3 (`demo-verifier-accredited`, `demo-verifier-unaccredited`, `demo-untrusted`), presenting the DemoCredential received in section 5 — which is why the issuer trio comes first. The accredited card's payoff: logged in with a credential, no password, no account — the trust chain did the work.

> **v3 launch note:** the DemoCredential runs over **AnonCreds / DIDComm**; initially **Hologram Messaging** is the only user wallet completing the full loop. Other wallets' pages ship with the resolve/connect scenarios live and the credential scenarios marked *coming* — they activate per wallet when OpenID4VC lands or the wallet supports the AnonCreds flow.

## 5. The cloud-wallet playground (identical template)

**Every cloud wallet gets exactly the same playground page** at `/cloud-wallets/<slug>`, generated from its `integration.yaml`. The template is a **use case to test**: the cloud wallet hosts a demo Verifiable Service, and the visitor exercises it end to end.

> **Alignment note:** a future revision of this template reuses the **Playground Ecosystem (demo)** and its **DemoCredential** schema (§6) — the ecosystem is deliberately shared across playground sections; each hosted demo service gets its participant entries there instead of a per-wallet ecosystem.

1. **Breadcrumb** — `Playground › Cloud wallets › <Wallet>`: each segment clickable (home, the §3.4 list anchor), so the main page is always one tap away.
2. **Header** — logo, name, organization, pattern/license chips, links: **Get it** (URL of the hosted instance / product page) · repo · demo video.
3. **The hosted demo service** — a standing service run **by this cloud wallet**, Verana-verified: its DID and its live **Proof-of-Trust card** (TRUSTED · ECS-Org · ECS-Service · the demo credential), resolved on page load.
4. **The use case to test** — the same loop on every cloud-wallet page, run with **any integrated user wallet** (picker linking to the §4 pages):
   1. **Resolve** the hosted service — see the Proof-of-Trust.
   2. **Receive** a credential issued by the hosted service (it holds the ISSUER participant entry).
   3. **Present** it back to the hosted service's verifier endpoint (it holds the VERIFIER participant entry).
5. **Under the hood (expandable)** — the integration's pattern (native / sidecar / bridge), its credential-acquisition path ([CW-ECS-1]: out-of-band or `vt-flow`), and registry links (ecosystem, schema, participant entries). This completes the [CW-TEST] acceptance loop.

## 6. Shared machinery

| Piece | Definition |
| --- | --- |
| **Reference implementation** | [`verana-labs/verana-demos`](https://github.com/verana-labs/verana-demos) — the working v3 demo ecosystem the new [`verana-labs/playground`](https://github.com/verana-labs/playground) builds on: `organization-vs` (anchor: ECS credentials, own Trust Registry + schema + AnonCreds cred def), issuer/verifier chatbot & web VSs, the tutorial playground app (PoT, invitation and session-result APIs), numbered deploy workflows, and the vs-agent API automation (`common/common.sh`). |
| **Playground demo cast (§4/§5)** | The **Playground Organization (demo)** — a corporation on testnet, created for all demo services of the user-wallet and cloud-wallet playgrounds — controls the anchor VS **Playground Demo**, which owns the **Playground Ecosystem (demo)** and its single **DemoCredential** schema (AnonCreds cred def; minimal claims: `name`, `demoId`; issued instantly, no evidence step). Five standing services (each its own vs-agent instance): `demo-issuer-accredited` (ISSUER participant entry), `demo-verifier-accredited` (VERIFIER entry), `demo-issuer-unaccredited` and `demo-verifier-unaccredited` (TRUSTED VSs, no DemoCredential entries), and `demo-untrusted` (no ECS credentials — fails Q1; shared by both trios). The ecosystem is reusable by other playground sections. Monitored — a demo service in the wrong trust state is a paging incident, **including `demo-untrusted` resolving as anything but UNTRUSTED**. |
| **Story cast (Vesta)** | The [Vesta Appliances story cast](./verana-explained/spec.md): CertBody issuers, Vesta Appliances and its services, Umbra Repairs, Zenith Repairs — serves the `/usecases/vesta` chapters only (see the story spec's deployment inventory). **Each story participant runs its own dedicated vs-agent instance.** Standing services, monitored. |
| **Integration registry** | [`verana-labs/playground`](https://github.com/verana-labs/playground): `integrations/<slug>/integration.yaml` + logo, submitted by PR; CI validates; the site generates the §3.3/§3.4 lists and the §4/§5 pages from it. |
| **Sessions & fees** | Anonymous browser session only; chain transactions run from pooled playground accounts (faucet-refilled) — visitors never touch keys or VNA. |
| **Onboarding portal** | For cloud-wallet integrators: delivers ECS credentials per [CW-ECS-1]. [DECISION: in-app vs separate service] |
| **Stack** | Next.js (verana.io family: App Router, Tailwind, TypeScript); open source; light+dark; WCAG-AA; consent-gated analytics; no accounts/PII beyond the anonymous session. |

## 7. Out of scope (this revision)

ECS-UserAgent and Participant Sessions / trust fees (deferred in the guidelines) · mainnet anything · user accounts · ecosystem *management* UX (→ `app.testnet.verana.network`) · documentation (→ docs.verana.io) · marketing (→ verana.io).

## 8. Publication & award surface

The playground is the living evidence of the *"One trust layer, many wallets"* FIDES use case — see the [submission kit](./submission/README.md). During the award window, Home carries a discreet support banner → the FIDES use-case page; wallet tiles link their org's FIDES catalog entries when they exist. UNFOLD: the OID4VC-capable demo issuer/verifier get listed in the EUDIW Unfold marketplace. Listed integrations may use the "Runs on the Verana open trust layer" badge.

## 9. Milestones

| # | Milestone | Target |
| --- | --- | --- |
| M1 | Specs reviewed/approved | Jul 20 |
| M2 | Demo cast live (§6, TRUSTED, monitored) | Jul 25 |
| M3 | Site MVP: Home (§3) + ≥ 3 user-wallet playgrounds (Hologram, Paradym, Talao) + `/integrate` | Jul 27 |
| M4 | FIDES submission + catalog entries + campaign wave 1 | ~Jul 31 |
| M5 | Cloud-wallet playgrounds + remaining integrations + Verana Explained pages | Aug 7 |
| M6 | Award window ops (finalists Aug 24, voting → Sept 2, GDC Sept 1–3) | Sept |

## 10. Open items

1. ~~Demo-entity naming~~ — **resolved (rev 2026-07-28):** **Vesta Appliances** (protagonist, formerly Acme) / CertBody / **Umbra Repairs** / Zenith Repairs / "ISO Certification Ecosystem (demo)"; standing demo services to be rebranded from ACME to Vesta (see verana-explained open item 7).
2. ~~Testnet ECS Ecosystem DID~~ — **resolved:** the demo organization anchor from `verana-labs/verana-demos` (`organization-vs`); published in the [README config](./README.md#network-configuration-wl-whitelists).
3. ~~Demo credential issued to visitors~~ — **superseded (rev 2026-07-30):** the §4 pages issue the **DemoCredential** of the Playground Ecosystem (demo) (§6); AnonCreds/DIDComm for now, Hologram first; OID4VC/OID4VP when available. (ECS-Badge remains the story credential in `/usecases/vesta`.)
4. Onboarding portal placement (§6). [DECISION]
5. ~~Integration-registry repo~~ — **resolved:** [`verana-labs/playground`](https://github.com/verana-labs/playground) (created).
6. [UW-POT-2] hard-block vs warn — inherited from the user-wallet guideline.
7. Integrator support channel for `/integrate`. [TODO]
8. Playground demo cast display names — working proposal: **Accredited Issuer (demo)** · **Unaccredited Issuer (demo)** · **Accredited Verifier (demo)** · **Unaccredited Verifier (demo)** · **Untrusted Service (demo)**; anchor **Playground Demo**; confirm at provisioning time. [DECISION]
