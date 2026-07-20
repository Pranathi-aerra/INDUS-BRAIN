"""
Nazar — Phase 7: Backend API Test Suite
Tests all endpoints for correctness.
"""
import httpx
import json
import sys

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")

def run_tests():
    global PASS, FAIL
    client = httpx.Client(timeout=60)

    # ============================================
    print("\n🔹 1. ROOT & HEALTH")
    # ============================================
    r = client.get(f"{BASE}/")
    test("Root returns 200", r.status_code == 200)
    data = r.json()
    test("Project name is Nazar", data.get("name") == "Nazar")
    test("Status is running", data.get("status") == "running")

    r = client.get(f"{BASE}/api/health")
    test("Health returns 200", r.status_code == 200)
    data = r.json()
    test("Health status healthy", data.get("status") == "healthy")
    kg = data.get("knowledge_graph", {})
    test(f"KG has nodes ({kg.get('total_nodes', 0)})", kg.get("total_nodes", 0) > 100)
    test(f"KG has edges ({kg.get('total_edges', 0)})", kg.get("total_edges", 0) > 100)
    vs = data.get("vector_store", {})
    test(f"Vector store has chunks ({vs.get('total_chunks', 0)})", vs.get("total_chunks", 0) > 100)

    # ============================================
    print("\n🔹 2. DASHBOARD STATS")
    # ============================================
    r = client.get(f"{BASE}/api/dashboard/stats")
    test("Dashboard returns 200", r.status_code == 200)
    data = r.json()
    test(f"Total documents: {data.get('total_documents', 0)}", data.get("total_documents", 0) >= 3)
    test(f"Total equipment: {data.get('total_equipment', 0)}", data.get("total_equipment", 0) >= 20)
    test(f"Compliance score: {data.get('compliance_score', 0)}%", data.get("compliance_score", 0) > 0)
    test("Has work order stats", len(data.get("work_orders_by_status", {})) > 0)
    test(f"Overdue inspections: {data.get('overdue_inspections', 0)}", data.get("overdue_inspections") is not None)

    # ============================================
    print("\n🔹 3. EQUIPMENT API")
    # ============================================
    r = client.get(f"{BASE}/api/equipment/list")
    test("Equipment list returns 200", r.status_code == 200)
    data = r.json()
    test(f"Has {data.get('total', 0)} equipment", data.get("total", 0) >= 20)

    # Test specific equipment
    r = client.get(f"{BASE}/api/equipment/P-201-A")
    test("Equipment P-201-A returns 200", r.status_code == 200)
    data = r.json()
    eq = data.get("equipment", {})
    test("P-201-A name correct", "Naphtha" in eq.get("name", ""))
    test(f"P-201-A has {len(data.get('work_orders', []))} work orders", len(data.get("work_orders", [])) >= 0)
    test(f"P-201-A has graph connections", len(data.get("graph_connections", [])) > 0)

    # Test 404
    r = client.get(f"{BASE}/api/equipment/NONEXIST")
    test("Unknown equipment returns 404", r.status_code == 404)

    # ============================================
    print("\n🔹 4. KNOWLEDGE GRAPH API")
    # ============================================
    r = client.get(f"{BASE}/api/knowledge/graph?max_nodes=50")
    test("Graph returns 200", r.status_code == 200)
    data = r.json()
    test(f"Graph has {len(data.get('nodes', []))} nodes", len(data.get("nodes", [])) > 0)
    test(f"Graph has {len(data.get('edges', []))} edges", len(data.get("edges", [])) > 0)
    test("Graph has stats", data.get("stats", {}).get("total_nodes", 0) > 0)

    # Node detail
    r = client.get(f"{BASE}/api/knowledge/node/V-102")
    test("Node V-102 returns 200", r.status_code == 200)
    data = r.json()
    test("V-102 has node data", data.get("node") is not None)
    test(f"V-102 has {len(data.get('neighbors', []))} neighbors", len(data.get("neighbors", [])) > 0)

    # Subgraph
    r = client.get(f"{BASE}/api/knowledge/subgraph/P-101-A?depth=1")
    test("Subgraph returns 200", r.status_code == 200)
    data = r.json()
    test(f"Subgraph has {len(data.get('nodes', []))} nodes", len(data.get("nodes", [])) > 1)

    # Search
    r = client.get(f"{BASE}/api/knowledge/search?q=pump")
    test("KG search returns 200", r.status_code == 200)
    data = r.json()
    test(f"KG search found {len(data.get('results', []))} results for 'pump'", len(data.get("results", [])) > 0)

    # ============================================
    print("\n🔹 5. COMPLIANCE API")
    # ============================================
    r = client.get(f"{BASE}/api/compliance/dashboard")
    test("Compliance dashboard returns 200", r.status_code == 200)
    data = r.json()
    test(f"Overall score: {data.get('overall_score', 0)}%", data.get("overall_score", 0) > 0)
    test(f"Total requirements: {data.get('total_requirements', 0)}", data.get("total_requirements", 0) >= 10)
    test(f"Gaps found: {len(data.get('gaps', []))}", len(data.get("gaps", [])) > 0)
    test("Has regulation breakdown", len(data.get("by_regulation", {})) > 0)
    test(f"Upcoming audits: {len(data.get('upcoming_audits', []))}", len(data.get("upcoming_audits", [])) > 0)

    r = client.get(f"{BASE}/api/compliance/requirements?status=non_compliant")
    test("Non-compliant filter returns 200", r.status_code == 200)
    data = r.json()
    test(f"Found {data.get('total', 0)} non-compliant items", data.get("total", 0) >= 1)

    # ============================================
    print("\n🔹 6. MAINTENANCE API")
    # ============================================
    r = client.get(f"{BASE}/api/maintenance/dashboard")
    test("Maintenance dashboard returns 200", r.status_code == 200)
    data = r.json()
    test(f"Total work orders: {data.get('total_work_orders', 0)}", data.get("total_work_orders", 0) >= 50)
    test(f"Open work orders: {data.get('open_work_orders', 0)}", data.get("open_work_orders") is not None)
    test(f"Avg downtime: {data.get('avg_downtime_hours', 0)} hrs", data.get("avg_downtime_hours", 0) > 0)
    test(f"Equipment health items: {len(data.get('equipment_health', []))}", len(data.get("equipment_health", [])) > 0)
    test(f"Top failing: {len(data.get('top_failing_equipment', []))}", len(data.get("top_failing_equipment", [])) > 0)
    test(f"Failure trends: {len(data.get('failure_trends', []))}", len(data.get("failure_trends", [])) > 0)

    r = client.get(f"{BASE}/api/maintenance/work-orders?equipment_tag=P-101-A")
    test("Work orders for P-101-A returns 200", r.status_code == 200)

    r = client.get(f"{BASE}/api/maintenance/inspections")
    test("Inspections returns 200", r.status_code == 200)
    data = r.json()
    test(f"Total inspections: {data.get('total', 0)}", data.get("total", 0) >= 10)

    r = client.get(f"{BASE}/api/maintenance/incidents")
    test("Incidents returns 200", r.status_code == 200)
    data = r.json()
    test(f"Total incidents: {data.get('total', 0)}", data.get("total", 0) >= 5)

    # ============================================
    print("\n🔹 7. DOCUMENTS API")
    # ============================================
    r = client.get(f"{BASE}/api/documents/list")
    test("Documents list returns 200", r.status_code == 200)
    data = r.json()
    test(f"Total documents: {len(data.get('documents', []))}", len(data.get("documents", [])) >= 3)

    # ============================================
    print("\n🔹 8. CHAT / QUERY API (Gemini RAG)")
    # ============================================
    r = client.post(f"{BASE}/api/query/chat", json={
        "query": "What is the maintenance history of pump P-201-A?",
        "mode": "copilot"
    })
    test("Chat returns 200", r.status_code == 200)
    data = r.json()
    has_answer = len(data.get("answer", "")) > 50
    test(f"Answer length: {len(data.get('answer', ''))} chars", has_answer, "Answer too short or empty")
    test(f"Sources: {len(data.get('sources', []))}", len(data.get("sources", [])) > 0)
    test(f"Confidence: {data.get('confidence', 0)}", data.get("confidence", 0) > 0)
    test("Has follow-up questions", len(data.get("follow_up_questions", [])) > 0)
    test("Mode is copilot", data.get("mode") == "copilot")

    # Test compliance mode
    r = client.post(f"{BASE}/api/query/chat", json={
        "query": "What are the OISD-118 compliance gaps?",
        "mode": "compliance"
    })
    test("Compliance chat returns 200", r.status_code == 200)
    cdata = r.json()
    test(f"Compliance answer length: {len(cdata.get('answer', ''))}", len(cdata.get("answer", "")) > 50)

    # ============================================
    print("\n" + "=" * 50)
    print(f"  RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
    print("=" * 50)
    
    if FAIL > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
