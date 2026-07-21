# Roadmap

## Spec

### V3 2025 (MVP)

### V4 Q1-Q3 2026

Changelog: 

- Terminology overhaul: trust registry => Ecosystem, Permission => Participant (vt-spec, vt-vpr-spec)
- Corporation Management (vt-vpr-spec)
- Exchange Rate module & multi-asset pricing: TU / COIN / FIAT (vt-vpr-spec)
- VS Operator Authorization & payment delegation: VSOA, fee grants (vt-vpr-spec)
- Schema Authorization Policy, base mechanism (vt-vpr-spec)
- ECS-Badge, fifth Essential Credential Schema (vt-spec)
- Business/Cloud Wallet (verana-spec/v4/vs-agent)
- VT-Flows for automatic credential issuance / revocation / presentation (verana-spec/v4/vt-flow-protocol)
- Indexer/Resolver specification, incl. ToIP TRQP endpoint (verana-spec/v4/verana-indexer)
- Trust Graph specification (verana-spec/v4/verana-graph)
- mcp-server specification (verana-spec/v4/mcp-server)

### V5 Q3-Q4 2026

Changelog: 

- Schema Authorization Policy extension: limit presentation-requestable attributes (vt-vpr-spec)
- Council-based governance (vt-vpr-spec)
- Tokenomics updates

### V6 2027

Changelog: 

- Add the Trust Spanning Protocol (verifiable-trust-spec) https://trustoverip.org/blog/2023/01/05/the-toip-trust-spanning-protocol/
- Multi-tenancy wallet (vs-agent)
- additional vt-flows
- delegation — two complementary layers: standing registry-anchored authorization on-chain (VSOA-style: operator X may act/pay for ecosystem/service Y — durable, publicly resolvable), plus ephemeral per-action execution grants at the agent runtime (OpenVTC-style consent gate: a human context-admin approves one specific task for one AI agent, then authority evaporates). Combined story: VPR answers "is this agent's operator authorized in this ecosystem at all?", the consent gate answers "did an accountable human approve this specific action?"
- Enclave & HSM key custody for vs-agent / business wallet: PKCS#11, cloud KMS, TEE deployment profile (vs-agent)
- [vLEI / GLEIF](https://www.gleif.org/en/organizational-identity/lei-vlei/the-verifiable-lei-vlei) as an alternative source of trust for Organizations (vt-spec)
- [OpenVTC](https://github.com/OpenVTC) interop/acceptance: Personhood Credentials (PHC) and Verifiable Relationship Credentials (VRC) as an alternative source of trust for natural persons (vt-spec)
- Verifiable enclave attestation as a trust signal (research — attestation evidence linked from DID doc / ECS credential)

## Infrastructure Software

### Spec V3 Implementation (MVP) 2025/Q1 2026

- Q4 2025: node (ledger) v3
- Q1 2026: indexer v3
- Q4 2025: vs-agent v3
- Q1 2026: resolver v3
- Q1 2026: frontend v3
- Q4 2025: documentation v3 (docs.verana.io)
- Q3 2025: visualizer v3
- Q3 2025: faucet (Hologram chatbot VS)

### Spec V4 Implementation Q2/Q3 2026

- Q3 2026: node (ledger) v4
- Q3 2026: vs-agent v4
- Q3 2026: indexer v4
- Q3 2026: resolver v4
- Q3 2026: trust graph v4
- Q3 2026: frontend v4
- Q3 2026: mcp-server v4
- Q3 2026: visualizer v4
- Q3 2026: documentation v4 (docs.verana.io)

### Spec V5 Implementation

- Q4 2026: node (ledger) v5
- Q4 2026: indexer v5
- Q4 2026: vs-agent v5
- Q4 2026: frontend v5
- Q4 2026: resolver v5
- Q4 2026: trust graph v5
- Q4 2026: mcp-server v5
- Q4 2026: documentation v5 (docs.verana.io)

### Spec V6 Implementation 2027

- 2027: node (ledger) v6
- 2027: indexer v6
- 2027: vs-agent v6
- 2027: frontend v6
- 2027: resolver v6
- 2027: trust graph v6
- 2027: mcp-server v6
- 2027: documentation v6 (docs.verana.io)


## Services and Integrations

- Q4 2026: council software for ECS participant onboarding
- Q3 2026: integration of main third party personal wallet / business wallet software & demos (mosip, eu unfold, fides.community, etc) 
- Q3 2026: playground playground.testnet.verana.network

## Infrastructure Network

### Testnet 2025-05

- Q3 2026: testnet upgrade to v4
- Q3 2026: testnet upgrade to v5
- Q4 2026: genesis validator set rehearsal (founding council members' testnet nodes)

### Mainnet Q1 2027

- Q4 2026: security audit (ledger modules; resolver / trust-resolution path)
- Q4 2026: HSM-backed validator signing (tmkms) guidance for founding council validators
- Q1 2027: genesis ceremony / mainnet launch / TGE

## Verana Council

- Q3 2026: veranacouncil.org website
- Q3 2026: council bodies definition
- Q3 2026: seed cohort of 3 designated (2060 + first 2 vetted candidates, rationale published)
- Q3 2026: Network GF, ECS-EGF, Sectorial EGF template — incl. resolving the open [DECISION] flags in the drafts
- Q3 2026: Bylaws & Code of Conduct
- Q3 2026: Council Membership Agreement drafted (binding instrument at seating; replaces abandoned MoU v1)
- Q4 2026: selected Founding Council seats
- Q4 2026: council association created (swiss verein) — constitutive General Assembly ratifies pre-incorporation seatings en bloc
- Q4 2026: all founding council members joined testnet
- Q4 2026: ECS Ecosystem Participant recruitment opens (governed by the ECS-EGF)
- Q1 2027: initial ECS participants permissioned (before mainnet)
- Q1 2027: mainnet launch / TGE
- Q1 2027: ECS Ecosystem launch


## Verana Foundation

- Q3 2026: veranafoundation.org website
- Q3 2026: verana.io website
- Q3 2026: launch of the first working groups
- Q3 2026: membership program open (Associate / Contributor, self-service apply + billing)
- Q4 2026: tokenomics finalized (VNA genesis allocation, emission, vesting; SAFT / token T&Cs)
- Q4 2026: foundation group entities created (ownerless foundation company — Cayman — plus OpCo and token-issuer entities)
- Q4 2026: specifications ownership transferred to the Foundation
- Q4 2026: grants program launch
- Q1 2027: mainnet launch / TGE
