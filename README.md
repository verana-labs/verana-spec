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
v4/
  vs-agent/
    spec.md
```

## Current specifications

### v4

| Component | Spec                                            | Status |
| --------- | ----------------------------------------------- | ------ |
| VS Agent  | [`v4/vs-agent/spec.md`](./v4/vs-agent/spec.md)  | Draft  |

## Versioning

A new top-level `vN/` directory is created when a breaking change is introduced across one or more component specs. Within a version, individual component specs evolve independently and carry their own draft / release markers in their front matter.

## Contributing

Editorial fixes, clarifications, and new component specs are welcome via pull request. For changes that touch the public Verifiable Trust or VPR specifications, please open the PR against the relevant upstream repository listed in [Scope](#scope) instead.

## License

See [LICENSE](./LICENSE).
