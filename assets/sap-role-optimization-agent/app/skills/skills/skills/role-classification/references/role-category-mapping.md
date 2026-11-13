# Role Category Keyword Mapping Reference

## Functional Category
| Pattern | Example SAP Role | Notes |
|---------|-----------------|-------|
| `employee` | SAP_EMPLOYEE_SELF_SERVICE | Standard ESS role |
| `self_service` | ESS_SELF_SERVICE_USER | Employee self-service |
| `manager` | SAP_HCM_MANAGER | HCM manager role |
| `approver` | PURCHASE_REQN_APPROVER | Any approval role |
| `fi` | FI_ACCOUNTING_USER | Finance module |
| `mm` | MM_PURCHASING_USER | Materials management |
| `sd` | SD_SALES_ORDER_PROCESS | Sales and distribution |
| `co` | CO_COST_CENTER_MANAGER | Controlling |
| `hr` | HR_PAYROLL_USER | Human resources |

## Technical Category
| Pattern | Example SAP Role | Notes |
|---------|-----------------|-------|
| `developer` | ABAP_DEVELOPER | SAP developer |
| `abap` | ABAP_WORKBENCH | ABAP development |
| `fiori_dev` | FIORI_DEVELOPER | Fiori app development |
| `api` | API_INTEGRATION_USER | API access roles |
| `btp_dev` | BTP_DEVELOPER | SAP BTP development |

## Backend/Basis Category
| Pattern | Example SAP Role | Notes |
|---------|-----------------|-------|
| `admin` | BASIS_ADMINISTRATOR | Full system admin |
| `basis` | SAP_BASIS_ADMIN | Basis operations |
| `transport` | TRANSPORT_MANAGER | TMS transport |
| `su_` | SU_USER_ADMIN | User admin transactions |
| `sm_` | SM_SYSTEM_MONITOR | System monitoring |
| `rfc` | RFC_DESTINATION_ADMIN | RFC management |

## Support Category
| Pattern | Example SAP Role | Notes |
|---------|-----------------|-------|
| `helpdesk` | IT_HELPDESK_AGENT | L1 support |
| `l1` | SUPPORT_L1_AGENT | Level 1 support |
| `l2` | SUPPORT_L2_SPECIALIST | Level 2 support |
| `incident` | INCIDENT_MANAGER | Incident management |
| `monitoring` | SYSTEM_MONITORING | Ops monitoring |

## Security/Compliance Category
| Pattern | Example SAP Role | Notes |
|---------|-----------------|-------|
| `audit` | AUDIT_LOG_VIEWER | Read audit logs |
| `security` | SECURITY_ADMIN | Security administration |
| `grc` | GRC_ACCESS_CONTROL | GRC module |
| `role_admin` | ROLE_ADMINISTRATOR | Manage role assignments |
| `iam` | IAM_GOVERNANCE_USER | Identity governance |
| `compliance` | COMPLIANCE_OFFICER | Compliance review |

## Edge Cases
- Roles starting with `SAP_` are often functional unless the suffix indicates otherwise.
- Roles containing both `admin` and `fi` should be classified as Backend/Basis (admin takes precedence).
- Generic roles like `ALL_USERS` should be classified as Functional.
- Emergency access roles (e.g., `FIREFIGHTER`, `EMERGENCY_ACCESS`) → Security/Compliance.
