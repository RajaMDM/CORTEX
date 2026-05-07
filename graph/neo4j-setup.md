# CORTEX — Neo4j Graph Layer Setup

## Quickest Path: Neo4j AuraDB Free Tier

No install. No Docker. Full property graph. Free forever for the free tier.

### Step 1 — Create your free instance
1. Go to: https://neo4j.com/cloud/platform/aura-graph-database/
2. Sign up → Create Free Instance
3. Save the credentials shown (username, password, connection URI)
4. URI format: `neo4j+s://xxxxxxxx.databases.neo4j.io`

### Step 2 — Install the Python driver
```bash
pip install neo4j
```

### Step 3 — Set environment variables
```bash
export NEO4J_URI="neo4j+s://xxxxxxxx.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
```

### Step 4 — Test connection
```bash
python graph/neo4j_writer.py --test
```

### Step 5 — Push your CORTEX graph to Neo4j
```bash
python graph/neo4j_writer.py --from-gbrain
```

---

## The Graph Schema in Cypher

```cypher
// Constraints (run once on fresh DB)
CREATE CONSTRAINT cortex_slug IF NOT EXISTS
FOR (n:CortexNode) REQUIRE n.slug IS UNIQUE;

// Node creation pattern
MERGE (n:CortexNode {slug: $slug})
SET n.title = $title,
    n.type = $type,
    n.summary = $summary,
    n.cortex_version = "0.1"
WITH n
CALL apoc.create.addLabels(n, [$type]) YIELD node
RETURN node;

// Edge creation pattern
MATCH (a:CortexNode {slug: $from}), (b:CortexNode {slug: $to})
CALL apoc.create.relationship(a, $type, {}, b) YIELD rel
RETURN rel;
```

## Useful Cypher Queries

```cypher
-- All decisions approved by a steward
MATCH (d:DECISION)-[:APPROVED_BY]->(s:STEWARD)
RETURN d.title, s.title, d.slug
ORDER BY d.title;

-- Everything connected to Customer domain
MATCH (n)-[r]-(d:DOMAIN {slug: "customer-domain"})
RETURN n.title, type(r), d.title;

-- Two-hop graph from any node
MATCH path = (start {slug: "uc-c02-cross-channel-merge"})-[*1..2]-(connected)
RETURN path;

-- Rules that apply to multiple domains
MATCH (r:RULE)-[:APPLIES_TO]->(d:DOMAIN)
WITH r, count(d) as domain_count
WHERE domain_count > 1
RETURN r.title, domain_count
ORDER BY domain_count DESC;

-- Steward knowledge load (decisions approved)
MATCH (d:DECISION)-[:APPROVED_BY]->(s:STEWARD)
WITH s, count(d) as total
RETURN s.title as steward, total
ORDER BY total DESC;
```
