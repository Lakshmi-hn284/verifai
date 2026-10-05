"""
VERIFAI - NetworkX Knowledge Graph Provider
Provides in-memory & file-backed knowledge graph operations.
Fully implements KnowledgeGraphProvider interface without requiring an external Neo4j daemon.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import networkx as nx
from app.providers.base import KnowledgeGraphProvider
from app.core.config import settings


class NetworkXGraphProvider(KnowledgeGraphProvider):
    def __init__(self, persistence_file: Optional[str] = None):
        self.persistence_file = persistence_file or str(Path(settings.VAULT_STORAGE_PATH) / "knowledge_graph.json")
        self.graph = nx.MultiDiGraph()
        self._load()

    def _load(self):
        p = Path(self.persistence_file)
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data, edges="edges")
            except Exception:
                self.graph = nx.MultiDiGraph()

    def _save(self):
        p = Path(self.persistence_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = nx.node_link_data(self.graph, edges="edges")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    async def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> None:
        props = properties.copy()
        props["label"] = label
        self.graph.add_node(node_id, **props)
        self._save()

    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        props = (properties or {}).copy()
        props["relationship"] = relationship
        self.graph.add_edge(source_id, target_id, **props)
        self._save()

    async def get_user_subgraph(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch all connected nodes and edges accessible to user_id.
        Formatted for frontend visualization (e.g., vis-network / cytoscape).
        """
        nodes = []
        edges = []

        # Find nodes belonging or connected to user_id
        matching_nodes = set()
        for n, attrs in self.graph.nodes(data=True):
            if attrs.get("user_id") == user_id or n == user_id:
                matching_nodes.add(n)

        # Include 1-hop connected neighbors (e.g. skills, requirements)
        extended_nodes = set(matching_nodes)
        for n in matching_nodes:
            extended_nodes.update(self.graph.successors(n))
            extended_nodes.update(self.graph.predecessors(n))

        for n in extended_nodes:
            if n in self.graph:
                attrs = self.graph.nodes[n]
                nodes.append({
                    "id": str(n),
                    "label": attrs.get("label", "Node"),
                    "title": attrs.get("name", attrs.get("field_value", str(n))),
                    "group": attrs.get("label", "Default"),
                    "properties": {k: str(v) for k, v in attrs.items() if k not in ["label"]}
                })

        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if u in extended_nodes and v in extended_nodes:
                edges.append({
                    "from": str(u),
                    "to": str(v),
                    "label": data.get("relationship", "RELATED_TO"),
                    "relationship": data.get("relationship", "RELATED_TO"),
                    "properties": {k: str(v) for k, v in data.items() if k not in ["relationship"]}
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

    async def delete_node(self, node_id: str) -> None:
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            self._save()
