# VS Agent spec v4-draft8 — Events API and DIDComm Messaging redesign

Both areas are now specified in [spec.md](spec.md) (348 insertions, draft bumped to v4-draft8). Here is what changed and the reasoning behind the design.

## Messaging: the DIDComm scope is now organized in protocol modules

The abstract `sendMessage` endpoint with its `text` / `credential-issuance` / `identity-proof-request` types is gone. In its place, each DIDComm protocol is one **module** with its own path family, records, and events — and the API exposes protocol steps, not abstractions ([spec.md:1409](spec.md#L1409)):

- **[Protocol Discovery](spec.md#L1419)** — `GET /v2/didcomm/protocols` returns the modules a deployment serves with their `didcomm.org` protocol URIs, so a controller can discover capabilities instead of hard-coding them.
- **[Basic Messages](spec.md#L1497)** — a thin wrapper over `basicmessage/1.0` and `/2.0`: `sendBasicMessage`, `listBasicMessages`.
- **[Presentations](spec.md#L1532)** — wraps Present Proof 2.0 with explicit steps in both roles: `createPresentationRequest` (now also accepts `connectionId` for an established connection), prover-side `acceptPresentationRequest`, verifier-side `acceptPresentation`, and `decline`. The per-request `callbackUrl` / `ref` mechanism is removed — events replace it.
- **[Credential Exchanges](spec.md#L1653)** — wraps Issue Credential 2.0: offer → `request-received` event → `acceptCredentialRequest` issues, plus holder-side `acceptCredentialOffer` / `acceptCredential`, `decline`, and a new `deleteCredentialExchange`. An OPTIONAL `autoAccept` (default `false`) on offer/request creation keeps the one-call flow available without an abstraction layer — it is Credo's own knob, and auto-driven exchanges still emit the same events.
- **[Extension Protocol Modules](spec.md#L1788)** — the scalability answer: five normative rules (path shape, message-send methods, records, events, 404 for unserved modules) that any plug-in protocol follows, with a non-normative table of the current ones (`receipts`, `reactions`, `user-profile`, `media-sharing`, `calls`, `action-menu`, `mrtd` — URIs verified against the actual plugin builds). A new protocol extends the API without a new API shape.

Both core exchange modules explicitly do not implement the proposal step (inbound proposals get a problem report), which keeps the surface small until you need it.

## Events API: one webhook, one envelope, every transport at the same level

New top-level section at [spec.md:2423](spec.md#L2423), with config in [VSA-VTI-CFG-ENV-EVT](spec.md#L272):

- `EVENTS_WEBHOOK_URL` replaces `EVENTS_BASE_URL`: every event goes as one `POST` to that exact URL (no per-type path suffix), with optional `Authorization: Bearer` via `EVENTS_WEBHOOK_API_KEY`.
- Envelope is `{id, type, timestamp, data}`. Type grammar is `{scope}.{module}.{event}`, mirroring Admin API paths, with two kinds: `state-updated` and `message-received`.
- The load-bearing consistency rule: **a `state-updated` event's `data` is the record exactly as the corresponding `get` method returns it, plus `previousState`**. Events tell the consumer when to look; records stay the source of truth, so missed events are recoverable by design — which lets delivery stay honest (best-effort, non-blocking, `MAY` retry, dedupe by `id`) instead of pretending at-least-once.
- The catalog covers DIDComm connections/basic-messages/presentations/credential-exchanges, the `didcomm.{module}.message-received` extension pattern, **new** `openid4vc.credential-exchanges` and `openid4vc.presentations` events (previously poll-only), `vt.flows.state-updated`, and `indexer.notification` — still emitted for every indexer event regardless of `VERANA_INDEXER_DEFAULT_HANDLERS_OVERRIDE`.

Supporting edits: method summary table, scope table, naming conventions (new protocol-step path rule, generalized from the VT flow methods), the pagination bounded-collection exception, and the abstract. All internal anchors verified to resolve.

One thing worth flagging for the implementation side: the OpenID4VC `state-updated` events inherit the OID record shapes, which deliberately exclude claim values and offer URLs on the issuance side — so adding those events leaks nothing new. The DIDComm presentation event does carry disclosed claims, which is why delivery rule [VSA-EVT-DEL-6](spec.md#L2439) requires `https://` when the webhook leaves the trusted network.
