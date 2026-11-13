---
name: backup-recommendation
description: Identifies eligible backup users for single-holder critical roles based on functional category match, role overlap, and criticality scoring
allowed-tools: []
---

# Backup User Recommendation Skill

## Purpose
For each single-holder critical role, identify eligible backup candidates and
rank them by eligibility score. All recommendations require human approval.

## Criticality Classification
See `references/criticality-criteria.md` for the full criticality rule set.

**High Criticality** (immediate action required):
- System-wide admin access
- Financial payment execution
- Security/audit access
- User/role administration
- Emergency access (firefighter roles)

**Medium Criticality** (action within 2 weeks):
- Period closing
- Financial posting
- Transport management
- Manager/approval roles

**Low Criticality** (include in next review cycle):
- Standard business roles
- Read-only reporting roles

## Candidate Scoring Logic

### Scoring Criteria (total 100 points)
| Criterion | Points | Description |
|-----------|--------|-------------|
| Category match | 40 | Candidate's primary category matches the target role's category |
| Role name overlap | 30 | Candidate holds a role with 2+ common name tokens to the target role |
| Partial role overlap | 10 | Candidate holds a role with 1 common token to the target role |
| Multi-role holder | 10 | Candidate holds 3+ roles (indicates broader access exposure) |
| Broad portfolio | 10 | Candidate holds 5+ roles (indicates senior/multi-function user) |

### Eligibility Threshold
Only candidates with score > 0 are included.
Rank candidates by score (highest first). Return top 3.

## Step-by-Step Instructions

### Step 1 — Identify Current Holder
Retrieve the current holder of the target role from the session dataset.
Exclude this user from the candidate pool.

### Step 2 — Build Candidate Pool
All other users in the session dataset (same or any environment) are candidates.

### Step 3 — Score and Rank
Apply the scoring criteria above to each candidate.
Exclude candidates with score = 0.

### Step 4 — Generate Access Request Summaries
For each recommended candidate, generate a structured access request summary:
- Candidate user ID
- Role to assign
- Environment
- Justification (from scoring)
- Explicit note: "Requires human approval before any access change is made"

### Step 5 — Handle No-Candidate Scenarios
If no eligible candidates are found:
- State this explicitly.
- Recommend either: (a) training an existing user in a related role, or (b) hiring/contracting.
- Do NOT invent candidates.

## Output Requirements
- Always state that recommendations require human approval.
- Always cite the scoring rationale for each candidate.
- Never directly assign or modify roles.
