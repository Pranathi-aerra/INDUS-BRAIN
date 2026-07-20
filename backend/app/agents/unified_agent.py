"""
Nazar — Unified Agent Controller
Single Gemini-powered RAG pipeline that handles all agent modes:
  - copilot: General Q&A over the full document corpus
  - maintenance: RCA and maintenance intelligence
  - compliance: Regulatory gap analysis
  - failure: Incident pattern analysis
"""
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional
import json
import traceback

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.vector_store import vector_store
from app.services.knowledge_graph import knowledge_graph


# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# SYSTEM PROMPTS PER MODE
# ============================================================

SYSTEM_PROMPTS = {
    "copilot": """You are Nazar Copilot — an expert AI assistant for industrial plant operations at Bharat Petrochemicals Ltd, Jamnagar Unit-3 (a petrochemical refinery).

You answer questions about equipment, maintenance, procedures, safety, inspections, and operations using the provided context from plant documents.

RULES:
1. ALWAYS base your answers on the provided context documents. Never make up information.
2. Cite specific document IDs, equipment tags, and dates when available.
3. If the context doesn't contain enough information, say so clearly.
4. Use technical but accessible language suitable for plant engineers and technicians.
5. When referencing equipment, always include the tag (e.g., P-201-A) and name.
6. Provide actionable, specific answers — not vague generalities.
7. At the end, suggest 2-3 follow-up questions the user might want to ask.

FORMAT your response as:
- Clear, structured answer with bullet points or numbered steps where appropriate
- Source citations in [brackets] like [WO-1005] or [SOP-CDU-001]
- A confidence assessment: High (>80%), Medium (50-80%), Low (<50%)
- Follow-up suggestions""",

    "maintenance": """You are Nazar Maintenance Intelligence Agent — specializing in maintenance analysis, Root Cause Analysis (RCA), and predictive maintenance for Bharat Petrochemicals Ltd.

You analyze work orders, failure patterns, equipment history, and inspection records to provide maintenance intelligence.

CAPABILITIES:
1. ROOT CAUSE ANALYSIS: Given a failure event, identify root causes by analyzing historical patterns
2. FAILURE PATTERNS: Identify recurring failure modes and their frequencies
3. MTBF/MTTR: Calculate Mean Time Between Failures and Mean Time To Repair
4. RECOMMENDATIONS: Suggest maintenance schedule optimizations
5. PREDICTIVE: Flag equipment at risk based on historical failure patterns

RULES:
1. Base analysis on provided work order history, inspection records, and incident data
2. Always reference specific work order numbers and dates
3. Calculate quantitative metrics where possible (MTBF, MTTR, failure frequency)
4. Recommend specific, actionable maintenance improvements
5. Prioritize recommendations by impact and urgency""",

    "compliance": """You are Nazar Compliance Intelligence Agent — specializing in Indian industrial regulatory compliance for Bharat Petrochemicals Ltd.

You analyze compliance status against key Indian regulations:
- Factories Act, 1948
- OISD-118 (Fire Protection for Refineries)
- OISD-144 (Petroleum Storage Safety)
- OISD-150 (LPG Plant Safety)
- PESO (Petroleum & Explosives Safety Organisation)
- Environment Protection Act

CAPABILITIES:
1. GAP ANALYSIS: Identify non-compliant or partially compliant requirements
2. RISK ASSESSMENT: Prioritize compliance gaps by severity and regulatory consequence
3. EVIDENCE MAPPING: Identify which documents provide evidence for compliance
4. AUDIT PREPARATION: Generate compliance status summaries for auditors
5. DEADLINE TRACKING: Flag upcoming audit dates and license renewals

RULES:
1. Always cite specific regulation names, clause numbers, and requirement text
2. Clearly distinguish between compliant, non-compliant, and partially compliant status
3. Recommend specific corrective actions for each gap
4. Prioritize by regulatory risk (PESO/Factory Act violations carry legal consequences)""",

    "failure": """You are Nazar Failure Intelligence Agent — specializing in incident analysis, pattern recognition, and lessons learned for Bharat Petrochemicals Ltd.

You analyze incident reports, near-miss records, and failure data to identify systemic patterns and proactively warn about recurring risks.

CAPABILITIES:
1. PATTERN ANALYSIS: Identify common themes across incidents (equipment type, failure mode, area)
2. TREND DETECTION: Identify increasing/decreasing incident trends
3. LESSONS LEARNED: Extract and synthesize key learnings from historical incidents
4. PROACTIVE WARNINGS: Based on patterns, flag conditions that could lead to similar incidents
5. CROSS-REFERENCE: Connect incidents to related work orders and inspections

RULES:
1. Reference specific incident IDs, dates, and equipment tags
2. Identify systemic root causes, not just individual event causes
3. Recommend organizational improvements, not just technical fixes
4. Quantify patterns where possible (frequency, severity distribution)""",
}


async def query_agent(
    query: str,
    mode: str = "copilot",
    equipment_tag: str = None,
) -> Dict[str, Any]:
    """
    Unified agent query handler.
    1. Retrieves relevant context from vector store + knowledge graph
    2. Constructs a prompt with context
    3. Calls Gemini for generation
    4. Returns structured response with sources
    """
    try:
        # Step 1: Retrieve context from vector store
        search_filter = None
        if equipment_tag:
            search_filter = {"equipment_tag": equipment_tag}
        
        vector_results = vector_store.search(query, n_results=8, filter_metadata=search_filter)
        
        # Step 2: Retrieve context from knowledge graph
        kg_context = ""
        if knowledge_graph.is_initialized():
            # Search KG for relevant nodes
            kg_nodes = knowledge_graph.search_nodes(query)[:10]
            if equipment_tag:
                eq_nodes = knowledge_graph.search_nodes(equipment_tag)
                kg_nodes = eq_nodes + kg_nodes
            
            if kg_nodes:
                kg_parts = ["KNOWLEDGE GRAPH CONTEXT:"]
                for node in kg_nodes[:8]:
                    node_copy = {k: v for k, v in node.items() if k != "id"}
                    kg_parts.append(f"- [{node.get('node_type', 'entity')}] {node.get('id')}: {json.dumps(node_copy, default=str)[:300]}")
                    
                    # Get connected nodes
                    neighbors = knowledge_graph.get_neighbors(node["id"])[:5]
                    for nb in neighbors:
                        rel = nb.get("relationship", {})
                        rel_type = rel.get("relationship", "related_to") if isinstance(rel, dict) else "related_to"
                        kg_parts.append(f"  → {rel_type} → {nb.get('id', 'unknown')}")
                
                kg_context = "\n".join(kg_parts)
        
        # Step 3: Build context string from vector results
        doc_context_parts = ["DOCUMENT CONTEXT (Retrieved from plant knowledge base):"]
        sources = []
        seen_docs = set()
        
        for i, result in enumerate(vector_results):
            doc_id = result.get("doc_id", f"doc-{i}")
            if doc_id in seen_docs:
                continue
            seen_docs.add(doc_id)
            
            doc_context_parts.append(f"\n--- Source [{doc_id}] (Relevance: {result.get('relevance_score', 0):.0%}) ---")
            doc_context_parts.append(result["text"])
            
            sources.append({
                "doc_id": doc_id,
                "title": result.get("metadata", {}).get("title", doc_id),
                "doc_type": result.get("metadata", {}).get("doc_type", "general"),
                "relevance_score": result.get("relevance_score", 0),
                "excerpt": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
            })
        
        doc_context = "\n".join(doc_context_parts)
        
        # Step 4: Construct the full prompt
        system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["copilot"])
        
        full_context = doc_context
        if kg_context:
            full_context = kg_context + "\n\n" + doc_context
        
        user_message = f"""Based on the following context from our plant knowledge base, please answer this question:

{full_context}

USER QUESTION: {query}"""
        
        # Step 5: Call Gemini (with fallback if API key is invalid)
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[user_message],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    max_output_tokens=2048,
                ),
            )
            answer = response.text if response.text else "I couldn't generate a response. Please try rephrasing your question."
        except Exception as llm_err:
            # Fallback: return raw context as the answer
            print(f"[Agent] Gemini API error: {llm_err}")
            context_summary = "\n".join(
                f"- [{s['doc_id']}] ({s['doc_type']}): {s['excerpt'][:150]}"
                for s in sources[:5]
            )
            answer = (
                f"**Note:** AI summarization is temporarily unavailable (API key issue). "
                f"Here are the most relevant documents found for your query:\n\n{context_summary}\n\n"
                f"*Please update your Gemini API key in backend/app/config.py to enable AI-powered answers.*"
            )
        
        # Step 6: Estimate confidence based on retrieval quality
        avg_relevance = sum(s["relevance_score"] for s in sources) / len(sources) if sources else 0
        confidence = min(95, max(15, avg_relevance * 100))
        
        # Step 7: Generate follow-up questions
        follow_ups = _generate_follow_ups(query, mode, sources)
        
        return {
            "answer": answer,
            "confidence": round(confidence, 1),
            "sources": sources,
            "follow_up_questions": follow_ups,
            "mode": mode,
        }
    
    except Exception as e:
        traceback.print_exc()
        return {
            "answer": f"An error occurred while processing your query: {str(e)}",
            "confidence": 0,
            "sources": [],
            "follow_up_questions": [],
            "mode": mode,
        }


def _generate_follow_ups(query: str, mode: str, sources: List[Dict]) -> List[str]:
    """Generate contextual follow-up question suggestions."""
    follow_ups = {
        "copilot": [
            "What are the recent maintenance activities on this equipment?",
            "Show me the related inspection findings",
            "What safety procedures apply to this operation?",
        ],
        "maintenance": [
            "What is the failure trend for this equipment type?",
            "Show me similar failures across other equipment",
            "What spare parts are most frequently needed?",
        ],
        "compliance": [
            "What are the critical compliance gaps requiring immediate attention?",
            "When are the next regulatory audit deadlines?",
            "Show me the evidence documents for this requirement",
        ],
        "failure": [
            "Are there patterns in failures across different plant areas?",
            "What lessons learned apply to current operations?",
            "Show me the timeline of incidents for this equipment",
        ],
    }
    
    # Extract equipment tags from sources for personalized follow-ups
    eq_tags = set()
    for s in sources:
        meta = s.get("metadata", {}) if isinstance(s, dict) else {}
        tag = s.get("doc_id", "") if s.get("doc_id", "").startswith(("P-", "V-", "HX-", "C-", "H-")) else ""
        if tag:
            eq_tags.add(tag)
    
    base_follow_ups = follow_ups.get(mode, follow_ups["copilot"])
    
    if eq_tags:
        tag = list(eq_tags)[0]
        base_follow_ups = [
            f"What is the complete maintenance history of {tag}?",
            f"Are there any compliance issues related to {tag}?",
            f"What incidents have occurred involving {tag}?",
        ]
    
    return base_follow_ups[:3]
