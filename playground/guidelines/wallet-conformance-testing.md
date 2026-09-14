# Verana Playground — Wallet Conformance Testing

**Status:** DRAFT 0.1 · 2026-09-14
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
| **Outcome** | `works`, `broken`, or `incompatible-by-design` (§7). Never a bare pass/fail. |

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
- **[CONF-T2-2]** The suite MUST assert the resolver answer that [PW-RES] requires the wallet to act on, by field: `trustStatus`, `production`, `evaluatedAt`, `expiresAt`, `credentials`, `dereferenceErrors`, `failedCredentials`. A wallet cannot render a correct verdict from a wrong answer, so the answer is verified first.
- **[CONF-T2-3]** Q2 and Q3 MUST be asserted per scenario: an accredited issuer authorises the offered schema, an unaccredited one does not, and an untrusted service resolves `UNTRUSTED`. These map one-to-one onto the six [PW-TEST] scenarios.
- **[CONF-T2-4]** Policies that a published build enforces MUST be encoded as assertions, so their effect is proven rather than assumed: signed issuer metadata, certificate-chain trust anchoring, and refusal of DID methods the build cannot resolve.
- **[CONF-T2-5]** A flow check MUST read its verdict from the service's recorded exchange state, never only from the client's belief. Where the two disagree, the disagreement is the finding.

## 6. Tier 3 — device spot-checks [CONF-T3]

Tier 3 exists only for what no simulator can prove: that a human sees the truth.

- **[CONF-T3-1]** The device tier MUST verify, per listed wallet, that the Proof-of-Trust renders per [PW-POT] and that a failed Q2 or Q3 **blocks** the accept or share control per [PW-POT-2] and [PW-POT-3]. Rendering and gating are the only claims this tier owns.
- **[CONF-T3-2]** The device tier MUST run on a real device against deployed services. It SHOULD run on a schedule rather than per change, and its scope SHOULD stay small enough to finish within one overnight window.
- **[CONF-T3-3]** Screen evidence MUST be captured for every device run and retained with the verdict, so a disputed result is settled by looking rather than by re-running.
- **[CONF-T3-4]** Where a wallet's view tree cannot be read (single-view renderers), the screen MUST be read by OCR from a screenshot. A tier that cannot read a screen MUST report "unknown", and MUST NOT infer a verdict from an earlier screen: grading a wallet by a stale capture produces a confident wrong answer, which is worse than no answer.

## 7. Outcomes and reporting [CONF-OUT]

- **[CONF-OUT-1]** Every wallet × build × scenario cell MUST carry one of three outcomes: `works`, `broken`, or `incompatible-by-design`. The third MUST carry its cause and reference, and MUST NOT be counted as a failure.
- **[CONF-OUT-2]** A report MUST name the exact identity of what was tested: build kind, package and version or commit, the service, the vs-agent image version behind it, and the network. A result that cannot name its inputs is not evidence.
- **[CONF-OUT-3]** Results MUST be machine-readable and diffable, so a regression is a change between runs rather than an impression.
- **[CONF-OUT-4]** The public listing of a wallet MUST reflect what is proven for the build a user can actually install, and MUST distinguish a proven store build from a proven fork. Claiming compatibility a user cannot obtain is a defect of the listing.

## 8. Networks and versions [CONF-NET]

- **[CONF-NET-1]** Network endpoints (resolver, indexer, chain) and the target vs-agent version MUST be inputs to every tier, never constants. A check that cannot be pointed at another network cannot survive the v3→v4 migration.
- **[CONF-NET-2]** Assertions that name registry vocabulary MUST be expressed so that the v3↔v4 rename (Trust Registry → Ecosystem, Permission → Participant) is a configuration change, not a rewrite.
- **[CONF-NET-3]** A network is testable when it exposes a resolver **and** deployed cast services. As of this draft, testnet v3 qualifies and devnet v4 does not: devnet serves an indexer only. The suite MUST run every network that qualifies and MUST report the others as not yet testable rather than silently skipping them.

## 9. Hazards the checks MUST encode [CONF-OPS]

These have each cost a day and MUST NOT be rediscovered by hand.

- **[CONF-OPS-1]** The resolver caches a negative verdict for up to an hour. A check that reads trust state after a deployment MUST refresh before asserting, and MUST NOT conclude from a reading taken during a roll.
- **[CONF-OPS-2]** A green workflow is not a deployment. A check MUST verify the version actually serving, not the conclusion of the run that was supposed to deploy it.
- **[CONF-OPS-3]** Cast services drift apart in version. A failure MUST be attributed against the version a service is really running before it is attributed to a wallet.
- **[CONF-OPS-4]** Cast deployments share one concurrency group and only one queued run survives per group, so rolls MUST be issued one at a time. Parallel dispatches report as cancelled and leave services on the old version.

## 10. Listing policy [CONF-LIST]

- **[CONF-LIST-1]** A wallet MAY be listed when at least one of its builds reaches `works` on the canonical six [PW-TEST] scenarios for every rail it claims.
- **[CONF-LIST-2]** A listing MUST state which build was proven and when, and MUST be marked unverified when its evidence is older than the current vs-agent version on the cast it was proven against.
- **[CONF-LIST-3]** A wallet whose maintenance is paused SHOULD be hidden rather than deleted: hiding keeps the evidence and the entry, and makes re-listing a one-line change.
- **[CONF-LIST-4]** Where a wallet ships on more than one platform from a single codebase, a proven build on one platform MAY be recorded as presumptive for the other, and MUST be labelled as presumption rather than evidence.

## 11. References

- [Personal wallet integration guideline](./personal-wallet-integration.md) — [PW-CFG], [PW-RES], [PW-POT], [PW-TEST]
- [Business wallet integration guideline](./business-wallet-integration.md)
- [Playground README](../README.md) — demo cast, endpoints, v3↔v4 mapping
- Trust Resolver API — `https://resolver.testnet.verana.network/docs`
- OpenID4VCI drafts 11 through current, and the wallet libraries that implement them
