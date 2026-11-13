---
name: sod-detection
description: SoD conflict detection rules and resolution guidance for SAP role analysis
allowed-tools: []
---

# SoD Conflict Detection Skill

## Purpose
Evaluate user role combinations against the SoD rule library to detect conflicts,
determine severity, and formulate remediation recommendations.

## Step-by-Step Instructions

### Step 1 — Load the Rule Library
Load the SoD rule definitions from `references/sod-rule-template.json`.
Each rule defines two conflicting role patterns, a risk level, and a mitigation action.

### Step 2 — Evaluate Each User
For each user in the session dataset:
1. Retrieve all roles assigned to the user.
2. For each SoD rule, check whether the user holds BOTH `role_a_pattern` AND `role_b_pattern`.
3. A match occurs when either pattern appears as a substring (case-insensitive) in any role name.

### Step 3 — Assign Risk Level
Map each detected conflict to the rule's `risk_level`:
- **High**: Direct fraud enablement potential (e.g., create + approve payments, admin + audit)
- **Medium**: Elevated risk requiring compensating controls (e.g., admin self-assignment)
- **Low**: Policy violation without direct fraud risk

### Step 4 — Formulate Recommendations
For each conflict:
1. Quote the rule's `mitigation` guidance verbatim.
2. State which specific roles are conflicting.
3. Recommend the least-disruptive fix (e.g., "Remove role X from user Y and assign to a separate user").
4. If a compensating control exists (e.g., manager approval log), mention it.

### Step 5 — Prioritize Output
Sort conflicts: High → Medium → Low.
Present High-risk conflicts with an explicit urgency notice.

## Decision Criteria
- If the same user-role conflict appears in multiple environments: report once per environment.
- If a user has only ONE of the two conflicting roles: no conflict — do not flag.
- If a role name partially matches two different rules: flag both separately.

## Output Format
Return a structured list:
- user_id
- environment
- rule_id
- description
- conflicting_role_a (exact role name)
- conflicting_role_b (exact role name)
- risk_level
- mitigation
