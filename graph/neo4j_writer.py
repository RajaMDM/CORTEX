#!/usr/bin/env python3
"""
CORTEX — Neo4j Graph Layer Writer

Pushes extracted nodes + edges from gbrain into Neo4j for
full Cypher traversal and property graph queries.

Usage:
    python graph/neo4j_writer.py --test          # test connection
    python graph/neo4j_writer.py --node slug     # push one node
    python graph/neo4j_writer.py --from-gbrain   # push all cortex pages
"""

import os
import json
import argparse
import subprocess

NEO4J_URI  = os.environ.get("NEO4J_URI", "")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "")

def get_driver():
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j")
        raise
    if not NEO4J_URI:
        raise ValueError("Set NEO4J_URI environment variable. See graph/neo4j-setup.md")
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def gbrain(cmd):
    env = {**os.environ, "PATH": f"{os.path.expanduser('~/.bun/bin')}:{os.environ.get('PATH','')}"}
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return r.stdout + r.stderr

def test_connection():
    driver = get_driver()
    with driver.session() as s:
        result = s.run("RETURN 'CORTEX connected' as msg")
        print(result.single()["msg"])
    driver.close()
    print("✓ Neo4j connection OK")

def push_node(slug: str, title: str, node_type: str, summary: str = ""):
    driver = get_driver()
    with driver.session() as s:
        s.run("""
            MERGE (n:CortexNode {slug: $slug})
            SET n.title = $title,
                n.type = $type,
                n.summary = $summary,
                n.cortex_version = '0.1'
        """, slug=slug, title=title, type=node_type, summary=summary)

        # Add type label
        s.run(f"""
            MATCH (n:CortexNode {{slug: $slug}})
            SET n:{node_type}
        """, slug=slug)
    driver.close()
    print(f"  ✓ Node: [{node_type}] {slug}")

def push_edge(from_slug: str, to_slug: str, edge_type: str):
    driver = get_driver()
    with driver.session() as s:
        s.run(f"""
            MATCH (a:CortexNode {{slug: $from_slug}})
            MATCH (b:CortexNode {{slug: $to_slug}})
            MERGE (a)-[:{edge_type}]->(b)
        """, from_slug=from_slug, to_slug=to_slug)
    driver.close()
    print(f"  ✓ Edge: {from_slug} --[{edge_type}]--> {to_slug}")

def push_from_gbrain():
    """Read all cortex-tagged pages from gbrain and push to Neo4j."""
    raw = gbrain("gbrain list -n 500")
    pushed = 0
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or not line[0].isalpha():
            continue
        slug = line.split()[0]
        # Get page content
        content = gbrain(f"gbrain get {slug}")
        if "cortex_extracted: true" not in content and "type:" not in content:
            continue
        # Parse type from frontmatter
        node_type = "CONCEPT"
        title = slug.replace("-", " ").title()
        for l in content.split("\n"):
            if l.startswith("type:"):
                node_type = l.split(":", 1)[1].strip().upper()
            if l.startswith("title:"):
                title = l.split(":", 1)[1].strip()
        push_node(slug, title, node_type)
        pushed += 1

    print(f"\n✅ Pushed {pushed} nodes to Neo4j")

    # Push links
    raw = gbrain("gbrain list -n 500")
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or not line[0].isalpha():
            continue
        slug = line.split()[0]
        backlinks_raw = gbrain(f"gbrain backlinks {slug}")
        try:
            links = json.loads(backlinks_raw)
            for link in links:
                push_edge(link["from_slug"], link["to_slug"],
                         link.get("link_type", "RELATES_TO").upper() or "RELATES_TO")
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--node", help="Push single node by slug")
    parser.add_argument("--from-gbrain", action="store_true")
    args = parser.parse_args()

    if args.test:
        test_connection()
    elif args.from_gbrain:
        push_from_gbrain()
    elif args.node:
        content = gbrain(f"gbrain get {args.node}")
        node_type = "CONCEPT"
        title = args.node
        for l in content.split("\n"):
            if l.startswith("type:"):
                node_type = l.split(":", 1)[1].strip().upper()
            if l.startswith("title:"):
                title = l.split(":", 1)[1].strip()
        push_node(args.node, title, node_type)

if __name__ == "__main__":
    main()
