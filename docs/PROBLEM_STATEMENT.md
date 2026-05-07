# The Problem CORTEX Solves

> *"Each memory is individual. How it is associated with other memory,
> project, domain, entity — that is missing. This is something a graph database does."*
>
> — Gaurav, the question that started CORTEX

---

## Section 1 — The Knowledge Fragmentation Problem

Consider a team that has been running a Master Data Management programme
for two years. They have:

- 847 DQ rules written and maintained
- 12,000 stewardship decisions made and logged
- 200+ documented use cases and playbooks
- A governance framework covering 4 regulatory jurisdictions
- A team of 14 specialists across architecture, DQ, stewardship, compliance

Now ask them any of these questions:

> *"Why was the UAE phone format rule written the way it was?"*
> *"Who last changed the loyalty tier survivorship rule — and what triggered it?"*
> *"Which steward has approved the most cross-domain merges in the last 6 months?"*
> *"What decisions have been made about Apex Group across all domains?"*
> *"When a new case involving dual-role entity detection arrives — what did we decide last time?"*

In most teams: **no one can answer these quickly.**

Not because the knowledge doesn't exist. Because it was never structured.

---

## Section 2 — Where Knowledge Actually Lives

In a typical knowledge-intensive team, knowledge is distributed across:

```
Email threads          → decisions buried in reply chains
Slack messages         → archived, unsearchable in context
Confluence / Notion    → flat documents, no typed relationships  
Jira / ServiceNow      → tickets closed, context lost
People's heads         → evaporates when they leave or rotate
Spreadsheets           → no graph, no traversal, no semantic search
```

Each of these is a silo. None of them know about each other.
The knowledge exists. The **connections** do not.

---

## Section 3 — Why Existing Tools Don't Solve This

### Document stores (Notion, Confluence, gbrain)
Search finds documents. They do not extract the entities *inside* the documents.
"Gaurav approved the merge of CUST-00142" is a sentence in a document.
It is not a typed [DECISION] node connected to [STEWARD: Gaurav] and [ENTITY: CUST-00142].

### Graph databases (Neo4j, Amazon Neptune)
Traversal is powerful. But graph databases require structured input.
They cannot read "Gaurav approved the merge" and create the nodes themselves.
Someone has to do the extraction first. No one does.

### Vector databases (Pinecone, Weaviate, pgvector)
Semantic similarity is useful. But similarity is not structure.
"Loyalty tier wins" and "highest tier survives" are semantically similar.
A vector database tells you they are close. It does not merge them into
one canonical [RULE: loyalty-tier-survivorship] node.

### LLMs / AI assistants
Can answer questions from context. But context must be provided.
If the knowledge was never structured, there is nothing to provide.
The AI answers from training data — which knows nothing about your team,
your decisions, your domain.

---

## Section 4 — The Gap, Precisely Stated

The gap has three components:

**Gap 1 — Extraction**
No tool automatically reads free-text knowledge and produces typed nodes.
Entities, decisions, rules, concepts, stewards — they sit inside sentences,
never extracted into a queryable graph.

**Gap 2 — Resolution**
Even when nodes are extracted, duplicates accumulate.
"Loyalty tier wins", "highest loyalty tier survives", "tier survivorship rule"
are the same concept. No tool resolves them to a single canonical node.

**Gap 3 — Connection**
Even when nodes exist and are deduplicated, they are not connected.
A decision is not linked to the steward who made it, the domain it affects,
the rule it applied, the entity it concerns, the compliance framework that governs it.
Without connections, there is no graph. Without a graph, there is no traversal.
Without traversal, knowledge does not compound.

---

## Section 5 — What CORTEX Does Differently

CORTEX addresses all three gaps in sequence:

```
Free text in
     ↓
CAPTURE — any source, any format
     ↓
EXTRACT — AI reads content, produces typed nodes
           "Gaurav approved the merge" →
           [STEWARD: Gaurav] + [DECISION: merge-cust-00142] + APPROVED_BY edge
     ↓
RESOLVE — duplicate concepts merged to one canonical node
           "loyalty tier wins" + "highest tier survives" →
           [RULE: loyalty-tier-survivorship]
     ↓
CONNECT — typed edges wired across all nodes
           every node connected to everything it relates to
     ↓
SERVE — graph queryable by AI agents + humans
         before any action: what does the graph already know?
```

---

## Section 6 — Who This Problem Affects

This is not an MDM-specific problem. It appears wherever:

- Knowledge is created faster than it can be structured
- Teams rotate and institutional knowledge walks out the door
- AI agents need context but context was never formalised
- The same question is answered from scratch, repeatedly
- Decisions are made without knowing what was decided before

Industries where this is acute:
**Financial services · Healthcare · Legal · Government · Engineering · Data & AI teams**

---

## Section 7 — The Metric That Makes This Concrete

A team that has been running for 2 years has made, conservatively, 10,000 decisions.

How many of those decisions are queryable today?

In most teams: **zero.**

Not because the decisions were bad. Because they were never structured.

CORTEX makes them queryable. All of them. Retroactively and going forward.

---

*CORTEX v0.1 — github.com/RajaMDM/CORTEX*
*Dedicated to Gaurav — who asked the right question.*
