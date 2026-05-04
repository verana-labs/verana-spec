> important: these rules must be applied each time a permission card is shown, for any view that include permission cards.

## Conventions

- Grantee permission: a permission which `permission.grantee` is equal to the account that is manipulating the frontend.
- Validator permission: the permission, obtained by getting permission referred by a grantee permission as `permission. validator_perm_id`.

see [permission tree](https://verana-labs.github.io/verifiable-trust-vpr-spec/#credential-schemas-and-permissions).

## Where are permission cards used

Permission cards are used at least in the following existing/future components:

- Credential Schemas => My Permissions
- Credential Schemas => My Grantees
- Pending Tasks

## Design

A new design has been delivered for permission cards. This design is very similar to previous one, but has several improvement, such as a row-like presentation, which provides better UX.

<img width="1196" height="447" alt="Image" src="https://github.com/user-attachments/assets/0e41d5d5-0085-4624-b2db-32825c4e69c4" />

Design is available here: https://verana-labs.github.io/verana-frontend-spec/templates/permissions-improved.html

Few notes:

- for labels (expired, slashed, etc... refer to issue #142 

## Actions (3 dot menu)

- actions depend on my role in a given permission. I can be: the grantee, or the validator. See below based on my role the possible actions on the 3 dot menu.

### Actions to show in menu - Case #1

**CASE 1: I am the grantee of the permission (perm.grantee == verana account using the front)**

> **Important**: match ALL conditions.
> make sure to understand what is a valid permission as explained [in spec](https://verana-labs.github.io/verifiable-trust-vpr-spec/#terminology)
>
>**valid permission**:
>
>For a given country code, a credential schema permission of a given type, which (country attribute is null or equals to the given country code), and effective_from timestamp is lower than current timestamp, and (effective_until timestamp is null or greater than current timestamp), and revoked is null and slashed is null.

|permission type|schema issuer mode| schema verifier mode|slashed|repaid| revoked | expired| vp_state| vp_exp|renew|cancel request|revoke|extend|repay|
|----------------|--------------------|----------------------|--------|-------|---------|--------|---------|--------|---------|---------|---------|---------|---------|
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|null|null|null| any| VALIDATED| any|yes, if and only if **validator permission** (NOT this permission) is a valid permission| no| yes, if and only if grantee permission (this permission) is a **valid permission** | no |no |no |
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|yes|null|any| any| any| any|no| no| no | no | yes |
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|yes|yes|any| any| any| any|no| no| no | no | no |
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|null|null|null| any| PENDING| any|no| yes| no | no | no |
|ISSUER|OPEN|any|null|null|null| any| null| null|no| no| yes, if and only if grantee permission (this permission) is a **valid permission** | yes, only if effective_until is not null | no |
|ISSUER|OPEN|any|yes|null|any| any| any| any|no| no| no | no | yes |
|ISSUER|OPEN|any|yes|yes|any| any| any| any|no| no| no | no | no |
|HOLDER|any|any|null|null|null| any| VALIDATED| any|yes, if and only if **validator permission** (NOT this permission) is a valid permission| no| yes, if and only if grantee permission (this permission) is a **valid permission** | no | no |
|HOLDER|any|any|yes|null|any| any| any| any|no| no| no | no | yes |
|HOLDER|any|any|yes|yes|any| any| any| any|no| no| no | no | no |
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|null|null|null| any| VALIDATED| any|yes, if and only if **validator permission** (NOT this permission) is a valid permission| no| yes, if and only if grantee permission (this permission) is a **valid permission** | no | no|
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|yes|null|any| any| any| any|no| no| no | no | yes |
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|any|yes|yes|any| any| any| any|no| no| no | no | no |
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|any|null|null| any| PENDING| any|no| yes| no | no | no |
|VERIFIER|any|OPEN|null|null|null| any| null| null|no| no| yes, if and only if grantee permission (this permission) is a **valid permission** | yes, only if effective_until is not null | no |
|VERIFIER|any|OPEN|yes|null|any| any| any| any|no| no| no | no | yes |
|VERIFIER|any|OPEN|yes|yes|any| any| any| any|no| no| no | no | no |
|ECOSYSTEM|any|any|null|null|null| any| null| null|no| no| yes, if and only if grantee permission (this permission) is a **valid permission** | yes, only if effective_until is not null | no |
|ECOSYSTEM|any|any|yes|null|any| any| any| any|no| no| no | no | yes |
|ECOSYSTEM|any|any|yes|yes|any| any| any| any|no| no| no | no | no |

### Actions to show in menu - Case #2

**CASE 2:**

- verana account using the front is an ancestor of the permission (a validator in the permission branch until the root permission (GRANTOR, ECOSYSTEM, OPEN schema mode)).
- verana account using the front is the TrustRegistry controller (owner of the credential schema).

|permission type|schema issuer mode| schema verifier mode|     slashed|repaid| revoked | expired|   vp_state| vp_exp|   set validated|revoke|slash
|----------------|--------------------|----------------------|--------|-------|---------|--------|---------|--------|---------|---------|---------|
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|    null| null| any | any|       any| any|    no | no | yes |
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|    null| null| null | none (effective_until null or > now())|       any| any|    no | yes | yes |
|ISSUER_GRANTOR, ISSUER|GRANTOR, ECOSYSTEM|any|    null|null|null| null|           PENDING| any| yes| no | no |
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|    null| null| any | any|       any| any|    no | no | yes |
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|    null| null| null | none (effective_until null or > now())|       any| any|    no | yes | yes |
|VERIFIER_GRANTOR, VERIFIER|any|GRANTOR, ECOSYSTEM|    null|null|null| null|           PENDING| any| yes| no | no |
|HOLDER|any|any|    null| null| any | any|       any| any|    no | no | yes |
|HOLDER|any|any|    null| null| null | none (effective_until null or > now())|       any| any|    no | yes | yes |
|HOLDER|any|any|    null|null|null| null|           PENDING| any| yes| no | no |
|ECOSYSTEM|any|any|    null| null| null | none (effective_until null or > now())|       any| any|    no | yes | no |

## Behavior of menu actions

Use a popup similar to the add governance framework document

- action show a popup
- form (see below)
- price to pay, and if user has sufficient balance to execute the transaction, a confirm button
- execute the transaction and show the transaction mini popup
- refresh the component when transaction completes.

### Renew

- Renew [[MOD-PERM-MSG-2]](https://github.com/verana-labs/verana-frontend/issues/new#mod-perm-msg-2-renew-permission-vp)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;

### Cancel Validation Request

- Cancel Request [MOD-PERM-MSG-6](https://github.com/verana-labs/verana-frontend/issues/new#mod-perm-msg-6-cancel-permission-vp-last-request)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;

### Revoke Permission

- Revoke  [MOD-PERM-MSG-9](https://github.com/verana-labs/verana-frontend/issues/new#mod-perm-msg-9-revoke-permission)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;

### Extend Permission

- Extend [MOD-PERM-MSG-8](https://github.com/verana-labs/verana-frontend/issues/new#mod-perm-msg-8-extend-permission)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;
- `effective_until` (timestamp) (*mandatory*): timestamp until when (exclusive) this `Permission` should be effective.

### Set Validated (Accept Request)

- Set Validated [MOD-PERM-MSG-3](https://github.com/verana-labs/verana-frontend/issues/new#mod-perm-msg-3-set-permission-vp-to-validated)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;
- `effective_until` (timestamp) (*optional*): timestamp until when (exclusive) this `Permission` is effective, null if no time limit should been set for this permission or if we want it to be aligned with the validation process expiration timestamp calculated by this method.
- `validation_fees` (number) (*optional*): Agreed validation_fees for this permission. Can be set only the first time this method is called (cannot be set for renewals).
- `issuance_fees` (number) (*optional*): Agreed issuance_fees for this permission. Can be set only the first time this method is called (cannot be set for renewals).
- `verification_fees` (number) (*optional*): Agreed verification_fees for this permission. Can be set only the first time this method is called (cannot be set for renewals).
- `country` (string) (*optional*): country, as an alpha-2 code (ISO 3166), this permission refers to. If null, it means permission is not linked to a specific country. Can be set only the first time this method is called (cannot be set for renewals).
- `vp_summary_digest_sri` (digest_sri) (*optional*): an optional digest_sri, set by [[ref: validator]], of a summary of the information, proofs... provided by the [[ref: applicant]].

### Slash Deposit

- Slash [MOD-PERM-MSG-12] (https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-perm-msg-12-slash-permission-trust-deposit)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;

### Repay Slashed Deposit

- Repay slashed trust deposit [MOD-PERM-MSG-13] (https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-perm-msg-13-repay-permission-slashed-trust-deposit)

**form parameters:**

- `id` (*mandatory*) (hidden): id of the validation process / permission;
