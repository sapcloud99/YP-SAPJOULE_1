---
name: role-classification
description: Maps SAP roles to functional user categories based on role name patterns, business catalog assignments, and authorization objects
allowed-tools: []
---

# Role Classification Skill

## Purpose
Classify SAP roles and users into one of five functional categories:
Functional, Technical, Backend/Basis, Support, Security/Compliance.

## Functional Categories

### Functional
Business process users who execute day-to-day transactions.
**Keywords**: employee, self_service, manager, approver, end_user, business,
procurement, finance, hr, sales, mm, sd, fi, co, pp, pm, ps, wm, qm

### Technical
Developers, architects, and integration specialists.
**Keywords**: developer, development, abap, fiori_dev, api, integration,
technical, btp_dev, extension, middleware

### Backend/Basis
System administrators managing SAP infrastructure and operations.
**Keywords**: basis, admin, sysadmin, system_admin, transport, client,
rfc, batch, background, dialog, developer_admin, netweaver, abap_admin, sm_, se_, su_

### Support
Helpdesk and operational support staff.
**Keywords**: helpdesk, support, l1, l2, l3, service_desk,
incident, ticket, operations, monitoring

### Security/Compliance
IAM, audit, and GRC staff.
**Keywords**: audit, security, grc, compliance, sod, access_control,
authorization, auth_admin, role_admin, iam, identity

## Classification Logic

### Step 1 — Single Role Classification
For a single role name:
1. Check against each category's keyword list (case-insensitive substring match).
2. Return the FIRST matching category (priority order: Security/Compliance → Backend/Basis → Technical → Support → Functional).
3. If no keyword matches, default to **Functional**.

### Step 2 — User Classification (Portfolio-Based)
For a user with multiple roles:
1. Classify each role individually.
2. Count the frequency of each category across all roles.
3. The category with the highest count is the **primary category**.
4. If a user has roles from 2+ categories: mark as **cross-functional**.
5. If confidence (top category count / total roles) < 70%: flag for human review.

## Cross-Functional Users
Cross-functional users require additional attention:
- Verify their job function spans multiple areas (legitimate).
- Check for unauthorized access accumulation (suspicious).
- Document the legitimate reason for cross-functional access in the review notes.

## See Also
- `references/role-category-mapping.md` for keyword examples and edge cases.
