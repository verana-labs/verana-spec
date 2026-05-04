# Ecosystem

Page title:

- Trust registry icon (provided image is squared)
- Trust registry service name: string, and on the same row a trust indicator icon: certificate like green icon if ecosystem is trusted, or orange warning sign like icon or red warning sign like icon if untrusted.
- Trust registry service description: string, xs chars, truncated if too big
- minimum age required, examples: 18+, 6+, 0+
- archived badge: if archived, show an archived badge.

## Section: Service Provider

- Organization name: (string), then on the same row a trust indicator icon: certificate like green icon if ecosystem is trusted, or orange warning sign like icon or red warning sign like icon if untrusted.
- Organization logo (provided image is squared). Must be smaller than Trust registry icon.
- organization country flag
- organization address
- organization registryId (string)
- credential issuer (did) (link to external page)

## Section: Basic Information

- id (integer)
- controller corporation (verana address)
- Primary Governance Framework Language (BCP 47 language tags)
- Active GF Version (integer)

## Section: Mutable Configuration

- did (did, example: did:example:123456789)
- aka (uri, example: https://psycho.uche.org)

a button "Edit Configuration" that switches the Mutable Configuration to editable, and show Cancel / Confirm buttons
a button "Archive" (or "Unarchive")

## Section: EGF Documents

- a button "add new EGF Document"
- a button "increase active EGF Document"
- a list of EGF document, represented by rows like this one: Version <version>: <uri> <BCP 47 language tag> <state label>

where state label is a label whch contain either:
- draft, if EGF is being created and is not active yet
- active since <date>, if this is the current active version
- from <date1> to <date2>, mean that this EGF was active between date1 to date2

contains a list of EGF Document URIs

## Section: Credential Schemas

- a New Schema button
- a tickbox "Show Archived"

Show a card for each credential schema. For each card, show:

- title (string) (example: Organization Credential). Aligned on the right and vertically, a participant icon, to go to the participant page (no need to design the participant page) (only icon, no text), and an icon to open a popup to preview the credential json schema (only icon, no text)
- description (string) (example: A credential that represent an organization, including its logo and address.)
- My role(s) in this schema, as a badge (ECOSYSTEM: text purple-800, bg purple-100, ISSUER_GRANTOR: text blue-800, bg blue-100, VERIFIER_GRANTOR: text slate-800, bg slate-100, ISSUER: text green-800, bg green-100, VERIFIER: text orange-800, bg orange-100, HOLDER: text pink-800, bg pink-100)
- Participants: integer
- issued credentials: integer
- verified credentials: integer
- Trust Value: value in VNA

Finally, if schema is archived, it should appear with a diagonal "Archived" watermark, and a slightly darker card background.

## Consideration for the design of the page

- all content must be fully responsive
