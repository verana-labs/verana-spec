# Verana Playground — Wallet Conformance Testing

**Status:** DRAFT 0.2 · 2026-10-06
**Audience:** maintainers of the Verana playground and of the wallet forks it links, and anyone who needs to answer "does this wallet still work with our services?" without taking someone's word for it.
**Goal:** make the compatibility of every listed wallet **continuously provable**, so a listing is evidence rather than a memory of a demo that once worked.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14).

Normative background: the [personal-wallet integration guideline](./personal-wallet-integration.md) ([PW-CFG], [PW-RES], [PW-POT], [PW-TEST]) defines what a wallet MUST do; this document defines how we **verify** it. Shared endpoints, the demo cast and the v3↔v4 vocabulary mapping: [playground README](../README.md).

---

## 1. Why this exists

Every wallet failure found in the field so far was invisible from the code and from the page, and each was discovered by hand, late, by someone driving a phone. Three examples, all real:

- A wallet downloaded from an app store failed **every** demo with "Credential information could not be extracted", while the same wallet's Verana fork passed. The cause was in the issuer metadata, not the wallet: claim labels were published only under `credential_metadata`, and the OpenID4VCI library strips exactly that key when it derives the legacy `credentials_supported` array that older builds read.
- A published wallet build cannot pass at all: since its 2026.07 release the EUDI reference wallet enforces signed issuer metadata anchored in the EU trusted list, with no runtime toggle, so a demo issuer is refused before any credential is offered.
- 14 of 44 cast services carry a `did:webvh` log whose first entry was signed with a bare `did:key` verification method. A wallet that replays the log from version 1 rejects the DID **forever**; rolling the image forward does not repair history.

None of these needed a phone to detect. The point of this document is that they are caught by a script, on every change, and that what a device is still needed for is small, named, and stable.

## 2. Vocabulary

| Term | Meaning |
| --- | --- |
| **Build** | One installable artifact of a wallet: `store` (app store listing), `publisher` (APK published by the wallet's own project), `fork` (our Verana-integrated build), `browser` (web wallet, nothing to install). |
| **Profile** | The machine-readable description of a wallet: its rails, its builds, its quirks, its unlock recipe. The single source of truth every tier reads. |
| **Tier** | A class of verification: contract (§4), flow (§5), device (§6). |
| **Outcome** | `works`, `broken`, `incompatible-by-design`, `unknown`, or `not-testable` (§7). Never a bare pass/fail. |
| **Level** | What one build is proven to do on one network: `trust-screen`, `protocol`, or `incompatible` (§10). |
| **Evidence** | The result cells a level rests on (§12). |

## 3. The wallet profile [CONF-PROF]

- **[CONF-PROF-1]** Every listed wallet MUST have exactly one profile entry. All three tiers MUST read their wallet-specific behaviour from it; no tier may hard-code a package name, a coordinate, a PIN or a rail.
- **[CONF-PROF-2]** A profile MUST declare, per build: the build kind, how to obtain it (store URL, release URL, or hosted URL), the identity actually under test (package id and version for Android, commit or tag for a fork), and what that build **promises** to a user. A wallet MAY have several builds with different promises.
- **[CONF-PROF-3]** A profile MUST declare the credential rails the wallet claims (`anoncreds`, `openid4vc-sdjwt`) and, for OpenID4VP, which request rail it can read. The rails are mutually exclusive per request: a wallet that never implemented DCQL needs Presentation Exchange, one that resolves no DIDs needs an `x509_hash` client id. Handing a wallet the wrong rail produces a failure that looks like a wallet bug and is not one.
- **[CONF-PROF-4]** A profile MUST record known incompatibilities as facts with a cause and, where one exists, an upstream reference. An incompatibility recorded here is the input to the `incompatible-by-design` outcome (§7) and MUST NOT be reported as a regression.
- **[CONF-PROF-5]** A profile SHOULD record the operational quirks that otherwise cost hours: whether the wallet acts on a link only at cold start, whether it locks on backgrounding, how it is unlocked, and whether its screens can be read from the view tree at all.

## 4. Tier 1 — contract checks [CONF-T1]

Contract checks fetch exactly what a wallet fetches and assert it, without running a wallet. They are the cheapest tier and MUST run on every change.

- **[CONF-T1-1]** For every deployed service, issuer metadata MUST parse under **each OpenID4VCI draft a listed wallet speaks**, not only the newest. Parsing MUST use the wallets' own library schemas rather than a hand-written model.
- **[CONF-T1-2]** Credential display MUST be published in **both** shapes while any listed wallet reads the legacy one: `credential_metadata` for current drafts, and configuration-level `display` plus a claim-keyed `claims` object for drafts 11-13. A check MUST fail when either is absent.
- **[CONF-T1-3]** Authorization-server discovery MUST answer at the paths the fleet uses (`/.well-known/oauth-authorization-server`, and `/.well-known/openid-configuration` where a wallet insists on it).
- **[CONF-T1-4]** Offer links MUST carry a percent-encoded `credential_offer_uri` and a scheme the target wallet registers. A wallet that silently drops an unparseable link is indistinguishable from a wallet that is broken, so the link shape is asserted, not assumed.
- **[CONF-T1-5]** Every service DID MUST resolve, and its `did:webvh` log MUST be signed with a fully qualified verification method (`did:key:z…#z…`). A log that fails this MUST be reported as unrepairable-by-rolling, because a DID's history is immutable.
- **[CONF-T1-6]** Transport MUST be checked as a wallet experiences it: a real certificate, no cleartext, and a redirect whose headers fit in the ingress buffer. An invitation link that serves JSON correctly but returns 502 to a browser is a failure.
- **[CONF-T1-7]** Human-visible strings published by a service (connection labels, service names) MUST be checked for encoding damage, for example a value serialised as `map[…]` because an unquoted colon was parsed as a mapping.

## 5. Tier 2 — headless flows [CONF-T2]

Tier 2 runs the protocol with the libraries the wallets ship, and asserts the **inputs** on which a wallet's trust verdict depends.

- **[CONF-T2-1]** For each rail a wallet claims, the suite MUST complete the flow end to end against the demo cast: offer resolved, token obtained, credential issued and stored; request resolved, presentation submitted and accepted.
- **[CONF-T2-2]** The suite MUST assert the resolver answer that [PW-RES] requires the wallet to act on, by field: `trustStatus`, `production`, `evaluatedAt`, `expiresAt`, `credentials`, `dereferenceErrors`, `failedCredentials`. A wallet cannot render a correct verdict from a wrong answer, so the answer is verified first. On a v4 network, which has no resolver, the same inputs come from the indexer: its resolve answer (`trusted`, `evaluatedAtTime`, `expiresAtTime`, the ECS credentials, `unresolvableCredentialIds`) for Q1, and an `ACTIVE` participant with the `ISSUER` or `VERIFIER` role on the offered schema for Q2 or Q3.
- **[CONF-T2-3]** Q2 and Q3 MUST be asserted per scenario: an accredited issuer authorises the offered schema, an unaccredited one does not, and an untrusted service resolves `UNTRUSTED`. These map one-to-one onto the six [PW-TEST] scenarios.
- **[CONF-T2-4]** Policies that a published build enforces MUST be encoded as assertions, so their effect is proven rather than assumed: signed issuer metadata, certificate-chain trust anchoring, and refusal of DID methods the build cannot resolve.
- **[CONF-T2-5]** A flow check MUST read its verdict from the service's recorded exchange state, never only from the client's belief. Where the two disagree, the disagreement is the finding.

## 6. Tier 3 — device spot-checks [CONF-T3]

Tier 3 exists only for what no simulator can prove: that a human sees the truth.

- **[CONF-T3-1]** The device tier MUST verify, per listed build, the scenarios its level requires (§11): for a `trust-screen` build, that the Proof-of-Trust renders per [PW-POT] and that a failed Q2 or Q3 **blocks** the accept or share control per [PW-POT-2] and [PW-POT-3]; for a `protocol` build, that the accredited scenarios complete. Rendering, gating and completion on a device are the only claims this tier owns.
- **[CONF-T3-2]** The device tier MUST run the build a user installs (its APK, its store install, or its hosted wallet) against deployed services, on an emulator or a real device. It SHOULD run on a schedule rather than per change, and its scope SHOULD stay small enough to finish within one overnight window.
- **[CONF-T3-3]** Screen evidence MUST be captured for every device run and retained with the verdict, so a disputed result is settled by looking rather than by re-running.
- **[CONF-T3-4]** Where a wallet's view tree cannot be read (single-view renderers), the screen MUST be read by OCR from a screenshot. A tier that cannot read a screen MUST report "unknown", and MUST NOT infer a verdict from an earlier screen: grading a wallet by a stale capture produces a confident wrong answer, which is worse than no answer.

## 7. Outcomes and reporting [CONF-OUT]

- **[CONF-OUT-1]** Every wallet × build × scenario cell MUST carry one of five outcomes: `works`, `broken`, `incompatible-by-design`, `unknown`, or `not-testable`. `incompatible-by-design` MUST carry its cause and reference, and MUST NOT be counted as a failure. `unknown` means the check could not read what it needed; it MUST say why and MUST NOT be read as `works`. `not-testable` means the network, build or scenario cannot be exercised yet, and MUST say why. Only `works` is evidence.
- **[CONF-OUT-2]** A report MUST name the exact identity of what was tested: build kind, package and version or commit, the service, the vs-agent image version behind it, and the network. A result that cannot name its inputs is not evidence.
- **[CONF-OUT-3]** Results MUST be machine-readable and diffable, so a regression is a change between runs rather than an impression.
- **[CONF-OUT-4]** The public listing of a wallet MUST reflect what is proven for the build a user can actually install, and MUST distinguish a proven store build from a proven fork. Claiming compatibility a user cannot obtain is a defect of the listing.

## 8. Networks and versions [CONF-NET]

- **[CONF-NET-1]** Network endpoints (resolver, indexer, chain) and the target vs-agent version MUST be inputs to every tier, never constants. A check that cannot be pointed at another network cannot survive the v3→v4 migration.
- **[CONF-NET-2]** Assertions that name registry vocabulary MUST be expressed so that the v3↔v4 rename (Trust Registry → Ecosystem, Permission → Participant) is a configuration change, not a rewrite.
- **[CONF-NET-3]** A network is testable when it exposes its trust backend **and** a playground with deployed demo services. The trust backend is the resolver on a v3 network and the indexer on a v4 network, which answers Q1 itself (`POST /v4/verifiable-trust/resolve`) and Q2 and Q3 from its participants. As of this draft both qualify: testnet v3 resolves through `resolver.testnet.verana.network`, and devnet v4 runs the demo cast on vs-agent v2 and resolves through `idx.devnet.verana.network`, with no resolver service. The suite MUST run every network that qualifies, only on the casts it has deployed (devnet: `demo`), and MUST report the others as not yet testable rather than silently skipping them.

## 9. Hazards the checks MUST encode [CONF-OPS]

These have each cost a day and MUST NOT be rediscovered by hand.

- **[CONF-OPS-1]** The resolver caches a negative verdict for up to an hour. A check that reads trust state after a deployment MUST refresh before asserting, and MUST NOT conclude from a reading taken during a roll.
- **[CONF-OPS-2]** A green workflow is not a deployment. A check MUST verify the version actually serving, not the conclusion of the run that was supposed to deploy it.
- **[CONF-OPS-3]** Cast services drift apart in version. A failure MUST be attributed against the version a service is really running before it is attributed to a wallet.
- **[CONF-OPS-4]** Cast deployments share one concurrency group and only one queued run survives per group, so rolls MUST be issued one at a time. Parallel dispatches report as cancelled and leave services on the old version.

## 10. Compatibility levels [CONF-LVL]

Compatibility belongs to one build on one network, never to a wallet. One wallet ships builds that behave differently, and one build can pass on one network and fail on the next: the Hologram store build renders the trust screen, yet it cannot open devnet's DIDComm v2-only invitations.

- **[CONF-LVL-1]** Every listed build MUST hold exactly one level on each testable network it targets, on every rail it claims, derived from its evidence (§12) and never from what its vendor says:
  - **(a) `trust-screen`**: the build renders the Q1 verdict and the Q2 or Q3 authorization per [PW-POT], and gates the accept or share control on them, in all six demo scenarios (§11).
  - **(b) `protocol`**: the build completes issuance and presentation with the accredited services (`issue-accredited` and `present-accredited`) but does not meet (a), typically because it has no Verana trust screen and checks nothing against the registry. It cannot be relied on to refuse the unaccredited or untrusted services.
  - **(c) `incompatible`**: the build does not complete the accredited scenarios, by design ([CONF-PROF-4]) or not.
- **[CONF-LVL-2]** A partial trust screen is not a level. A build that shows Q1 without Q2 or Q3, shows them without gating, or gates only some of the six scenarios holds `protocol` when it meets (b), and `incompatible` otherwise.
- **[CONF-LVL-3]** The profile MUST declare the level each listed build claims on each network it targets, and the listing MUST agree with the profile. CI MUST derive the level the evidence supports and MUST fail when a claim is higher.
- **[CONF-LVL-4]** The listing of a network MUST show each build by its level there:
  - `trust-screen`: as a Verana build, before every other build;
  - `protocol`: after every `trust-screen` build, labelled as completing the demos without checking the registry. Its captures MUST NOT present a refusal scenario as a refusal;
  - `incompatible`: never as an install link. It MAY be named in a "tested, not compatible" note with its build identity, the date and the cause.

Levels on devnet v4 from the device runs of early October 2026 (informative; the latest run is authoritative):

| Build | Level | Why |
| --- | --- | --- |
| EUDI, swiyu and Inji (`v4-develop`) Verana forks, hosted wwWallet fork | `trust-screen` | issue and present with the accredited services, refuse the unaccredited and untrusted ones |
| Lissi, Paradym and Procivis One store builds | `protocol` | issue and present, check nothing against the registry |
| Hologram Messaging store build | `incompatible` | has the trust screen, but cannot open devnet's DIDComm v2-only invitations |
| Altme and Talao store builds | `incompatible` | the offer is ignored |
| swiyu store build | `incompatible` | "Invalid credential": it accepts only issuers on the Swiss trust infrastructure |
| BC Wallet | `incompatible` | cannot open devnet's DIDComm v2-only invitations |

## 11. The six demo scenarios [CONF-SCN]

The canonical scenarios are the six of [PW-TEST], run against the demo cast of the network. Each has one id, used in `scenarios.yaml`, in the listing captures and in every result cell.

- **[CONF-SCN-1]** The scenarios, the service each runs against, and the trust answer it exercises:

  | Id | Service, OpenID4VC rail | Service, DIDComm rail | Q1 | Q2 or Q3 |
  | --- | --- | --- | --- | --- |
  | `issue-accredited` | `demo-issuer-accredited` | `demo-issuer-accredited` | `TRUSTED` | authorized issuer |
  | `issue-unaccredited` | `demo-issuer-unaccredited` | `demo-issuer-unaccredited` | `TRUSTED` | not authorized |
  | `issue-untrusted` | `demo-issuer-untrusted` | `demo-untrusted` | `UNTRUSTED` | n/a |
  | `present-accredited` | `demo-verifier-accredited` | `demo-verifier-accredited` | `TRUSTED` | authorized verifier |
  | `present-unaccredited` | `demo-verifier-unaccredited` | `demo-verifier-unaccredited` | `TRUSTED` | not authorized |
  | `present-untrusted` | `demo-verifier-untrusted` | `demo-untrusted` | `UNTRUSTED` | n/a |

  The presentation scenarios present the DemoCredential received in `issue-accredited`. On a v4 network, authorized means an `ACTIVE` participant with the `ISSUER` or `VERIFIER` role on the DemoCredential schema of the Playground Ecosystem.
- **[CONF-SCN-2]** The expected verdict per level. A scenario completes when the service's exchange state reaches `done` for an issuance or `verified` for a presentation ([CONF-T2-5]), and is refused when it never gets there:

  | Id | `trust-screen` | `protocol` |
  | --- | --- | --- |
  | `issue-accredited` | `TRUSTED`, Q2 pass, accept enabled; completes | completes |
  | `issue-unaccredited` | `TRUSTED`, Q2 fail, accept disabled or absent; refused | recorded, not graded |
  | `issue-untrusted` | `UNTRUSTED` with its failure reasons, no accept; refused | recorded, not graded |
  | `present-accredited` | `TRUSTED`, Q3 pass, share enabled; completes | completes |
  | `present-unaccredited` | `TRUSTED`, Q3 fail, share disabled or absent; refused | recorded, not graded |
  | `present-untrusted` | `UNTRUSTED` with its failure reasons, no share; refused | recorded, not graded |

- **[CONF-SCN-3]** For a `trust-screen` build the negative scenarios are the point. A refusal scenario is `works` only when the screen shows the failed verdict, the control is disabled, absent or behind the explicit unsafe step of [PW-POT-2], **and** the service never completes. A build that completes a refusal scenario, or leaves its accept or share control enabled there, is `broken` whatever it rendered; so is a build that blocks an accredited scenario.
- **[CONF-SCN-4]** For a `protocol` build the refusal scenarios MAY run. Their outcome is recorded with the build and MUST NOT count for or against its level.

## 12. Evidence per level [CONF-EVD]

A level holds only while every cell it requires is `works` in the latest run that read that cell; a run that ends the cell `unknown` or `not-testable` did not read it, and leaves the earlier outcome standing (§13). Network-wide cells are prerequisites and are judged by the gate; build cells are the level's own evidence and are judged by their outcome.

- **[CONF-EVD-1] Service prerequisites.** Every tier 1 cell of the network and of the demo cast services (`network-testable`, `serving-version`, `did-resolves`, `webvh-log-signed`, `tls-certificate`, `no-cleartext`, `short-link-browser`, `metadata-parses`, `metadata-both-shapes`, `as-discovery:*`, `link:*`, `strings:*`) MUST pass the gate. A failing prerequisite blocks admission and re-validation on that network and demotes no build, because it is the service's failure ([CONF-OPS-3]).
- **[CONF-EVD-2] Reference holder.** On the OpenID4VC rail, every `reference-holder` and `reference-holder-*` cell of the DemoCredential on the network MUST pass the gate, with eudi-dev in strict mode. `reference-holder-haip` is required only for a build whose profile declares that it enforces HAIP, and is informative for every other build. These cells are prerequisites of the network too, not evidence about a build.
- **[CONF-EVD-3] Headless flow.** The tier 2 `flow` cells of the build, run on its own request shape ([CONF-PROF-3]), MUST be `works`: `issue-accredited` and `present-accredited` for `protocol`, all six for `trust-screen`, so the trust inputs of every refusal are proven before a screen is judged. Until tier 2 covers a rail (DIDComm today), a build on that rail rests on its device evidence alone, and its listing MUST say so.
- **[CONF-EVD-4] Device run.** The scenarios the level requires (§11) MUST be `works` on the build a user installs, from either source:
  - tier 3: the `consent-flow` cells of the build on the network;
  - a recorded real-device run, committed as cells in the tier 3 format and marked as recorded by hand. It MUST name the date; the build identity (package and version for a store build; package, version and tag or commit for a fork; URL and deployed commit for a hosted wallet); the platform, OS version and device model; the network and the vs-agent version each scenario service was serving; and, per scenario, the outcome, the service's exchange state and a capture of the consent screen. A run that cannot name all of these is not evidence.
- **[CONF-EVD-5] Rendering.** For `trust-screen`, the device evidence of each scenario MUST show the status band and, where consent is reached, the Q2 or Q3 sentence of [PW-POT-2] or [PW-POT-3]. Where the device tier reads the control but not the verdict, the rendering rests on the captures, and a reviewer MUST check them before the build is admitted.
- **[CONF-EVD-6] Platforms.** Evidence covers the platform it ran on and no other. A declared platform with no evidence MUST be listed as presumptive ([CONF-LIST-4]). As of this draft, iOS is presumptive for every build.
- **[CONF-EVD-7] No evidence, no level.** `incompatible` needs a cause, not a full run: one `incompatible-by-design` or `broken` cell on an accredited scenario, with its cause, is enough. A build with no evidence holds no level and is not listed.

## 13. Re-validation and demotion [CONF-REV]

Evidence is tied to a build identity and to the service versions it ran against. When either moves, the evidence goes stale, and CI has to notice before a user does.

- **[CONF-REV-1] Schedule.** Tier 1 and tier 2 MUST run nightly on every testable network, and on every change to a profile, the listing, the scenarios, the networks or the checks. Tier 3 SHOULD run nightly on every listed build it can install.
- **[CONF-REV-2] Service change.** When a demo service starts serving another vs-agent image (as `serving-version` reads it, [CONF-OPS-2]), tier 1 and tier 2 MUST run on that network against the new image, and device evidence recorded against the previous image becomes stale.
- **[CONF-REV-3] Build change.** A new fork tag or commit, a new store version, or a new deployment of a hosted wallet is a new build identity, and its device evidence starts empty. The profile MUST pin the new identity. A store version published without us, the usual case, MUST be detected by CI and handled the same way.
- **[CONF-REV-4] Stale evidence.** A build whose device evidence is stale keeps its level, marked unverified ([CONF-LIST-2]), until tier 3 or a new recorded run covers it. A build still unverified 30 days later MUST come off the listing until it is covered, its profile entry kept ([CONF-LIST-3]).
- **[CONF-REV-5] Known issues.** A known-issue entry MUST name the cells it covers, its cause, and an expiry at most 30 days after it was added or last renewed; an entry for a wallet-side failure MUST also name the wallet and the build. Renewing an entry is a reviewed change, like adding one. After expiry its cells fail the gate again, and an entry that matched nothing in a run of its tier and network MUST be removed.
- **[CONF-REV-6] Known issues hold the gate, not the level.** A known issue keeps the gate green. It never keeps a level: the level of every build is derived again from the outcomes of its own cells (§12) after every run, whether or not a known issue covers them.
- **[CONF-REV-7] Demotion.** When a cell a build's level requires (§12) turns `broken`, the build drops at once to the highest level whose required cells are all still `works`: a refusal scenario that stops blocking moves a `trust-screen` build to `protocol`, and a failed accredited scenario moves any build to `incompatible`. `unknown` neither demotes nor refreshes. The demotion MUST reach the listing with the next deployment of the playground, and a demoted build regains a level only with the complete evidence of that level, not by passing again the one cell that failed.

## 14. Listing policy [CONF-LIST]

- **[CONF-LIST-1]** A build MAY be listed on a network when it holds `trust-screen` or `protocol` there (§10). A wallet is listed when at least one of its builds is.
- **[CONF-LIST-2]** A listing MUST state, per build, its level, the build identity that was proven and the date of that evidence, and MUST mark the build unverified while its evidence is stale ([CONF-REV-2], [CONF-REV-3]).
- **[CONF-LIST-3]** A wallet whose maintenance is paused SHOULD be hidden rather than deleted: hiding keeps the evidence and the entry, and makes re-listing a one-line change.
- **[CONF-LIST-4]** Where a wallet ships on more than one platform from a single codebase, a proven build on one platform MAY be recorded as presumptive for the other, and MUST be labelled as presumption rather than evidence.
- **[CONF-LIST-5]** Every install link of a listing MUST be the `obtain` of a listed build of the wallet's profile, on the platform of the link, and every listed build MUST have its link, so a listing cannot point at a build nobody tested.

## 15. Admitting a wallet [CONF-ADM]

A new wallet, or a new build of a listed one, is admitted by a pull request to [`verana-labs/playground`](https://github.com/verana-labs/playground). CI decides; a reviewer checks only what CI cannot read yet ([CONF-EVD-5]).

- **[CONF-ADM-1]** The pull request MUST contain:
  1. the profile `conformance/profiles/<id>.yaml` per §3: the rails and request shape, and per build its kind, `obtain`, identity, platforms, presumptive platforms, networks, promises, policies, recorded incompatibilities, and the level it claims on each network ([CONF-LVL-3]);
  2. every build identity pinned: a fork to a tag or a commit, never a branch; a store build to its package and the version tested; a hosted build to its URL, repository and deployed commit;
  3. for an Android build with a direct APK, its signing certificate digest (`signerSha256`) and the `device` steps that onboard it and reach its scanner, so tier 3 can drive it;
  4. the entry in `personal-wallets.yaml`, whose links match the listed builds one to one ([CONF-LIST-5]) and whose trust-screen flag matches each build's claimed level;
  5. the device evidence of [CONF-EVD-4] for every listed build and network, unless tier 3 produces it in the same CI run.
- **[CONF-ADM-2]** The pull request MUST NOT merge unless CI shows that the profile and the listing validate, that the gate is green on every network the builds target, and that the evidence supports the level every listed build claims.
- **[CONF-ADM-3]** A wallet tested and found `incompatible` SHOULD still get a profile with its builds and their recorded incompatibilities, unlisted, so the next attempt starts from the facts instead of a new device session.

## 16. References

- [Personal wallet integration guideline](./personal-wallet-integration.md) — [PW-CFG], [PW-RES], [PW-POT], [PW-TEST]
- [Business wallet integration guideline](./business-wallet-integration.md)
- [Playground README](../README.md) — demo cast, endpoints, v3↔v4 mapping
- Trust Resolver API — `https://resolver.testnet.verana.network/docs`
- Indexer v4 API — `https://idx.devnet.verana.network/openapi.json`
- Conformance harness — [`conformance/`](https://github.com/verana-labs/playground/tree/main/conformance) in the playground repo: `scenarios.yaml`, `networks.yaml`, `known-issues.yaml`, the profiles and the gate
- [eudi-dev](https://github.com/dominikschlosser/eudi-dev) — the reference holder of [CONF-EVD-2]
- OpenID4VCI drafts 11 through current, and the wallet libraries that implement them
