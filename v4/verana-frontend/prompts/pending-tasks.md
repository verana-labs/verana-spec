# Pending Tasks

Build the "Pending Tasks" page.

background of the page: same color than other pages (light grey).
Page title "Pending Tasks".

Then 2 cards:
1. **Pending Actions**  
2. **Permission Detail Card** (opens BELOW the permission tree card when a node is selected)

The layout must feel modern, structured, and scalable for very large permission sets, and it must be responsive.

## Role and Permission state Badges

- Role badges: ECOSYSTEM: text purple-800, bg purple-100, ISSUER_GRANTOR: text blue-800, bg blue-100, VERIFIER_GRANTOR: text slate-800, bg slate-100, ISSUER: text green-800, bg green-100, VERIFIER: text orange-800, bg orange-100, HOLDER: text pink-800, bg pink-100
- Permission state badges: pending approbation: bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300, expire soon: bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300, expired / revoked / inactive: bg-grey-100 text-grey-800 dark:bg-grey-900/20 dark:text-grey-300, repaid: bg-grey-100 text-red-800 dark:bg-grey-900/20 dark:text-red-300, slashed: bg-red-900 text-red-100 dark:bg-red-300/20 dark:text-red-800, active: bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300

## Pending Actions Card
background of the card must be white.
### Overview:
Displays a tree-like list of Ecosystems => List of credential schemas => list of permissions with collapsible branches.

### Options to select or tick

Show select and tickable options before the tree, on the right side of the card.

- a on/off button similar to those in mobile UIs, with labels on the left and on the right of the button. Left position: label "flat". right position: label "tree".
- a tickable option called "include pending tasks of my grantees", that must appear only in "tree mode".

behavior of these option explained below.

### Flat tree mode - **Mandatory Hierarchy Structure:**

Ecosystem #A
├── Credential Schema A1
│       ├── Issuer 1
│       ├── Issuer 2
│       ├── Issuer 3
├── Credential Schema A2
│       ├── Holder 1
│       ├── Holder 2
│       ├── Holder 3
│       ├── Holder 4
Ecosystem #B
├── Credential Schema B1
│       ├── Holder 1
│       ├── Holder 2
│       ├── Holder 3
│       ├── Holder 4

### Full tree mode - **Mandatory Hierarchy Structure:**

Ecosystem #A
|- Credential Schema A1
|       |- Root Permission A1-1
│       │       ├── IssuerGrantors
│       │       │       ├── IssuerGrantor 1A
│       │       |       |     |-- Issuers
│       │       │       │     |  ├── Issuer 1
│       │       │       │     |  │     ├── Holders
│       │       │       │     |  │     |  ├── Holder A
│       │       │       │     |  │     |  └── Holder B
│       │       │       │     |  └── Issuer 2
│       │       │       └── IssuerGrantor 1B
│       │       |             |-- Issuers
│       │       └── VerifierGrantors
│       │       │       ├── VerifierGrantor X
│       │       |       |     |-- Verifiers   
│       │       │       │     |  ├── Verifier Alpha
│       │       │       │     |  └── Verifier Beta
│       │       │       └── VerifierGrantor Y
│       │       |       |     |-- Verifiers 
│       │- Root Permission A1-2
│       │       ├── IssuerGrantors
│       │       │       ├── IssuerGrantor 2A
│       │       |       |     |-- Issuers
│       │       └── VerifierGrantors

### Title
Pending Tasks - Flat Mode, or: Pending Tasks - Tree Mode

### Node Design
#### Directory nodes
Each directory (Ecosystem, Credential Schema, Root Permissions, Issuer Grantors, Verifier Grantors, Issuers, Verifiers, Holders) node must show:
- chevron that must rotate depending on expended/collapsed, directory icon with no background using the Role badge color (500), directory name + number of elements it contains. For credential schema directory icon, use color text-purple-200.

#### Permission tree nodes
Each permission tree node must show:

- on the left centered, the chevron that must rotates depending on expended/collapsed,
- aligned on the right of the chevron: Icon indicating authority Full control (yellow-500 crown) or Read-only (grey-500 eye) + name + Permission state badge

Do NOT show the role badge when in tree mode, MUST show the badge on the right of Permission state badge when in flat mode.

=> click on the chevron and icon authority: open/collapse only, do not select the node
=> click on the name or data located on the right of the name: select the node and show the permission in "Permission Detail Card" and scroll to it, do not open/collapse the node

All nodes of the same Role must be vertically aligned.
Nodes that display a chevron and nodes that do not must still start at the exact same horizontal position.
If a node does not have a chevron, insert a placeholder element (same width as the chevron) so that its icon and label align vertically with nodes that do have a chevron. Make sure that there is no space between nodes.

### Collapsing Rules:

- Everything open by default.

## Permission Detail Card

It must be exactly the same layout than for the Participants page.
