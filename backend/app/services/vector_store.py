"""
Nazar — Vector Store Service
ChromaDB-based vector store for semantic search over industrial documents.
"""
import chromadb
from chromadb.config import Settings
import hashlib
import re
from typing import List, Dict, Any, Optional
from app.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP


class VectorStore:
    """ChromaDB vector store for industrial document search."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialized = False
    
    def initialize(self):
        """Initialize ChromaDB client and collection."""
        if self._initialized:
            return
        
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
        self._initialized = True
        count = self.collection.count()
        print(f"[VectorStore] Initialized. Collection '{CHROMA_COLLECTION}' has {count} documents.")
    
    def _chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks."""
        if not text or len(text.strip()) == 0:
            return []
        
        # Split by sentences/paragraphs for better context preservation
        sentences = re.split(r'(?<=[.!?\n])\s+', text.strip())
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            if current_length + sentence_len > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Keep overlap
                overlap_text = " ".join(current_chunk)
                overlap_words = overlap_text.split()[-overlap:]
                current_chunk = overlap_words
                current_length = sum(len(w) + 1 for w in current_chunk)
            current_chunk.append(sentence)
            current_length += sentence_len + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [text[:chunk_size]]
    
    def _make_id(self, doc_id: str, chunk_index: int) -> str:
        """Generate a deterministic ID for a chunk."""
        raw = f"{doc_id}::chunk_{chunk_index}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """Add a document to the vector store (chunked)."""
        self.initialize()
        
        chunks = self._chunk_text(text)
        if not chunks:
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = self._make_id(doc_id, i)
            chunk_meta = {
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {})
            }
            # ChromaDB requires metadata values to be str, int, float, or bool
            clean_meta = {}
            for k, v in chunk_meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
            
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(clean_meta)
        
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return len(chunks)
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None) -> List[Dict]:
        """Semantic search across all documents."""
        self.initialize()
        
        kwargs = {
            "query_texts": [query],
            "n_results": min(n_results, self.collection.count() or 1),
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata
        
        results = self.collection.query(**kwargs)
        
        output = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                output.append({
                    "text": doc,
                    "metadata": meta,
                    "relevance_score": round(max(0, 1 - distance), 3),
                    "doc_id": meta.get("doc_id", "unknown"),
                })
        
        return output
    
    def delete_document(self, doc_id: str):
        """Delete all chunks for a document."""
        self.initialize()
        # Get all chunks for this doc_id
        results = self.collection.get(
            where={"doc_id": doc_id}
        )
        if results and results["ids"]:
            self.collection.delete(ids=results["ids"])
    
    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        self.initialize()
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": CHROMA_COLLECTION,
        }
    
    def seed_from_data(self, seed_data: Dict):
        """Index all seed data into the vector store."""
        self.initialize()
        total_chunks = 0
        
        # Index SOPs
        for sop in seed_data.get("sops", []):
            n = self.add_document(
                sop["doc_id"], sop["content_text"],
                {"title": sop["title"], "doc_type": "sop"}
            )
            total_chunks += n
        
        # Index work orders (combine description + root_cause + action)
        for wo in seed_data.get("work_orders", []):
            text_parts = [
                f"Work Order: {wo['wo_number']}",
                f"Equipment: {wo['equipment_tag']}",
                f"Type: {wo['wo_type']} | Priority: {wo.get('priority', 'medium')}",
                f"Description: {wo.get('description', '')}",
                f"Root Cause: {wo.get('root_cause', 'N/A')}",
                f"Action Taken: {wo.get('action_taken', 'N/A')}",
                f"Technician: {wo.get('technician', 'N/A')}",
                f"Date: {wo.get('reported_date', 'N/A')}",
            ]
            text = "\n".join(text_parts)
            n = self.add_document(
                wo["wo_number"], text,
                {"title": wo["wo_number"], "doc_type": "work_order", "equipment_tag": wo["equipment_tag"]}
            )
            total_chunks += n
        
        # Index inspections
        for insp in seed_data.get("inspections", []):
            text_parts = [
                f"Inspection: {insp['inspection_id']}",
                f"Type: {insp['inspection_type']}",
                f"Equipment: {insp.get('equipment_tag', 'N/A')}",
                f"Date: {insp.get('inspection_date', 'N/A')}",
                f"Inspector: {insp.get('inspector', 'N/A')}",
                f"Findings: {insp.get('findings', '')}",
                f"Severity: {insp.get('severity', 'none')}",
                f"Regulatory Reference: {insp.get('regulatory_ref', 'N/A')}",
                f"Corrective Actions: {insp.get('corrective_actions', 'N/A')}",
            ]
            text = "\n".join(text_parts)
            n = self.add_document(
                insp["inspection_id"], text,
                {"title": insp["inspection_id"], "doc_type": "inspection",
                 "equipment_tag": insp.get("equipment_tag", "")}
            )
            total_chunks += n
        
        # Index incidents
        for inc in seed_data.get("incidents", []):
            text_parts = [
                f"Incident Report: {inc['incident_id']}",
                f"Type: {inc['incident_type']} | Severity: {inc.get('severity', 'low')}",
                f"Date: {inc.get('date_occurred', 'N/A')}",
                f"Area: {inc.get('area', 'N/A')}",
                f"Equipment: {inc.get('equipment_tag', 'N/A')}",
                f"Description: {inc.get('description', '')}",
                f"Root Cause: {inc.get('root_cause', '')}",
                f"Corrective Actions: {inc.get('corrective_actions', '')}",
                f"Lessons Learned: {inc.get('lessons_learned', '')}",
            ]
            text = "\n".join(text_parts)
            n = self.add_document(
                inc["incident_id"], text,
                {"title": inc["incident_id"], "doc_type": "incident",
                 "equipment_tag": inc.get("equipment_tag", "")}
            )
            total_chunks += n
        
        # Index compliance requirements
        for req in seed_data.get("compliance_requirements", []):
            text_parts = [
                f"Compliance Requirement: {req['req_id']}",
                f"Regulation: {req['regulation']}",
                f"Clause: {req.get('clause', 'N/A')}",
                f"Requirement: {req['requirement_text']}",
                f"Category: {req.get('category', 'N/A')}",
                f"Status: {req.get('current_status', 'unknown')}",
                f"Gap: {req.get('gap_description', 'None')}",
            ]
            text = "\n".join(text_parts)
            n = self.add_document(
                req["req_id"], text,
                {"title": f"{req['regulation']} {req.get('clause', '')}", "doc_type": "compliance"}
            )
            total_chunks += n
        
        # Index equipment specs
        for eq in seed_data.get("equipment", []):
            text_parts = [
                f"Equipment: {eq['tag']} — {eq['name']}",
                f"Type: {eq['equipment_type']}",
                f"Area: {eq.get('area', 'N/A')}",
                f"Manufacturer: {eq.get('manufacturer', 'N/A')}",
                f"Model: {eq.get('model', 'N/A')}",
                f"Install Date: {eq.get('install_date', 'N/A')}",
                f"Criticality: {eq.get('criticality', 'medium')}",
                f"Status: {eq.get('status', 'operational')}",
                f"Specifications: {json.dumps(eq.get('specifications', {}), indent=2)}",
            ]
            text = "\n".join(text_parts)
            n = self.add_document(
                eq["tag"], text,
                {"title": f"{eq['tag']} — {eq['name']}", "doc_type": "equipment",
                 "equipment_tag": eq["tag"]}
            )
            total_chunks += n
        
        print(f"[VectorStore] Seeded {total_chunks} chunks from seed data")
        return total_chunks


# Need json import for equipment specs
import json

# Singleton instance
vector_store = VectorStore()
