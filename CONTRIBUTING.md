# Contributing to CORTEX

CORTEX is an open concept. If you have faced the knowledge fragmentation problem —
in any domain, any industry — your contribution is welcome.

## What We Need

### 1. Problem evidence
Have you seen this gap in your organisation? A short write-up of how it manifested —
what questions couldn't be answered, what knowledge was lost — is genuinely valuable.
Open an issue with the tag `problem-evidence`.

### 2. Domain adaptations of the schema
The default schema is built around MDM and data governance. If you work in legal,
healthcare, engineering, or any other knowledge-intensive domain — what node types
and edge types would your domain need? Open an issue with tag `schema-extension`.

### 3. Storage adapters
The reference implementation uses gbrain + Neo4j. Adapters for other storage
backends are welcome:
- Weaviate (semantic layer)
- Amazon Neptune (graph layer)
- Qdrant (semantic layer)
- TigerGraph (graph layer)

### 4. Extraction improvements
The AI extractor in `extractor/extract.py` is a starting point.
Better prompts, better JSON schema enforcement, better deduplication logic —
all welcome.

### 5. The RESOLVE stage
This is the hardest open problem in CORTEX — and the most important.
Deduplicating knowledge nodes by semantic similarity, electing canonical nodes,
redirecting edges. If you have worked on entity resolution, record linkage,
or knowledge graph deduplication — we need you here.

## How to Contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-contribution`
3. Commit with a clear message
4. Open a PR with a description of what problem you are solving

## Code of Conduct

Be direct. Be specific. No hype. If something is incomplete, say so.
CORTEX started with a question that exposed a gap — that spirit continues.

---

*In the spirit of Gaurav — who asked the right question.*
