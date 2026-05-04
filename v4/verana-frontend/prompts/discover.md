# Discover & Join

Build the "Discover & Join" page.

background of the page: same color than other pages (light grey).
Page title "Discover & Join".

Then 1 section:
1. **Search Form**
2. **Ecosystem List**  

The layout must feel modern, structured, and scalable for very large permission sets, and it must be responsive.

## Filter Form

- a text field and a filter button that filter names. If nothing is set in text field, show all ecosystems.

## Ecosystem List
background of the section must be white.

### Overview:
- Displays a list of Ecosystems as Ecosystem Cards. Ecosystems are orderdered by trust deposit size descending (the biggest first).
- One card per row
- pagination at the bottom

### Ecosystem Card

the card must show:

- Ecosystem name
- Number of credential schemas
- Ecosystem trust deposit size
- a link with scale-balanced icon and the word "EGF" to open a new window
- a link with shield-halved icon and the word "view ecosystem" to open a new window
- a link with handshake icon and the word "join ecosystem" to open a new window
- the List of credential schemas, with, for each schema, a Credential Schema card. Only one Credential Schema card per row is permitted.

#### Credential Schema card

**Top of the card:**
- on the top left side of the card, credential schema name (string): name of the schema
- on the top right side of the card, with no attribute name, one or several "role badges" specifying the roles in this credential schema the connected user already has. Role badge must not have an icon.

**Middle of the card**

In the middle of the card the following attributes, ideally on the same row if fits page width, else in 2 rows:

  - Issuer Permission Management Mode (enumeration): shown as a badge: ECOSYSTEM (purple-500), GRANTOR (blue-500), or OPEN (green-500). badge must not have an icon. Attribute name must be shown. 
  - Verifier Permission Management Mode (enumeration): shown as a badge: ECOSYSTEM (purple-500), GRANTOR (slate-500), or OPEN (orange-500). badge must not have an icon. Attribute name must be shown.

**Bottom of the card**
  - on the bottom left side of the card, number of participants (integer): show an icon, an the number of participants, no attribute name.
  - on the bottom right side of the card, a link with eye icon and the word "view schema" to open a new window


**Note**

"role badge" colors: ECOSYSTEM: text purple-800, bg purple-100, ISSUER_GRANTOR: text blue-800, bg blue-100, VERIFIER_GRANTOR: text slate-800, bg slate-100, ISSUER: text green-800, bg green-100, VERIFIER: text orange-800, bg orange-100, HOLDER: text pink-800, bg pink-100