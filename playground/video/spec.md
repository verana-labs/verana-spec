# Playground Use-Case Videos, Production Spec

**Status:** DRAFT 0.2 · 2026-08-20, shared intro locked in implementation; **Vesta act is the first video**; Verandia act drafted and deferred.
**Companions:** [playground spec](../spec.md) · [Vesta story spec](../verana-explained/spec.md) · [Verandia story spec](../utopia/spec.md) (Utopia was renamed Verandia) · [FIDES dossier: Verandia](../submission/use-case-verandia.md)

---

## 1. Purpose

**Implementation:** [`verana-labs/playground-videos`](https://github.com/verana-labs/playground-videos), a Remotion project whose shot data (`src/shots/`) mirrors the tables below; the shared intro, the acts, the outro, and the 9:16 recuts are compositions rendered from this spec.

One video per playground use case, all built from the same three-part template:

```
[ INTRO, shared, locked ]  →  [ handoff card ]  →  [ USE-CASE ACT ]  →  [ OUTRO, semi-shared ]
```

The intro explains what Verana is and why it matters, in 72 seconds, and is rendered **once** and reused verbatim in every video (Vesta, Verandia, Bolivia, MOSIP, ...). Only the act and the handoff card change per video. This spec locks the intro (§3), defines the first act, Vesta Appliances (§4), and keeps the drafted Verandia act for the second video (§5).

### Format decisions (defaults, flip here if changed)

| Decision | Value | Rationale |
| --- | --- | --- |
| Master format | 1920×1080, 16:9, 30 fps | YouTube, embeds, conference screens |
| Vertical cut | 9:16 recut of intro + act highlights (≤ 60 s) | X / LinkedIn / Shorts; see §8 |
| Narration | On-screen text + music. Script lines double as VO lines so a voiceover can be added later without re-editing | No language lock-in, cheaper iteration |
| Music | One continuous instrumental bed, calm-to-confident arc, ducked under wallet clips | |
| Branding | **Playground design language**: the playground lockup (bull-horn V, violet #7C3AED + emerald #10B981, wordmark "Verana" + violet "Playground"), the purple-blue gradient (#764ba2 to #667eea), light surfaces, white cards. Body text Inter; **brand wordmarks Space Grotesk**. The I-8 reveal carries the **verana.io lockup** (gradient tile + white V, "Verana" in black) | The video should look like the site it promotes |
| Playground banner | A "Verana Playground" banner (mark + wordmark, site-header white pill treatment) sits top-left from the **handoff card onward** (use-case content and outro, both formats; verticals from their payoff shot). The intro carries **verana.io branding only**, no banner | Playground branding on the use-case content; the shared intro stays brand-pure |
| Copy rules | **No em-dashes** and **no glyph symbols** (no ☑ ✕ ↗) in any on-screen text, same rule as rendered site copy. Words instead: "verified", "refused". Enforced at build time by the implementation | House rule |
| Honesty convention | Wallet and demo footage: real devices, live against the cast, silent, joined end to end, speed-ups disclosed in the video description. Same note style as the wallet `video.note` fields in the playground registry | Every claim reproducible |
| Fiction disclaimer | Lower-third on first act shot: "Vesta Appliances is a fictional company. Entities marked (demo) are fictional." (per-cast wording) | Same convention as the site's about page |

### Length budget

| Segment | Duration | Running total |
| --- | --- | --- |
| Intro (shared) | 1:12 | 1:12 |
| Handoff card | 0:05 | 1:17 |
| Act (Vesta) | 4:40 | 5:57 |
| Outro | 0:22 | 6:19 |

The Verandia act (deferred) keeps its 2:50 draft: its outro runs 4:07 to 4:29, total 4:29.

## 2. Series architecture and reuse rules

- **The intro is evergreen.** Nothing in it may age: no wallet counts, no dates, no roadmap, no "testnet", no partner names. Facts that age live in the act or the outro.
- **The intro is use-case-agnostic**, with one deliberate exception: I-10 closes on the real Vesta Appliances Proof of Trust as the canonical example (a stable artifact of the permanent demo cast) and the integrated personal-wallet logo roster (a roster change is an intro-version bump). Everything else never names a cast entity; wallet footage uses the generic DemoCredential six-scenario clips (already recorded, per wallet, in the playground repo), because those are story-neutral.
- **Versioning.** The rendered intro is tagged `INTRO v1`. Any change to its copy or footage bumps the version and §3 of this spec; older videos keep the version they shipped with.
- **The handoff card** is one full-frame title card per use case (5 s): use-case logo or emblem on the left, one line of text. It is the only bridge asset produced per video besides the act itself.
- **The outro** is shared except for one swappable element: the URL card (deep link to the use-case page). When mainnet replaces testnet, only the outro is re-rendered.

## 3. INTRO v1, shot by shot (0:00 to 1:12)

Pacing rule: every question shot (I-0 to I-6) holds **at least 3 seconds** with everything on screen (final text line included) before its cut.

Two movements: **the questions** (the viewer feels the gap) and **the answer** (Verana named and defined). Fast cuts, one line on screen at a time, music builds.

Q1, Q2, Q3 below refer to the trust-resolution questions the integrated wallets actually run: Q1 who is behind this service, Q2 is the issuer authorized, Q3 is the verifier authorized.

| # | Time | Visual | On-screen text (exact) | VO line (optional) |
| --- | --- | --- | --- | --- |
| I-0 | 0:00–0:06 | Cold open on the light stage: the **verana.io lockup** springs in; below it the kicker **[ OPEN · PUBLIC · NEUTRAL ]** (mono, letter-spaced) and the positioning line **The Open Trust Infrastructure for the Verifiable Internet**. The stage dims to night over the last second, a lights-out transition straight into I-1's question | (all copy in the visual) | Verana. The open trust infrastructure for the verifiable internet. |
| I-1 | 0:06–0:12 | (Each dark question shot, I-1 to I-7, dips to black at its cuts, one beat per question.) A realistic identity-verification form in a browser window: full name, date of birth, a passport-upload dropzone, a Continue button. And no way to tell who runs it: struck-out padlock in the URL bar, a "?" operator avatar, a scrambling "Operated by" line with an amber **identity unknown** tag, the window itself completely still (no jitter, no resize) while the unknown-identity cues gently pulse; on the second line, a **red pulsing organization icon** (same glow treatment as I-2's agent) appears below the card and **holds about three seconds** before the cut (no real branding) | Have you ever wondered... · who is really behind this service? | Have you ever wondered... who is really behind this service? The one asking for your name, your birth date, your passport? |
| I-2 | 0:12–0:19 | A chat with an AI agent, cursor blinking; the avatar carries a **robot icon** (clearly an agent, "online · AI agent"), the header an amber **identity unknown** badge, and the agent's identity flickers between three personas. Its typed reply: "Of course. First I just need your ID to feed my database." Once the reply lands, a **red pulsing AI-agent icon** (glowing, size-throbbing) appears below the card and **holds about three seconds** before the cut | And behind this AI agent? | And behind this AI agent? |
| I-3 | 0:19–0:25 | A credential-offer QR card first, centered ("Scan this QR to get your credential"; a real, scannable QR pinned to the personal-wallets page, changing its target bumps the intro version), then the QR travels **left** and the wallet clip arrives on the **right** (scenario `2-issuer-unaccredited`, phone in device frame); both stay on screen, and a **worried user** (face + drifting question marks) appears between them | And when you receive a credential... · is it real? Is the issuer accredited to issue it? | And when you receive a credential: is it real? Is the issuer even accredited to issue it? |
| I-4 | 0:25–0:31 | Mirrored: a presentation-request QR card first, centered ("Scan this QR to present your ID"), then the QR travels **right** and the wallet clip arrives on the **left** (scenario `5-verifier-unaccredited`, share blocked); both stay on screen, same worried user between them | And when a service asks for your ID... · is it even allowed to ask? | And when a service asks for your ID: is it even allowed to ask? |
| I-5 | 0:31–0:38 | Cut to a builder's view, drawn as objects: a **verifiable credential** card (real-looking frame, attribute values as unreadable bars, emerald seal; caption "attributes stay private") centered; with the second line it travels left and a **credential schema JSON** snippet (mono, PlumberCredential) plus a **symbolic pyramid of accredited issuers / verifiers** (gradient root on top, ticked circles below) appear beside it | And what if you want to build your own sovereign ecosystem... · where do you store your schemas? The list of accredited issuers and relying parties? | And what if you want to build your own sovereign ecosystem: where do you store your schemas, the list of accredited issuers and relying parties? |
| I-6 | 0:38–0:44 | A big **search lens** (gradient circle, magnifier, pulsing rings) over faint ecosystem nodes; two light up with green ticks: found, and joined | And finally... how do others find your ecosystem and join? | And finally: how do others find your ecosystem, and join? |
| I-7 | 0:44–0:48 | Hard cut to black. Beat in the music. | Today, most of us think we must stick to static trust lists, vendor lock-in, or silos. | Today, most of us think we must stick to static trust lists, vendor lock-in, or silos. |
| I-8 | 0:48–0:52 | The turn to daylight: the **verana.io lockup** alone (gradient tile + white V, "Verana" in black Space Grotesk) resolves centered on the light stage; the line sits in the lower third | But there is Verana. | But there is Verana. |
| I-9 | 0:52–1:00 | Continuous with I-8: the lockup **travels to the top** (pixel-continuous across the cut), and the three concept panels appear below it **one by one**, each carrying a numbered round bubble (1, 2, 3); once all three are shown, at least 5 seconds of reading time remain. One panel per concept, **visual-first** (mirroring the verana.io home "Verana, in three parts" section, drawn as diagrams instead of text): **Ecosystems** (a sovereign ecosystem tree: gradient root with sitemap glyph branching to governance (sealed document), schemas (fanned documents) and participants (three avatars, each with a green accreditation tick); mono tags only, closing "your rules · your business model"), **Verifiable Identity** (a violet shield, then service and operator tiles both getting green checks, a link drawing between them, the emerald TRUSTED pill, and the signature "Verify first. Then connect."), **Discovery** (the Trust Graph: a gradient query node with magnifier, edges lighting up to surrounding services, trusted ones marked with green ticks, "ranked by trust") | Ecosystems. Verifiable Identity. Discovery. · One open, public trust layer. | Build and/or join ecosystem trust registries, with their governance, schemas and accreditations. Verifiable identity for services and AI agents, with a Proof of Trust. And find services for what they prove. One open, public trust layer. |
| I-10 | 1:00–1:12 | The **verana.io lockup** (purple tile) and the standards strip (W3C DIDs, Verifiable Credentials, DIDComm, OpenID4VC, eIDAS 2 interoperable) sit at the **top**; then a **real Proof of Trust** animates in below and holds about 5 seconds: the playground's full TrustCard for **Vesta Appliances**, element for element (DID row with copy / open / close icons, Service and Operated-by checks, Verana-branded TRUSTED verdict with its registry note, the amber "Also presents: ISO 9001 (demo)" section with its verified line, and the three ISSUER accreditations: ECS-Service, ECS-Badge, Authorized Repairer); below the card, the logos of **every integrated personal wallet** appear one by one, captioned "integrated personal wallets". At 7.5 s the finale takes over: the line fades, the content shrinks away, the lockup travels to the center and grows, the closing URL appears: **https://verana.io**, and below it the closing tagline: **Build and join sovereign ecosystems on an open, public infrastructure, owned by no one.** | Attach credentials to your services. Prove you're accredited. Then let your users just verify they can trust you. | Attach credentials to your services. Prove you are accredited. Then let your users just verify they can trust you: a real Proof of Trust, resolved against the public registry, in any of the integrated wallets. Build and join sovereign ecosystems on an open, public infrastructure, owned by no one. |

**Locked-intro acceptance:** every question shot resolves in the act of at least one use case (I-1/I-4/Q3 by Verandia, I-3/Q2 by Vesta, I-5 by every builder chapter, I-6 by the directory teasers). The intro promises nothing the playground cannot show. Every visual inside the intro carries generic values only, never cast names.

## 4. The Vesta act, first video (1:17 to 5:57)

Distribution: each use-case video ships **standalone, without the intro** (the intro is its own video). It opens on a playground brand reveal (0:00 to 0:08): the **Verana Playground lockup** springs in center stage, travels to the top, and the use case is revealed below (emblem, title, subtitle); the act follows at 0:08, the outro closes it (Vesta standalone: 5:10 total). Each video carries its own music bed and narration track. The timecodes below are for the full assembly.

Pacing rule (whole act): on screen stay only the section kicker, the (large) section and subsection titles, and the imagery, diagrams and Proof-of-Trust panels; the narration is simplified and runs as lower-third voice-over lines, intro-style. The page's full copy informs the visuals and the VO, but is not displayed as paragraphs.

Source of truth: the [Vesta story spec](../verana-explained/spec.md) (cast: Vesta Appliances, Helvetia Trust Services, ISO Certification Ecosystem + NormaCert, the Vesta Repair Network with Vesta Iberia / Vesta Nordics and Zenith Repairs, and Umbra Repairs, the credentialed impostor) and the deployed `vesta-*` cast on testnet. Narrative arc mirrors the site chapters: problem, decision, build, payoff, refusal, discovery. The star scene is the refusal: **Umbra is verifiable but holds no Authorized Repairer credential; trust is not membership**, the Q2-family verdict from the missing credential.

Handoff card (1:12 to 1:17): Vesta logo left, text right:

> **Today: Vesta Appliances.**
> A brand fights impostors with proof.

| # | Time | Scene | Visual | On-screen text (exact) | VO line (optional) |
| --- | --- | --- | --- | --- | --- |
| S-1a | 1:17–1:28 | **The Company · The product line** | Playground journey §1: kicker "1 · The Company" and subheading "The product line" stay on screen with the **lineup photo** and its caption, center stage; the narration runs as lower-third voice-over lines, intro-style | Vesta Appliances: forty years of washing machines and ovens. · Machines that last, and get repaired, not replaced. | Vesta Appliances: forty years of washing machines and ovens. Machines that last, and get repaired, not replaced. |
| S-1b | 1:28–1:41 | **The Company · The factory** | Same layout: subheading "The factory", the **assembly-line photo** with its caption center stage, voice-over lines below | One plant, one assembly line, forty years of engineering. · Designed from the first screw to be serviceable in your kitchen. | One plant, one assembly line, forty years of engineering. Designed from the first screw to be serviceable in your kitchen. |
| S-1c | 1:41–1:57 | **The Company · The certified repair network** | The page's **hub-and-spokes diagram** center stage (Vesta logo hub, the eight named partners with cities and "Vesta Certified" pills, partner by partner), the stats chips and the emerald "Vesta Certified Repair Company badge" pill beneath; voice-over lines below (description only: the problems wait for S-2) | 120 independent repair companies, certified by Vesta. · Training, yearly audits, a signed partner contract. | 120 independent repair companies, certified by Vesta. Training, yearly audits, a signed partner contract. |
| S-1d | 1:57–2:11 | **The Company · Online services** | The page's **ownership chart** center stage: the Vesta card ("Vesta Appliances · owns & operates all three") connected down to the three service cards (Agentic Support, Employee badges, Staff & partner portal, each with icon and description); voice-over line below | Customers ask for help. Employees sign in. Partners order parts. | Customers ask for help. Employees sign in. Partners order parts. |
| S-2 | 2:11–2:23 | **The problems, and what they cost the brand** | Four red problem cards (titles only) beside the impostor-van photo | Fake support lines. Password pain. Paperwork, again and again. · And at the front door: fake authorized repairers. | Fake support lines. Password pain. Paperwork, again and again. And at the front door: fake authorized repairers. Nothing can be proven. |
| S-4 | 2:23–2:43 | **What Marc needs** | A small round photo of Marc beside the line "Marc, CTO of Vesta, will make the company verifiable.", then the five numbered cards, title + schema tag, one by one | (the five cards) | Marc, CTO of Vesta, will make the company verifiable. His list is short: verifiable identities for organizations. Verifiable identities for services. Credentials people can hold. Certifications as proof, not PDFs. And Vesta's own rules for its network. |
| S-5 | 2:43–3:01 | **The ecosystems Vesta wants to join** | The two HOLDER cards (Verana ECS, ISO Certification with the real ISO logo) | Vesta joins the Verana ECS Ecosystem: one KYB, provable everywhere. · And the ISO Certification Ecosystem: the paper certificate becomes proof. | Vesta picks the two it needs. The Verana ECS Ecosystem: one KYB, and Vesta is provable everywhere. And the ISO Certification Ecosystem: the paper certificate becomes proof. |
| S-6 | 3:01–3:17 | **The ecosystems Vesta wants to build** | The Vesta Repair Network hero card with the three governance tiles | Only Vesta can say who is an authorized Vesta repairer. · So Vesta builds its own ecosystem: governed issuance, open verification. | One need remains: only Vesta can say who is an authorized Vesta repairer. So Vesta builds its own ecosystem: the Vesta Repair Network. Issuance governed, verification open, and revocable. |
| J-1 | 3:17–3:31 | **Journey · Need 1 · 3.1 Marc deploys Vesta's Business Wallet** | Stage 3.1, Vesta selected, its Proof of Trust beside (UNTRUSTED note) | Marc deploys Vesta's Business Wallet: a DID is generated. · It proves nothing yet: the empty identity card. | (the lines) |
| J-2 | 3:31–3:47 | **Journey · Need 1 · 3.2 KYB with an accredited issuer** | Stage 3.2; selection on Helvetia Trust, then Vesta as the credential lands | Helvetia Trust runs the KYB, once, over DIDComm. · Vesta's wallet receives its Organization credential. | (the lines) |
| J-3 | 3:47–4:01 | **Journey · Need 2 · 3.3 The Service credential, self-issued** | Stage 3.3, Vesta selected: the Proof of Trust turns TRUSTED | Vesta self-issues its Service credential. · Valid: the same DID presents the proven organization. | (the lines) |
| J-4 | 4:01–4:15 | **Journey · Need 3 · 3.4 Vesta becomes an ECS-Badge issuer** | Stage 3.4; selection on Vesta, then an employee wallet | Vesta self-accredits as an ECS-Badge issuer. · Every employee gets a badge, in their own wallet. | (the lines) |
| J-5 | 4:15–4:33 | **Journey · Need 3 · 3.5 A verifiable login service** | Stage 3.5, the login service selected (VERIFIER on ECS-Badge) | A dedicated login service, verifiable in its own right. · Only badges from Vesta's trust anchor are accepted. · No passwords. The same badge opens the door. | (the lines) |
| J-6 | 4:33–4:49 | **Journey · Need 4 · 3.6 ISO 9001, without re-certifying** | Stage 3.6; selection on NormaCert, then Vesta with ISO 9001 presented | NormaCert recognizes Vesta's credential: no paperwork, no re-checks. · ISO 9001 becomes a verifiable credential. | (the lines) |
| J-7 | 4:49–5:07 | **Journey · Need 5 · 3.7 The Vesta Repair Network** | Stage 3.7; selection on the ecosystem, then Zenith Repairs | Vesta creates the Vesta Repair Network ecosystem. · Issuance governed. Verification open. · Zenith Repairs joins: an Authorized Repairer. | (the lines) |
| J-8 | 5:07–5:23 | **Journey · Need 5 · 3.8 Login, and at the front door** | Stage 3.8; selection on Zenith, then a technician wallet | Zenith badges its technicians. They log in to the Vesta portal. · And at the door: the Vesta Authorized Repairer seal. | (the lines) |
| J-9 | 5:23–5:39 | **Journey · Need 5 · 3.8 Unauthorized repair companies** | No diagram: the Umbra Proof of Trust, large, with the red refusal note | Umbra Repairs: verifiable, even trusted. · But no Authorized Repairer credential. Refused. | (the lines) |
| D-1 | 5:39–5:57 | **Run the demos** | Get a badge (Vesta / Zenith / Umbra), portal login, and the front-door photo | (the cards) | Try it yourself: get a badge from Vesta Appliances, Zenith Repairs, or even Umbra Repairs. Log in to the Vesta portal and see the result. And at the front door, scan the technician's badge: trust before you open. |

## 5. The Verandia act, second video, deferred (1:17 to 4:07)

Drafted and implemented (compositions exist); production waits until the Vesta video ships. `/usecases/verandia` is deployed (playground PR #192 merged), so its captures are unblocked whenever recording starts.

Handoff card: Verandia coat of arms left, text right:

> **Today: the Republic of Verandia.**
> A democracy deploys verifiable identity for citizens and businesses.

| # | Time | Scene | Visual | On-screen text (exact) | VO line (optional) |
| --- | --- | --- | --- | --- | --- |
| V-1 | 1:17–1:32 | **Meet Verandia** | `hero.webp` (the riverside capital), then `institutions.webp`; quick cuts: a password reset screen, a PDF company extract being edited, the fake tax-refund portal (`phishing.webp`) | A small democracy. Real institutions. · Passwords everywhere. Paper that anyone can edit. · And scammers who look exactly like the Republic. | Meet the Republic of Verandia. Real institutions, real services, and the same problem every country has: online, the Republic's word looks exactly like a scammer's word. |
| V-2 | 1:32–1:42 | **The decision** | PM portrait (`pm.webp`), then the Digital Minister (`minister.webp`) | "That has to change." · Five needs. One public trust layer. | The Prime Minister decides that has to change. The Digital Minister lists five needs, and builds them all on Verana. |
| V-3 | 1:42–2:17 | **The build** (chapter 3 compressed) | Entity build-up diagram turning verified in order: Business Registry, Civil Registry, Citizen ID ecosystem, Meridian Bank, Tax Buro, Legal Representation | The Business Registry becomes an accredited issuer. Company identity becomes a lookup, not paperwork. · The Civil Registry creates the Citizen ID ecosystem. Only it may issue. Relying parties must register to verify. · Banks and services prove who they are before you type anything. | The National Business Registry becomes an accredited issuer of Organization credentials, so proving a company is a lookup, not paperwork. The Civil Registry creates the Citizen ID ecosystem: it alone issues, and relying parties must register before wallets will share anything. Meridian Bank proves it is really your bank, before you type a password. |
| V-4 | 2:17–3:02 | **The payoff** (real screen captures) | a) Citizen ID lands in the wallet of choice · b) Tax Buro one-scan login · c) Meridian Bank KYC scan · d) Legal Representative corporate access | Your ID card, in the wallet you choose. · One scan to file your taxes. · KYC in one scan. · Sign for your company, provably, revocably. | Aria receives her Citizen ID in the wallet she chooses, any wallet from an open roster. One scan signs her in at the Tax Buro. One scan opens her account at Meridian Bank. Tomás presents his proof of legal representation and acts for his bakery, and the day it ends, it is revoked. |
| V-5 | 3:02–3:42 | **The refusal** (the star) | a) QuickCash Loans: verified organization, not authorized to request the Citizen ID; share refused · b) the fake refund portal fails trust resolution outright | QuickCash is a real, verified company. · But it never registered as a relying party. · The wallet refuses to share. Your data never leaves. · And the fake portal? It cannot even prove who it is. | Then QuickCash Loans asks for Aria's ID. QuickCash is real, verified, trustable. But it holds no verifier permission on the Citizen ID. Trust is not authorization: every compliant wallet refuses, and her data never leaves. The fake refund portal fails one step earlier: it cannot prove who it is at all. |
| V-6 | 3:42–4:07 | **Found, not maintained** | Directory type-on queries: all verified Verandian businesses · services accepting the Citizen ID · who represents Solaris Bakery (demo)? | Everything published here is public, resolvable, indexable. · A national service directory nobody maintains by hand. | And because everything the Republic published is public and resolvable, discovery comes for free: every verified business, every authorized service, every representative. A directory nobody maintains by hand. |

## 6. Outro (Vesta 5:57 to 6:19; Verandia, deferred, 4:07 to 4:29)

| # | Time | Visual | On-screen text (exact) |
| --- | --- | --- | --- |
| O-1 | 5:57–6:07 | Wallet roster strip (the integrated-wallet logos, the same strip as the playground home) sliding under the line | Try it yourself. Any of these wallets. Nothing simulated. |
| O-2 | 6:07–6:19 | The conclusion, the intro finale's shape in playground branding: the **Verana Playground lockup** (site typography and colors) springs to the center, the URL **https://playground.testnet.verana.network** below, then the line **See the other use cases in the Verana Playground.** | (all copy in the visual) |

Video description (not on screen) carries the honesty notes: real devices, live against the Verana testnet, silent captures, list of speed-ups, links to the story spec and repos.

## 7. Asset and capture inventory

Exists (playground repo, synced by the implementation's `npm run sync`):

| Asset | Where | Used in |
| --- | --- | --- |
| Vesta brand kit: logo, `lineup`, `factory`, `support`, impostor van, CEO / CTO portraits, ISO seal | `public/images/` (root) | S-1, S-2, handoff |
| Verandia brand kit: `hero`, `institutions`, `pm`, `minister`, `phishing`, `bank`, coat of arms | `public/images/verandia/` | V-1, V-2, handoff |
| Six-scenario wallet clips and screenshots (generic DemoCredential), per wallet | `public/wallets/<id>/clips/` | I-3, I-4 |
| Wallet logos (visible integrations) | `public/wallets/<id>/logo.*` | O-1 roster |
| Cast entity icons | `public/images/cast/*.svg` | optional diagram dressing |

To record for the **Vesta video** (real device, live against the `vesta-*` cast, one session):

1. `vesta-pot` — Proof of Trust on a Vesta service in a wallet (S-4a)
2. `vesta-badge-issuance` — employee badge lands in a wallet (S-4b)
3. `vesta-badge-login` — partner badge login on the portal (S-4c)
4. `vesta-door-scan` — technician badge scanned at the door, seal shown (S-4d)
5. `vesta-umbra-refusal` — the star capture: verified org, missing Authorized Repairer, refused (S-5a)
6. `vesta-umbra-door` — no credential, no seal (S-5b)

Prereq: the `vesta-*` cast agents live and the badge / login demos wired (Vesta story spec §5 inventory). Verandia's capture list (citizen-id-issuance, tax-login, bank-kyc, legal-rep, quickcash-refusal, fake-portal) is unblocked since PR #192 merged, and waits for the second video.

Also to produce: handoff and outro cards (from the brand kits, implemented), the music track (licensed for YouTube + X + LinkedIn), and screen recordings of the playground pages at 1080p+ where the acts show QR mint moments.

## 8. Vertical cut (≤ 60 s, per use case)

9:16 recut, phone footage full-bleed, text top third: I-1, I-4, I-7, I-8 (intro compressed to ~18 s) + one payoff capture (~15 s; Vesta: the door scan) + the refusal (~19 s; Vesta: Umbra) + O-2 (~8 s). No new footage required.

## 9. Reuse plan for the next acts

| Use case | Status | Handoff card line | Star scene |
| --- | --- | --- | --- |
| Vesta Appliances | **first video, this spec §4** | Today: Vesta Appliances. A brand fights impostors with proof. | Q2-family refusal: verified but uncertified impostor (Umbra) |
| Republic of Verandia | drafted, deferred, §5 | Today: the Republic of Verandia. A democracy deploys verifiable identity for citizens and businesses. | Q3 refusal (QuickCash) |
| Bolivia | future | Today: Bolivia. SEGIP, SEPREC and a bank on one trust layer. | Q3 refusal (Prestamista) |
| MOSIP Inji | future | Today: the MOSIP stack, trust-resolved. | full-triangle resolution |

The intro and outro are untouched in every case; production cost per new video is one handoff card + one act.

## 10. Open items

1. Confirm narration mode for v1 (text + music only, or record VO from the VO column).
2. Vesta captures (§7) blocked on the `vesta-*` cast demos being live end to end; record within one session so wallet UI versions match across shots.
3. V-3 / S-3 execution shipped as the implementation's build diagram; optionally upgrade to a screen-recorded site chapter 3 with its scene-graph for closer site parity.
4. S-6 / V-6 directory: mock the queries until the Trust Graph is queryable, disclose in the description, re-shoot live later.
5. Music selection and license; must allow YouTube + X + LinkedIn distribution.
6. Localization: master is English; the text-driven format makes subtitle tracks (ES, FR) cheap. Decide whether ES ships with v1 (Bolivia audience).
