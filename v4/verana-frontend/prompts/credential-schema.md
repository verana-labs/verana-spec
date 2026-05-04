# Build the Credential Schema page

background of the page: same color than other pages (light grey).
On the top a breadcrumbs indicating: ecosystem name, credential schema title
then the page title "Credential Schema" and a description "View and manage this Credential Schema"
Then 1 card: **Credential Schema Card**

The layout must feel modern, structured, and scalable for very large permission sets, and it must be responsive.

## Role and Permission state Badges

- perm_management_mode badges: ECOSYSTEM: text purple-800, bg purple-100, GRANTOR (for issuer_perm_management_mode): text blue-800, bg blue-100, GRANTOR (for verifier_perm_management_mode): text slate-800, bg slate-100, OPEN (for issuer_perm_management_mode): text green-800, bg green-100, OPEN (for verifier_perm_management_mode): text orange-800, bg orange-100

## Credential Schema Card
background of the card must be white.


### Content:

**Header:**
- Schema Name
- Schema Description
- On the top right side, a link with a fa-sitemap icon and label "Participants"

**Body:**
for each attribute, use data between => and ; for generating a tooltip for the corresponding attribute (tooltip shown only when I put the mouse over the attribute name, not the content. do not put a help icon). What's after the ; if present describes the button to show and their corresponding actions. All link buttons (icons + text) must be shown below their corresponding attributes. When actions are defined, they must go at the end of the section. Action button should include an icon and the action text. Each section must have a thin separator below the section name.

1. Basic Information (maximum 2 attributes per row):

- id (number) => credential schema Id
- state (enumeration, ENABLED, ARCHIVED) => Schema state. ENABLED means
- issuer_perm_management_mode (Enumeration, ECOSYSTEM, GRANTOR or OPEN)  =>  TRUST_REGISTRY, GRANTOR means a validation process is needed to obtain an Issuer or Issuer Grantor permission. OPEN means no approval is needed for joining the Ecosystem as Issuer. Use colored label for value: TRUST_REGISTRY: green, GRANTOR: blue, OPEN: light blue
- verifier_perm_management_mode (Enumeration, TRUST_REGISTRY, GRANTOR or OPEN) =>  TRUST_REGISTRY, GRANTOR means a validation process is needed to obtain an Verifier or Verifier Grantor permission. OPEN means no approval is needed for joining the Ecosystem as Verifier. Use colored label value. Use colored label for value: TRUST_REGISTRY: green, GRANTOR: blue, OPEN: light blue

Basic Information related Actions:
- Archive: if state is ENABLED, schema can be archived. Click generates popup: short text explaining, the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes the Archive Credential Schema transaction.
- Unarchive: if state is ARCHIVED, schema can be unarchived. Click generates popup: short text explaining, the approx transaction cost message, cancel / confirm button. Cancel clears the popup, confirm executes the Unarchive Credential Schema transaction.

2. Mutable Configuration section (maximum 2 attributes per row):

- issuer_grantor_validation_validity_period (number) => Validity Period, in days, of a permission granted to an Issuer Grantor.
- verifier_grantor_validation_validity_period (number) => Validity Period, in days, of a permission granted to a Verifier Grantor.
- issuer_validation_validity_period (number) => Validity Period, in days, of a permission granted to an Issuer.
- verifier_validation_validity_period (number) => Validity Period, in days, of a permission granted to a Verifier.
- holder_validation_validity_period (number) => Validity Period, in days, of a permission approved by an Issuer Grantor to an Issuer.

Mutable Configuration related Actions:
- Edit: set all attributes of this section editable, short text explaining, the approx transaction cost message, cancel / confirm button. Cancel revert back to not-editable view with the edit button, confirm executes the Update Credential Schema transaction with the set values. After transaction execution, show normal view (not editable) for this section.

3. Json Schema

- json_schema => The Json Schema of this Credential Schema, in a scrollable textarea, pretty view. Put a "copy" link to copy json_schema content, that show a tooltip "copied to clipboard" when I click it.


**Activity Timeline:**
Show full log of all changes(Actions named above) that have affected the schema since its creation, ordered by modified descending. Each action with the modified attributes.

## Verification
recheck that you didn't forget anything before delivering and that you comply with all instructions.
