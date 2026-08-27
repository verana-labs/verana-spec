# Verana Search Specification

**Specification Status:** Draft v1

## Abstract

**Verana Search** is a web interface for searching the Verana trust graph. It is a thin client over two public read APIs:

- the **Verana Graph** faceted-search endpoint (`POST /v4/graph/search`), as specified in [Faceted-search Queries](../verana-graph/spec.md#faceted-search-queries) of the Verana Graph spec;
- the **Verana Indexer** Verifiable Trust Resolver (`POST /v4/verifiable-trust/resolve`, [IDX-VT-QRY-1](../verana-indexer/spec.md#idx-vt-qry-1-resolve)), used to enrich DID hits with their ECS credential data for display.

The user types a query, optionally narrows it with structured filters, and gets a ranked, infinitely scrolling list of results, rendered with the verana.io design language. For Verifiable Services (the `Did` surface), each result row shows the service identity and its operator, in the style of the Proof-of-Trust card on the verana.io home page.

Verana Search holds no state of its own: every piece of displayed data is fetched from the graph and the resolver at render time.

## Conformance

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) when, and only when, they appear in all capitals.

Normative requirements are prefixed `[SRCH-]`.

## Configuration

[SRCH-CFG-1] The app MUST read its upstream endpoints from environment variables, with these defaults for devnet:

| Variable | Required | Default | Description |
|---|---|---|---|
| `GRAPH_BASE_URL` | REQUIRED | `https://graph.devnet.verana.network` | Base URL of the Verana Graph. The app calls `POST {GRAPH_BASE_URL}/v4/graph/search`. |
| `RESOLVER_BASE_URL` | REQUIRED | `https://idx.devnet.verana.network` | Base URL of the Verana Indexer. The app calls `POST {RESOLVER_BASE_URL}/v4/verifiable-trust/resolve`. |
| `NETWORK_LABEL` | OPTIONAL | `Devnet` | Human-readable network name shown in the header. |

[SRCH-CFG-2] **Container.** The app MUST be delivered as a versioned container image (Docker Hub, same packaging pattern as the other Verana frontends), and the endpoints of [SRCH-CFG-1] MUST be **runtime configuration of the container**, not build-time constants: the same image serves devnet, testnet, and mainnet by changing only its environment. For a Next.js build this means the values MUST NOT be baked in as `NEXT_PUBLIC_*` at build time; they are read server-side at startup (standalone output) and handed to the client (server component prop, or a tiny `/config` route), so that `docker run -e GRAPH_BASE_URL=... -e RESOLVER_BASE_URL=...` is sufficient. The container MUST log the resolved configuration at startup and MUST fail fast with a descriptive error when a REQUIRED variable is missing or malformed.

[SRCH-CFG-3] **Helm.** The repo MUST ship a Helm chart at `charts/` (chart name `verana-search-chart`, same layout as verana-frontend) that installs the app with `helm install`, exposing at minimum: `image.repository` / `image.tag` (defaulting to `veranalabs/verana-search` and the chart version), a flat `env:` map carrying the [SRCH-CFG-1] variables (`GRAPH_BASE_URL`, `RESOLVER_BASE_URL`, `NETWORK_LABEL`), `replicas` (default `1`), ingress host/TLS settings (`host` + `global.domain`, cert-manager `letsencrypt-prod`, ingress class `nginx`), and `resources`. Default resources MUST be the smallest values that run the app reliably; for the Next.js standalone server:

```yaml
resources:
  requests:
    cpu: 50m
    memory: 128Mi
  limits:
    cpu: 250m
    memory: 256Mi
```

The chart MUST define liveness and readiness probes against a lightweight route (e.g. `GET /api/health` returning 200 once the server is up and configuration is validated). Documentation for `docker run` and `helm install` MUST be provided in the README.

[SRCH-CFG-4] **CI/CD.** The repo MUST follow the verana-frontend release pipeline:

- `ci.yml`: the 2060-io organization reusable linter workflow on pull requests and pushes to `main`. It requires pnpm (`packageManager` pin + `pnpm-lock.yaml`) and the `build`, `check-format` (biome), `check-types` (tsc) and `test` scripts, and lints the Helm chart (`charts-dir: charts`).
- `dev-release.yml`: semantic-release on `main` publishes `dev` prereleases; on each release it pushes the Docker image `veranalabs/verana-search` with tags `dev`, `vX-dev`, `vX.Y-dev`, `vX.Y.Z-dev.N`, and the Helm chart to `oci://docker.io/veranalabs` with versions `vX.Y-dev` and `vX.Y.Z-dev.N`.
- `stable-release.yml`: release-please cuts stable releases; on release it pushes the image tags `latest` and `vX.Y.Z`, the chart at `vX.Y.Z`, and notifies Discord via the organization reusable workflow.

Third-party actions MUST be pinned to full commit SHAs (org policy); org-internal reusable workflows are exempt.

## Design

### [SRCH-DS-1] Design system

The app MUST reuse the **verana.io-website "Protocol Grid" design system** verbatim: same tokens, same fonts, same light/dark mechanism. Concretely (from `verana.io-website/app/globals.css`):

- **Stack**: Next.js + Tailwind v4, tokens declared in `@theme` so utilities (`bg-bg`, `bg-surface`, `text-ink`, `text-muted`, `border-rule`, `bg-primary`, `text-accent`, `text-success`, ...) are generated.
- **Brand palette**: primary `#763ef0` (Verana purple), primary-bright `#8c5bff`, accent `#2e6be6` (Electric Blue; `#1f57c9` in light for AA), success `#29c68c` (Signal Green; success-ink `#0e7a57` in light).
- **Surfaces (dark-first)**: bg `#0b0b12`, surface `#151824`, surface-2 `#1f2331`, rule `#2a2e3d`, ink `#ffffff`, muted `#8b94a5` — re-bound for light mode as in verana.io (`#ffffff` / `#f4f5f8` / `#eceef3` / `#e3e6ec` / `#0b0b12` / `#566071`).
- **Type**: Space Grotesk for display (`.display`), Inter for body, IBM Plex Mono for eyebrows/chips/DIDs (`.eyebrow`, `.chip`).
- **Theme switching**: `[data-theme="dark"|"light"]` on the root element, default follows the OS with dark fallback, set pre-paint exactly as verana.io does; a header toggle persists the choice.
- **Icons**: FontAwesome components, as on verana.io. Glyph characters (☑, ↗, ✕, ...) MUST NOT be used as UI symbols; country flags MAY use emoji flags derived from ISO 3166-1 alpha-2 codes (same `countryFlag()` approach as `ProofOfTrustCard`).
- **Copy**: rendered UI copy MUST NOT use em-dashes; use commas, colons, parentheses, or a spaced hyphen.

The implementation SHOULD copy `globals.css` tokens and the shared primitives (`.display`, `.eyebrow`, `.chip`, card borders) from verana.io-website rather than re-derive them, so the two sites cannot drift apart.

### [SRCH-DS-2] Layout

Single page:

- **Header**: Verana wordmark + "Search" label, `NETWORK_LABEL` chip, theme toggle.
- **Search zone**: the form of [Search Form](#search-form), horizontally centered, max width `--max-width-8xl`.
- **Result zone**: the list of [Result Presentation](#result-presentation), same max width.
- Fully responsive; no horizontal scroll at any width.

## Search Form

### [SRCH-FORM-1] Fields

The form is a single row (wrapping on small widths) with:

1. **Surface selector** — a select over the five [TG-FCT-1] surfaces: `Did` (labelled "Services", the default), `Ecosystem`, `Corporation`, `CredentialSchema` (labelled "Credential Schemas"), `ServiceEndpoint` (labelled "Service Endpoints").
2. **Free-text input** — a single text input bound to the request's `freeText`. Placeholder: `Search the Discovery layer and decentralized trust graph`. Matching follows the graph's semantics ([TG-FCT-4], and [TG-FCT-4a] once merged): whole-token, case-insensitive, conjunctive across tokens. The UI MUST NOT pre-process the string beyond trimming.
3. **Filters toggle** — a button ("Filters") that expands or collapses the filter panel of [SRCH-FORM-3]. A count badge shows how many filters are active while the panel is collapsed.

An empty free-text input with no filters is a valid query: it lists everything on the surface, ranked by the graph's trust signals.

### [SRCH-FORM-2] Search as you type

- Every change to the surface, the free-text input, or a filter (re)issues the query.
- Free-text changes MUST be **debounced** (RECOMMENDED: 250 ms) and the app MUST **abort the in-flight request** (`AbortController`) when a newer query supersedes it. Responses from superseded queries MUST be discarded.
- Surface or filter changes fire immediately (no debounce) and reset the result list.
- Every new query resets the cursor and the scroll position of the result zone.
- While a query is in flight, previous results remain rendered, with a subtle loading indicator; results are replaced when the response lands (no flashing blank state).

### [SRCH-FORM-3] Filter panel

The collapsible panel exposes the **structured filters of [TG-FCT-3] for the selected surface** and nothing else. Filters render per operator type:

- `eq` / `in` fields: multi-select (or single select where only `eq` is declared), populated where possible from the `facets` aggregations of the previous response (value + count), otherwise as free input.
- `range` fields: min/max numeric pair.
- `prefix`-capable fields (`legalJurisdiction`, `controllerJurisdiction`): text input, sent as `{ "prefix": <value> }`.
- `contains` / `containsAny` (`Did.serviceTypes`): tag input.

Surface switching re-renders the panel with that surface's filter set and clears filters that do not exist on the new surface.

The panel also exposes the visibility-gate overrides where the spec allows them: `includeUntrusted` (checkbox, `Did` and `ServiceEndpoint` surfaces) and `includeArchived` (checkbox, `Ecosystem` and `CredentialSchema` surfaces). Non-overridable gates (trust-expiry) are not surfaced.

### [SRCH-FORM-4] Request shape

Requests are exactly the [TG-FCT-9] payload:

```json
{
  "surface": "Did",
  "freeText": "hologram",
  "filters": { "Participant.role": "ISSUER" },
  "limit": 12,
  "cursor": null,
  "includeUntrusted": false
}
```

`freeText` and `filters` are omitted when empty. `limit` is computed per [SRCH-SCROLL-1].

## Result Loading

### [SRCH-SCROLL-1] Viewport-sized limit

`limit` MUST be derived from the available space, not hardcoded:

```
limit = clamp( ceil(resultZoneViewportHeight / estimatedRowHeight) + OVERSCAN, MIN, MAX )
```

with `OVERSCAN = 4`, `MIN = 6`, `MAX = 50`, and `estimatedRowHeight` the design height of one result row for the current surface and breakpoint (measured from the first rendered row when available, a constant estimate before first render). The intent: the first page fills the visible area plus a small overscan, so the user never sees an underfilled screen or pays for 100 rows they cannot see.

`limit` is recomputed on window resize; subsequent pages reuse the current value.

### [SRCH-SCROLL-2] Infinite scroll via cursor

There is **no pagination UI**. Loading is cursor-driven, per [TG-FCT-7]:

- A sentinel element sits after the last rendered row, observed with `IntersectionObserver`.
- When the sentinel becomes visible and the last response's `cursor` is non-null and no page request is in flight, the app requests the next page with the **same** `surface` / `freeText` / `filters` / gate flags and the returned `cursor`.
- Appended hits are deduplicated by `(type, id)` (keyset cursors can legitimately surface a record twice across live updates); duplicates are dropped.
- `cursor: null` in a response ends the stream: the sentinel is replaced by an end-of-results note showing `totalCount`.
- An `INVALID_CURSOR` error (per [TG-ERR-1]) restarts the query from the first page, preserving already-rendered rows until the fresh first page lands.

### [SRCH-SCROLL-3] States

- **Empty result** (`totalCount: 0`): a friendly empty state with the query echoed and a hint about whole-token matching ("Search matches whole words").
- **Error** (non-2xx / network): inline error card with a retry action; typed `error.code` values from [TG-ERR-1] get specific messages (`UNKNOWN_FILTER_FIELD`, `INVALID_INPUT`, ...).
- **Loading**: skeleton rows shaped like the surface's card.

## Result Enrichment

### [SRCH-ENR-1] Why enrichment

The devnet graph currently returns the pre-[TG-FCT-6a] minimum snippet for `Did` hits (`did`, `lastObservedAtTime`, `isTrustExpired`, `trusted`, `pattern`, `operatorKind`, `corporationId`) with **no ECS credential data**, so a `Did` row cannot be rendered from the search response alone.

[SRCH-ENR-2] For each `Did` hit, the app MUST call the resolver:

```json
POST {RESOLVER_BASE_URL}/v4/verifiable-trust/resolve
{ "did": "<hit.id>", "ecsCredentials": true, "services": true, "ecosystems": {} }
```

and extract the **entity bindings** for the badges of [SRCH-RES-1]: `isCorporation` MUST be true if and only if the DID **is** the declared `did` of a `Corporation` entry — determined by comparing the owner Corporation record's `did` (from the [SRCH-ENR-2a] fetch) with the hit DID, NOT by the mere presence of a resolver `corporation` object (some resolver builds return it for owned DIDs too); and `ecosystemIds` (the ids of `ecosystems[]`, the Ecosystems this DID controls). When the graph ships the [TG-FCT-6a] snippet fields ([SRCH-ENR-4]), `isCorporation` / `ecosystemIds` come from the snippet directly;

and extract, from `services[]` (the non-`LinkedVerifiablePresentation` service entries of the DID Document):

- the **service endpoint types** for the badge row of [SRCH-RES-1]: the deduplicated set of `services[].type` values;

and, from `ecsCredentials[]`:

- the **ServiceCredential** subject: `name`, `type`, `description`, `logoUri`;
- the **operator identity**: if the ServiceCredential is self-issued (pattern `A`), the same DID's `OrganizationCredential` / `PersonaCredential` subject; if delegated (pattern `B`), a second `resolve` on the ServiceCredential's issuer DID (recovered via `issuerParticipantId` → the issuer Participant's DID, or by resolving the credential issuer) to obtain the ORG / PERSONA subject. From it: `name`, `logoUri` or `avatarUri`, `countryCode` or `controllerCountryCode`, `registryId`, `address` (org only).

[SRCH-ENR-2a] **Owner-Corporation trust signals.** For each `Did` hit the app MUST also surface the owner Corporation's trust signals: `corporationId`, `corporationDeposit`, `corporationSlashedEvents` (`0` when never slashed), `corporationLastSlashedAtTime` and `corporationSlashedValue` (`null` when never slashed). Source: the [TG-FCT-6a] snippet fields when present; otherwise one indexer call per owner Corporation, `GET {RESOLVER_BASE_URL}/v4/corporation/get/{corporationId}` (cached by `corporationId`, shared across hits of the same Corporation), mapping `deposit` → `corporationDeposit`, `slash_count` → `corporationSlashedEvents`, `last_slashed` → `corporationLastSlashedAtTime`, `slashed_deposit` → `corporationSlashedValue`. Coin amounts are displayed in VNA (uvna / 10^6), whether they arrive as Coin strings (`"40000000uvna"`) or micro-denom numbers.

[SRCH-ENR-3] Enrichment mechanics:

- Enrichment runs **per rendered row, concurrently**, bounded to at most 6 in-flight resolver calls; rows render immediately with the snippet data and skeleton placeholders for the credential fields, then fill in as resolves land (no layout shift beyond the reserved placeholder areas).
- Responses MUST be **cached in memory keyed by `(did, lastObservedAtTime)`**, so re-queries, scroll-back, and shared operator DIDs (pattern B parents) resolve at most once per observation.
- A failed resolve degrades gracefully: the row keeps the DID, trust chip, and pattern, and shows "details unavailable" in place of the credential fields; it MUST NOT block the list.

[SRCH-ENR-4] **Forward compatibility.** Once the graph implements [TG-FCT-6a] (verana-spec PR #62) and its snippets carry `serviceName`, `serviceType`, `serviceDescription`, `serviceLogoUri`, `operatorName`, `operatorLogoUri`, `operatorCountryCode`, `serviceEndpoints[]`, and the `corporation*` trust signals, the app MUST prefer these snippet fields and skip the resolver and corporation calls for list rendering (feature-detected per hit: snippet field present and non-undefined). The endpoint badges of [SRCH-RES-1] then render from `snippet.serviceEndpoints[].type`. The resolver remains in use only for fields the snippet never carries (`registryId`, `address`) and for future detail views.

Non-`Did` surfaces are rendered from the snippet alone; no enrichment call is made.

## Result Presentation

Results render as a **single-column vertical list**, search-engine style: one bordered card (`bg-surface`, `border-rule`, rounded) per hit, full row width, ordered as returned (descending score). No grid, no columns.

### [SRCH-RES-1] `Did` rows (Verifiable Services)

Each row is a **condensed, two-zone version of the verana.io `ProofOfTrustCard`** (the SERVICE / OPERATED BY layout of the home page), one row per hit:

```
+------------------------------------------------------------------------------+
| SERVICE                                   | OPERATED BY                      |
| [logo] Service Name          [trust chip] | [logo] [flag] Operator Name      |
|        type (mono, muted)                 |        registryId (mono, muted)  |
| description, clamped to 2 lines           |        address (muted, 1 line)   |
| [DIDCOMM] [MCP] [A2A]  endpoint badges    | CORPORATION #8                   |
| did:webvh:... (mono, truncated, copy)     | deposit 40 VNA - slashes 0       |
+------------------------------------------------------------------------------+
```

- **Left zone (SERVICE)**: `eyebrow` label "SERVICE"; square service logo (`logoUri`, 40-48 px, rounded, `bg-surface-2` fallback with initial letter); service `name` in Space Grotesk semibold; `type` as a mono muted line; `description` clamped to 2 lines; the DID in IBM Plex Mono, middle-truncated, with a copy-to-clipboard icon button.
- **Right zone (OPERATED BY)**: `eyebrow` label "OPERATED BY"; operator logo/avatar (smaller than the service logo, per the ProofOfTrustCard convention); emoji country flag + operator `name`; `registryId` in mono muted (organizations); `address` muted, single line truncated (organizations). Personas show name + flag only.
- **Corporation trust signals** (below the operator identity, per [SRCH-ENR-2a]): a mono muted block showing the owner `corporationId` (`CORPORATION #8`), `corporationDeposit` in VNA, and `corporationSlashedEvents`; when `corporationSlashedEvents > 0` the slash count renders in red and the block adds `corporationLastSlashedAtTime` (date) and `corporationSlashedValue` in VNA.
- **Endpoint type badges** (SERVICE zone, between the description and the DID line): one mono `chip` per **deduplicated** service endpoint type of the DID Document — from `snippet.serviceEndpoints[].type` when present (per [SRCH-ENR-4]), else from `services[].type` of the enrichment resolve of [SRCH-ENR-2]. Display rules:
  - normalize the DIDComm entry labels: `DIDCommMessaging` and `did-communication` both render as a single `DIDCOMM` badge;
  - order: `DIDCOMM` first, then the remaining types alphabetically, uppercased (`A2A`, `LINKEDDOMAINS` rendered as `WEBSITE`, `MCP`, `VSAGENTADMINAPI` rendered as `ADMIN API`, unknown types verbatim);
  - at most 5 badges are shown; overflow collapses into a `+N` chip whose tooltip lists the rest;
  - badges are neutral (`bg-surface-2`, `text-muted`, `border-rule`), not colored: they state protocol reachability ("which protocols can I talk to it with"), not trust;
  - clicking a badge sets the `Did.serviceTypes` `containsAny` filter to that type and re-queries (same behaviour as a facet refinement per [SRCH-RES-3]).
- **Trust chip** (top right of the SERVICE zone): Signal-Green `chip` "VERIFIED" when `trusted && !isTrustExpired`; muted chip "UNTRUSTED" when `includeUntrusted` surfaced a non-trusted DID. `pattern` and `operatorKind` are not shown as chips (they are implicit in the card content).
- **Entity badges** (left of the trust chip): a purple `chip` "CORPORATION" when the DID is the declared DID of a `Corporation` entry, and a purple `chip` "ECOSYSTEM" when the DID controls one or more Ecosystems (tooltip lists the ecosystem ids). Sourced per [SRCH-ENR-2] (`isCorporation` / `ecosystemIds`).
- On small widths the two zones stack vertically, SERVICE first.
- The row is clickable. v1: opens the DID's resolver JSON in a new tab (`{RESOLVER_BASE_URL}/v4/verifiable-trust/resolve` result rendered raw or via a minimal drawer). A dedicated detail page is out of scope for v1.
- `highlights[]` fragments, when present, MAY be rendered under the description in muted small text with `<em>` matches styled in accent color, after sanitization: treat fragments as text and re-apply only the `<em>` markers; never inject response HTML.

### [SRCH-RES-2] Other surfaces

Simple single-zone rows from snippet data:

- **Ecosystem**: eyebrow "ECOSYSTEM"; `id` (mono chip), DID (mono, truncated, copy), archived chip when `archived`.
- **Corporation**: eyebrow "CORPORATION"; `id`, DID, `policyAddress` (mono, truncated), deposit and slash counters when present.
- **CredentialSchema**: eyebrow "CREDENTIAL SCHEMA"; `title` and `description` when present (from the loaded schema body), `id` (mono chip), owning `ecosystemId`, archived chip.
- **ServiceEndpoint**: eyebrow "SERVICE ENDPOINT"; `type` chip (`MCP`, `A2A`, ...), the `serviceEndpoint` URI (mono, truncated), and the owning DID.

These rows MAY be enriched in later versions (e.g. resolving the Ecosystem DID for its display identity); v1 renders snippets only.

### [SRCH-RES-3] Facets sidebar (SHOULD)

When the response's `facets` object is non-empty, the app SHOULD render the aggregations as clickable refinements (value + count) beside or above the list on wide viewports; clicking one sets the corresponding filter and re-queries. On narrow viewports facets fold into the filter panel.

## Accessibility

- All interactive elements keyboard-reachable; the result list is a `role="list"`; infinite scroll announces new content via `aria-live="polite"`.
- Color contrast follows the verana.io token pairs (already AA in both themes).
- The free-text input is focused on page load and refocusable with `/`.

## Out of Scope (v1)

- Detail pages per entity (only the raw-resolve drawer of [SRCH-RES-1]).
- Traversal queries (`/v4/graph/traverse`); everything shown comes from `search` + `resolve`.
- Query-understanding / natural-language parsing: the form maps 1:1 to the structured payload.
- Authentication: both upstream APIs are public.
