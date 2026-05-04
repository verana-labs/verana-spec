# Ecosystems

Page title: Ecosystems
Page description: Ecosystems you own and ecosystems you joined.

## Create Ecosystem

Create Ecosystem button.

## Search / filter

The following dearch filter must be on a single component, in 2 rows minimum for Desktop+ mode. May be on more rows for smaller widths.

### Row 1

- a text area for writing search attributes for filtering ecosystems shown in the list

### Row 2

- Show archived (tickbox)
- Hide owned ecosystems (tickbox)
- Hide participant ecosystems (tickbox)
- show untrusted ecosystems (tickbox)

## Ecosystem List

Ecosystem list must be shown as cards that contain the following info.

### Cards

Attribute list is ordered by importance.

- Trust registry icon (provided image is squared) (left, top of the icon aligned with Trust registry service name). Icon size: w-12, h-12.
- Trust registry service name: string, and on the same row a trust indicator icon: certificate like green icon if ecosystem is trusted, or orange warning sign like icon or red warning sign like icon if untrusted. (on the right of the Trust registry icon)
- Trust registry service description: string, xs chars, truncated if too big (on the right of the Trust registry icon)
- Organization icon (provided image is squared), (left, top of the icon aligned with Organization name). Icon size: w-8, h-8.
- Organization name: string (on the right of the Organization icon) (text size must be smaller than Trust registry service name)
- organization country flag, and on the same row EGF link (opens to new window) (on the right of the Organization icon)
- My role(s) in this Ecosystem, as a badge (ECOSYSTEM: text purple-800, bg purple-100, ISSUER_GRANTOR: text blue-800, bg blue-100, VERIFIER_GRANTOR: text slate-800, bg slate-100, ISSUER: text green-800, bg green-100, VERIFIER: text orange-800, bg orange-100, HOLDER: text pink-800, bg pink-100)
- Active Schemas: integer
- Participants: integer
- Trust Value: value in VNA
- Issued credentials: integer
- Verified credentials: integer

Finally, if ecosystem is archived, it should appear with a diagonal "Archived" watermark, and a slightly darker card background.

### Pagination

Pagination must be shown, as an example with about 15+ pages

## Consideration for the design of the page

- all content must be fully responsive
- we do not want any horizontal scroll for Ecosystem cards.
