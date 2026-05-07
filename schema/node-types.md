# CORTEX Node & Edge Schema

## Node Types

| Type | Description | Examples |
|---|---|---|
| `DOMAIN` | A bounded subject area | Customer, Vendor, Finance, HR, Legal |
| `ENTITY` | A named real-world object | Priya Sharma, Apex Group, SKU-0042 |
| `DECISION` | A specific choice made at a point in time | Merge CUST-00142, Override DQ threshold |
| `RULE` | A stated constraint, policy, or standard | UAE Phone Format, Loyalty Tier Survivorship |
| `CONCEPT` | An abstract pattern recurring across decisions | Dual-Role Detection, Golden Record Conflict |
| `STEWARD` | A named person who owns or approves knowledge | Jin, Gaurav, Shazia |
| `PROJECT` | A bounded initiative or programme | AURUM, New Store Opening |
| `COMPLIANCE` | A regulatory or governance framework | UAE PDPL, GDPR, KSA NDMO |
| `SYSTEM` | A named software system or data source | CRM, ERP, Loyalty Platform |
| `EVENT` | A named occurrence | DQ Incident 2026-05, Migration Wave 3 |

## Edge Types

| Type | Direction | Meaning |
|---|---|---|
| `BELONGS_TO` | node → DOMAIN or PROJECT | This node is part of that domain/project |
| `APPROVED_BY` | DECISION → STEWARD | Decision was approved by this steward |
| `APPLIES_TO` | RULE → DOMAIN or ENTITY | Rule applies to this domain or entity |
| `RESOLVES` | DECISION or CONCEPT → conflict | This resolves that conflict type |
| `GOVERNED_BY` | ENTITY or DOMAIN → COMPLIANCE | Governed by this framework |
| `CONFLICTS_WITH` | RULE ↔ RULE | These rules conflict |
| `SUPERSEDES` | RULE → RULE | New rule replaces old one |
| `EXTRACTED_FROM` | any → source page | Node was extracted from this document |
| `RELATES_TO` | any ↔ any | General semantic relationship |
| `DEPENDS_ON` | any → any | One node depends on another |
| `TRIGGERED_BY` | EVENT or DECISION → trigger | Caused by this event or decision |
| `MERGED_INTO` | ENTITY → ENTITY | Entity was merged into another |
| `APPROVED_BY` | DECISION → STEWARD | Who made the call |

## Frontmatter Convention

Every CORTEX page should include:

```yaml
---
title: Human Readable Title
type: decision          # one of the node types above, lowercase
domain: customer        # optional: which domain this belongs to
steward: jin            # optional: who owns this knowledge
tags: [cortex, decision, merge, customer]
cortex_version: "0.1"
---
```
