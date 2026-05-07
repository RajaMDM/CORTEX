# CORTEX

> **Connected Object Resolution and Typed EXtraction**

[![Status](https://img.shields.io/badge/status-concept%20v0.1-blueviolet.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

*Dedicated to Gaurav — who asked the right question.*

> *"Each memory is individual. How it is associated with other memory, project, domain, entity — that is missing. This is something a graph database does."*
>
> — Gaurav, Tech Architect

That question didn't have an answer. CORTEX is the answer.

---

## The Problem

Every knowledge management tool in existence has this gap:

```
What you store:      "Merged CUST-00142 into CUST-00089. Loyalty tier wins."

What you get back:   A document.

What you actually
need:
  [ENTITY: CUST-00142] ──MERGED_INTO──► [ENTITY: CUST-00089]
       │                                        │
  APPROVED_BY                             BELONGS_TO
       │                                        │
  [STEWARD: Gaurav]                    [DOMAIN: Customer]
       │                                        │
  APPLIED_RULE                          GOVERNED_BY
       │                                        │
  [RULE: Loyalty Tier Survivorship]   [COMPLIANCE: UAE PDPL]
```

The knowledge exists. The connections do not.

Tools today give you one of three things:

| Tool type | What it gives you | What it misses |
|---|---|---|
| **Document stores** (Notion, Confluence, gbrain) | Full text search, semantic search | Relationships between concepts |
| **Graph databases** (Neo4j, Amazon Neptune) | Traversal, relationship depth | Semantic understanding, free text |
| **Vector databases** (Pinecone, Weaviate) | Semantic similarity | Structure, typed relationships |

None of them extract typed nodes from free text **and** wire them into a traversable graph **and** expose them to AI agents as queryable institutional memory.

That is the gap. That is what CORTEX fills.

---

## The Insight

The fragmentation problem that MDM solves for *data* exists identically in *knowledge*:

| MDM for Data | CORTEX (MDM for Knowledge) |
|---|---|
| Records fragmented across systems | Decisions fragmented across heads, Slack, tickets |
| Duplicate entities | Duplicate concepts (same idea, different words) |
| No single source of truth | No canonical knowledge node |
| Golden Record | Golden Knowledge Node |
| Entity resolution | Concept deduplication |
| Survivorship rules | Knowledge authority rules |
| Lineage store | Decision provenance graph |
| Steward approval | Knowledge validation |

CORTEX applies MDM discipline to knowledge itself.

---

## What CORTEX Does

CORTEX sits between your systems of record and your AI agents.
It turns free-text knowledge into a typed, traversable, queryable graph.

```
┌──────────────────────────────────────────────────────────────┐
│  Any source of knowledge                                      │
│  (MDM decisions, Slack, tickets, emails, meeting notes,      │
│   runbooks, incident reports, governance docs...)            │
└────────────────────────┬─────────────────────────────────────┘
                         │ free text
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  CORTEX                                                       │
│                                                               │
│  1. CAPTURE   → ingest any free-text knowledge               │
│  2. EXTRACT   → AI pulls typed nodes from content            │
│  3. RESOLVE   → duplicate concepts merged → one canonical    │
│  4. CONNECT   → typed edges wired across all nodes           │
│  5. SERVE     → graph exposed to AI agents + humans          │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
             ▼                          ▼
   ┌──────────────────┐      ┌─────────────────────┐
   │  Semantic Layer  │      │  Graph Layer         │
   │  (vector store)  │      │  (property graph)    │
   │                  │      │                      │
   │  "What relates   │      │  MATCH (d:DECISION)  │
   │   to loyalty     │      │  -[:APPROVED_BY]->   │
   │   tier merges?"  │      │  (s:STEWARD)         │
   │                  │      │  RETURN s.name       │
   └──────────────────┘      └─────────────────────┘
```

---

## The Five Stages

| # | Stage | Plain English |
|---|---|---|
| **1. CAPTURE** | Any free text in. Typed node out. | Write a decision in plain English. CORTEX reads it. |
| **2. EXTRACT** | AI reads content → pulls named nodes | "Gaurav approved the merge" → [STEWARD: Gaurav] + [DECISION: merge] + APPROVED_BY edge |
| **3. RESOLVE** | Same concept, different words → one node | "Loyalty tier wins" + "highest tier survives" → [RULE: loyalty-tier-survivorship] |
| **4. CONNECT** | Typed edges wired across all nodes | Every node connected to everything it relates to |
| **5. SERVE** | Graph queryable by AI agents + humans | Before any action: check what the graph already knows |

---

## Node Types

CORTEX is domain-agnostic. The default schema covers knowledge-intensive domains:

```
[DOMAIN]      A bounded subject area (Customer, Vendor, Finance, HR...)
[ENTITY]      A named real-world object (a person, company, product, asset)
[DECISION]    A specific choice made at a point in time, by someone
[RULE]        A stated constraint, policy, or standard
[CONCEPT]     An abstract idea or pattern recurring across decisions
[STEWARD]     A named person who owns or approves knowledge
[PROJECT]     A bounded initiative or programme
[COMPLIANCE]  A regulatory or governance framework
[SYSTEM]      A named software system or data source
[EVENT]       A named occurrence (incident, release, migration)
```

Custom node types can be added per domain. The schema is yours to extend.

---

## Edge Types

```
BELONGS_TO        Node belongs to a domain or project
APPROVED_BY       Decision approved by a steward
APPLIES_TO        Rule applies to a domain, entity, or system
RESOLVES          Decision or concept resolves a conflict
GOVERNED_BY       Entity governed by a compliance framework
CONFLICTS_WITH    Concept conflicts with another concept
SUPERSEDES        New rule supersedes an older one
EXTRACTED_FROM    Node was extracted from a source document
RELATES_TO        General semantic relationship
DEPENDS_ON        One node depends on another
TRIGGERED_BY      Event or decision triggered by another node
```

---

## Storage Architecture

CORTEX is storage-agnostic by design. The reference implementation uses two layers:

**Layer 1 — Semantic (gbrain + PGLite)**
Handles free-text search, vector embeddings, semantic similarity.
Zero-config. Runs locally. No server needed.

```bash
gbrain query "what decisions relate to loyalty tier survivorship?"
→ finds related pages even when exact words differ
```

**Layer 2 — Graph (Neo4j AuraDB)**
Handles typed traversal, relationship depth, pattern queries.
Free cloud tier. Full Cypher query language.

```cypher
MATCH (d:DECISION)-[:APPROVED_BY]->(s:STEWARD)
WHERE d.domain = 'Customer'
RETURN s.name, count(d) as decisions_approved
ORDER BY decisions_approved DESC
```

Neither layer alone answers all questions. Together they do.

---

## Who This Is For

CORTEX is for any team where:

- Knowledge lives in people's heads, not in queryable systems
- The same question gets answered from scratch every time someone asks it
- New team members take weeks or months to reach the knowledge level of experienced ones
- AI agents act without context — because the context was never structured
- Decisions are made without knowing what was decided before

That is: **most teams, in most organisations, in every industry.**

The reference implementation is built around MDM and data governance — because that is
where the authors work. But the problem is universal. The framework is not MDM-specific.

---

## Status

| Component | Status |
|---|---|
| Concept + architecture | ✅ v0.1 |
| AI entity extractor (Python) | ✅ Working |
| Semantic layer (gbrain) | ✅ Working |
| Graph layer (Neo4j) | 🔧 In progress |
| RESOLVE deduplication engine | 📋 Planned v0.2 |
| MCP server (query interface) | 📋 Planned v0.2 |
| Domain-agnostic schema builder | 📋 Planned v0.3 |
| REST API | 📋 Planned v0.3 |

---

## The Name

**CORTEX** — the outer layer of the brain where complex thought, memory,
and reasoning live. Knowledge without structure is noise.
CORTEX gives it structure.

**C**onnected **O**bject **R**esolution and **T**yped **EX**traction.

---

## Contributing

CORTEX is an open problem. If you have faced this gap — in MDM, in data governance,
in engineering, in any knowledge-intensive domain — contributions are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Dedication

*To Gaurav — who spotted that the connections were missing.*
*The best concepts begin with the right question.*

---

## Author

Raja Shahnawaz Soni
21 years in IT and data, 13 in MDM.

*[LinkedIn](https://linkedin.com/in/raja-shahnawaz/) · [AURUM](https://github.com/RajaMDM/AURUM)*

---

**#KnowledgeGraph #MDM #AI #OpenSource #DataGovernance #CORTEX #GraphDatabase**
