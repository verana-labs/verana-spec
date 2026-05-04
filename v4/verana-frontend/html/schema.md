# Credential Schema

Link to go back with left arrow: trust registry icon, trust registry service name

Page title:

- Credential Schema title (string), example: Organization Credetial
- Credential Schema description (string), example: A credential that represent an organization, including its logo and address.
- archived badge: if archived, show an archived badge.
- a Participants button (fa-sitemap icon mandatory).
- id (integer)
- issuer permission mode: badge: ECOSYSTEM: text purple-800, bg purple-100, GRANTOR (for issuer_perm_management_mode): text blue-800, bg blue-100, GRANTOR (for verifier_perm_management_mode): text slate-800, bg slate-100, OPEN (for issuer_perm_management_mode): text green-800, bg green-100, OPEN (for verifier_perm_management_mode): text orange-800, bg orange-100
- verifier permission mode: badge: ECOSYSTEM: text purple-800, bg purple-100, GRANTOR (for issuer_perm_management_mode): text blue-800, bg blue-100, GRANTOR (for verifier_perm_management_mode): text slate-800, bg slate-100, OPEN (for issuer_perm_management_mode): text green-800, bg green-100, OPEN (for verifier_perm_management_mode): text orange-800, bg orange-100


## Section: Mutable Configuration

- issuer grantor validity period
- verifier grantor validity period
- issuer validity period
- verifier validity period
- holder validity period

a button "Edit Configuration" that switches the Mutable Configuration to editable, and show Cancel / Confirm buttons
a button "Archive" (or "Unarchive")

## Section: Json Schema

- show the full Json Schema in a textarea. No scroll permitted (all schema must be shown). Add an icon to copy the content on the top right corner

## Consideration for the design of the page

- all content must be fully responsive
