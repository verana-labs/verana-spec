# Verana MCP Server spec

Purpose:

a container for fully controlling Verana via MCP.

- ledger API: for executing all possible transactions specified in VPR spec
- indexer API: for querying the indexer, including the resolver API
- for querying the graph

Container:

- must be implemented in typescript
- must have a cosmos sdk wallet, and be able to use verana types typescript library @verana-labs/verana-types
- must define an env variable for defining the BIP39 phrase for the wallet
- API must provide GET (queries) and POST methods