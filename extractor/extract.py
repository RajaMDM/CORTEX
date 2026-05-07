#!/usr/bin/env python3
"""
CORTEX — AI Entity Extractor + Neo4j Writer
Reads plain text MDM content → AI extracts typed nodes + edges
→ writes to gbrain (semantic layer) + Neo4j (graph layer)

Usage:
    python3 extractor/extract.py --text "your MDM content"
    python3 extractor/extract.py --slug uc-c02-cross-channel-merge
    python3 extractor/extract.py --limit 10
    python3 extractor/extract.py --dry-run --limit 5
"""

import os, sys, json, subprocess, argparse

# ── OpenAI ────────────────────────────────────────────────────────────────────
from openai import OpenAI
oai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ── Neo4j ─────────────────────────────────────────────────────────────────────
from neo4j import GraphDatabase
NEO4J_URI  = os.environ.get("NEO4J_URI",  "neo4j+s://050018f2.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "050018f2")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "")
neo = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ── gbrain ────────────────────────────────────────────────────────────────────
BENV = {**os.environ, "PATH": f"{os.path.expanduser('~/.bun/bin')}:{os.environ.get('PATH','')}"}

def gbrain(cmd):
    r = subprocess.run(f"gbrain {cmd}", shell=True,
                       capture_output=True, text=True, env=BENV)
    return r.stdout + r.stderr

# ── Extraction prompt ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are CORTEX — a knowledge graph extractor for MDM (Master Data Management).

Given MDM content, extract all meaningful typed nodes and their relationships.

Return ONLY valid JSON with this exact structure:
{
  "nodes": [
    {
      "type": "DOMAIN|ENTITY|DECISION|RULE|CONCEPT|STEWARD|PROJECT|COMPLIANCE|PIPELINE",
      "slug": "kebab-case-id",
      "title": "Human Readable Title",
      "summary": "One sentence description"
    }
  ],
  "edges": [
    {
      "from": "slug-a",
      "to": "slug-b",
      "type": "BELONGS_TO|APPROVED_BY|APPLIES_TO|RESOLVES|GOVERNED_BY|RELATES_TO|EXTRACTED_FROM"
    }
  ]
}

Node type guide:
- DOMAIN: Customer, Vendor, Product, Asset, Location, Employee, Counterparty
- ENTITY: Named real-world objects (people, companies, products, locations)
- DECISION: Specific choices made (merge decisions, approvals, overrides)
- RULE: DQ rules, matching rules, survivorship rules
- CONCEPT: Abstract MDM ideas (dual-role detection, golden record conflict)
- STEWARD: People who own/approve decisions
- PROJECT: Business initiatives
- COMPLIANCE: Regulatory frameworks (GDPR, UAE PDPL, etc.)
- PIPELINE: ASSAY/UNEARTH/REFINE/UNFURL/MARK stages

Rules:
- Every node must link via at least one edge
- Slugs: lowercase, hyphens only, unique
- Include EXTRACTED_FROM edge from each node back to the source page slug
- Be specific: "loyalty-tier-survivorship" not just "survivorship"
"""

def extract(source_slug: str, content: str, dry_run=False) -> dict:
    """Extract typed nodes + edges from content using GPT-4o."""
    resp = oai.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Source page: {source_slug}\n\n{content[:4000]}"}
        ]
    )
    try:
        data = json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"    ⚠ Parse error: {e}")
        return {"nodes": [], "edges": []}

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    print(f"    → {len(nodes)} nodes, {len(edges)} edges")

    if dry_run:
        for n in nodes:
            print(f"       NODE [{n['type']}] {n['slug']}: {n['title']}")
        for e in edges:
            print(f"       EDGE {e['from']} --[{e['type']}]--> {e['to']}")
        return data

    # ── Write to gbrain ───────────────────────────────────────────────────────
    for n in nodes:
        page_md = f"""---
title: {n['title']}
type: {n['type'].lower()}
cortex: true
source: {source_slug}
tags: [cortex, {n['type'].lower()}]
---

# {n['title']}

{n['summary']}

Extracted from: [[{source_slug}]]
"""
        proc = subprocess.run(
            f"gbrain put {n['slug']}",
            input=page_md, shell=True,
            capture_output=True, text=True, env=BENV
        )
        status = "✓" if proc.returncode == 0 else "⚠"
        print(f"    {status} gbrain: [{n['type']}] {n['slug']}")

    for e in edges:
        out = gbrain(f"link {e['from']} {e['to']} --type {e['type']}")
        ok = "ok" in out.lower()
        print(f"    {'✓' if ok else '⚠'} link: {e['from']} --[{e['type']}]--> {e['to']}")

    # ── Write to Neo4j ────────────────────────────────────────────────────────
    with neo.session() as s:
        for n in nodes:
            safe_label = n["type"].replace("-","_").upper()
            s.run("""
                MERGE (x:CortexNode {slug: $slug})
                SET x.title=$title, x.type=$type, x.summary=$summary, x.source=$src
            """, slug=n["slug"], title=n["title"],
                 type=n["type"], summary=n["summary"], src=source_slug)
            s.run(f"MATCH (x:CortexNode {{slug:$slug}}) SET x:{safe_label}",
                  slug=n["slug"])
            print(f"    ✓ neo4j: [{n['type']}] {n['slug']}")

        for e in edges:
            rel = e["type"].replace("-","_").upper()
            s.run(f"""
                MATCH (a:CortexNode {{slug:$from_s}})
                MATCH (b:CortexNode {{slug:$to_s}})
                MERGE (a)-[:{rel}]->(b)
            """, from_s=e["from"], to_s=e["to"])

    return data


def get_gbrain_pages(limit=10):
    raw = gbrain("list -n 200")
    slugs = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line and line[0].isalpha() and " " in line:
            slugs.append(line.split()[0])
    return slugs[:limit]


def main():
    ap = argparse.ArgumentParser(description="CORTEX AI Entity Extractor")
    ap.add_argument("--text",    help="Extract from raw text string")
    ap.add_argument("--slug",    help="Extract from a single gbrain page")
    ap.add_argument("--limit",   type=int, default=10)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total_nodes = total_edges = 0

    if args.text:
        result = extract("inline-text", args.text, dry_run=args.dry_run)
        total_nodes = len(result.get("nodes", []))
        total_edges = len(result.get("edges", []))

    elif args.slug:
        content = gbrain(f"get {args.slug}")
        result  = extract(args.slug, content, dry_run=args.dry_run)
        total_nodes = len(result.get("nodes", []))
        total_edges = len(result.get("edges", []))

    else:
        slugs = get_gbrain_pages(args.limit)
        print(f"Processing {len(slugs)} pages...\n")

        # Count neo4j before
        with neo.session() as s:
            before_nodes = s.run("MATCH (n:CortexNode) RETURN count(n) as c").single()["c"]
            before_edges = s.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]

        for i, slug in enumerate(slugs, 1):
            print(f"  [{i}/{len(slugs)}] {slug}")
            content = gbrain(f"get {slug}")
            if len(content.strip()) < 80:
                print("    (skipped — too short)")
                continue
            result = extract(slug, content, dry_run=args.dry_run)
            total_nodes += len(result.get("nodes", []))
            total_edges += len(result.get("edges", []))
            print()

        with neo.session() as s:
            after_nodes = s.run("MATCH (n:CortexNode) RETURN count(n) as c").single()["c"]
            after_edges = s.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]

        print("=" * 50)
        print("✅ CORTEX extraction complete")
        print(f"\n  Pages processed  : {len(slugs)}")
        print(f"  Nodes extracted  : {total_nodes}")
        print(f"  Edges created    : {total_edges}")
        print(f"\n  Neo4j before     : {before_nodes} nodes, {before_edges} edges")
        print(f"  Neo4j after      : {after_nodes} nodes, {after_edges} edges")
        print(f"  Net new nodes    : {after_nodes - before_nodes}")
        print(f"  Net new edges    : {after_edges - before_edges}")
        return

    print(f"\n✅ Done — {total_nodes} nodes, {total_edges} edges")


if __name__ == "__main__":
    main()
