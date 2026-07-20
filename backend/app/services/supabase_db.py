"""
Nazar — Supabase Integration
Cloud database layer that syncs local SQLite data to Supabase.
Provides read/write operations for cloud persistence.
"""
import logging
from app.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Lazy-loaded Supabase client
_client = None


def get_client():
    """Get or create the Supabase client (lazy initialization)."""
    global _client
    if _client is not None:
        return _client

    if not SUPABASE_URL or not SUPABASE_KEY or "placeholder" in SUPABASE_KEY:
        logger.warning("[Supabase] No valid credentials found — running in local-only mode.")
        return None

    try:
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"[Supabase] Connected to {SUPABASE_URL}")
        return _client
    except ImportError:
        logger.warning("[Supabase] supabase-py not installed. Run: pip install supabase")
        return None
    except Exception as e:
        logger.error(f"[Supabase] Connection failed: {e}")
        return None


def is_connected() -> bool:
    """Check if Supabase is available."""
    return get_client() is not None


# ---- Equipment ----
def sync_equipment(equipment_list: list[dict]) -> int:
    """Upsert equipment records to Supabase."""
    client = get_client()
    if not client:
        return 0
    try:
        result = client.table("equipment").upsert(
            equipment_list, on_conflict="tag"
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"[Supabase] Equipment sync failed: {e}")
        return 0


def get_equipment_cloud(tag: str = None) -> list[dict]:
    """Fetch equipment from Supabase."""
    client = get_client()
    if not client:
        return []
    try:
        query = client.table("equipment").select("*")
        if tag:
            query = query.eq("tag", tag)
        result = query.execute()
        return result.data or []
    except Exception as e:
        logger.error(f"[Supabase] Equipment fetch failed: {e}")
        return []


# ---- Work Orders ----
def sync_work_orders(wo_list: list[dict]) -> int:
    """Upsert work orders to Supabase."""
    client = get_client()
    if not client:
        return 0
    try:
        result = client.table("work_orders").upsert(
            wo_list, on_conflict="wo_number"
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"[Supabase] Work orders sync failed: {e}")
        return 0


# ---- Inspections ----
def sync_inspections(insp_list: list[dict]) -> int:
    """Upsert inspections to Supabase."""
    client = get_client()
    if not client:
        return 0
    try:
        result = client.table("inspections").upsert(
            insp_list, on_conflict="inspection_id"
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"[Supabase] Inspections sync failed: {e}")
        return 0


# ---- Incidents ----
def sync_incidents(inc_list: list[dict]) -> int:
    """Upsert incidents to Supabase."""
    client = get_client()
    if not client:
        return 0
    try:
        result = client.table("incidents").upsert(
            inc_list, on_conflict="incident_id"
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"[Supabase] Incidents sync failed: {e}")
        return 0


# ---- Compliance ----
def sync_compliance(req_list: list[dict]) -> int:
    """Upsert compliance requirements to Supabase."""
    client = get_client()
    if not client:
        return 0
    try:
        result = client.table("compliance_requirements").upsert(
            req_list, on_conflict="req_id"
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"[Supabase] Compliance sync failed: {e}")
        return 0


# ---- Documents ----
def sync_documents(doc_list: list[dict]) -> int:
    """Upsert documents to Supabase."""
    client = get_client()
    if not client:
        return 0
    try:
        result = client.table("documents").upsert(
            doc_list, on_conflict="doc_id"
        ).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        logger.error(f"[Supabase] Documents sync failed: {e}")
        return 0


# ---- Full Sync ----
def sync_all_to_cloud(db_data: dict) -> dict:
    """
    Sync all local data to Supabase cloud.
    db_data should contain keys: equipment, work_orders, inspections, incidents, compliance
    """
    if not is_connected():
        return {"status": "skipped", "reason": "Supabase not configured"}

    results = {}
    if "equipment" in db_data:
        results["equipment"] = sync_equipment(db_data["equipment"])
    if "work_orders" in db_data:
        results["work_orders"] = sync_work_orders(db_data["work_orders"])
    if "inspections" in db_data:
        results["inspections"] = sync_inspections(db_data["inspections"])
    if "incidents" in db_data:
        results["incidents"] = sync_incidents(db_data["incidents"])
    if "compliance" in db_data:
        results["compliance"] = sync_compliance(db_data["compliance"])
    if "documents" in db_data:
        results["documents"] = sync_documents(db_data["documents"])

    logger.info(f"[Supabase] Cloud sync complete: {results}")
    return {"status": "synced", "counts": results}
