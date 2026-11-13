# Role Criticality Criteria

## High Criticality Roles
Roles in this category have the highest business continuity risk if their sole holder is unavailable.
Immediate backup assignment is required (within 5 business days).

| Role Pattern | Criticality | Risk Reason |
|-------------|-------------|-------------|
| `admin` | High | Administrative access to systems or security settings |
| `basis` | High | SAP Basis system-level operations |
| `super_user` | High | Super-user / emergency access (firefighter) |
| `security` | High | Security administration and policy enforcement |
| `role_admin` | High | Can assign roles to any user — critical control point |
| `user_admin` | High | User account management — critical control point |
| `payment` | High | Financial payment execution — fraud risk |
| `audit` | High | Audit log access — evidence integrity |
| `firefighter` | High | Emergency access — must always have backup |
| `emergency_access` | High | Emergency bypass — must always have backup |

## Medium Criticality Roles
Roles where a missing backup causes significant operational delays.
Backup assignment required within 2 weeks.

| Role Pattern | Criticality | Risk Reason |
|-------------|-------------|-------------|
| `fi_post` | Medium | Financial posting — blocks month-end close |
| `period_close` | Medium | Period closing — blocks financial reporting |
| `transport` | Medium | System transport management — blocks deployments |
| `manager` | Medium | Manager-level approval rights — blocks workflows |
| `approve` | Medium | Approval rights — blocks business processes |
| `bank_master` | Medium | Bank data management — financial risk |
| `vendor_master` | Medium | Vendor data management — procurement risk |

## Low Criticality Roles
Standard business roles where coverage can be arranged within the normal review cycle.

All roles not matching High or Medium patterns are classified as Low criticality.

## Determining "Critical" for Access Coverage
A role is considered **critical for backup purposes** if:
1. It matches any High or Medium pattern above, OR
2. It is the only role enabling a mandatory business process step (e.g., only approver for a transaction type), OR
3. It has been explicitly flagged by the IAM team as business-critical.
