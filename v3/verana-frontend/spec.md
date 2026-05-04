# Verana Frontend v3 Specification

**Specification Status:** Pre-Draft


## About this Document

This specification is for the Verana Network frontend, a container-based App easily deployable locally, or in any modern cloud infrastructure.

## Introduction

*This section is non-normative.*

## Specification

### [GENERAL] General

The Verana App MUST be delivered as a container.

#### [GENERAL-DEPLOYMENT] General - Deployment

- [GENERAL-DEPLOYMENT-HUB] Container MUST be versioned and deployed to docker hub.
- [GENERAL-DEPLOYMENT-DOCKER] Documentation for running the container with docker MUST be provided.
- [GENERAL-DEPLOYMENT-KUBE] Documentation for deploying the container in Kubernetes MUST be provided.
- [GENERAL-DEPLOYMENT-HELM] Verana App MUST be installable in Kubernetes by using helm install. Documentation MUST be provided.
- [GENERAL-DEPLOYMENT-LAMBDA] Verana App MUST be runnable in Amazon Lambda. Documentation MUST be provided.

#### [GENERAL-ENV] General - Container Variables

| Type                           |Variable                               | Description                    | Default Value (if unspecified)                    |
|--------------------------------|---------------------------------------|----------------------------------|----------------------------------|
| General                        | APP_NAME                              |                                  | Veranito                         |
|                                | APP_LOGO                              |                                  | logo.svg                        |
|                                | ADDRESS_EXPLORER                      |                                  | https://explorer.verana.network/Verana%20Mainnet/account/VERANA_ADDRESS   |
| Network Configuration          | API_ENDPOINT                  |                                  | https://api.verana.network       |
|                                | RPC_ENDPOINT                  |                                  | https://rpc.verana.network       |
|                                | IDX_ENDPOINT                  |                                  | https://idx.verana.network       |
|                                | CHAIN_ID                      |                                  | vna-mainnet-1       |
|                                | CHAIN_NAME                          |                                  | Mainnet       |
|                                | TOPUP_VS                      |   List of VSs for top-up       | did:example:123, did:example:456       |
| Internationalization           | DEFAULT_LOCALE                        |   Failover locale | en_US       |
|                                | SUPPORTED_LOCALES                     |                                  | en_US, fr_FR, en:en_US, fr:fr_FR       |
|                                | SESSION_LIFETIME_SECONDS                     |                                  | 86400       |
|                                | SHOW_PERMISSION_EXPIRE_BEFORE_DAYS                     |                                  | 30       |

#### General - Fee Calculation and Preview

As mentioned in [this issue](https://github.com/verana-labs/verana-blockchain/issues/98)

Front end must calculate an estimation of trust fees in **Trust Unit** and use `trust_unit_price`, `trust_deposit_rate`, `user_agent_reward_rate`  + `wallet_user_agent_reward_rate` to calculate trust fees.

1. For DID directory create/renew: value is set as a global variable `did_directory_trust_deposit` 
2. For trust registry creation: `trust_registry_trust_deposit` 
3. For Credential Schema: `credential_schema_trust_deposit`
4. For Start Permission / Renew Permission: for the selected validator permission, `Permission. validation_fees` + `trust_deposit_rate`%
5. Session: use query method `Find Beneficiaries`, and add `trust_deposit_rate + user_agent_reward_rate  + wallet_user_agent_reward_rate `%

> Plus **gas fees** obviously.

Other methods have just **gas fees**. Gas fee estimation depends on the size of the sent message. Default might be enough - this spec does not define how to calculate gas fee, but how to calculate required trust fee / deposit.

#### General - Internationalization

[GENERAL-I18N-DEFAULT]

[GENERAL-I18N-LOCALE-DATA] All texts, labels, rollover texts, images with texts, videos, sounds, text icons MUST be centralized in a directory per locale

[GENERAL-I18N-CONTENT-KEY] Each content MUST be identified by its key, `content_key`.

[GENERAL-I18N-RENDER-CONTENT] Render content from `content_key`:

Get `locale` from `settings.locale` from user settings. If null, use `locale` from user agent.

- find content with its `content_key` for locale `locale`
- if not found, try to use the default locale for the same language. So if `locale` is equal to `en_GB`, look for entry en:... in `SUPPORTED_LOCALES` to get default locale for `en`.
- else fallback to `DEFAULT_LOCALE` (normally `en_US`).

:::note
At least the content of the default locale MUST be provided by development/design team.
Default locale for development MUST be en_US.
:::

:::warning
Right to left text (like Arabic) MUST be supported.
:::

#### [GENERAL-LAYOUT] General - Layout

[GENERAL-LAYOUT-RESPONSIVE] App MUST be usable from any device, layout MUST be responsive.

[GENERAL-LAYOUT-HEADER] Header MUST include a squared App logo and App name on the left side, and on the right side the setting icon, a dark/light mode, and a crypto account zone. Optionally, if layout is very small, a Menu hamburger icon CAN appear on te left side of the header, and the App name MAY disappear.

[GENERAL-LAYOUT-FAVICON]
Package available in [favicons directory](favicons/). Add all including the site.webmanifest.

##### Header - Not Connected

![layout-header-not-connected](assets/layout-header-not-connected.png)

##### Header - Connected

![layout-header-connected](assets/layout-header-connected.png)

##### Header - Crypto account details

![layout-header-crypto-account](assets/layout-header-crypto-account.png)

[GENERAL-LAYOUT-MENU] On the left size, a menu. When size of window is small, menu is hidden and a hamburger icon appears for showing the menu.

[GENERAL-LAYOUT-MENU-NORMAL]

![normal menu](assets/layout-menu-normal.png)

[GENERAL-LAYOUT-MENU-SMALL]

![small menu](assets/layout-menu-small.png)

[GENERAL-LAYOUT-MENU-SMALL-OPENED]

![small menu - opened](assets/layout-menu-small-opened.png)

[GENERAL-LAYOUT-CONTENT] The content zone.

![content zone](assets/layout-content-zone.png)

### Menu

[MENU] Menu entries:

- Dashboard (default page): go to Dashboard  => [DASHBOARD]
- Account (user MUST be connected to see this menu entry) => [ACCOUNT-MAIN]
- DID Directory (user MUST be connected to see this menu entry) => [DIDS-LIST-DIDS-I-CONTROL]

### Crypto Wallet Integration

#### Crypto Wallet Integration - General

[CW-GENERAL-KIT]  Use a kit such as the [interchain-kit repo](https://github.com/hyperweb-io/interchain-kit) to easily integrate any wallet to the Verana App.

[CW-CONNECT-WALLET]

If user reaches the App through any URL of the App, and if a detected installed wallet is found and it has been already granted, App MUST connect to it immediately with no user intervention. (same will happen if I am connected and I reload the page in my browser).

- read the doc of interchain-kit or any other library you want to use
- detect any installed wallet extension, and put them in the "Detected Installed Wallets" section.
- show available mobile wallets, in the "Mobile Wallets" section
- show available non mobile wallets not detected, in the "Other Wallets" section

![connect wallet](assets/cw-main.png)

#### Crypto Wallet - Browser Extension

[CW-CONNECT-WALLET-EXT]

Follow kit instructions and be inventive. Example mockup:

![connect wallet ext](assets/cw-connect-ext.png)

#### Crypto Wallet - Connect with Mobile

[CW-CONNECT-WALLET-MOB]

Follow kit instructions and be inventive. Example mockup:

![connect wallet mobile](assets/cw-connect-mobile.png)

#### Crypto Wallet - Connected

[CW-CONNECT-WALLET-CONNECTED]

Redirect user to where he was before connecting.

![just connected](assets/cw-justconnected.png)

### Dashboard

[DASHBOARD]

- show the network I am connect to (as selected in settings)
- show the block height
- If user is not connected, show a button "connect wallet"

![dashboard-not connected](assets/dashboard-notconnected.png)

![dashboard-not connected](assets/dashboard-connected.png)

### Crypto Transaction execution

[CRYPTO-TRANSACTIONS-DISPLAY-ZONE]

When a transaction is executed, it MUST be always shown as a popup. Transaction info (a text, _renew DID did:example:abc_ in the example below) MUST be passed as a description so that the display text can be shown in the popup.

![display zone](assets/transaction-display-zone.png)

[CRYPTO-TRANSACTIONS-EXEC] When executing a transaction:

- `Transaction in progress` MUST be shown with message "Your transaction _renew DID did:example:abc_ is being broadcasted to the network".
- when transaction ID is known, message should change to "Your transaction _renew DID did:example:abc_ is being processed [link](https://mintscan.com)" with a link to the transaction explorer.

![pending](assets/transaction-pending.png)

[CRYPTO-TRANSACTIONS-SUCCESS] when transaction is successful:

![success](assets/transaction-success.png)

[CRYPTO-TRANSACTIONS-ERROR] when error:

![error](assets/transaction-error.png)

### Account

[ACCOUNT-MAIN]

Account shows balances:

- Main balance
- Trust Deposit balance

and 3 use cases:

- Main Balance > get VNA: to top-up crypto account main balance.
- Trust Deposit > claim interests: to collect my Trust Deposit interests and receive them in my main balance. Use [MOD-TD-MSG-2] from verifiable-trust-vpr-spec.
- Trust Deposit > reclaim deposit: to get back claimable deposit, if any. Use [MOD-TD-MSG-3] from verifiable-trust-vpr-spec.

![account](assets/account.png)

Header Actions

- [ACCOUNT-HEADER-ACTIONS-QR] show QR of my account address
- [ACCOUNT-HEADER-ACTIONS-COPY] copy my account address
- [ACCOUNT-HEADER-ACTIONS-EXPLORE] show in configured explorer (`ADDRESS_EXPLORER`) (opens in new window)
- [ACCOUNT-HEADER-ACTIONS-LOGOUT] disconnect wallet

#### Account - Get VNA

Present a list of services to top-up my verana account.

The list of the services is configurable in variables `*TOPUP-VS` which depends on network. Use this list of service to generate a radio button type select. 

- [ACCOUNT-GET-VNA-RESOLVE-VS] Selected Verifiable Service MUST be trust resolved to get service name (service credential) and organization name (organization credential) shown in service description text, and get supported payment methods to show related icons.

- [ACCOUNT-GET-VNA-QR] MUST show a QR code for connecting to it and passing the vna account address as a parameter. User then scans the service with Hologram and follow instructions to top-up his/her account.

![account](assets/account-get-vna.png)

#### Account - Claim Interests

[ACCOUNT-TD-CLAIM-INTERESTS] If interests are available, user sees the text and the cancel / confirm buttons like in mockup. Else, show text "You do not have interests to claim yet." with no buttons.

![account](assets/account-claim.png)

#### Account - reclaim TD

[ACCOUNT-TD-RECLAIM] If reclaimable trust deposit is not equal to 0, user sees the text, confirm check, and the cancel / confirm buttons like in mockup. Else, show text "You do not have reclaimable trust deposit." with no check box and no buttons.

![account](assets/account-reclaim.png)

### Settings

All customized settings MUST be persisted in browser session.

[SETTINGS-MAIN] The Settings page MUST be shown when user hits the settings icon in header. Settings include 2 sections: General and Networks. Settings MUST work even if user is not connected.

![settings](assets/settings.png)

#### Settings - General

[SETTINGS-GENERAL-LOCALE-SELECT] Default to user agent presented locale "Browser Default" which sets `settings.locale` to  NULL (undefined). User can force a locale here and store it to `settings.locale`. Locale list MUST contain all supported locales. Changing locale does not require any confirmation and is immediate.

![alt text](assets/settings-general.png)

### DID Directory

#### List DIDs

[DIDS-LIST-RESULTS]

- search results are clickable and lead to DID info use case.
- search result pagination MUST be managed by frontend, as we can assume a given account will not have tons of DIDs, and because we want to be able to order result by clicking columns.

When screen size is reduced, column are progressively eliminated, in this order:

- created
- deposit
- controller
- modified

DID and expire MUST be shown always.

[DIDS-LIST-QUERY-PERSISTENCE]

By default, Did query option is preselected with "Show DIDs I control / All DIDs". When user customizes the query, query is persisted in user session. If user go to DID Info by clicking a result row, and go back to list using the browser "back" or clicks "back to directory" from other DID screens, query is loaded from session. If user hits the "DID Directory" menu, query session is cleared.  

[DIDS-LIST-DIDS-I-CONTROL]

- filters are self-explained (see [MOD-DD-QRY-1] List DIDs in VPR spec)

![list I control](assets/dids-search-list-i-control.png)

[DIDS-LIST-SEARCH-DID]

- User MUST write the full DID in order to do a search. Due to backend limitations, only the full DID name can be specified, subtext search is not supported. A better version will be specified when idx endpoint will be available.
- If a result is returned, save this DID in session so that we can use auto-completion when user wants to search again the same DID
- If a DID is in session but a new search doesn't return anything (removed DID), remove it from session.

![alt text](assets/dids-search-did.png)

[DIDS-LIST-FOR-CONTROLLER]

- controller is mandatory
- other filters are self-explained (see [MOD-DD-QRY-1] List DIDs in VPR spec)

![list for controller](assets/dids-search-list-for-controller.png)

#### DID Infos

[DIDS-DID-INFOS] Show DID infos and Action use cases:

- renew
- touch
- remove

![did infos](assets/dids-did-info.png)

#### Add a DID

[DIDS-DID-ADD] Adds a DID to the Directory. Use [MOD-DD-MSG-1-2-2] from VPR spec to estimate approx transaction cost.

- CANCEL: go back to where I was, with the same search filters
- CONFIRM: execute transaction, show transaction status until successful. If successful, go to DID Info.
- back to directory: return to DID directory, with current search filter (stored in session)

![add a DID](assets/dids-add.png)

#### Renew a DID

[DIDS-DID-RENEW] Renew a DID. Use [MOD-DD-MSG-2-2-2] from VPR spec to estimate approx transaction cost.

- CANCEL: close renew section
- CONFIRM: execute transaction, show transaction status until successful. If successful, refresh DID info data (without reloading page).
- back to directory: return to DID directory, with current search filter (stored in session)

![renew a DID](assets/dids-did-renew.png)

#### Touch a DID

[DIDS-DID-TOUCH] Renew a DID. Use [MOD-DD-MSG-4-2-2] from VPR spec to estimate approx transaction cost.

- CANCEL: close touch section
- CONFIRM: execute transaction, show transaction status until successful. If successful, refresh DID info data (without reloading page).
- back to directory: return to DID directory, with current search filter (stored in session)

![touch a DID](assets/dids-did-touch.png)

#### Remove a DID

[DIDS-DID-REMOVE] Renew a DID. Use [MOD-DD-MSG-3-2-2] from VPR spec to estimate approx transaction cost.

- CANCEL: close remove section
- CONFIRM: execute transaction, show transaction status until successful. If successful, return to DID directory, with previous search filter stored in session.
- back to directory: return to DID directory, with current search filter (stored in session)

![remove a DID](assets/dids-did-remove.png)

### Trust Registries

#### List Trust Registries

[TR-LIST-RESULTS]

When screen size is reduced, column are progressively eliminated, in this order:

- created
- deposit
- controller
- modified

DID and expire MUST be shown always.

![List Trust Registries](assets/tr-list.png)

#### Add a Trust Registry

[TR-NEW] Adds a Trust Registry.

When user confirms:

- CONFIRM: as it is required when executing the method for creating the trust registry, governance framework document must be downloaded, and its digest_sri calculated. See [mod-tr-msg-1-create-new-trust-registry](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-tr-msg-1-create-new-trust-registry). Execute transaction, show transaction status until successful. If successful, go to Trust Registry Info.

- CANCEL: go back to where I was

![new Trust Registry](assets/tr-new.png)

#### Trust Registry Infos - Basic Information

[TR-INFOS] Show Trust Registry infos. To switch to edit user hits the "edit" icon.

![alt text](assets/tr-infos-basic.png)

Edit:

[mod-tr-msg-4-update-trust-registry](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-tr-msg-4-update-trust-registry)

![alt text](assets/tr-infos-basic-edit.png)

:::note
primary governance framework language cannot be modified
:::

#### Trust Registry - Add Governance Framework Document

[TR-EGF-ADD-DOC] Add EGF document.

When user confirms:

- CONFIRM: as it is required when executing the method for creating the trust registry, governance framework document must be downloaded, and its digest_sri calculated. See [mod-tr-msg-2-add-governance-framework-document](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-tr-msg-2-add-governance-framework-document). Execute transaction, show transaction status until successful. If successful, stay on the same view and refresh next version table content.

- CANCEL: collapse and clear form.

#### Trust Registry - Set EGF version active

[TR-EGF-SET-ACTIVE] Set EGF version active.

When user confirms:

- CONFIRM: execute the [mod-tr-msg-3-increase-active-governance-framework-version](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-tr-msg-3-increase-active-governance-framework-version) show transaction status until successful. If successful, stay on the same view and refresh view.

- CANCEL: collapse.

#### Trust Registry - Credential Schema List

Show existing Credential Schemas for this Trust Registry ordered by id desc, with a link for creating a new Credential Schema at the top.

[TR-CS-LIST]

![TR CS List](assets/tr-cs-list.png)

#### Trust Registry - New Credential Schema

Create a new Credential Schema

[TR-CS-NEW]

![TR CS New1](assets/tr-cs-new1.png)

part2:

![TR CS New2](assets/tr-cs-new2.png)

When user confirms:

- CONFIRM: [mod-cs-msg-1-create-new-credential-schema](https://verana-labs.github.io/verifiable-trust-vpr-spec/#mod-cs-msg-1-create-new-credential-schema). Execute transaction, show transaction status until successful. If successful, stay on the same view and refresh to [TR-CS-VIEW].

- CANCEL: collapse and clear form.

#### Trust Registry - View Credential Schema

[TR-CS-VIEW]

Do not show permissions yet.

![TR CS View](assets/tr-cs-view.png)
