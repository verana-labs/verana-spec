# My Services

Build the "My Services" page.

background of the page: same color than other pages (light grey).
Page title "My Services".
small summary below the title: "Manage your Verifiable Services"

Then 1 section:
1. **Search Form**
2. **Service List**  

The layout must feel modern, structured, and scalable for very large service sets, and it must be responsive.

## Filter Form

- a text field and a filter button that filter by DID. If nothing is set in text field, show all services.

## Service List
background of the section must be white.

### Overview:
- Displays a list of Services as Service Cards. Service are ordered by last modified datetime descending (the most recently modified first).
- One card per row
- pagination at the bottom

### Service Card

the card must show:

If both either of the two Service and Organization credentials are self-signed: show a yellow icon meaning the service is not verifiable. Else show a green icon that means service is verifiable.

**Infos**
- Service DID
- Service icon
- Service name
- Service description
- link to terms and conditions
- link to privacy policy
- minimum age required

**Ownership**
- Organization name (service owner)
- Organization company registry ID
- Organization country

**Stats**
- number of connections
- number of issued credentials
- number of verified credentials
- trust deposit size

**Additional credentials**
- if the service has additional credentials presented in this DID Document, they should appear as a list. Each list item is clickable and open the credential in a new window