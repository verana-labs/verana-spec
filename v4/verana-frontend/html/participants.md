# Participants 

Link to go back with left arrow: trust registry icon, trust registry service name

Page title:

- Credential Schema title (string), example: Organization Credetial
- Credential Schema description (string), example: A credential that represent an organization, including its logo and address.
- archived badge: if archived, show an archived badge.

## Section: Permission Tree Card
background of the card must be white.
### Overview:
Displays the hierarchical permission structure with collapsible branches, lazy loading for large subsections, and scoped search inside each subtree.

### **Mandatory Hierarchy Structure:**

Ecosystem Permission 1
├── IssuerGrantors
│       ├── IssuerGrantor 1A
|       |     |-- Issuers
│       │     |  ├── Issuer 1
│       │     |  │     ├── Holders
│       │     |  │     |  ├── Holder A
│       │     |  │     |  └── Holder B
│       │     |  └── Issuer 2
│       └── IssuerGrantor 1B
|             |-- Issuers
└── VerifierGrantors
│       ├── VerifierGrantor X
|       |     |-- Verifiers   
│       │     |  ├── Verifier Alpha
│       │     |  └── Verifier Beta
│       └── VerifierGrantor Y
|       |     |-- Verifiers 
Ecosystem Permission 2
├── IssuerGrantors
│       ├── IssuerGrantor 2A
|       |     |-- Issuers
└── VerifierGrantors

### Title
Permission Tree
### Node Design
#### Directory nodes
Each directory (Issuer Grantors, Verifier Grantors, Issuers, Verifiers, Holders) node must show:
- chevron that must rotate depending on expended/collapsed, directory icon with no background using the Role badge color (500), directory name + number of elements it contains.
- Append on the right side of the card a small link of the same color of the icon: "join", with on the left an handshake fa icon of the same color, and on the left a badge saying either "validation process" or "open", and of the same color.

#### Permission tree nodes
Each permission tree node must show:

- on the left centered, the chevron that must rotates depending on expended/collapsed,
- aligned on the right of the chevron: Icon indicating authority Full control (yellow-500 crown) or Read-only (grey-500 eye) + Service icon (provided image is squared) + Service name: string, + Organization icon (provided image is squared) + Organization name: string, plus organization country (flag), and on the same row a trust indicator icon: certificate like green icon if ecosystem is trusted, or orange warning sign like icon or red warning sign like icon if untrusted + Permission state badge

Do NOT show the role badge.

=> click on the chevron and icon authority: open/collapse only, do not select the node
=> click on the name or data located on the right of the name: select the node, do not open/collapse

All nodes of the same Role must be vertically aligned.
Nodes that display a chevron and nodes that do not must still start at the exact same horizontal position.
If a node does not have a chevron, insert a placeholder element (same width as the chevron) so that its icon and label align vertically with nodes that do have a chevron. Make sure that there is no space between nodes.

## Consideration for the design of the page

- Role badges: ECOSYSTEM: text purple-800, bg purple-100, ISSUER_GRANTOR: text blue-800, bg blue-100, VERIFIER_GRANTOR: text slate-800, bg slate-100, ISSUER: text green-800, bg green-100, VERIFIER: text orange-800, bg orange-100, HOLDER: text pink-800, bg pink-100
- Permission state badges: pending approbation: bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300, expire soon: bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300, expired / revoked / inactive: bg-grey-100 text-grey-800 dark:bg-grey-900/20 dark:text-grey-300, repaid: bg-grey-100 text-red-800 dark:bg-grey-900/20 dark:text-red-300, slashed: bg-red-900 text-red-100 dark:bg-red-300/20 dark:text-red-800, active: bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300
