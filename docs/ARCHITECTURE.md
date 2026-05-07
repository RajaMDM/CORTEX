# CORTEX Architecture

## Overview

CORTEX is a three-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│  INGESTION LAYER                                             │
│  Any source → structured knowledge                          │
│  Files, APIs, webhooks, pipelines                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CORTEX CORE                                                 │
│  CAPTURE → EXTRACT → RESOLVE → CONNECT → SERVE              │
│                                                             │
│  AI extraction engine (Claude / any LLM)                    │
│  Deduplication engine (RESOLVE stage — v0.2)                │
│  Graph wiring engine (typed edges)                          │
└───────────┬──────────────────────────────┬──────────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐    ┌────────────────────────────────┐
│  SEMANTIC LAYER       │    │  GRAPH LAYER                    │
│                       │    │                                 │
│  gbrain + PGLite      │    │  Neo4j AuraDB                   │
│  (or any vector DB)   │    │  (or any property graph DB)     │
│                       │    │                                 │
│  • Vector embeddings  │    │  • Typed nodes                  │
│  • Semantic search    │    │  • Typed edges                  │
│  • Free-text memory   │    │  • Cypher queries               │
│  • Keyword search     │    │  • Graph traversal              │
│                       │    │  • Pattern detection            │
└───────────────────────┘    └────────────────────────────────┘
            │                              │
            └──────────────┬───────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  SERVE LAYER                                                 │
│                                                             │
│  • MCP server (AI agents query natively)                    │
│  • REST API (any system integration)                        │
│  • CLI (human queries)                                      │
│  • Dashboard (visual graph browser — v0.3)                  │
└─────────────────────────────────────────────────────────────┘
```

## Storage Layer Comparison

| Question | Semantic Layer | Graph Layer |
|---|---|---|
| "What relates to loyalty tier merges?" | ✅ Vector similarity finds it | ❌ No semantic understanding |
| "Who approved the most decisions in Customer domain?" | ❌ No typed traversal | ✅ Cypher aggregation |
| "What is two hops from Apex Group in the graph?" | ❌ | ✅ MATCH pattern |
| "Find me something similar to this new case" | ✅ | ❌ |
| "What rules apply to this domain?" | ⚠ Approximate | ✅ Exact typed edges |
| "Deduplicate these concepts by meaning" | ✅ | ❌ |

Use both. Route queries to the right layer.

## Extraction Engine

The AI extractor (extractor/extract.py) uses a structured prompt to pull
typed nodes from free text. It is model-agnostic — any LLM with a JSON
output mode works.

```
Input:  "Gaurav approved merging CUST-00142 into CUST-00089.
         Loyalty tier survivorship rule applied. UAE PDPL governs."

Output:
  Nodes:
    [STEWARD]    gaurav
    [DECISION]   merge-cust-00142
    [ENTITY]     cust-00142
    [ENTITY]     cust-00089
    [RULE]       loyalty-tier-survivorship
    [COMPLIANCE] uae-pdpl

  Edges:
    merge-cust-00142 --APPROVED_BY--> gaurav
    merge-cust-00142 --APPLIED_RULE--> loyalty-tier-survivorship
    cust-00142 --MERGED_INTO--> cust-00089
    merge-cust-00142 --GOVERNED_BY--> uae-pdpl
```

## RESOLVE Stage (v0.2 — planned)

The RESOLVE stage deduplicates knowledge nodes using vector similarity:

1. Embed all concept/rule/decision nodes
2. Cluster by cosine similarity threshold (default: 0.92)
3. Within each cluster, elect a canonical node (most recent, most linked, or steward-designated)
4. Redirect all edges from deprecated nodes to canonical node
5. Mark deprecated nodes as aliases

This is the hardest stage. It is the equivalent of entity resolution in MDM —
applied to knowledge instead of data.

---

*CORTEX v0.1 · github.com/RajaMDM/CORTEX*
