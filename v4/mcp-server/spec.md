# Verana MCP Server spec

Purpose:

a container for fully controlling Verana via MCP.

- ledger API: for executing all possible Msg transactions specified in the VPR spec
- indexer API: for querying the indexer, including the resolver API

- for querying the graph
- for connecting to vs-agent admin API

Using the MCP server, one can, based on the OperatorAuthorizations its account is granted:

- Create and manage Corporations, Ecosystems, Participant

Container:

- must be implemented in typescript
- must have a cosmos sdk wallet, and be able to use verana types typescript library @verana-labs/verana-types
- must define an env variable for defining the BIP39 phrase for the wallet
