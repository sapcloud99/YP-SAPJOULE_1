# Product Requirements Document (PRD)

**Title:** SAP Role Optimization & Access Governance Agent
**Date:** 2026-11-13
**Owner:** IAM / IT Governance Team
**Solution Category:** AI Agent (Python / A2A Protocol on SAP BTP)

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Organizations running SAP across BTP, On-Premise, Cloud, and multi-tenant environments manage roles manually today. This creates undetected SoD conflicts, over- and under-privileged users, and critical access areas with no backup holder. This AI agent discovers the full role landscape, identifies every gap, recommends optimized assignments, and ensures no critical access point depends on a single person — all surfaced through conversation, automated reports, and dashboards.

**Business Need:**
Without automated role analysis, IAM teams have no systematic view of who has what access across environments, whether those accesses conflict, or whether losing one person would break a critical business process. Audits are manual, time-consuming, and prone to gaps. The agent fills this void as the first automated IAM intelligence layer for the organization.

**Expected Value:**
- Eliminate all SoD conflicts within 6 months
- Achieve 100% role-to-function mapping within 6 months
- Reduce the number of single-holder critical roles to zero within 6 months
- Drive overall IAM risk score below 10%

**Product Objectives (Prioritized):**
1. Discover and establish the IAM baseline across all SAP environments from day one
2. Identify and prioritize SoD conflicts, access gaps, and single points of failure
3. Deliver actionable recommendations for role optimization and backup coverage
4. Auto-generate statistical compliance reports (graphical + tabular) for large datasets
5. Provide all findings through a conversational interface, email reports, and a visual dashboard

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| SoD conflicts eliminated | To be discovered by agent | 0 conflicts | 6 months | Access Governance & Authorization Management | user |
| Role assignments organized by functional category | To be discovered by agent | 100% roles mapped to user function | 6 months | Identity & Access Governance | user |
| Critical roles with no backup user (single-holder) | To be discovered by agent | 0 single-holder critical roles | 6 months | Identity & Access Governance | user |
| Overall IAM risk score | To be discovered by agent | Below 10% risk | 6 months | Identity & Access Governance | user |

**Notes:** The agent itself establishes the baseline on first run; no prior baseline data exists. All targets are to be achieved within a 6-month window from go-live.

---

## User Profiles & Personas

### Primary Persona: Priya — IT Security / IAM Manager

Priya is a 38-year-old IT Security Manager responsible for SAP role governance across four environments. She spends 30% of her week manually reviewing role requests and trying to maintain an Excel-based role matrix. She is frustrated that role conflicts only surface during audits — always too late. She is technically confident but overwhelmed by scale. She needs a tool that gives her a live, structured view of the IAM landscape and flags issues before they become audit findings.

### Secondary Persona: Marcus — SAP Basis Administrator

Marcus is a 44-year-old Basis admin who manages user accounts and system access across S/4HANA On-Premise, BTP, and Cloud tenants. He knows each system individually but has no cross-system view. When a colleague leaves, he discovers too late that no one else had their access. He needs to quickly identify who holds unique access and assign backups before gaps become operational risks.

### Tertiary Persona: Clara — Compliance & Audit Officer

Clara is a 35-year-old internal auditor who prepares quarterly access control reviews. She relies on manual reports from the Basis team, which are always outdated. She needs clean, time-stamped, evidence-quality reports showing SoD status, access coverage, and risk scores — generated on demand without manual effort.

### Other User Types

- **James (HR / Business Line Manager):** Needs assurance that team members have the right access for their roles, and wants to flag access that no longer matches a person's job function.
- **L1/L2 Support Staff:** Use the conversational interface to self-check their own access scope and understand why access was flagged.

---

## User Goals & Tasks

### For Priya (IAM Manager):

**Goals:**
- Maintain a clean, compliant IAM landscape across all SAP environments
- Detect and resolve SoD conflicts before they appear in audits
- Ensure every critical access area has at least one backup holder

**Key Tasks:**
- Ask the agent: "Show me all SoD conflicts in our S/4HANA On-Premise environment"
- Request a full role optimization report grouped by functional category
- Review and approve backup user recommendations proposed by the agent

### For Marcus (Basis Administrator):

**Goals:**
- Identify single-holder critical roles before a team member leaves
- Quickly find eligible backup candidates for flagged access areas

**Key Tasks:**
- Query: "Which critical roles have only one holder across all environments?"
- Review the agent's backup recommendations and assign co-holders
- Upload CSV extracts from environments without API connectivity

### For Clara (Compliance & Audit Officer):

**Goals:**
- Produce audit-ready access control evidence without manual effort
- Track IAM risk score improvement over time

**Key Tasks:**
- Trigger a compliance report: "Generate the quarterly IAM risk report"
- Download graphical + tabular reports (PDF/Excel) for audit files
- Compare risk scores across reporting periods

---

## Product Principles

1. **Baseline First:** The agent must always establish what exists before making any recommendation. No optimization without a complete picture.
2. **Evidence Over Opinion:** Every finding — conflict, gap, recommendation — must be traceable to source data (API record or uploaded file row).
3. **Human in the Loop for Changes:** The agent recommends; it never modifies role assignments directly. All changes require human approval.
4. **Scale-Aware Reporting:** When data volumes are large, the agent automatically produces graphical and tabular summaries rather than raw lists.
5. **Environment Agnostic:** Logic must work uniformly across BTP, On-Premise, Cloud, and multi-tenant data — regardless of data source type.

---

## Business Context

**Current State:**
Role management is performed manually using spreadsheets and ad hoc requests to the Basis team. Neither SAP Cloud Identity Access Governance (IAG) nor SAP GRC Access Control is deployed. There is no cross-environment visibility, no systematic SoD checking, and no process to ensure backup holders exist for critical access. Gaps are discovered during audits — reactively and at high cost.

**Strategic Alignment:**
This agent directly supports the organization's Governance, Risk & Compliance (GRC) strategy by introducing automated IAM intelligence as a foundational capability. It also reduces audit risk and supports business continuity by eliminating single points of failure in critical access areas.

**Success Criteria:**
See Business Metrics section above.

---

## Goals and Non-Goals

### Goals (In Scope)

- Discover and catalog the current role landscape across BTP, S/4HANA On-Premise, S/4HANA Cloud, and multi-tenant environments
- Classify every role and user by functional category (Functional, Technical, Backend/Basis, Support, Security/Compliance)
- Detect SoD conflicts using a configurable rule library
- Identify single-holder critical roles and recommend backup users
- Recommend optimized role assignments per user type and environment
- Auto-generate statistical reports (graphical + tabular) for large datasets
- Deliver findings via conversational chat, email reports, and a visual dashboard

### Non-Goals (Out of Scope)

- Deploying or configuring SAP Cloud Identity Access Governance (IAG) or SAP GRC Access Control
- Automatically provisioning or modifying role assignments in any SAP system
- Replacing HR onboarding or offboarding workflows
- Managing non-SAP system access (e.g., Azure AD, Okta, third-party SaaS)
- Real-time, event-driven role change notifications

---

## Requirements

### Must-Have Requirements

**REQ-01: Role Landscape Discovery**

- **Problem to Solve:** No single view exists of who has what roles across all SAP environments.
- **User Story:** As an IAM Manager, I need the agent to discover and catalog all user-role assignments across BTP, S/4HANA On-Premise, S/4HANA Cloud, and multi-tenant systems so that I have a single, accurate baseline to work from.
- **Acceptance Criteria:**
  - Given the agent is connected to S/4HANA APIs and/or a CSV file has been uploaded, when I ask for the role landscape, then the agent returns a complete list of users, their assigned roles, environments, and functional categories.
  - Given data from multiple environments, when the agent consolidates them, then duplicates are detected and normalized to a single record per user-role-environment combination.
- **Maps to Objective:** Objective 1 — Establish the IAM baseline
- **Priority Rank:** 1

---

**REQ-02: Role Classification by Functional Category**

- **Problem to Solve:** Roles are not organized by user function, making it impossible to assess whether someone has access appropriate to their job type.
- **User Story:** As an IAM Manager, I need every user and role mapped to a functional category (Functional, Technical, Backend/Basis, Support, Security/Compliance) so that I can assess alignment between job function and access level.
- **Acceptance Criteria:**
  - Given a complete role dataset, when the agent analyzes it, then each user is assigned exactly one primary functional category based on their role portfolio.
  - Given a role that spans multiple categories, when the agent classifies it, then it flags the role as cross-functional and surfaces it for review.
- **Maps to Objective:** Objective 2 — Identify gaps
- **Priority Rank:** 2

---

**REQ-03: SoD Conflict Detection**

- **Problem to Solve:** Conflicting role combinations create audit risk and potential for fraud, but no tool currently checks for them.
- **User Story:** As a Compliance Officer, I need the agent to detect Segregation of Duties conflicts across all user-role assignments so that I can remediate them before an audit.
- **Acceptance Criteria:**
  - Given a configurable SoD rule library, when the agent scans all user-role assignments, then every conflicting combination is flagged with user name, environment, conflicting roles, and risk level.
  - Given a large dataset, when the scan completes, then the agent automatically generates a graphical and tabular SoD conflict summary report.
- **Maps to Objective:** Objective 2 — Identify and prioritize gaps
- **Priority Rank:** 3

---

**REQ-04: Single-Point-of-Failure Detection**

- **Problem to Solve:** Critical access areas held by only one person create business continuity risk that is invisible without cross-system analysis.
- **User Story:** As a Basis Administrator, I need the agent to identify all critical roles or authorizations held by only a single user so that I can address coverage gaps before they cause operational disruption.
- **Acceptance Criteria:**
  - Given the full role landscape, when the agent analyzes holder counts, then all roles where only one user holds the authorization are flagged and ranked by criticality.
  - Given a flagged single-holder role, when the agent presents it, then it includes the role name, environment, current holder, and a risk statement.
- **Maps to Objective:** Objective 2 — Identify single points of failure
- **Priority Rank:** 4

---

**REQ-05: Backup User Recommendation**

- **Problem to Solve:** Even when single-holder roles are known, finding eligible backup candidates is a manual, time-consuming process.
- **User Story:** As a Basis Administrator, I need the agent to recommend eligible backup users for each single-holder critical role so that I can assign co-holders efficiently.
- **Acceptance Criteria:**
  - Given a flagged single-holder role, when I ask for backup recommendations, then the agent proposes at least one eligible candidate based on functional category match and existing access profile.
  - Given a recommendation, when the human accepts it, then the agent generates an access request summary (but does not provision the access directly).
- **Maps to Objective:** Objective 3 — Deliver actionable recommendations
- **Priority Rank:** 5

---

**REQ-06: Role Optimization Recommendations**

- **Problem to Solve:** Users accumulate roles over time that no longer match their job function, creating over-privilege risk.
- **User Story:** As an IAM Manager, I need the agent to recommend optimized role assignments per user type and environment so that access is right-sized and aligned with current job functions.
- **Acceptance Criteria:**
  - Given the role landscape and functional category classification, when the agent analyzes it, then it identifies over-privileged users (excess roles beyond their functional category) and under-privileged users (missing roles for their function).
  - Given an optimization recommendation, when presented, then it includes the user, environment, current roles, recommended roles, and the rationale.
- **Maps to Objective:** Objective 3 — Deliver actionable recommendations
- **Priority Rank:** 6

---

**REQ-07: Automated Statistical Reporting**

- **Problem to Solve:** Large role datasets produce unwieldy raw outputs that are hard to interpret; compliance teams need structured summaries with visual evidence.
- **User Story:** As a Compliance Officer, I need the agent to auto-generate graphical and tabular statistical reports when the dataset is large so that I can share audit-ready evidence without manual formatting.
- **Acceptance Criteria:**
  - Given a query that returns more than a configurable threshold of records, when the agent responds, then it automatically produces a statistical summary containing at minimum: total users analyzed, total roles analyzed, SoD conflict count, single-holder role count, risk score, and a distribution chart by functional category.
  - Given a report request, when the user specifies delivery format, then the agent outputs PDF, Excel, or both and supports email delivery.
- **Maps to Objective:** Objective 4 — Auto-generate reports
- **Priority Rank:** 7

---

**REQ-08: Multi-Source Data Ingestion**

- **Problem to Solve:** Not all SAP environments expose APIs; some data must be loaded manually from exports.
- **User Story:** As a Basis Administrator, I need to upload CSV or Excel role extracts from environments without API connectivity so that the agent has a complete cross-environment picture.
- **Acceptance Criteria:**
  - Given a CSV or Excel file upload, when the agent processes it, then it validates, normalizes, and merges the data into the role landscape dataset.
  - Given an invalid or incomplete upload, when the agent detects it, then it returns a structured error message identifying the problematic rows and expected format.
- **Maps to Objective:** Objective 1 — Establish the IAM baseline
- **Priority Rank:** 8

---

### High-Want Requirements

**REQ-09: Configurable SoD Rule Library**

- **Problem to Solve:** SoD conflict rules must reflect the organization's specific risk tolerance and business processes.
- **User Story:** As an IAM Manager, I need to define and update the SoD rule library used by the agent so that conflict detection reflects our organization's policies.
- **Priority Rank:** 1

**REQ-10: Historical Trend Tracking**

- **Problem to Solve:** Without trend data, it is impossible to demonstrate progress toward IAM targets over time.
- **User Story:** As a Compliance Officer, I need to compare IAM risk scores and SoD conflict counts across reporting periods so that I can demonstrate measurable improvement.
- **Priority Rank:** 2

**REQ-11: Role-to-User Similarity Matching**

- **Problem to Solve:** Finding backup candidates manually requires deep system knowledge; peer-group matching accelerates the process.
- **User Story:** As a Basis Administrator, I need the agent to identify users with similar role profiles so that backup recommendations are based on actual access patterns, not just job titles.
- **Priority Rank:** 3

---

### Nice-to-Have Requirements

**REQ-12: Natural Language SoD Rule Authoring**

- **Problem to Solve:** Security teams without technical skills struggle to define SoD rules in structured formats.
- **User Story:** As an IAM Manager, I want to describe SoD rules in plain language and have the agent translate them into the rule library format.
- **Priority Rank:** 1

**REQ-13: Integration with SAP Cloud Identity Access Governance (IAG)**

- **Problem to Solve:** If IAG is deployed in the future, the agent should be able to leverage its rule library and workflow capabilities.
- **User Story:** As an IAM Manager, I want the agent to optionally connect to SAP IAG so that we can reuse its certified SoD rule library if the product is deployed.
- **Priority Rank:** 2

---

## Non-Functional Requirements

### Performance
- **Latency:** Conversational responses must return within 10 seconds for queries against pre-loaded data.
- **Throughput:** The agent must handle role datasets of up to 50,000 user-role-environment records without degradation.
- **Report Generation:** Statistical reports must be generated within 60 seconds for datasets up to 50,000 records.

### Reliability
- **Availability:** 99% uptime during business hours (07:00–19:00 in the primary timezone).
- **Fallback:** If an S/4HANA API is unavailable, the agent falls back to last-loaded data and notifies the user of the staleness.

### Explainability
- **Traceability:** Every finding (SoD conflict, single-holder flag, recommendation) must reference its source data record (API response row or uploaded file row number).
- **Decision Logging:** All agent actions, tool calls, and recommendations are logged with timestamps and user session context.
- **Uncertainty Communication:** When the agent cannot determine a classification or recommendation with high confidence, it explicitly states the uncertainty and recommends human review.

---

## Solution Architecture

**Architecture Overview:**
A pro-code Python AI agent (A2A protocol) deployed on SAP BTP Cloud Foundry. The agent connects to SAP S/4HANA via three OData/REST APIs through MCP integration tools, accepts file uploads for offline environments, applies internal SoD and gap analysis logic, and delivers outputs through a conversational interface, email delivery, and a dashboard.

**Key Components:**

- **Python AI Agent (A2A):** Core reasoning and orchestration layer deployed on SAP BTP
- **MCP Tool — Business Role API:** Reads current business role definitions from S/4HANA (`CE_BUSINESSROLE_0001:v1`)
- **MCP Tool — Business Role Changes API:** Retrieves role change history for audit trail (`CE_APS_IAM_API_BROLE_CDOC_0001:v1`)
- **MCP Tool — SCIM User Management API:** Reads user identities and assignments across systems (`CE_APS_IAM_API_SCIM:v1`)
- **File Ingestion Module:** Parses, validates, and normalizes CSV/Excel role exports
- **SoD Rule Engine:** Configurable rule library for conflict detection; maintained by the security team
- **Report Generation Module:** Produces graphical (charts) and tabular (tables) statistical summaries; outputs PDF and Excel formats
- **Conversational Interface:** Chat-based interaction for queries and recommendations
- **Email Delivery Module:** Sends generated reports to specified recipients
- **Dashboard View:** Visual summary of IAM risk score, conflict count, single-holder role count, and optimization status

**Integration Points:**

- SAP S/4HANA (On-Premise / Cloud): OData/REST via MCP tools — read-only, on-demand
- Manual File Uploads: CSV/Excel ingested via the file module — batch, user-initiated
- Email System: Outbound report delivery — on report generation trigger
- Dashboard: Read from agent's in-session data store — on-demand rendering

**Deployment Environments:**

- **Development:** Full agent stack on BTP with test role datasets; isolated from production systems
- **Production:** Agent deployed on BTP; connects to live S/4HANA APIs with read-only credentials

---

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
The agent is designed with the following extension points to accommodate future capabilities without rearchitecting:
- **New Environment Connectors:** Additional MCP tools can be registered (e.g., SAP IAG, SAP GRC, Azure AD) without modifying core agent logic
- **Custom SoD Rule Packs:** The SoD rule engine accepts pluggable rule library files (JSON/YAML), allowing environment-specific or industry-specific rule sets
- **Report Templates:** Report generation supports pluggable templates for organization-specific formatting and branding
- **Skill Extensions:** The agent supports skill-based extensibility (A2A protocol) for adding new analysis capabilities (e.g., behavioral analytics, peer-group comparison) as separate skills

**Business Step Instrumentation:**
All key business logic steps are instrumented with structured log statements following the pattern: `[MILESTONE_ID].[achieved|missed]: [description]`. This enables production monitoring, debugging, and business process observability via OpenTelemetry.

---

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent with human-in-the-loop for action approval

**Actions the system performs without human approval:**
- Read role data from S/4HANA APIs
- Parse and normalize uploaded CSV/Excel files
- Classify roles by functional category
- Detect SoD conflicts and single-holder roles
- Generate statistical reports and charts
- Send reports via email (when triggered by a user)

**Actions that require human review or approval:**
- Applying role optimization recommendations (agent proposes; human executes in the SAP system)
- Assigning backup users to single-holder critical roles
- Adding or modifying SoD rules in the rule library

**Model or engine used:** SAP Generative AI Hub (LLM for conversational reasoning); deterministic rule engine for SoD conflict detection

**Knowledge & data sources accessed:**

- SAP S/4HANA Business Role API: current role definitions (read-only)
- SAP S/4HANA Business Role Changes API: audit trail of role modifications (read-only)
- SAP S/4HANA SCIM API: user identity and assignment data (read-only)
- Manual CSV/Excel uploads: role data from environments without API access

**Tools or connectors invoked:**

- `get_business_roles` (MCP — CE_BUSINESSROLE_0001): Reads business role definitions from S/4HANA — read-only
- `get_business_role_changes` (MCP — CE_APS_IAM_API_BROLE_CDOC_0001): Retrieves role change log for audit purposes — read-only
- `get_scim_users` (MCP — CE_APS_IAM_API_SCIM): Reads user identities and role assignments — read-only
- `file_ingestion_tool`: Parses and validates CSV/Excel uploads — read-only
- `report_generation_tool`: Generates statistical reports — read-only output
- `email_delivery_tool`: Sends generated reports to specified recipients — outbound only

**Guardrails & fail-safes:**

- The agent never writes to or modifies any SAP system — all API access is strictly read-only
- Confidence below 70% on any classification or recommendation triggers a "human review required" flag
- If an API connection fails mid-session, the agent notifies the user and completes the analysis on previously loaded data, clearly marking results as potentially stale
- SoD rule changes require explicit confirmation from an authorized user before taking effect in the rule engine
- All personal data (user names, IDs) is handled within SAP BTP and not transmitted to external systems

---

## Governance, Risk & Compliance

**Data Handling:**
- All role and identity data is processed within SAP BTP; no data is transmitted outside the SAP landscape
- User identity data (names, email addresses, user IDs) is treated as sensitive and is not stored persistently beyond the agent session unless explicitly saved to a report
- Reports containing personal data must be handled in compliance with the organization's data retention policy

**Compliance Frameworks:**
- Supports evidence generation for SOX, ISO 27001, and internal GRC audit requirements
- SoD rule library should be aligned to SAP's standard SoD conflict rule sets as a starting reference

**Approval Flows:**
- Role assignments and backup user activations require approval through the existing ITSM or access request workflow — the agent provides the recommendation and supporting evidence, not the execution

---

## Milestones

### M1: Baseline Established

- **Description:** The agent has successfully discovered and cataloged the current role landscape across all in-scope SAP environments, ingesting data from both APIs and manual file uploads.
- **Achieved when:** The agent returns a complete, deduplicated role dataset covering all connected environments with no pending data sources.
- **Log on achievement:** `M1.achieved: IAM baseline established — {N} users, {R} roles, {E} environments ingested`
- **Log on miss:** `M1.missed: IAM baseline incomplete — one or more environments returned no data or upload was not provided`

### M2: Gap Analysis Complete

- **Description:** The agent has completed SoD conflict detection, single-holder role identification, and over/under-privilege analysis across the full baseline dataset.
- **Achieved when:** The agent has flagged all SoD conflicts, single-holder roles, and privilege misalignments with source traceability.
- **Log on achievement:** `M2.achieved: gap analysis complete — {C} SoD conflicts, {S} single-holder roles, {P} privilege gaps identified`
- **Log on miss:** `M2.missed: gap analysis incomplete — SoD rule library missing or dataset was empty`

### M3: Role Optimization Recommendations Delivered

- **Description:** The agent has mapped all users and roles to functional categories and generated right-sizing recommendations per user type and environment.
- **Achieved when:** Every user in the baseline has been classified and a recommendation (optimize / retain / review) has been generated.
- **Log on achievement:** `M3.achieved: role optimization recommendations ready — {U} users classified, {O} optimization actions proposed`
- **Log on miss:** `M3.missed: role optimization incomplete — classification failed for one or more user categories`

### M4: Backup Coverage Plan Generated

- **Description:** The agent has identified all single-holder critical roles and proposed at least one eligible backup user for each.
- **Achieved when:** Every single-holder role flagged in M2 has at least one backup candidate recommendation.
- **Log on achievement:** `M4.achieved: backup coverage plan complete — {B} backup recommendations generated for {S} single-holder roles`
- **Log on miss:** `M4.missed: backup coverage incomplete — no eligible backup candidates found for {X} roles`

### M5: Compliance Report Published

- **Description:** The agent has generated and delivered a statistical compliance report (graphical + tabular) covering all findings from M1–M4.
- **Achieved when:** A complete report has been generated and delivered via the requested channel (chat, email, or dashboard).
- **Log on achievement:** `M5.achieved: compliance report published — IAM risk score {R}%, report delivered via {channel}`
- **Log on miss:** `M5.missed: compliance report generation failed — report module error or delivery channel unavailable`

---

## Risks, Assumptions, and Dependencies

### Risks

- **Data Completeness:** On-premise and multi-tenant environments may not expose complete role data via API. Manual uploads introduce dependency on IT team accuracy and timeliness.
- **SoD Rule Library Quality:** Conflict detection is only as good as the rules configured. Without SAP IAG's maintained library, the team must build and maintain their own — this adds ongoing governance overhead.
- **API Read Permissions:** The agent requires read-only access to S/4HANA APIs. Provisioning these credentials across environments may require security reviews and approval cycles.
- **Large Dataset Performance:** Role datasets exceeding 50,000 records may require query optimization or pagination strategies to maintain acceptable response times.

### Assumptions

- The organization has at least one S/4HANA environment accessible via OData/REST APIs, or can provide CSV exports for all environments.
- The IAM/Security team will own and maintain the SoD rule library going forward.
- Read-only API credentials for S/4HANA can be provisioned for the agent without extended approval delays.
- The agent is not expected to integrate with non-SAP identity systems (e.g., Azure AD) in the initial version.

### Dependencies

- SAP BTP environment provisioned and accessible for agent deployment
- Read-only API access to SAP S/4HANA Business Role, Business Role Changes, and SCIM APIs
- MCP translation files generated for the three S/4HANA APIs
- Initial SoD rule library defined and loaded by the security team before gap analysis can run

---

## Open Questions

- Should the SoD rule library be pre-seeded with SAP standard conflict rules, or does the security team prefer to build from scratch?
- What is the email distribution list for automated compliance report delivery?
- Is there a preferred threshold (number of records) at which the agent should switch from inline list output to auto-generated statistical reports?
- Will the dashboard be embedded in an existing SAP BTP Launchpad, or delivered as a standalone web application?

---

## Appendix

### Glossary

- **SoD (Segregation of Duties):** A control principle requiring that no single user holds two or more roles that, in combination, could enable fraud or error.
- **Single-Holder Role:** A critical authorization or role assigned to exactly one user, meaning loss of that user would eliminate all access to that capability.
- **IAM (Identity and Access Management):** The discipline of ensuring the right users have the right access to the right systems at the right time.
- **MCP (Model Context Protocol):** The protocol used by the AI agent to call external tools and APIs in a structured, auditable way.
- **A2A (Agent-to-Agent):** The communication protocol used by the Python agent for interoperability and extensibility.
- **BTP (SAP Business Technology Platform):** The cloud platform where the agent is deployed.

### References

- SAP Cloud Identity Access Governance: https://www.sap.com/products/cloud-identity-access-governance.html
- SAP Identity Provisioning Service: https://help.sap.com/docs/identity-provisioning
- SAP S/4HANA Business Role API (CE_BUSINESSROLE_0001): SAP Business Accelerator Hub
- SAP S/4HANA SCIM API (CE_APS_IAM_API_SCIM): SAP Business Accelerator Hub
- SAP BTP Cloud Foundry Runtime: https://help.sap.com/docs/btp/sap-business-technology-platform/cloud-foundry-environment
