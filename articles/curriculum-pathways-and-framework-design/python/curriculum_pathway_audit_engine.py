#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
import csv, json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
AUDIT_LOGS = ROOT / "outputs" / "audit_logs"
CATALOG = ROOT / "outputs" / "catalog_exports"

THRESHOLD = 0.78
WEIGHTS = {
    "sequence_support": 0.22,
    "objective_alignment": 0.22,
    "accessibility": 0.16,
    "feedback": 0.18,
    "transfer": 0.22
}

@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    identifier: str
    message: str
    recommended_action: str

def yes(value):
    return str(value).strip().lower() in {"yes", "true", "1", "ready", "complete"}

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def build_graph(prerequisites):
    requires = defaultdict(set)
    supports = defaultdict(set)
    for row in prerequisites:
        requires[row["node_slug"]].add(row["prerequisite_slug"])
        supports[row["prerequisite_slug"]].add(row["node_slug"])
    return requires, supports

def prerequisite_report(nodes, prerequisites):
    node_by_slug = {node["node_slug"]: node for node in nodes}
    requires, supports = build_graph(prerequisites)
    rows, findings = [], []

    for node in nodes:
        slug = node["node_slug"]
        required = requires.get(slug, set())
        published = [item for item in required if item in node_by_slug and node_by_slug[item]["status"] == "published"]
        readiness = len(published) / len(required) if required else 1.0

        rows.append({
            "node_slug": slug,
            "title": node["title"],
            "learning_stage": node["learning_stage"],
            "required_prerequisites": len(required),
            "published_prerequisites": len(published),
            "prerequisite_readiness": round(readiness, 4),
            "supports_downstream_nodes": len(supports.get(slug, set()))
        })

        if node["status"] == "published" and readiness < 0.8:
            findings.append(Finding(
                "medium",
                "prerequisites",
                slug,
                f"Prerequisite readiness is {readiness:.0%}.",
                "Publish, link, or revise prerequisite learning nodes."
            ))

    return rows, findings

def objective_report(nodes, objectives):
    by_node = defaultdict(list)
    for objective in objectives:
        by_node[objective["node_slug"]].append(objective)

    rows, findings = [], []

    for node in nodes:
        slug = node["node_slug"]
        required = [item for item in by_node.get(slug, []) if yes(item["required"])]
        supported = [item for item in required if yes(item["support_material_present"])]
        assessed = [item for item in required if yes(item["assessment_present"])]

        coverage = len(supported) / len(required) if required else 1.0
        assessment = len(assessed) / len(required) if required else 1.0

        rows.append({
            "node_slug": slug,
            "title": node["title"],
            "required_objectives": len(required),
            "supported_required_objectives": len(supported),
            "assessed_required_objectives": len(assessed),
            "objective_coverage_score": round(coverage, 4),
            "assessment_alignment_score": round(assessment, 4)
        })

        if node["status"] == "published" and coverage < 0.8:
            findings.append(Finding(
                "medium",
                "objective_coverage",
                slug,
                f"Objective coverage is {coverage:.0%}.",
                "Add support materials for required learning objectives."
            ))

    return rows, findings

def pathway_readiness(nodes, prereq_rows, objective_rows):
    prereq = {row["node_slug"]: row for row in prereq_rows}
    objective = {row["node_slug"]: row for row in objective_rows}
    rows, findings = [], []

    for node in nodes:
        slug = node["node_slug"]
        sequence = float(prereq[slug]["prerequisite_readiness"])
        objective_alignment = float(objective[slug]["objective_coverage_score"])

        accessibility = (
            int(yes(node["clear_headings"])) +
            int(yes(node["descriptive_links"])) +
            int(yes(node["alt_text"])) +
            int(yes(node["plain_language_summary"]))
        ) / 4

        feedback = (
            int(yes(node["reflection_prompt"])) +
            int(yes(node["assessment_point"])) +
            int(yes(node["revision_prompt"]))
        ) / 3

        transfer = (
            int(yes(node["application_example"])) +
            int(yes(node["transfer_task"])) +
            int(yes(node["repository_support"]))
        ) / 3

        readiness = (
            WEIGHTS["sequence_support"] * sequence +
            WEIGHTS["objective_alignment"] * objective_alignment +
            WEIGHTS["accessibility"] * accessibility +
            WEIGHTS["feedback"] * feedback +
            WEIGHTS["transfer"] * transfer
        )

        status = "ready" if readiness >= THRESHOLD else "governance review"

        rows.append({
            "node_slug": slug,
            "title": node["title"],
            "status": node["status"],
            "pathway_cluster": node["pathway_cluster"],
            "learning_stage": node["learning_stage"],
            "sequence_support_score": round(sequence, 4),
            "objective_alignment_score": round(objective_alignment, 4),
            "accessibility_score": round(accessibility, 4),
            "feedback_score": round(feedback, 4),
            "transfer_score": round(transfer, 4),
            "pathway_readiness_score": round(readiness, 4),
            "pathway_status": status
        })

        if node["status"] == "published" and status != "ready":
            findings.append(Finding(
                "medium",
                "pathway_readiness",
                slug,
                f"Pathway readiness is {readiness:.2f}.",
                "Review sequence support, objectives, accessibility, feedback, and transfer supports."
            ))

    return rows, findings

def pathway_depth(nodes, prerequisites):
    node_by_slug = {node["node_slug"]: node for node in nodes}
    _, supports = build_graph(prerequisites)
    roots = [node["node_slug"] for node in nodes if node["learning_stage"] in {"orientation", "foundation"}]

    distance = {slug: None for slug in node_by_slug}
    queue = deque()
    for root in roots:
        distance[root] = 0
        queue.append((root, 0))

    while queue:
        current, depth = queue.popleft()
        for target in supports.get(current, set()):
            if target in distance and distance[target] is None:
                distance[target] = depth + 1
                queue.append((target, depth + 1))

    return [{
        "node_slug": slug,
        "title": node_by_slug[slug]["title"],
        "learning_stage": node_by_slug[slug]["learning_stage"],
        "pathway_depth": distance[slug] if distance[slug] is not None else "unreachable",
        "reachable_from_foundation": distance[slug] is not None
    } for slug in sorted(node_by_slug)]

def cluster_coverage(nodes):
    grouped = defaultdict(Counter)
    for node in nodes:
        grouped[node["pathway_cluster"]][node["status"]] += 1

    rows = []
    for cluster in sorted(grouped):
        total = sum(grouped[cluster].values())
        published = grouped[cluster]["published"]
        rows.append({
            "pathway_cluster": cluster,
            "published": published,
            "planned": grouped[cluster]["planned"],
            "total": total,
            "published_coverage_rate": round(published / total, 4) if total else 0.0
        })
    return rows

def main():
    for d in [TABLES, REPORTS, AUDIT_LOGS, CATALOG]:
        d.mkdir(parents=True, exist_ok=True)

    nodes = read_csv(DATA / "curriculum_pathway_inventory.csv")
    prerequisites = read_csv(DATA / "prerequisite_relationships.csv")
    objectives = read_csv(DATA / "learning_objectives.csv")
    manual_queue = read_csv(DATA / "editorial_review_queue.csv")

    prereq_rows, prereq_findings = prerequisite_report(nodes, prerequisites)
    objective_rows, objective_findings = objective_report(nodes, objectives)
    readiness_rows, readiness_findings = pathway_readiness(nodes, prereq_rows, objective_rows)
    depth_rows = pathway_depth(nodes, prerequisites)
    coverage_rows = cluster_coverage(nodes)

    findings = prereq_findings + objective_findings + readiness_findings

    queue_rows = [
        {
            "source": "manual_review_queue",
            "severity": row["severity"],
            "category": row["issue_type"],
            "identifier": row["record_id"],
            "message": row["review_note"],
            "recommended_action": "Resolve through curriculum pathway governance."
        }
        for row in manual_queue
    ] + [asdict(finding) for finding in findings]

    catalog_rows = [{
        "series": "Content Frameworks",
        "node_slug": row["node_slug"],
        "title": row["title"],
        "pathway_cluster": row["pathway_cluster"],
        "learning_stage": row["learning_stage"],
        "pathway_readiness_score": row["pathway_readiness_score"],
        "pathway_status": row["pathway_status"],
        "github_path": f"articles/{row['node_slug']}/"
    } for row in readiness_rows]

    write_csv(TABLES / "prerequisite_readiness_report.csv", prereq_rows)
    write_csv(TABLES / "objective_coverage_report.csv", objective_rows)
    write_csv(TABLES / "pathway_readiness_report.csv", readiness_rows)
    write_csv(TABLES / "pathway_depth_report.csv", depth_rows)
    write_csv(TABLES / "cluster_coverage_report.csv", coverage_rows)
    write_csv(TABLES / "curriculum_pathway_governance_queue.csv", queue_rows)
    write_csv(CATALOG / "curriculum_pathway_catalog_export.csv", catalog_rows)

    report = {
        "article": "Curriculum Pathways and Framework Design",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "nodes": len(nodes),
            "prerequisite_relationships": len(prerequisites),
            "learning_objectives": len(objectives),
            "findings": len(findings),
            "governance_queue": len(queue_rows)
        },
        "pathway_readiness": readiness_rows,
        "governance_queue": queue_rows
    }

    write_json(REPORTS / "curriculum_pathway_audit.json", report)
    write_json(AUDIT_LOGS / "curriculum_pathway_findings.json", [asdict(finding) for finding in findings])
    (REPORTS / "curriculum_pathway_audit.md").write_text("# Curriculum Pathway Audit\n\nGenerated outputs are available in `outputs/`.\n", encoding="utf-8")

    print("Curriculum pathway audit complete.")
    print(TABLES / "pathway_readiness_report.csv")
    print(TABLES / "curriculum_pathway_governance_queue.csv")
    print(REPORTS / "curriculum_pathway_audit.json")

if __name__ == "__main__":
    main()
