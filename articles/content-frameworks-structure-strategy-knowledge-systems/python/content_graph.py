"""
Content Frameworks: Pillar, Cluster, and Internal-Link Graph

Educational workflow for modeling content as a graph of pillars, articles,
related topics, and internal links.
"""

from __future__ import annotations

import pandas as pd
import networkx as nx


def build_content_graph(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> nx.DiGraph:
    """Build a directed content graph from node and edge tables."""
    graph = nx.DiGraph()

    for _, row in nodes_df.iterrows():
        graph.add_node(row["node_id"], node_type=row["node_type"], title=row["title"])

    for _, row in edges_df.iterrows():
        graph.add_edge(row["source"], row["target"], relationship=row["relationship"])

    return graph


def graph_metrics(graph: nx.DiGraph) -> pd.DataFrame:
    """Calculate simple graph metrics for content architecture."""
    centrality = nx.degree_centrality(graph)

    return pd.DataFrame({
        "node_id": list(graph.nodes()),
        "title": [graph.nodes[node]["title"] for node in graph.nodes()],
        "node_type": [graph.nodes[node]["node_type"] for node in graph.nodes()],
        "in_degree": [graph.in_degree(node) for node in graph.nodes()],
        "out_degree": [graph.out_degree(node) for node in graph.nodes()],
        "degree_centrality": [centrality[node] for node in graph.nodes()]
    }).sort_values("degree_centrality", ascending=False)


def main() -> None:
    nodes = pd.read_csv("../data/content_nodes.csv")
    edges = pd.read_csv("../data/content_edges.csv")

    graph = build_content_graph(nodes, edges)
    metrics = graph_metrics(graph)

    metrics["underconnected"] = (
        (metrics["in_degree"] == 0)
        & (metrics["out_degree"] == 0)
    )

    print(metrics)

    metrics.to_csv("../outputs/content_graph_metrics.csv", index=False)


if __name__ == "__main__":
    main()
