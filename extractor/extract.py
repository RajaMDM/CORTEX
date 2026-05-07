#!/usr/bin/env python3
"""
CORTEX — AI Entity Extractor (Stage 2: EXTRACT)

Reads any free-text knowledge source → AI extracts typed nodes + edges →
writes to semantic layer (gbrain) and graph layer (Neo4j).

Usage:
    python extractor/extract.py --text "Gaurav approved merging CUST-00142..."
    python extractor/extract.py --file path/to/decision.md
    python extractor/extract.py --gbrain-slug uc-c02-cross-channel-merge
    python extractor/extract.py --dry-run --file decision.md
"""

import json
import argparse
import os
import subprocess
import sys

CORTEX_PROMPT = """You are CORTEX — a knowledge graph extraction engine.

Given any free-text content, extract all typed nodes and relationships.

Return ONLY valid JSON:
{
  "nodes": [
    {
      "type": "DOMAIN|ENTITY|DECISION|RULE|CONCEPT|STEWARD|PROJECT|COMPLIANCE|SYSTEM|EVENT",
      "slug": "unique-kebab-case-id",
      "title": "Human Readable Title",
      "summary": "One precise sentence."
    }
  ],
  "edges": [
    {
      "from": "slug-a",
      "to": "slug-b",
      "type": "BELONGS_TO|APPROVED_BY|APPLIES_TO|RESOLVES|GOVERNED_BY|CONFLICTS_WITH|SUPERSEDES|EXTRACTED_FROM|RELATES_TO|DEPENDS_ON|TRIGGERED_BY|MERGED_INTO"
    }
  ]
}

Node type definitions:
- DOMAIN: A bounded subject area (Customer, Vendor, Finance, HR...)
- ENTITY: A named real-world object (person, company, product, asset)
- DECISION: A specific choice made at a point in time by someone
- RULE: A stated constraint, policy, validation, or standard
- CONCEPT: An abstract pattern or idea recurring across decisions
- STEWARD: A named person who owns or approves knowledge
- PROJECT: A bounded initiative or programme
- COMPLIANCE: A regulatory or governance framework
- SYSTEM: A named software system or data source
- EVENT: A named occurrence (incident, release, migration)

Rules:
- Every node needs at least one edge
- Slugs: lowercase, hyphens only, globally unique, specific
- Only extract what is explicitly stated — do not infer
- Be precise: "loyalty-tier-survivorship-rule" not "rule"
"""

def gbrain_cmd(cmd: str) -> dict:
    env = {**os.environ, "PATH": f"{os.path.expanduser('~/.bun/bin')}:{os.environ.get('PATH', '')}"}
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return {"out": result.stdout + result.stderr, "code": result.returncode}

def extract(text: str, source_slug: str = None, dry_run: bool = False) -> dict:
    """Core extraction: text in, typed nodes + edges out."""
    try:
        from anthropic import Anthropic
        client = Anthropic()
    except ImportError:
        print("pip install anthropic")
        sys.exit(1)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"{CORTEX_PROMPT}\n\nContent to extract from:\n\n{text[:4000]}"
        }]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1][4:] if parts[1].startswith("json") else parts[1]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Parse error on: {raw[:200]}")
        return {"nodes": [], "edges": []}

    nodes = result.get("nodes", [])
    edges = result.get("edges", [])

    # Add EXTRACTED_FROM edges if source provided
    if source_slug:
        for node in nodes:
            edges.append({"from": node["slug"], "to": source_slug, "type": "EXTRACTED_FROM"})

    if dry_run:
        print(f"\n📊 Extracted {len(nodes)} nodes, {len(edges)} edges (dry run)\n")
        for n in nodes:
            print(f"  [{n['type']}] {n['slug']}")
            print(f"    {n['title']} — {n['summary']}")
        print()
        for e in edges:
            print(f"  {e['from']} --[{e['type']}]--> {e['to']}")
        return result

    # Write to gbrain
    for node in nodes:
        body = f"""---
title: {node['title']}
type: {node['type'].lower()}
cortex_extracted: true
tags: [cortex, {node['type'].lower()}, auto-extracted]
---

# {node['title']}

{node['summary']}
"""
        cmd = f'echo {json.dumps(body)} | gbrain put {node["slug"]}'
        r = gbrain_cmd(cmd)
        status = "✓" if r["code"] == 0 else "✗"
        print(f"  {status} Node: {node['slug']}")

    for edge in edges:
        r = gbrain_cmd(f'gbrain link {edge["from"]} {edge["to"]} --type {edge["type"]}')
        ok = '"status":"ok"' in r["out"].replace(" ", "")
        status = "✓" if ok else "✗"
        print(f"  {status} Edge: {edge['from']} --[{edge['type']}]--> {edge['to']}")

    print(f"\n✅ {len(nodes)} nodes, {len(edges)} edges written to brain")
    return result

def main():
    parser = argparse.ArgumentParser(description="CORTEX AI Entity Extractor")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Free text to extract from")
    group.add_argument("--file", help="Markdown file to extract from")
    group.add_argument("--gbrain-slug", help="gbrain page slug to extract from")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.text:
        content = args.text
        source = None
    elif args.file:
        with open(args.file) as f:
            content = f.read()
        source = os.path.splitext(os.path.basename(args.file))[0]
    elif args.gbrain_slug:
        r = gbrain_cmd(f"gbrain get {args.gbrain_slug}")
        content = r["out"]
        source = args.gbrain_slug

    print(f"\n🧠 CORTEX Extractor")
    print(f"   Source: {source or 'inline text'}")
    print(f"   Mode: {'dry run' if args.dry_run else 'write'}\n")

    extract(content, source_slug=source, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
