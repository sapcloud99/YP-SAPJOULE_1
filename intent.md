# SAP Role Optimization & Access Governance Agent

SAP IAM Role Optimization and Access Backup Agent across BTP, On-Premise, Cloud, and Multi-Tenant Environments

## Business Challenge

Organizations running SAP across multiple environments (BTP, S/4HANA On-Premise, S/4HANA Cloud, and multi-tenant setups) struggle to maintain clean, optimized role assignments. Roles are managed manually today — without automated tooling. This leads to SoD (Segregation of Duties) conflicts, over- or under-privileged users, and critical access areas held by only a single person (single point of failure). There is no systematic way to map roles by functional category (Functional, Technical, Backend/Basis, Support, Security/Compliance) or to ensure every critical access area has a backup holder. The solution requires an AI agent that can discover the current role landscape, identify gaps and risks, recommend optimized assignments, propose backup coverage, and deliver findings as conversational answers, automated reports, and visual dashboards.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| SoD conflicts eliminated | To be discovered by agent | 0 conflicts | 6 months | Access Governance & Authorization Management | user |
| Role assignments organized by functional category | To be discovered by agent | 100% roles mapped to user function | 6 months | Identity & Access Governance | user |
| Critical roles with no backup user (single-holder) | To be discovered by agent | 0 single-holder critical roles | 6 months | Identity & Access Governance | user |
| Overall IAM risk score | To be discovered by agent | Below 10% risk | 6 months | Identity & Access Governance | user |

## Key Milestones

1. **Baseline Established** — Agent discovers and reports the current role landscape across all SAP environments (BTP, On-Premise, Cloud, multi-tenant), ingesting data from APIs and manual CSV/Excel uploads
2. **Gap Analysis Complete** — SoD conflicts, over/under-privileged users, and single-holder critical roles are identified and flagged per environment and user type
3. **Role Optimization Recommendations Delivered** — Agent maps every role to a functional category and recommends optimized assignments per user type and environment
4. **Backup Coverage Plan Generated** — Agent proposes backup users for all critical access areas ensuring no single point of failure remains
5. **Compliance Report Published** — Agent auto-generates statistical reports (graphical + tabular) for audit and GRC teams, with findings accessible via conversational interface and email/dashboard delivery

## Business Architecture (RBA)

### End-to-End Process

Governance

### Process Hierarchy

```
Governance (E2E)
└── Manage Governance, Risk and Compliance (generic)
    └── Manage identity and access governance (generic) [BPS-399]
        └── Manage access governance and authorisations
        └── Manage authentication
        └── Manage identity
```

### Summary

The challenge maps to the Manage Identity and Access Governance sub-process within the Governance E2E, covering identity lifecycle management, access governance and authorizations, and authentication — all of which are required to analyze, optimize, and back up SAP role assignments across a heterogeneous multi-environment landscape.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Read and analyze business roles from S/4HANA | SAP S/4HANA Business Role API | `sap.s4:apiResource:CE_BUSINESSROLE_0001:v1` | — | — | — | — | No | OData API available; no MCP server found — custom MCP integration needed |
| Track role changes and audit trail | SAP S/4HANA Business Role Changes API | `sap.s4:apiResource:CE_APS_IAM_API_BROLE_CDOC_0001:v1` | — | — | — | — | No | OData API available; no MCP server found |
| User provisioning and identity management | SAP S/4HANA SCIM API | `sap.s4:apiResource:CE_APS_IAM_API_SCIM:v1` | — | — | — | — | No | REST API available; no MCP server found |
| Automated SoD conflict detection | SAP Cloud Identity Access Governance (IAG) | — | — | — | — | — | Yes | IAG not deployed; agent must implement SoD logic based on role data |
| GRC Access Control integration | SAP GRC Access Control (on-premise) | — | — | — | — | — | Yes | GRC not deployed; gap covered by agent reasoning over extracted role data |
| Backup user recommendation for single-holder roles | Custom agent capability | — | — | — | — | — | Yes | No standard SAP product covers backup recommendation — agent logic required |
| Manual data ingestion (CSV/Excel uploads) | Custom agent capability | — | — | — | — | — | Yes | Agent must parse and normalize uploaded role data files |
| Graphical + tabular statistical reporting | Custom agent capability | — | — | — | — | — | Yes | No standard API; agent generates reports dynamically based on query volume |
| Multi-environment role aggregation (BTP, Cloud, On-Prem) | SAP Cloud Identity Services / IPS | — | — | — | — | — | Maybe | Identity Provisioning Service aggregates identity data; direct API access needed |

### Key findings

- SAP does not provide a single out-of-the-box product covering all requirements; SAP IAG and GRC Access Control address subsets but are not deployed in this landscape
- Three S/4HANA APIs are available (Business Role Read, Business Role Changes, SCIM User Management) and will serve as primary data sources; no MCP servers exist for them — MCP translation files must be generated
- Roles are managed manually today; the agent must establish the baseline from scratch, making the "discover baseline" milestone critical before any optimization can occur
- SoD conflict detection, backup coverage logic, and reporting must be built as agent capabilities — these are genuine gaps not covered by available standard assets
- Large dataset handling must trigger automatic statistical report generation (graphical + tabular), requiring the agent to assess data volume at query time
- Multi-environment aggregation across BTP, on-premise, and cloud requires data ingestion from multiple source types (API + file upload), which increases architectural complexity

## Recommendations

### SAP IAM Role Optimization & Access Backup AI Agent

#### Executive Summary

Build a Python AI agent that analyzes SAP roles, detects gaps, and ensures backup coverage across all environments.

#### Recommended Solution

A pro-code Python AI agent (A2A protocol) deployed on SAP BTP that:
- Connects to SAP S/4HANA via OData/REST APIs (Business Role, SCIM) to read current role assignments
- Accepts manual CSV/Excel uploads for environments without API access
- Analyzes roles by functional category (Functional, Technical, Backend/Basis, Support, Security/Compliance)
- Detects SoD conflicts using built-in logic, flags single-holder critical roles, and identifies over/under-privileged users
- Recommends optimized role assignments and proposes backup users per environment and role type
- Delivers findings conversationally (chat interface), via automated PDF/Excel reports (email delivery), and as graphical dashboards
- Auto-triggers report generation when the queried dataset is large, providing statistics in both graphical and tabular format

#### Problem Statement

Manual role management across BTP, S/4HANA On-Premise, S/4HANA Cloud, and multi-tenant environments creates uncontrolled SoD conflicts, access gaps, and single points of failure. Without automated analysis, the organization cannot maintain a clean authorization landscape, comply with audit requirements, or ensure business continuity in critical access areas.

#### Affected User Roles

- IT Security / IAM team
- SAP Basis / System administrators
- Compliance & Audit team
- HR and business line managers

#### Important factors

##### Roles managed manually today — agent must build the baseline

Since neither SAP IAG nor SAP GRC Access Control is deployed, the agent is the first systematic tool to analyze this landscape. Establishing an accurate baseline is the most important first step.

##### Large dataset support with auto-reporting

The agent must detect when queried data volumes are large and automatically produce graphical and tabular statistical summaries — ensuring that insights are always accessible regardless of data size.

##### Multi-source data ingestion

The agent must handle both live API data (S/4HANA, SCIM) and manually uploaded files (CSV/Excel) to cover all environments uniformly.

#### Potential risks

##### Data completeness across environments

On-premise and multi-tenant systems may not expose all role data via API. Manual uploads become a dependency — data quality and completeness depend on the accuracy of what the IT team provides.

##### SoD rule library maintenance

The agent's SoD conflict detection is only as good as the ruleset it uses. Without SAP IAG's maintained rule library, the team must define and maintain SoD rules — this adds ongoing governance overhead.

#### Recommended solution category

AI Agent

#### Intent fit
92%
