# verana-spec

Specifications for all **Verana** software components.

## Scope

This repository hosts the normative specifications of the runtime components built and maintained by [Verana Labs](https://github.com/verana-labs) — the agents, services, and tooling that consume the Verifiable Trust layer.

The two **public, ecosystem-level specifications** are intentionally **not** part of this repository and are maintained separately so the broader community can contribute to them independently of Verana's product roadmap:

- [`verana-labs/verifiable-trust-spec`](https://github.com/verana-labs/verifiable-trust-spec) — the Verifiable Trust model.
- [`verana-labs/verifiable-trust-vpr-spec`](https://github.com/verana-labs/verifiable-trust-vpr-spec) — the Verifiable Public Registry (VPR) modules and on-chain message format.

Everything else — the Verana-specific software stack — lives here.

## Layout

Specifications are versioned at the top level. Each version contains one folder per component.

```text
playground/            Verana Playground: site spec, wallet-integration guidelines,
                       the Verana Explained story, and the publication/award kit
v4/
  vs-agent/
    spec.md
  vt-flow-protocol/
    spec.md
  ...
```

The `playground/` directory is unversioned: it specifies the [Verana Playground](./playground/README.md) website (`playground.testnet.verana.network`) and the third-party wallet-integration guidelines.

## Current specifications

### v4

| Component        | Spec                                                                | Status |
| ---------------- | ------------------------------------------------------------------- | ------ |
| VS Agent         | [`v4/vs-agent/spec.md`](./v4/vs-agent/spec.md)                       | Draft  |
| VT Flow Protocol | [`v4/vt-flow-protocol/spec.md`](./v4/vt-flow-protocol/spec.md)       | Draft  |
| Verana Indexer   | [`v4/verana-indexer/spec.md`](./v4/verana-indexer/spec.md)           | Draft  |
| Verana Graph     | [`v4/verana-graph/spec.md`](./v4/verana-graph/spec.md)               | Draft  |
| MCP Server       | [`v4/mcp-server/spec.md`](./v4/mcp-server/spec.md)                   | Draft  |
| Verana Frontend  | [`v4/verana-frontend/spec.md`](./v4/verana-frontend/spec.md)         | Draft  |

### Playground

| Document | Purpose |
| --- | --- |
| [`playground/`](./playground/README.md) | The Verana Playground: website spec, user/cloud wallet integration guidelines, the *Verana Explained* story, submission kit |

## Versioning

A new top-level `vN/` directory is created when a breaking change is introduced across one or more component specs. Within a version, individual component specs evolve independently and carry their own draft / release markers in their front matter.

## Contributing

Editorial fixes, clarifications, and new component specs are welcome via pull request. For changes that touch the public Verifiable Trust or VPR specifications, please open the PR against the relevant upstream repository listed in [Scope](#scope) instead.

## License

See [LICENSE](./LICENSE).
