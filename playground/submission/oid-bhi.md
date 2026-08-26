# Verifiable Hiring — Better Hiring Institute

> **Playground use case source.** Four pages, mirroring the Vesta Appliances structure:
> `/usecases/bhi` · `/usecases/bhi/solution` · `/usecases/bhi/journey` · `/usecases/bhi/demos`
>
> Draft v4. Two quotes await sign-off and are marked. Nothing referencing the Orchestrating Identity–Verana relationship should be published before that agreement is signed.

---

<!-- PAGE 1 — /usecases/bhi -->

## Chapter 1 · Meet the Recruitment Trust Network

**Page title:** Learn with BHI how to make hiring verifiable, end to end

**Standfirst:** Follow a single job application from search to offer — a candidate, an employer, a job board and a screening provider — and see what breaks today, what changes when every party can be verified, and how to run every step yourself with a real wallet.

### The organisation

| | |
|---|---|
| **Better Hiring Institute** | A brand of the Modern Work Foundation CIC (104403) |
| Mission | Faster, fairer, safer hiring across the UK |
| Employer reach | ~15,000 employer members |
| ARTP | The Association of RecTech Providers — BHI's membership for hiring-technology providers. 36+ UK members. |
| ARTP workstreams | Standards · Right to Work · Criminal Background Checks · Digital Identity · Digital Wallets and Credentials |
| Works with | Home Office · Disclosure and Barring Service · DSIT · Disclosure Scotland · Information Commissioner's Office |

BHI convenes both sides of the hiring market: the employers who buy hiring technology and, through ARTP, the providers who build it. That is the position from which a sector-wide trust network can credibly be governed — by the body that already sets the standard, rather than by any one vendor within it.

### 1.1 · The hiring journey today

A candidate applies for a job. Between "I'd like to apply" and "you start on Monday" sit four to eight weeks of a single repeated task: proving things.

**The cast**

| Entity | Role | Status |
|---|---|---|
| **Meridian Technologies (demo)** | Employer — hiring a Senior Software Engineer, London, £70–85k | Fictional |
| **JobSearch (demo)** | Job board — `jobsearch.example.co.uk` | Fictional |
| **Alex Chen (demo)** | Candidate — 5 years' experience, BSc Computer Science | Fictional |
| **Halcyon Talent (demo)** | Agency running fake job ads to harvest identity documents | Fictional — antagonist |
| **Northgate Screening (demo)** | Screening provider, not certified | Fictional |
| **Orchestrating Identity** | Certified Orchestration Service Provider; onboards organisations onto the network | Real |
| **Trustworthy Verification Services (demo)** | A second certified DVS provider, acting as an alternative grantor | Fictional |
| **Caledonian University (demo)** | Awarding body — issues the degree credential | Fictional |
| **Northbank Identity (demo)** | Certified DVS provider — issues right-to-work and employment-history credentials | Fictional |
| **Cirrus Certification (demo)** | Cloud certification body — issues the professional certification | Fictional |
| HMRC | Data source for employment history, accessed under the Data (Use and Access) Act 2025 information gateway. Not an issuer. | Real — see 3.4 |

### 1.2 · What the candidate carries

Alex has four things worth proving, and no way to prove any of them without sending copies of documents to strangers:

- BSc Computer Science — First Class Honours, 2017
- Employment history — 5 years, 3 employers
- Right to Work (UK) — British citizen
- Professional cloud certification — 2024

Today each exists as a PDF, a scan, or a database record behind someone else's login. Alex emails the same four artefacts to every employer, and every employer verifies them from scratch.

### 1.3 · The problems, and what they cost

**For the candidate**

- **The same paperwork, every time.** Every application asks for the same certificates, the same payslips, the same passport scan. Nothing carries over.
- **Data everywhere.** A passport scan sits in the inbox of every employer, agency and screening provider the candidate has ever spoken to. The candidate has no idea who still holds it.
- **Weeks of dead time.** Offers are made conditional, then stall while references and checks grind through email.

**For the employer**

- **CV fraud.** Qualifications and employment dates are asserted, not proven. Detection happens late, or never.
- **Verification cost.** Every hire funds a fresh round of reference chasing and certificate checking — the same facts, verified again.
- **Manual right to work.** Document inspection is slow, inconsistent, and carries statutory-excuse risk when it goes wrong.

**For the market**

- **Fake job ads and fake recruiters.** A recruitment scam and a real application look identical: both are a form on a website asking for your passport.
- **Uncertified providers.** An employer choosing a screening or identity provider has no machine-checkable way to confirm the provider is who it claims to be, or certified for what it claims to do. The DVS register exists — but it is a web page a human checks at procurement time, not something a system checks at transaction time.

> **A real job ad and a scam job ad look exactly the same. A real degree and a claimed degree look exactly the same. On both sides of the hire, nothing can be proven.**

### 1.4 · The word of the Institute

> `[QUOTE TO BE APPROVED — Keith Rosser, Chair of the BHI Advisory Board]`
>
> *Suggested substance: hiring is the last major life transaction still run on emailed PDFs; the technology to fix it now exists; the sector needs one shared trust layer rather than thirty-six incompatible ones.*

**→ Continue: 2 · The solution: become verifiable**

---

<!-- PAGE 2 — /usecases/bhi/solution -->

## Chapter 2 · The solution: become verifiable

**Standfirst:** Five needs, the infrastructure they run on, and the ecosystems BHI joins or builds.

> `[QUOTE TO BE APPROVED — David Rennie, ARTP Digital Identity lead and Chief Trust Officer, Orchestrating Identity]`
>
> *Suggested substance: open-source personal and business wallets now exist; public trust infrastructure now exists; the UK now has a statutory framework for digital verification services. The pieces are in place — what has been missing is a way to connect them for hiring.*

### What BHI needs

**1. Verifiable identities for organisations** → *ECS-Organization*
Employers, job boards, agencies and screening providers must be able to prove who they are, checkable by anyone, without sending company documents around.

**2. Verifiable identities for services** → *ECS-Service*
A careers portal, an ATS, or a credential-request endpoint must prove what it is and who operates it — before a candidate shares a single document.

**3. Credentials people can hold**
Candidates need their proofs in their own wallet, disclosed selectively, reusable across every application. These are issued by others — universities, government, certified DVS providers, professional bodies — not by BHI.

**4. Existing certifications as proof, not PDFs**
DVS certification, DBS Responsible Organisation status and ARTP membership already exist. They should travel with an organisation's identity and be checkable at the moment a request arrives, not at the next procurement cycle.

**5. The sector's own rules for the hiring side** → *the Recruitment Trust Network*
A way for BHI to say who is a recognised RecTech provider and who is a verified employer — and to revoke it.

### Where this runs

Two layers, and they should never be conflated. The first is statutory; the second is infrastructure.

| | |
|---|---|
| **The rules: the UK DVS trust framework** | Published by OfDIA under the Data (Use and Access) Act 2025. It defines the roles a digital verification service can be certified against, and the DVS register records who holds that certification. It is the eligibility criterion for participating in this network as an issuer or verifier of identity-derived credentials. BHI does not grant it and cannot. |
| **The infrastructure: Verana** | Public, permissionless trust infrastructure on which ecosystems publish their governance frameworks, credential schemas and participant registries — so that a claim like "this organisation is certified" becomes something a wallet can resolve in the moment, rather than something a human looks up afterwards. Anyone may create an ecosystem or join one. |

What Verana provides out of the box:

- **Sovereign ecosystems — Trust Ecosystems.** Build an ecosystem with your own schemas, governance framework, participants and business model, or join an existing one.
- **Verifiable identity — Verifiable Trust.** Identify any service and the organisation controlling it, and verify it before you connect. Verify first. Then connect.
- **Discovery — the Trust Graph.** Find services and ecosystems by the credentials they hold, ranked by trust — for people, search engines and AI agents.

> **Who decides what**
>
> OfDIA sets and administers DVS certification. BHI governs the Recruitment Trust Network and decides what a Verified Employer is. Orchestrating Identity, as a certified Orchestration Service Provider, onboards organisations and confirms DVS register status. Verana is public infrastructure with no gatekeeper: any organisation can join an ecosystem, and any group can create one.
>
> Four parties. No single one both writes the rules and controls the door.

### The ecosystems BHI joins

**Verana ECS Ecosystem** — *BHI and every participating organisation joins as HOLDER*

The identity card. The ecosystem that governs the essential credential schemas. An accredited issuer runs Know-Your-Business once, then issues an ECS-Organization credential; services carry ECS-Service credentials describing what they are and who operates them. One KYB, and an organisation's identity is provable everywhere — this is what turns the check green, and the foundation everything else builds on.

**DVS-Aligned Provider Ecosystem (demo)** — *certified providers join as HOLDERS · operated by Orchestrating Identity*

Today, DVS certification is an entry on a register that a machine cannot check mid-transaction. Carried as a credential on an organisation's verified identity, it becomes something a candidate's wallet evaluates at the moment a request arrives.

Eligibility is DVS register status and nothing else. This ecosystem mirrors OfDIA's register; it does not constitute it, and it is neither operated by nor endorsed by OfDIA. If a provider leaves the register, its participant entry is revoked. Orchestrating Identity operates it because a certified Orchestration Service Provider already carries the obligation to check that the services it orchestrates are registered — this makes that check machine-readable. Its governance framework provides for other certified OSPs to be admitted as grantors.

### The ecosystem BHI builds

One need remains. No existing ecosystem can answer *"is this a legitimate employer, and is this a recognised provider in UK hiring?"* Only the sector can. So BHI builds its own — and builds it narrowly, on purpose.

**The Recruitment Trust Network** — *BHI operates as ECOSYSTEM*

| Credential schema | Issuance | Verification | Held by |
|---|---|---|---|
| **Recognised RecTech Provider** | ECOSYSTEM (BHI) | OPEN | Member providers |
| **Verified Employer** | GRANTOR (certified DVS providers) | OPEN | Employers |

That is the whole registry. Two schemas, both about organisations.

BHI governs who may participate in hiring — not what a degree is, not who is entitled to work. Those credentials belong to the ecosystems that already own them: universities and awarding bodies, the Home Office and certified DVS providers, professional certification bodies. The Recruitment Trust Network consumes them and sets the terms on which its own participants may ask for them.

#### Who may ask, and who may hold

Two rules follow, and they run in opposite directions on purpose.

- **Asking is restricted.** A candidate's right-to-work status is not something any passing website may request. Within the Recruitment Trust Network, only participants holding a Recognised RecTech Provider or Verified Employer credential may request identity-derived credentials, and the wallet enforces this before anything is presented. This is a data-protection decision recorded in the governance framework.
- **Holding is not.** Any individual may hold a wallet and receive credentials under the rules of whichever scheme issues them. Candidates get no entry in any public registry — the registry records organisations and their permissions, not people and their attributes. Nothing about an individual is written to a public ledger.

> **The design decision that keeps this defensible**
>
> **BHI accredits who may ask, not who may issue.** A job board holding a Recognised RecTech Provider credential is what qualifies it to request a candidate's right-to-work status — but the credential itself is issued by a certified DVS provider under the Home Office's rules, and BHI has no hand in it.
>
> This keeps the build small, keeps BHI inside its actual authority, and avoids the sector body appearing to arbitrate government-derived attributes.

**Why BHI builds it:** sector integrity as a structural property. Real employers and recognised providers turn green, fake job ads and unrecognised providers turn red, and a member that goes rogue can be revoked. What the sector consumed, the sector now provides.

**→ Continue: 3 · The journey**

---

<!-- PAGE 3 — /usecases/bhi/journey -->

## Chapter 3 · The journey

**Standfirst:** Six builds — BHI's identity and ecosystem, the employer, the job board, the candidate's wallet, the application itself, and what happens to the impostors.

*Each step follows the Vesta template: narrative → trust-graph diagram → Reproduce it → Under the hood.*

### 3.1 · BHI's identity, and its ecosystem

`[DIAGRAM: BHI DID → ECS-Organization → Recruitment Trust Network root]`

**BHI deploys its Business Wallet.** A `vs-agent` is deployed on a BHI domain. A DID is generated — the identifier everything else attaches to. It proves nothing yet; it is the empty identity card.

**KYB, through a certified DVS provider.** BHI joins the Verana ECS Ecosystem and completes a Know-Your-Business exchange over DIDComm. In this demonstrator Orchestrating Identity runs that onboarding, as a provider certified under DVS 1.0, and confirms register status as part of it. Any certified DVS provider accredited on the ECS-Organization schema can perform the same function; the route is not the point, the credential is — and 3.3 shows a participant taking a different one.

**BHI creates the Recruitment Trust Network.** BHI publishes its governance framework — the sector standard the Standards workstream is already producing, rendered as an Ecosystem Governance Framework — and creates its registry with the two schemas from Chapter 2.

*New in this step: BHI's DID is born · the check turns green · the Recruitment Trust Network exists.*

**Reproduce it**

1. Deploy a `vs-agent` on a public domain (Docker image and compose examples in the vs-agent repository).
2. Open `https://<your-host>/.well-known/did.json` — that document is your Business Wallet's DID.
3. Resolve it: `https://resolver.testnet.verana.network/v1/trust/resolve?did=<your-did>` → UNTRUSTED. That is the starting line.
4. In the Verana app: Discover & Join → ECS Ecosystem → Organization schema → Participants → join under an active issuer branch. Complete the KYB exchange over DIDComm.
5. My Ecosystems → create a trust registry (name plus governance-framework document) → add credential schemas → create root participant entries.

**Under the hood**

- The vs-agent generates the DID (`did:webvh` recommended) and publishes its DID Document with a DIDComm endpoint.
- Joining creates a HOLDER participant entry on the Organization schema; the validating issuer sets it to Validated and it becomes ACTIVE in the public tree.
- Ecosystem creation is three transactions: *Create New Ecosystem* (with EGF document) → *Create New Credential Schema* → *Create Root Participant*.

### 3.2 · Meridian Technologies becomes a verifiable employer

*Wireframe screens 1–2: the job listing and the job detail page.*

`[DIAGRAM: Meridian DID → ECS-Org + ECS-Service → Verified Employer]`

Meridian walks the same path BHI just walked — anchor, KYB, ECS-Organization — then self-accredits as an ECS-Service issuer and issues an ECS-Service credential to its careers and ATS service. It then applies to the Recruitment Trust Network as a holder of **Verified Employer**. The validating provider identifies Meridian by the ECS-Organization credential already on its DID: reusable KYB, no fresh paperwork.

That is what stands behind the **Apply with Verifiable Credentials** flag on the listing. The flag is not a marketing claim; it is a resolvable credential chain.

**Reproduce it**

1. Repeat 3.1 steps 1–4 for the employer's Business Wallet.
2. ECS Ecosystem → Service schema → Participants → join on the issuer side; self-issue the ECS-Service credential via the vs-agent Admin API and link it.
3. Recruitment Trust Network → Verified Employer schema → Participants → Join. Present ECS-Organization when asked to identify.

**Under the hood**

- Self-issuance of ECS-Service is valid because the same DID already presents a proven ECS-Organization — every service traces back to an accountable organisation.
- Meridian joins as HOLDER under a grantor branch; validation is an ECS-Organization presentation check, not a document review.

### 3.3 · JobSearch becomes a recognised verifier — and picks its own provider

*Wireframe screens 3–4: the QR code, and "Continue on your phone".*

`[DIAGRAM: two grantor branches side by side — Orchestrating Identity and Trustworthy Verification Services (demo) — with JobSearch under the second]`

The job board is the party that actually asks the candidate for credentials, so it needs two things: its own verifiable identity (ECS-Organization plus ECS-Service), and a **VERIFIER** participant entry on each candidate credential schema it intends to request.

JobSearch is an ARTP member, so it also holds a **Recognised RecTech Provider** credential. Its verifier policy accepts qualification credentials from issuers accredited on the Qualification schema, right-to-work credentials from certified DVS issuers, and employment-reference credentials from accredited issuers.

> **The step that shows the network is open**
>
> **JobSearch does not use Orchestrating Identity.** It already has a commercial relationship with Trustworthy Verification Services (demo), another certified DVS provider. So Trustworthy Verification Services is established as a verifier grantor in the network, and JobSearch is onboarded by them instead — same schemas, same rules, same verdict in the candidate's wallet. Nothing about the trust the candidate sees depends on which provider did the onboarding.

When the candidate scans the QR code, the wallet does not see "a website". It sees a DID presenting ECS-Service, controlled by an organisation presenting ECS-Organization and Recognised RecTech Provider, holding verifier entries for exactly the credentials it is asking for.

**Reproduce it**

1. Deploy a vs-agent for the credential-request service; issue it an ECS-Service credential from the organisation anchor and link it.
2. Join each candidate credential schema tree as VERIFIER for that service's DID, under whichever grantor you have chosen.
3. Generate a DIDComm out-of-band invitation as a QR code; the wallet resolves the inviting DID before showing the request.

**Under the hood**

- The QR code carries a DIDComm out-of-band invitation, not a URL to a form. Nothing is submitted to a web endpoint.
- The Personal Wallet applies the mirror rule before presenting: verify the verifier is trusted, and authorised to request these schemas.
- This is the step that kills the fake job ad. See 3.6.

### 3.4 · The candidate's wallet

Alex's four credentials arrive from four different issuers, in four different ecosystems, over DIDComm — and sit in one wallet:

| Credential | Issued by | Ecosystem |
|---|---|---|
| BSc Computer Science, First Class | Caledonian University (demo) | Qualification — external |
| Employment history, 3 employers, 5 years | Northbank Identity (demo), from HMRC payroll records | Employment Reference — external |
| Right to Work — British citizen | Northbank Identity (demo) | Right to Work — external |
| Professional certification | Cirrus Certification (demo) | Professional Certification — external |

> **Where the employment credential actually comes from**
>
> **This is the one credential in the demonstration with a real statutory route behind it.** The Data (Use and Access) Act 2025 created an information gateway through which a certified DVS provider can request data from HMRC on behalf of a citizen. HMRC already holds the payroll history that establishes where someone has worked and when.
>
> **So the issuer is the DVS provider, and HMRC is the data source.** That distinction matters: HMRC has not agreed to become a credential issuer and is not being represented as one. What the demonstration shows is a credential built on a data route that already exists in law — which is why this part of the model requires a request to HMRC rather than a change to it.

Every one of these is issued by somebody else. BHI issues none of them, and that is the point: the Recruitment Trust Network governs the hiring side and consumes the rest.

Each credential is issued to Alex's DID, held by Alex, revocable by its issuer, and — critically — **not held by any employer**. The wireframe's line stands: *your credentials remain in your wallet.*

**Under the hood**

- Issuance runs over DIDComm; the Personal Wallet verifies the issuer is trusted and authorised to issue that schema before accepting.
- Revocation is issuer-side and visible at verification time — a suspended certification or a withdrawn right-to-work status shows up on the next presentation, not at the next audit.

### 3.5 · The application

*Wireframe screens 3–6, end to end.*

| Wireframe step | What actually happens |
|---|---|
| 1 · Search jobs — listing shows the VC-enabled flag | The board filters listings to employers presenting a Verified Employer credential |
| 2 · Job details — credentials requested, declared up front | The four schemas the verifier holds VERIFIER entries for |
| 3 · Scan QR | DIDComm out-of-band invitation; the wallet resolves the requesting DID |
| **NEW — Proof-of-Trust card** | Who is asking, what credentials they present, who certified them — shown before anything is shared |
| 4 · Select credentials | Selective disclosure — the candidate chooses per credential, and per attribute |
| 5 · Verify & submit — biometric, then "checking cryptographic proofs against issuer registries" | Wallet unlock, presentation over DIDComm; the verifier checks signature, revocation status, and the issuer's registry entry |
| 6 · Confirmed — 4 of 4 verified, reference number | Application submitted with a verified presentation attached; the activity log is the audit trail |

**Elapsed time in the wireframe: 9:41 to 9:44. Elapsed time today: two to six weeks.**

**Under the hood**

- Verification is three checks per credential: the signature is valid, the credential is not revoked, and the issuer holds an active issuer entry on that schema in the registry. The third check is the one with no equivalent today.
- The employer receives a cryptographically signed proof, not a document set. There is nothing to store and nothing to leak.

### 3.6 · The impostors

**Halcyon Talent (demo) — the fake job ad.** Halcyon can build a convincing careers site, copy Meridian's branding, and put up a QR code. What it cannot do is present a Verified Employer credential, because only the Recruitment Trust Network issues one and it never recognised Halcyon. The candidate's wallet refuses before any data moves. *The scam fails at the point where scams currently succeed: the moment of asking.*

Worth stating plainly: Halcyon may itself be a perfectly verifiable organisation, with valid ECS-Organization and ECS-Service credentials — like Umbra Repairs in the Vesta story. Verifiable is not the same as authorised. **Legitimate organisation, wrong network.**

**Northgate Screening (demo) — the uncertified provider.** Holds ECS-Organization. Does not hold Recognised RecTech Provider, and is not on the DVS register. An employer evaluating providers can establish this in one resolution instead of one procurement cycle.

**The forged degree.** A credential claiming a First Class BSc, signed by a DID with no issuer entry on the Qualification schema. It verifies as a signature and fails as a credential. That distinction is the whole point.

**→ Continue: 4 · Run the demos**

---

<!-- PAGE 4 — /usecases/bhi/demos -->

## Chapter 4 · Run the demos

**Standfirst:** Get your credentials, apply for a job, and watch a fake employer fail.

> Always verify the certified organisation name and data shown in the Proof-of-Trust card in your wallet before proceeding.

**Choose a wallet.** Pick any of the integrated personal wallets — every one reaches the same verdict by the same route. The demo QR codes are minted for the wallet you choose.

- **Demo 1 · Receive your credentials.** Request the four demo credentials and watch your wallet check each issuer's accreditation before offering to accept.
- **Demo 2 · Apply to Meridian Technologies (demo).** The full flow: scan, review the requester, select, approve, submit. Note what you are shown before you are asked to share anything.
- **Demo 3 · Apply to Halcyon Talent (demo).** Same flow, same-looking site. Watch the wallet stop you — a red Proof-of-Trust card.
- **Demo 4 · Present a revoked credential.** Verification fails at the registry check, not at the signature check.
- **Demo 5 · Search the directory.** *(Trust Graph — coming later, per the Vesta pattern.)* Query the registry for organisations presenting a Verified Employer credential; narrow to those also presenting Recognised RecTech Provider. Discovery by proof, not by claim.

Participation in the demonstrator is free. It runs on the Verana testnet, and no party charges a fee for joining, issuing or verifying within it.

---

## Build notes — not for publication

- **Wallet branding.** The BHI-branded wallet is removed from the wireframes and is not replaced by any other vendor's brand. The wallet chooser stays neutral. Orchestrating Identity appears where it acts — onboarding and orchestration in Chapter 3, named in the narrative and in the trust-graph diagrams.
- **Diagrams.** Six needed, one per journey step, following the Vesta pattern. The 3.3 diagram matters most: two grantors side by side is the visual form of the openness argument.
- **Spec vocabulary.** This copy uses Verana v5 terms (Participant, onboarding modes). The existing Vesta pages use v3 (Permission, PermissionManagementMode). Consistency across the site is a decision for the Playground maintainers.
- **Before publication.** Verana agreement signed · both quotes approved · certification scope confirmed in writing.
