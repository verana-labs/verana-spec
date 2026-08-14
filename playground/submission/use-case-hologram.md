# FIDES use-case dossier — Hologram: a browser for decentralized AI chatbot services

**Status:** READY 1.0 · 2026-08-12
**Submitted by:** 2060 org account on FIDES · **Award lane:** Innovation (FIDES Community Awards) — deliberately not competing with Verana's Collaboration lane.
**Form:** https://fides.community/ecosystem-explorer/use-cases/submit-use-case/ (requires the 2060 FIDES Community account; entries are reviewed before publication).

Paste-ready values below; field names follow the published Vesta entry structure.

## Title

> Hologram: a browser for decentralized AI chatbot services, self-hosted and verified before the first message

## Core fields

| Field | Value |
| --- | --- |
| Organization | 2060 |
| Sector | Technology (cross-sector) |
| Country | Estonia (2060 OÜ) |
| Production deployment status | **Yes** — all services live on `*.vs.hologram.zone` |
| VC formats | AnonCreds |
| Issuance protocols | Other (DIDComm issue-credential v2) |
| Presentation protocols | DIDComm v2 |
| Interaction modes | Remote flow |
| Credential types used | Avatar credential (custom) · Passport credential (custom, eMRTD-derived) · ECS Organization Credential · ECS Service Credential |
| Personal wallets supported | Hologram Messaging |
| Business wallets | VS Agent (Verana Business Wallet) |
| More information | https://hologram.zone/demos |

## Overview

> Hologram Messaging turns the messenger into a browser for decentralized services: scan a QR and you are in an encrypted DIDComm chat with a self-hosted chatbot or AI agent, verified before the first message. It is built on Verana, the open public trust layer: every service is a Verifiable Service whose identity, operator and permissions any wallet can resolve. Five production services show the range: an Avatar credential issuer, a Passport issuer with NFC and liveness, AI agents for GitHub and Wise over MCP gated by your Avatar credential, and an X agent whose right to post is bound to verifiable credentials. Everything is open source and self-hosted from forkable repos: no app store, no platform, no vendor lock-in.

## How it works (1,088 / 1,200 chars)

> Hologram Messaging is an open-source messenger that doubles as a browser: scanning a QR opens an encrypted DIDComm chat with a self-hosted service. No app store, no platform account. Each demo runs from a forkable repo (GitHub Actions deploy to Kubernetes) behind an open-source VS Agent. A self-hosted organization anchor obtains Organization and Service credentials, runs its own trust registry on the Verana Verifiable Public Registry, and accredits its child services, so the app can trust-resolve every service before the first message. The Avatar chatbot issues you an identity credential in conversation; the Passport issuer reads a government ID over NFC and verifies liveness on a video call. The GitHub and Wise agents are AI assistants over MCP: they authenticate you with your Avatar credential, then act on your own accounts with your own API token, inside the encrypted chat. The X Agent flips authority around: an Agent Pack policy binds the right to post in the account's name to verifiable credentials you choose, so every AI action is credential-gated and attributable.

## Tags

decentralized AI · verifiable AI agents · DIDComm · chatbot · MCP · verifiable credentials · self-hosted · open source · trust registry · agentic · Hologram · Verana

## Links for the body

- Demos landing: https://hologram.zone/demos (per-demo copy matches this dossier) and https://vs.hologram.zone
- Repo (all services, one structure): https://github.com/2060-io/hologram-verifiable-services
- Docs: https://docs.hologram.zone
- Trust layer cross-links: the Verana catalog entries (Vesta Appliances use case, Republic of Verandia once published, ECS credential types)

## Assets

- **Card thumbnail: capture from [`media/hologram-card.html`](./media/hologram-card.html)** — open in a browser at 100% zoom and screenshot the 1600x900 stage (press G for guides). Text sits in the top half only; the bottom stays visual and calm because FIDES overlays its own title on the lower part of card thumbnails.
- Alternates: the demo-grid art from hologram.zone (Avatar photo or the X Agent "Compose. Draw. Publish." card).
- The "Runs on the Verana open trust layer" badge (collaborator kit, §5 of the README) in the image set.
- Screenshots: hologram.zone/demos grid, one in-chat capture per agent (Avatar issuance, Wise agent action with MCP config menu, X Agent approval step).
- Video (≤3 min, uncut): scan Avatar QR → receive credential → connect Wise agent → authenticate with the credential → one real action in chat.

## Positioning notes (why this entry stands out in the catalog)

1. **The browser metaphor** — Hologram Messaging is to chatbot services what a web browser is to websites; nothing in the catalog covers browsable agentic services.
2. **Verified AI in the deepfake era** — every service is a Verifiable Service, trust-resolved before the first message; only Spherity Trusted AI is adjacent.
3. **Credential-governed AI authority** — the X Agent's "who may post in this account's name" Agent Pack policy is a novel answer to AI-agent governance.
4. **Production: Yes** — live services, while most catalog entries are pilots; sovereignty angle (open source, self-hosted, forkable) shared with the Verandia entry.
