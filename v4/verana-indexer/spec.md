# Indexer v4 Specification

**Latest Draft:** spec v4-draft1

## Abstract

## About this Document

In order to fully understand the concepts developed in this document, you should have some basic knowledge of DID, DIDComm, AnonCreds, the Verifiable Trust model, and the [ToIP stack](https://www.trustoverip.org/toip-model/). All terms used in this specification are defined in the [Terminology](#terminology) section.

## Conformance

As well as sections marked as non-normative, all authoring guidelines, diagrams, examples, and notes in this specification are non-normative. Everything else in this specification is normative.

The key words MAY, MUST, MUST NOT, OPTIONAL, RECOMMENDED, REQUIRED, SHOULD, and SHOULD NOT in this document are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) [RFC2119](https://w3c.github.io/vc-data-model/#bib-rfc2119) [RFC8174](https://w3c.github.io/vc-data-model/#bib-rfc8174) when, and only when, they appear in all capitals, as shown here.

## Terminology

- **AnonCreds** — Anonymous Credentials, a privacy-preserving verifiable credential format supporting selective disclosure and unlinkability.
- **decentralized identifier (DID, DIDs)** — A decentralized identifier, as specified in [DID-CORE](https://www.w3.org/TR/did-core/).
- **DIDComm** — A peer-to-peer messaging protocol built on DIDs, as specified by the [DIDComm Messaging Specification](https://identity.foundation/didcomm-messaging/spec/).
- **Verifiable Public Registry (VPR, VPRs)** — A decentralized registry used to publish and resolve trust-related resources (credential schemas, trust registries, governance frameworks, etc.), as specified by the [Verifiable Trust VPR specification](https://github.com/verana-labs/verifiable-trust-vpr-spec).
- **Verifiable Service (Verifiable Services)** — A service that identifies its operator, purpose, and governance context through verifiable credentials, as defined in the [Verifiable Trust specification](https://github.com/verana-labs/verifiable-trust-spec).
- **Verifiable Trust** — The open, decentralized trust layer specified at [verana-labs/verifiable-trust-spec](https://github.com/verana-labs/verifiable-trust-spec).
- **VS Agent** — The runtime component specified by this document, which hosts a Verifiable Service and exposes a REST API and event model to backend implementations.
- **VTJSC, Verifiable Trust JSON Schema Credential** — A W3C `JsonSchemaCredential` issued by an Ecosystem DID that references a `CredentialSchema` entry in a Verifiable Public Registry, cryptographically binding that schema to the Ecosystem that controls the Trust Registry in which the schema is defined. Specified in [VT-JSON-SCHEMA-CRED-W3C](https://github.com/verana-labs/verifiable-trust-spec/blob/main/spec.md#vt-json-schema-cred-w3c-verifiable-trust-json-schema-credential) of the Verifiable Trust Specification.
- **W3C Verifiable Credentials Data Model (W3C VC Data Model)** — The W3C Recommendation defining a standard data model for verifiable credentials, as specified in [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model/).


## Trust Resolution

## API

### DID Resolver

Given a DID and an optional point-in-time (ISO 8601 datetime or block height, defaults to now/latest block):

1. **Is the DID a Verifiable Service?** Return the trust status: `TRUSTED`, or `UNTRUSTED`.

   Per the VT spec ([VS-REQ]), a DID qualifies as a **Verifiable Service** only if:
   - **[VS-REQ-2]** It presents a valid Service Credential (`ECS-SERVICE` VTC).
   - **[VS-REQ-3]** If the issuer of the Service Credential **is the VS itself** (self-issued), the VS MUST also present exactly one `ECS-ORG` or `ECS-PERSONA` credential.
   - **[VS-REQ-4]** If the issuer of the Service Credential **is another DID**, then the DID Document of that issuer MUST present exactly one `ECS-ORG` or `ECS-PERSONA` credential.

   This ensures every VS is ultimately bound to a legally or naturally accountable entity — either directly (the VS identifies itself) or indirectly (the issuer of its Service Credential identifies itself). A service MUST satisfy these requirements in at least one ecosystem to be `TRUSTED`. Else the status is `UNTRUSTED`.

2. **What credentials does it present?** For each credential extracted from the DID's linked-vps:
   - The evaluation result: `VALID`, `IGNORED`, or `FAILED`
   - Whether the credential satisfies an **ECS** requirement (and which one: `ECS-SERVICE`, `ECS-ORG`, `ECS-PERSONA`, `ECS-UA`, or non-ECS)
   - The full **subject claims** (human-readable data from the credential)
   - The **permission chain** — every participant from the ISSUER up to the ECOSYSTEM permission, including for each:
     - Participant DID and whether it is itself a Verifiable Service
     - Permission type (`ISSUER` → optional `ISSUER_GRANTOR` → `ECOSYSTEM`)
     - Trust deposit amount, service name, organization name, and jurisdiction (from their own ECS credentials)

> **Note:** This method supports two modes:
> - **Summary mode** — returns only `trustStatus` and `production` (lightweight check: "is this DID a Verifiable Service?")
> - **Detailed mode** — returns the full credential list with claims and permission chains
>
> To get full details about any participant in the chain (their own credentials and claims), call this same method on their DID.


| Module | Method Name | Relative REST API path | Type | Requirements | Authz |
| --- | --- | --- | --- | --- | --- |


### Example resolution response

```json
{
  "did": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
  "trusted": true,
  "evaluatedAt": "2026-05-06T17:00:00.000Z",
  "evaluatedAtBlock": 1500000,
  "expiresAt": "2026-05-07T17:00:00.000Z",
  "ecsCredentials": [
    {
      "ecsType": "ECS-SERVICE",
      "issuer": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
      "ecosystem": "did:webvh:QmcTCdA8z7cs7BwCKyrrJrTTmvff3wmxSn7WUZtP2iAM7T:ecs-trust-registry.testnet.verana.network",
      "id": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#cc5c398f-bc64-45df-9482-9cb583cce197",
      "validFrom": "2010-01-01T19:23:24Z",
      "validUntil": "2030-01-01T19:23:24Z",
      "credentialSubject": {
        "id": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
        "name": "Acme MCP Service",
        "type": "MCPService",
        "description": "AI tooling backend for Acme partners.",
        "minimumAgeRequired": 0,
        "termsAndConditions": "https://acme-vs.example.com/terms",
        "termsAndConditionsDigestSRI": "sha384-…",
        "privacyPolicy": "https://acme-vs.example.com/privacy",
        "privacyPolicyDigestSRI": "sha384-…",
        "logo": "https://acme-vs.example.com/logo",
        "logoDigestSRI": "sha384-…"
      }
    },
    {
      "ecsType": "ECS-ORG",
      "issuer": "did:webvh:QmcTCdA8z7cs7BwCKyrrJrTTmvff3wmxSn7WUZtP2iAM7T:ecs-trust-registry.testnet.verana.network",
      "ecosystem": "did:webvh:QmcTCdA8z7cs7BwCKyrrJrTTmvff3wmxSn7WUZtP2iAM7T:ecs-trust-registry.testnet.verana.network"
      "id": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#28825648-aa0d-4706-88ff-4a47304fcaa5",
      "validFrom": "2010-01-01T19:23:24Z",
      "validUntil": "2030-01-01T19:23:24Z",
      "credentialSubject": {
        "id": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone",
        "name": "Acme Corp",
        "registryId": "BE0123456789",
        "registryUri": "https://kbo-data.economie.fgov.be/",
        "address": "Rue de la Loi 1, 1000 Brussels",
        "countryCode": "BE",
        "legalJurisdiction": "BE",
        "lei": "529900T8BM49AURSDO55",
        "organizationKind": "PRIVATE",
        "logo": "https://acme-vs.example.com/logo",
        "logoDigestSRI": "sha384-…"
      },
    }
  ],
  "schemas": [ {
        "type": "JsonSchema",
        "id": "https://idx.testnet.verana.network/verana/cs/v1/js/223",
        "digestSRI": "sha384-…"
    }
  ],

  "presentations": [
    {
      "id": "https://organization.vs.hologram.zone/vt/vp1.json",
      "vtcCredentialIds": [
        "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#cc5c398f-bc64-45df-9482-9cb583cce197",
        "urn:uuid:22222222-aaaa-bbbb-cccc-222222222222",
        "urn:uuid:33333333-aaaa-bbbb-cccc-333333333333"
      ],
      "unresolvableCredentialIds": [
        "urn:uuid:44444444-aaaa-bbbb-cccc-444444444444"
      ],
      "invalidCredentialIds": [
        "urn:uuid:88888888-aaaa-bbbb-cccc-888888888888"
      ],
      "serviceId": "did:web:organization.vs.hologram.zone#vt-vp1"
    }
  ],
  
  "services": [
    {
      "id": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#mcp",
      "type": "MCP",
      "serviceEndpoint": "https://organization.vs.hologram.zone/mcp"
    },
    {
      "id": "did:webvh:QmRhJBzLMF6L3REha9xFpLgxui9X5tFm4TDxHoEHpA8Kpr:organization.vs.hologram.zone#did-communication",
      "serviceEndpoint": "wss://organization.vs.hologram.zone/didcomm",
      "type": "did-communication",
      "accept": [
        "didcomm/aip2;env=rfc19",
        "didcomm/v2"
      ]
    }
  ]
}
```