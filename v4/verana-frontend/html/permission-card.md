## Permission Card

### Content:

**Header:**

Title: Issuer role for schema Organization Credential. on the right side of the card, the Role badge + the Permission state badge

Granted Service:
- Service name, trust indicator icon: certificate like green icon if ecosystem is trusted, or orange warning sign like icon or red warning sign like icon if untrusted., service icon (provided image is squared), Severice description. Age restriction (ex: 18+, 8+, 0+), link (icon only) to term and conditions, link (icon only) to privacy policy.
Granted Service Provider:
- Organization name: (string), then on the same row a trust indicator icon: certificate like green icon if ecosystem is trusted, or orange warning sign like icon or red warning sign like icon if untrusted.
- Organization logo (provided image is squared). Must be smaller than Trust registry icon.
- organization country flag

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

**Activity Timeline:**
Show full log of all changes(Actions named above) that have affected the permission since its creation, ordered by modified descending. Each action with the modified attributes.
