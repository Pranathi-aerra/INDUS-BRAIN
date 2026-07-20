"""
Nazar — Knowledge Graph Service
NetworkX-based industrial knowledge graph.
Manages entities, relationships, and graph queries.
"""
import networkx as nx
import json
from typing import List, Dict, Any, Optional, Tuple


class KnowledgeGraph:
    """Industrial Knowledge Graph built on NetworkX."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self._initialized = False
    
    def is_initialized(self):
        return self._initialized
    
    # ---- Node Operations ----
    
    def add_node(self, node_id: str, node_type: str, **properties):
        """Add or update a node in the graph."""
        self.graph.add_node(node_id, node_type=node_type, **properties)
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node data by ID."""
        if node_id in self.graph:
            return {"id": node_id, **self.graph.nodes[node_id]}
        return None
    
    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Get all nodes of a given type."""
        return [
            {"id": n, **self.graph.nodes[n]}
            for n in self.graph.nodes
            if self.graph.nodes[n].get("node_type") == node_type
        ]
    
    # ---- Edge Operations ----
    
    def add_edge(self, source: str, target: str, relationship: str, **properties):
        """Add a relationship between two nodes."""
        self.graph.add_edge(source, target, relationship=relationship, **properties)
    
    def get_edges(self, node_id: str) -> List[Dict]:
        """Get all edges connected to a node."""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            if u == node_id or v == node_id:
                edges.append({"source": u, "target": v, **data})
        return edges
    
    def get_neighbors(self, node_id: str, relationship: str = None) -> List[Dict]:
        """Get neighbors of a node, optionally filtered by relationship type."""
        neighbors = []
        for _, target, data in self.graph.out_edges(node_id, data=True):
            if relationship is None or data.get("relationship") == relationship:
                neighbors.append({"id": target, **self.graph.nodes.get(target, {}), "relationship": data})
        for source, _, data in self.graph.in_edges(node_id, data=True):
            if relationship is None or data.get("relationship") == relationship:
                neighbors.append({"id": source, **self.graph.nodes.get(source, {}), "relationship": data})
        return neighbors
    
    # ---- Query Operations ----
    
    def find_path(self, source: str, target: str) -> List[str]:
        """Find shortest path between two nodes."""
        try:
            return nx.shortest_path(self.graph, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def search_nodes(self, query: str, node_type: str = None) -> List[Dict]:
        """Search nodes by text in their properties."""
        query_lower = query.lower()
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if node_type and data.get("node_type") != node_type:
                continue
            # Search in node ID and all string properties
            searchable = f"{node_id} " + " ".join(
                str(v) for v in data.values() if isinstance(v, str)
            )
            if query_lower in searchable.lower():
                results.append({"id": node_id, **data})
        return results
    
    def get_subgraph(self, center_node: str, depth: int = 2) -> Dict:
        """Get a subgraph around a center node up to given depth."""
        if center_node not in self.graph:
            return {"nodes": [], "edges": []}
        
        # BFS to collect nodes within depth
        visited = {center_node}
        frontier = {center_node}
        for _ in range(depth):
            next_frontier = set()
            for node in frontier:
                for neighbor in nx.all_neighbors(self.graph, node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.add(neighbor)
            frontier = next_frontier
        
        # Build subgraph
        sub = self.graph.subgraph(visited)
        nodes = [{"id": n, **sub.nodes[n]} for n in sub.nodes]
        edges = [{"source": u, "target": v, **d} for u, v, d in sub.edges(data=True)]
        return {"nodes": nodes, "edges": edges}
    
    def get_full_graph(self, max_nodes: int = 200) -> Dict:
        """Get the full graph (limited to max_nodes) for visualization."""
        nodes_list = list(self.graph.nodes(data=True))[:max_nodes]
        node_ids = {n[0] for n in nodes_list}
        
        nodes = [{"id": n, **data} for n, data in nodes_list]
        edges = [
            {"source": u, "target": v, **d}
            for u, v, d in self.graph.edges(data=True)
            if u in node_ids and v in node_ids
        ]
        return {"nodes": nodes, "edges": edges}
    
    def get_stats(self) -> Dict:
        """Get graph statistics."""
        type_counts = {}
        for _, data in self.graph.nodes(data=True):
            t = data.get("node_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        rel_counts = {}
        for _, _, data in self.graph.edges(data=True):
            r = data.get("relationship", "unknown")
            rel_counts[r] = rel_counts.get(r, 0) + 1
        
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": type_counts,
            "relationship_types": rel_counts,
        }
    
    # ---- Seed from data ----
    
    def build_from_seed_data(self, data: Dict):
        """Build the knowledge graph from seed data."""
        
        # 1. Add equipment nodes
        for eq in data.get("equipment", []):
            self.add_node(
                eq["tag"], "equipment",
                label=f"{eq['tag']} — {eq['name']}",
                name=eq["name"],
                equipment_type=eq["equipment_type"],
                area=eq.get("area", ""),
                manufacturer=eq.get("manufacturer", ""),
                status=eq.get("status", "operational"),
                criticality=eq.get("criticality", "medium"),
                install_date=eq.get("install_date", ""),
            )
        
        # Add area nodes and connect equipment
        areas = set(eq.get("area", "") for eq in data.get("equipment", []) if eq.get("area"))
        for area in areas:
            self.add_node(area, "area", label=area, name=area)
        for eq in data.get("equipment", []):
            if eq.get("area"):
                self.add_edge(eq["tag"], eq["area"], "located_in")
        
        # Connect parent-child equipment
        for eq in data.get("equipment", []):
            if eq.get("parent_tag"):
                self.add_edge(eq["tag"], eq["parent_tag"], "part_of")
        
        # 2. Add work order nodes and connect to equipment
        for wo in data.get("work_orders", []):
            self.add_node(
                wo["wo_number"], "work_order",
                label=wo["wo_number"],
                wo_type=wo["wo_type"],
                priority=wo.get("priority", "medium"),
                status=wo.get("status", "open"),
                description=wo.get("description", "")[:200],
                equipment_tag=wo["equipment_tag"],
                reported_date=wo.get("reported_date", ""),
                downtime_hours=wo.get("downtime_hours", 0),
            )
            self.add_edge(wo["wo_number"], wo["equipment_tag"], "maintenance_on")
            
            # Add technician node
            tech = wo.get("technician")
            if tech:
                self.add_node(tech, "person", label=tech, name=tech, role="technician")
                self.add_edge(wo["wo_number"], tech, "assigned_to")
        
        # 3. Add inspection nodes
        for insp in data.get("inspections", []):
            self.add_node(
                insp["inspection_id"], "inspection",
                label=insp["inspection_id"],
                inspection_type=insp["inspection_type"],
                status=insp.get("status", "completed"),
                severity=insp.get("severity", "none"),
                findings=insp.get("findings", "")[:200],
                inspection_date=insp.get("inspection_date", ""),
                regulatory_ref=insp.get("regulatory_ref", ""),
            )
            if insp.get("equipment_tag"):
                self.add_edge(insp["inspection_id"], insp["equipment_tag"], "inspected")
            
            # Connect to regulation
            if insp.get("regulatory_ref"):
                reg_id = insp["regulatory_ref"].replace(" ", "_")
                if reg_id not in self.graph:
                    self.add_node(reg_id, "regulation", label=insp["regulatory_ref"], name=insp["regulatory_ref"])
                self.add_edge(insp["inspection_id"], reg_id, "governed_by")
        
        # 4. Add incident nodes
        for inc in data.get("incidents", []):
            self.add_node(
                inc["incident_id"], "incident",
                label=inc["incident_id"],
                incident_type=inc["incident_type"],
                severity=inc.get("severity", "low"),
                description=inc.get("description", "")[:200],
                root_cause=inc.get("root_cause", "")[:200],
                date_occurred=inc.get("date_occurred", ""),
                area=inc.get("area", ""),
                lessons_learned=inc.get("lessons_learned", "")[:200],
            )
            if inc.get("equipment_tag"):
                self.add_edge(inc["incident_id"], inc["equipment_tag"], "occurred_on")
        
        # 5. Add compliance requirement nodes
        for req in data.get("compliance_requirements", []):
            self.add_node(
                req["req_id"], "compliance",
                label=f"{req['regulation']} {req.get('clause', '')}",
                regulation=req["regulation"],
                clause=req.get("clause", ""),
                requirement_text=req.get("requirement_text", "")[:200],
                current_status=req.get("current_status", "unknown"),
                category=req.get("category", ""),
            )
            # Connect regulation node
            reg_name = req["regulation"].replace(" ", "_")
            if reg_name not in self.graph:
                self.add_node(reg_name, "regulation", label=req["regulation"], name=req["regulation"])
            self.add_edge(req["req_id"], reg_name, "part_of_regulation")
        
        # 6. Add SOP document nodes
        for sop in data.get("sops", []):
            self.add_node(
                sop["doc_id"], "document",
                label=sop["title"],
                title=sop["title"],
                doc_type=sop.get("doc_type", "sop"),
            )
        
        # 7. Connect equipment to P&ID connectivity (basic piping connections)
        piping_connections = [
            ("V-101", "HX-101", "feeds_into"),
            ("HX-101", "HX-102", "feeds_into"),
            ("HX-102", "H-101", "feeds_into"),
            ("H-101", "V-102", "feeds_into"),
            ("V-102", "V-201", "naphtha_to"),
            ("V-102", "V-103", "residue_to"),
            ("P-101-A", "V-101", "pumps_to"),
            ("P-101-B", "V-101", "pumps_to"),
            ("P-201-A", "V-201", "pumps_to"),
            ("HX-301", "V-102", "condenses_for"),
            ("PSV-101", "V-102", "protects"),
            ("PSV-301", "V-301", "protects"),
            ("TI-1001", "V-102", "monitors"),
            ("PI-1002", "V-102", "monitors"),
            ("FI-2001", "V-201", "monitors"),
            ("LI-3001", "V-301", "monitors"),
            ("XV-101", "V-101", "isolates"),
            ("CV-201", "V-201", "controls_flow_to"),
            ("C-101", "V-102", "compresses_gas_from"),
        ]
        for src, tgt, rel in piping_connections:
            if src in self.graph and tgt in self.graph:
                self.add_edge(src, tgt, rel)
        
        self._initialized = True
        stats = self.get_stats()
        print(f"[KG] Knowledge graph built: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
        return stats


# Singleton instance
knowledge_graph = KnowledgeGraph()
