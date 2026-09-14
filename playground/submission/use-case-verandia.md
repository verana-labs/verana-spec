# FIDES use-case dossier — Republic of Verandia

**Status:** READY 1.0 · 2026-08-12 — **blocked on deploy:** submit only after playground PR #192 is merged and deployed, so `/usecases/verandia` resolves (production still serves `/usecases/utopia`).
**Submitted by:** Verana org account on FIDES.
**Form:** https://fides.community/ecosystem-explorer/use-cases/submit-use-case/ (requires a FIDES Community account; entries are reviewed before publication).

Paste-ready values below; field names follow the published Vesta entry ([catalog link](https://fides.community/ecosystem-explorer/use-cases/?usecase=vesta-appliances-from-impostors-to-proof-of-trust-ATYNCN)).

## Title

> Republic of Verandia: sovereign citizen IDs, business IDs and legal representation, open source and self-hosted with no vendor lock-in

Shorter fallback if the form clips long titles:

> Republic of Verandia: sovereign digital identity, open source, self-hosted, no vendor lock-in

## Core fields

| Field | Value |
| --- | --- |
| Organization | Verana |
| Sector | Government / Public services |
| Country | Estonia (the Vesta-entry convention for fictional settings; adjust if the form allows) |
| Production deployment status | No |
| VC formats | AnonCreds · SD-JWT VC |
| Issuance protocols | OpenID4VCI · Other (DIDComm issue-credential v2) |
| Presentation protocols | DIDComm v2 · OpenID4VP |
| Interaction modes | Remote flow · Proximity flow |
| Credential types used | Verandia Citizen ID (eIDAS-2-PID-inspired, demo) · Legal Representative (demo) · ECS Organization Credential · ECS Service Credential |
| Personal wallets supported | Inji, EUDI Reference Implementation, Paradym, Procivis One, Hologram Messaging, Sphereon Edge, SWIYU, Altme, wwWallet, BC Wallet (the Vesta roster; the same playground integrations serve both stories) |
| Business wallets | VS Agent (Verana Business Wallet) |
| More information | https://playground.testnet.verana.network/usecases/verandia |

## Overview

> A fictional democracy runs its own digital identity as sovereign infrastructure: every component is open source and self-hosted by its institutions, with no vendor to depend on. The Civil Registry operates its own issuing service for an eIDAS-2-compatible Citizen ID, the Business Registry issues verifiable Business IDs and Proofs of Legal Representation, and the Republic itself governs who may issue and who may verify, on a neutral public trust registry that a state can equally self-host. Citizens hold their credentials in the wallet they choose, from an open roster of independent open-source wallets, so no single app is ever mandated. One scan signs them in to the Tax Buro or their bank; an unauthorized lender's over-asking request and a fake refund portal are both refused, with proof.

## How it works (1,183 / 1,200 chars)

> The Republic anchors everything on a Verifiable Public Registry: an open, neutral registry of ecosystems, schemas and permissions that a state can equally self-host. The National Business Registry becomes an accredited issuer of Organization credentials, so proving a company's identity is a lookup, not paperwork. The National Civil Registry runs its own open-source issuing service and creates the Citizen ID ecosystem: it defines the eIDAS-2-inspired schema and holds the ISSUER permission, while relying parties like the Tax Buro and Meridian Bank must obtain VERIFIER permissions before wallets will share anything, the registry analog of eIDAS 2 relying-party registration. Citizens scan a QR and receive the Citizen ID in any wallet from the open roster, over AnonCreds/DIDComm or OpenID4VCI (SD-JWT VC). Companies attach Business IDs to self-hosted business wallets and publish services; representatives add a Proof of Legal Representation. Before anything is shared, the wallet trust-resolves the counterparty against the registry and renders a Proof-of-Trust. An unauthorized lender that over-asks and a fake refund portal both fail resolution and are refused, with proof.

## Tags

sovereign identity · open source · self-hosted · no vendor lock-in · trust registry · citizen ID · eIDAS 2 · governed verification · KYB · legal representation · proof-of-trust · Verana

## Assets

- Thumbnail: `public/images/verandia/hero.webp` (the riverside capital) from the playground image kit.
- Screenshots: the 3.8 refusal diagram, the Tax Buro / Meridian Bank login windows, a wallet Proof-of-Trust capture.

## Supporting facts for a longer description field

- The wallet roster is OSI-licensed by playground policy (the no-lock-in claim, concretely).
- The entire chain (registry node, resolver, indexer, vs-agent, wallets) is public open-source repos a government could fork and operate (the sovereignty claim, concretely).
- Story spec: `playground/verandia/spec.md` in this repo; live journey at the More-information URL.
