Build the "Participants" page.

background of the page: same color than other pages (light grey).
On the top a breadcrumbs indicating: ecosystem name, credential schema title, "Participants"
then the page title "Participants".
Then 2 cards:
1. **Permission Tree Card**  
2. **Permission Detail Card** (opens BELOW the permission tree card when a node is selected)

The layout must feel modern, structured, and scalable for very large permission sets, and it must be responsive.

## Role and Permission state Badges

- Role badges: ECOSYSTEM: text purple-800, bg purple-100, ISSUER_GRANTOR: text blue-800, bg blue-100, VERIFIER_GRANTOR: text slate-800, bg slate-100, ISSUER: text green-800, bg green-100, VERIFIER: text orange-800, bg orange-100, HOLDER: text pink-800, bg pink-100
- Permission state badges: pending approbation: bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300, expire soon: bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300, expired / revoked / inactive: bg-grey-100 text-grey-800 dark:bg-grey-900/20 dark:text-grey-300, repaid: bg-grey-100 text-red-800 dark:bg-grey-900/20 dark:text-red-300, slashed: bg-red-900 text-red-100 dark:bg-red-300/20 dark:text-red-800, active: bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300

## Permission Tree Card
background of the card must be white.
### Overview:
Displays the hierarchical permission structure with collapsible branches, lazy loading for large subsections, and scoped search inside each subtree.
### Options to tick

Show tickable options before the tree, on the right side of the card, default to none ticked.
- weight
- business rules
- stats

displays Adds-on defined below when ticked.

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
- Append on the right side of the card a small link of the same color of the icon: "join"

#### Permission tree nodes
Each permission tree node must show:

- on the left centered, the chevron that must rotates depending on expended/collapsed,
- aligned on the right of the chevron: Icon indicating authority Full control (yellow-500 crown) or Read-only (grey-500 eye) + name + Permission state badge

Append on the right side of the card, when ticked:
 + (if weight enabled: scale-balanced icon using the role badge text color and the text 234kVNA) + (if business rules enabled: coins icon using the role badge text color and the text issuance: 0.25 VNA verification: 0.25 VNA) + (if stats enabled: chart-column icon using the role badge text color and the text issued: 1234 verified: 789)

Do NOT show the role badge.

=> click on the chevron and icon authority: open/collapse only, do not select the node
=> click on the name or data located on the right of the name: select the node, do not open/collapse

All nodes of the same Role must be vertically aligned.
Nodes that display a chevron and nodes that do not must still start at the exact same horizontal position.
If a node does not have a chevron, insert a placeholder element (same width as the chevron) so that its icon and label align vertically with nodes that do have a chevron. Make sure that there is no space between nodes.

### Collapsing Rules:
- First Ecosystem Permission expanded by default
- IssuerGrantors, VerifierGrantors, Issuers, Verifiers, Holders collapsed by default. When opened,if more than 10 items, show First 10 items and “Show more…” button that loads more on demand

### Create a root permission
- Just below the last "Ecosystem Permission", add a link with icon: + new Ecosystem Permission


## Permission Detail Card
Background of the card must be white. Opens when a node is clicked. Clicked node must be highlighted on the Permission tree (slight purple background), but only put the purple background on the leaf node, not on all nodes from the tree branch.

### Content:
**Header:**
- Node name, on the right side of the card, the Role badge + the Permission state badge
- full breadcrumbs from root permission until excluding current node, example if the role of the shown node is HOLDER: show: "Holder under Ecosystem Permission 1 -> Issuer Grantor 1A -> Issuer 1", example if the role of the shown node is ISSUER: show: "Issuer under Ecosystem Permission 1 -> Issuer Grantor 1A"
- credential schema name

**Body:**
for each attribute, use data between => and ; for generating a tooltip for the corresponding attribute (tooltip shown only when I put the mouse over the attribute name, not the content. do not put a help icon). What's after the ; if present describes the button to show and their corresponding actions. All link buttons (icons + text) must be shown below their corresponding attributes. When actions are defined, they must go at the end of the section. Action button should include an icon and the action text. Each section must have a thin separator below the section name.

1. Key metadata section (maximum 2 attributes per row):
- truncated DID (hover: show full DID) (string) (monospace) => DID of the related verifiable service; icon links with hover: copy, visualizer, service.
- grantee (string) (monospace) => Verana account; links: copy,visualizer,block explorer.
- id: uint64 => id; links: copy, visualizer
- deposit: number, in VNAs => deposit
- effective_from: timestamp => effective from
- effective_until: timestamp => effective until
- country: string => country
- issued credentials: integer => issued credentials
- verified credentials: integer => verified credentials

2. Permission Lifecycle section (maximum 2 attributes per row):
- created: timestamp => date of creation
- created_by: Verana account; links: copy, visualizer, block explorer.
- modified: timestamp => modified
- modified_by: Verana account; links: copy, visualizer, block explorer.
- extended: timestamp => extended
- extended_by: Verana account; links: copy, visualizer, block explorer.
- revoked: timestamp => revoked
- revoked_by: Verana account; links: copy, visualizer, block explorer.

Lifecycle related Actions:
- Extend Permission: popup: a text explaining what will do the transaction, a form requesting user to input the new effective_until; the message that shows the approx transaction cost, cancel / confirm button. Cancel clears the popup, confirm executes the Extend Permission transaction.
- Revoke Permission: popup: short text explaining, the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes the Revoke Permission transaction.

3. Validation Process section (maximum 2 attributes per row):

show a validation process State badge: PENDING (yellow), VALIDATED (green), TERMINATED (grey) on the ride side of the card, akigned with section title
- vp_exp: timestamp => expiration of this vp
- vp_last_state_change: timestamp => date the validation process of this permission last changed state
- vp_validator_deposit: number => deposit managed by this validation process
- vp_current_fees: number => ees
- vp_current_deposit: number => deposit of this vp 
- vp_summary_digest_sri: digest_sri => checksum

Validation Process related possible Actions
- Start (Validation Process) (never shown here. Provided for the Activity Timeline only.)
- Renew (Validation Process): popup: short explanation,  the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes transaction.
- Cancel Request (Validation Process): popup: short explanation, the approx transaction cost message, cancel / confirm button. Cancel clears the popup, executes transaction.
- Accept and Set Validated (Validation Process): popup: short explanation, a form requesting user to input the validation_fees, issuance_fees, verification_fees, and the vp_summary_digest_sri (string);  the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes transaction.

4. Business Models section (maximum 3 attributes per row):
- validation_fees: number => fees
- issuance_fees: number => fees
- verification_fees: number => fees

5. Slashing (maximum 2 attributes per row):
- slashed_deposit: number => slashed
- repaid_deposit: number => repaid
- slashed: timestamp => date last slashed
- slashed_by: Verana account; links: copy, visualizer, block explorer.
- repaid: timestamp => date repaid
- repaid_by: Verana account; links: copy, visualizer, block explorer.

Slashing related Actions
- Slash Deposit: popup: short explanation showing it is a dangerous and irreversible action, the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes transaction.
- Repay Slashed Deposit: popup: short explanation, the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes transaction.

**Activity Timeline:**
Show full log of all changes(Actions named above) that have affected the permission since its creation, ordered by modified descending. Each action with the modified attributes.


## Verification
recheck that you didn't forget anything before delivering and that you comply with all instructions.