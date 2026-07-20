"""
Nazar — Synthetic Data Generator
Creates realistic industrial plant data for demonstration.
Based on a fictional petrochemical refinery: "Bharat Petrochemicals Ltd, Jamnagar Unit-3"
"""
import json
import random
from datetime import datetime, timedelta


# ============================================================
# EQUIPMENT REGISTRY — 30+ assets across a petrochemical unit
# ============================================================
EQUIPMENT = [
    # Vessels
    {"tag": "V-101", "name": "Crude Oil Feed Drum", "equipment_type": "vessel", "area": "CDU-1",
     "manufacturer": "Larsen & Toubro", "model": "LT-PV-500", "install_date": "2015-03-15",
     "criticality": "critical", "status": "operational",
     "specifications": {"capacity_m3": 50, "design_pressure_bar": 12, "material": "SA-516 Gr.70"}},
    {"tag": "V-102", "name": "Atmospheric Distillation Column", "equipment_type": "vessel", "area": "CDU-1",
     "manufacturer": "Godrej Process Equipment", "model": "GPE-DC-1200", "install_date": "2015-03-15",
     "criticality": "critical", "status": "operational",
     "specifications": {"height_m": 45, "diameter_m": 4.5, "trays": 42, "material": "SS-316L"}},
    {"tag": "V-103", "name": "Vacuum Distillation Column", "equipment_type": "vessel", "area": "VDU-1",
     "manufacturer": "Godrej Process Equipment", "model": "GPE-VDC-800", "install_date": "2015-06-20",
     "criticality": "critical", "status": "operational",
     "specifications": {"height_m": 35, "diameter_m": 6, "packing_type": "structured", "material": "SS-304"}},
    {"tag": "V-201", "name": "Naphtha Splitter Column", "equipment_type": "vessel", "area": "NHT-1",
     "manufacturer": "BHEL", "model": "BHEL-NS-600", "install_date": "2016-01-10",
     "criticality": "high", "status": "operational",
     "specifications": {"height_m": 30, "diameter_m": 3, "trays": 35}},
    {"tag": "V-301", "name": "LPG Storage Sphere", "equipment_type": "vessel", "area": "STORAGE",
     "manufacturer": "Larsen & Toubro", "model": "LT-SPH-1000", "install_date": "2014-11-01",
     "criticality": "critical", "status": "operational",
     "specifications": {"capacity_m3": 1000, "design_pressure_bar": 17, "product": "LPG"}},
    
    # Pumps
    {"tag": "P-101-A", "name": "Crude Oil Charge Pump A", "equipment_type": "pump", "area": "CDU-1",
     "manufacturer": "Kirloskar Brothers", "model": "KBL-HPC-350", "install_date": "2015-03-15",
     "criticality": "critical", "status": "operational",
     "specifications": {"flow_m3h": 350, "head_m": 120, "power_kw": 250, "type": "centrifugal"}},
    {"tag": "P-101-B", "name": "Crude Oil Charge Pump B (Standby)", "equipment_type": "pump", "area": "CDU-1",
     "manufacturer": "Kirloskar Brothers", "model": "KBL-HPC-350", "install_date": "2015-03-15",
     "criticality": "critical", "status": "standby",
     "specifications": {"flow_m3h": 350, "head_m": 120, "power_kw": 250, "type": "centrifugal"}},
    {"tag": "P-201-A", "name": "Naphtha Transfer Pump", "equipment_type": "pump", "area": "NHT-1",
     "manufacturer": "Sulzer", "model": "SLZ-CPT-200", "install_date": "2016-01-10",
     "criticality": "high", "status": "operational",
     "specifications": {"flow_m3h": 200, "head_m": 80, "power_kw": 150, "type": "centrifugal"}},
    {"tag": "P-301-A", "name": "Cooling Water Pump", "equipment_type": "pump", "area": "UTILITY",
     "manufacturer": "KSB", "model": "KSB-CW-500", "install_date": "2015-01-20",
     "criticality": "high", "status": "operational",
     "specifications": {"flow_m3h": 500, "head_m": 40, "power_kw": 110}},
    {"tag": "P-401-A", "name": "Boiler Feed Water Pump", "equipment_type": "pump", "area": "UTILITY",
     "manufacturer": "Grundfos", "model": "GF-BFW-300", "install_date": "2015-01-20",
     "criticality": "high", "status": "degraded",
     "specifications": {"flow_m3h": 300, "head_m": 180, "power_kw": 350}},
    
    # Heat Exchangers
    {"tag": "HX-101", "name": "Crude Preheat Exchanger 1", "equipment_type": "heat_exchanger", "area": "CDU-1",
     "manufacturer": "Alfa Laval", "model": "AL-PHE-500", "install_date": "2015-03-15",
     "criticality": "high", "status": "operational",
     "specifications": {"type": "shell_and_tube", "duty_mw": 15, "area_m2": 500}},
    {"tag": "HX-102", "name": "Crude Preheat Exchanger 2", "equipment_type": "heat_exchanger", "area": "CDU-1",
     "manufacturer": "Alfa Laval", "model": "AL-PHE-600", "install_date": "2015-03-15",
     "criticality": "high", "status": "operational",
     "specifications": {"type": "shell_and_tube", "duty_mw": 18, "area_m2": 600}},
    {"tag": "HX-201", "name": "Naphtha Cooler", "equipment_type": "heat_exchanger", "area": "NHT-1",
     "manufacturer": "Thermax", "model": "TH-AC-300", "install_date": "2016-01-10",
     "criticality": "medium", "status": "operational",
     "specifications": {"type": "air_cooled", "duty_mw": 8}},
    {"tag": "HX-301", "name": "Overhead Condenser", "equipment_type": "heat_exchanger", "area": "CDU-1",
     "manufacturer": "Thermax", "model": "TH-OHC-800", "install_date": "2015-03-15",
     "criticality": "critical", "status": "operational",
     "specifications": {"type": "shell_and_tube", "duty_mw": 25, "area_m2": 800}},
    
    # Compressors
    {"tag": "C-101", "name": "Gas Compressor", "equipment_type": "compressor", "area": "GAS-PLANT",
     "manufacturer": "Atlas Copco", "model": "AC-GC-2000", "install_date": "2015-06-20",
     "criticality": "critical", "status": "operational",
     "specifications": {"type": "reciprocating", "power_kw": 2000, "suction_pressure_bar": 2, "discharge_pressure_bar": 12}},
    
    # Fired Heaters
    {"tag": "H-101", "name": "Crude Heater / Furnace", "equipment_type": "furnace", "area": "CDU-1",
     "manufacturer": "Thermax", "model": "TH-FH-50MW", "install_date": "2015-03-15",
     "criticality": "critical", "status": "operational",
     "specifications": {"duty_mw": 50, "fuel": "refinery_fuel_gas", "tube_material": "9Cr-1Mo"}},
    
    # Instruments
    {"tag": "TI-1001", "name": "CDU Column Top Temperature", "equipment_type": "instrument", "area": "CDU-1",
     "manufacturer": "Emerson", "model": "Rosemount 3144P", "install_date": "2015-03-15",
     "criticality": "high", "status": "operational",
     "specifications": {"type": "thermocouple", "range": "0-500°C", "output": "4-20mA"}},
    {"tag": "PI-1002", "name": "CDU Column Pressure", "equipment_type": "instrument", "area": "CDU-1",
     "manufacturer": "Yokogawa", "model": "EJA530E", "install_date": "2015-03-15",
     "criticality": "high", "status": "operational",
     "specifications": {"type": "pressure_transmitter", "range": "0-20 bar", "output": "4-20mA"}},
    {"tag": "FI-2001", "name": "Naphtha Flow Meter", "equipment_type": "instrument", "area": "NHT-1",
     "manufacturer": "Endress+Hauser", "model": "Promass 80F", "install_date": "2016-01-10",
     "criticality": "medium", "status": "operational",
     "specifications": {"type": "coriolis", "range": "0-500 m3/h"}},
    {"tag": "LI-3001", "name": "LPG Sphere Level", "equipment_type": "instrument", "area": "STORAGE",
     "manufacturer": "Emerson", "model": "Rosemount 5300", "install_date": "2014-11-01",
     "criticality": "critical", "status": "operational",
     "specifications": {"type": "radar_level", "range": "0-15m"}},
    
    # Safety Valves
    {"tag": "PSV-101", "name": "CDU Column Relief Valve", "equipment_type": "safety_valve", "area": "CDU-1",
     "manufacturer": "Emerson", "model": "Crosby J-Series", "install_date": "2015-03-15",
     "criticality": "critical", "status": "operational",
     "specifications": {"set_pressure_bar": 14, "type": "spring_loaded"}},
    {"tag": "PSV-301", "name": "LPG Sphere Relief Valve", "equipment_type": "safety_valve", "area": "STORAGE",
     "manufacturer": "Emerson", "model": "Crosby J-Series", "install_date": "2014-11-01",
     "criticality": "critical", "status": "operational",
     "specifications": {"set_pressure_bar": 18, "type": "spring_loaded"}},
    
    # Valves
    {"tag": "XV-101", "name": "Crude Feed Isolation Valve", "equipment_type": "valve", "area": "CDU-1",
     "manufacturer": "L&T Valves", "model": "LT-GV-300", "install_date": "2015-03-15",
     "criticality": "high", "status": "operational",
     "specifications": {"type": "gate_valve", "size_inch": 12, "rating": "ANSI 300"}},
    {"tag": "CV-201", "name": "Naphtha Flow Control Valve", "equipment_type": "valve", "area": "NHT-1",
     "manufacturer": "Fisher", "model": "DVC6200", "install_date": "2016-01-10",
     "criticality": "high", "status": "operational",
     "specifications": {"type": "control_valve", "size_inch": 8, "actuator": "pneumatic"}},
]


# ============================================================
# WORK ORDERS — 50+ maintenance records with realistic patterns
# ============================================================
TECHNICIANS = ["Rajesh Kumar", "Suresh Patel", "Amit Singh", "Priya Sharma", "Vikram Joshi",
               "Mohammed Ali", "Deepak Verma", "Anita Reddy", "Sunil Yadav", "Meera Nair"]

FAILURE_MODES = {
    "pump": ["seal_leak", "bearing_failure", "impeller_erosion", "cavitation", "motor_overload", "vibration_high"],
    "vessel": ["corrosion", "tray_damage", "nozzle_leak", "insulation_damage", "internal_fouling"],
    "heat_exchanger": ["tube_leak", "fouling", "gasket_failure", "baffle_damage", "corrosion"],
    "compressor": ["valve_failure", "bearing_failure", "piston_ring_wear", "vibration_high", "seal_leak"],
    "furnace": ["tube_failure", "refractory_damage", "burner_malfunction", "coking", "flame_instability"],
    "instrument": ["calibration_drift", "sensor_failure", "signal_loss", "corrosion", "wiring_fault"],
    "safety_valve": ["seat_leakage", "set_pressure_drift", "spring_fatigue", "corrosion"],
    "valve": ["seat_leakage", "actuator_failure", "stem_packing_leak", "corrosion"],
}

def generate_work_orders():
    """Generate 60 realistic work orders spanning 3 years."""
    work_orders = []
    base_date = datetime(2023, 1, 1)
    wo_counter = 1000
    
    for i in range(60):
        eq = random.choice(EQUIPMENT)
        eq_type = eq["equipment_type"]
        failure_modes = FAILURE_MODES.get(eq_type, ["general_maintenance"])
        failure = random.choice(failure_modes)
        
        reported = base_date + timedelta(days=random.randint(0, 900))
        is_completed = random.random() < 0.85
        completed = reported + timedelta(hours=random.randint(4, 120)) if is_completed else None
        downtime = random.uniform(2, 72) if is_completed else 0
        
        wo_type = random.choices(
            ["corrective", "preventive", "emergency", "inspection"],
            weights=[40, 35, 10, 15]
        )[0]
        
        priority = random.choices(
            ["low", "medium", "high", "critical"],
            weights=[10, 40, 35, 15]
        )[0]
        
        descriptions = {
            "seal_leak": f"Seal leakage observed on {eq['tag']} ({eq['name']}). Process fluid dripping from mechanical seal area. Immediate containment measures applied.",
            "bearing_failure": f"High vibration alarm triggered on {eq['tag']}. Bearing temperature elevated to 95°C (normal: 65°C). Equipment tripped on high vibration.",
            "impeller_erosion": f"Reduced discharge pressure observed on {eq['tag']}. Performance test indicates impeller wear. Capacity reduced by approximately 15%.",
            "cavitation": f"Cavitation noise detected on {eq['tag']}. NPSH analysis indicates insufficient suction head. Suction strainer partially blocked.",
            "tube_leak": f"Hydrocarbon traces detected in cooling water return from {eq['tag']}. Leak test confirms tube failure in pass 2.",
            "fouling": f"Heat transfer coefficient dropped below design value on {eq['tag']}. ΔT approach increased from 10°C to 25°C. Chemical cleaning required.",
            "corrosion": f"Wall thickness survey on {eq['tag']} revealed thinning below minimum required thickness at 2 o'clock position. Under-deposit corrosion suspected.",
            "calibration_drift": f"Calibration check on {eq['tag']} shows reading deviation of +2.5% from reference standard. Beyond acceptable tolerance of ±0.5%.",
            "refractory_damage": f"Hot spot detected on {eq['tag']} casing using IR thermography. Temperature reading 180°C at location Row-3, suggesting refractory failure.",
            "seat_leakage": f"Pop test on {eq['tag']} indicates seat leakage at 85% of set pressure. Requires lapping or replacement of seat/disc.",
        }
        
        root_causes = {
            "seal_leak": "Mechanical seal O-ring degradation due to chemical attack from H2S in process fluid",
            "bearing_failure": "Lubrication oil contamination with moisture. Oil analysis showed water content >500ppm",
            "impeller_erosion": "Erosive wear from catalyst fines carryover in feed stream",
            "cavitation": "Suction strainer blocked with debris from upstream vessel cleaning",
            "tube_leak": "Stress corrosion cracking (SCC) in 304SS tubes due to chloride ingress in cooling water",
            "fouling": "Crude oil fouling from asphaltene deposition during high-TAN crude processing",
            "corrosion": "Under-deposit corrosion from salt deposition. Desalter efficiency below 95%",
            "calibration_drift": "Sensor aging and ambient temperature effects",
            "refractory_damage": "Thermal shock during emergency shutdown. Rapid cooldown rate exceeded 50°C/hr limit",
            "seat_leakage": "Corrosion products from H2S service causing pitting on valve seat",
        }
        
        actions = {
            "seal_leak": "Replaced mechanical seal assembly with upgraded AESSEAL DWB-series. Flush plan changed from Plan 11 to Plan 53A.",
            "bearing_failure": "Replaced DE and NDE bearings (SKF 6316). Flushed lube oil system. Installed new oil mist lubrication system.",
            "tube_leak": "Plugged 4 leaking tubes. Hydrotested to 1.5x design pressure. Scheduled full re-tube during next turnaround.",
            "fouling": "Performed CIP chemical cleaning with 5% citric acid solution. Restored heat transfer coefficient to 90% of design.",
            "corrosion": "Applied weld overlay repair. Installed corrosion monitoring coupon. Increased inhibitor injection rate.",
            "calibration_drift": "Re-calibrated using certified reference standard. Applied 5-point calibration across full range.",
            "refractory_damage": "Removed damaged refractory section (2m²). Applied new castable refractory. Cured as per OEM procedure.",
        }
        
        wo = {
            "wo_number": f"WO-{wo_counter + i}",
            "equipment_tag": eq["tag"],
            "wo_type": wo_type,
            "priority": priority,
            "status": "completed" if is_completed else random.choice(["open", "in_progress"]),
            "description": descriptions.get(failure, f"Routine {wo_type} maintenance on {eq['tag']} ({eq['name']}). {failure.replace('_', ' ').title()} addressed."),
            "root_cause": root_causes.get(failure, f"{failure.replace('_', ' ').title()} — standard wear and tear") if is_completed else None,
            "action_taken": actions.get(failure, f"Performed {wo_type} maintenance. {failure.replace('_', ' ').title()} rectified. Equipment restored to service.") if is_completed else None,
            "technician": random.choice(TECHNICIANS),
            "reported_date": reported.strftime("%Y-%m-%d"),
            "completed_date": completed.strftime("%Y-%m-%d") if completed else None,
            "downtime_hours": round(downtime, 1),
            "parts_used": [],
        }
        work_orders.append(wo)
    
    return work_orders


# ============================================================
# INSPECTIONS — Safety & regulatory inspections
# ============================================================

def generate_inspections():
    """Generate 20 inspection records."""
    inspections = []
    inspectors = ["Dr. K. Raghavan (Factory Inspector)", "S. Mukherjee (OISD Auditor)", 
                  "R. Iyer (In-house Safety)", "V. Chauhan (Third-party NDT)", "M. Fernandes (QA Manager)"]
    
    insp_types = [
        ("safety", "OISD-118", "Fire protection system audit as per OISD-118 guidelines"),
        ("regulatory", "Factories Act Sec 36", "Annual statutory safety inspection under Factories Act"),
        ("regulatory", "PESO", "PESO license renewal inspection for LPG storage facilities"),
        ("routine", "Internal SOP", "Monthly safety round — Unit CDU-1"),
        ("special", "OISD-144", "Special inspection of petroleum storage tanks post-monsoon season"),
        ("safety", "OISD-150", "LPG handling and storage safety audit"),
        ("regulatory", "Environment Clearance", "Annual emission monitoring and environmental compliance check"),
        ("routine", "Internal SOP", "Quarterly instrument calibration verification"),
    ]
    
    for i in range(20):
        insp_type, reg_ref, base_finding = random.choice(insp_types)
        eq = random.choice(EQUIPMENT)
        insp_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 900))
        severity = random.choices(["none", "minor", "major", "critical"], weights=[30, 40, 25, 5])[0]
        
        findings_map = {
            "none": f"Inspection of {eq['tag']} ({eq['name']}) completed. All parameters within acceptable limits. No deviations noted.",
            "minor": f"Minor observation on {eq['tag']}: paint degradation on external surface. Fire protection signage faded at location. Documentation update required for last PM record.",
            "major": f"Major finding on {eq['tag']}: Emergency isolation valve XV-101 response time measured at 45 seconds (requirement: <30 seconds per OISD-118 Clause 7.3). Corrective action required within 30 days.",
            "critical": f"Critical non-conformance: PSV-301 on LPG sphere V-301 found set pressure drifted to 19.5 bar (design: 18 bar). Immediate re-calibration/replacement mandatory per PESO regulations.",
        }
        
        insp = {
            "inspection_id": f"INS-{2023001 + i}",
            "equipment_tag": eq["tag"],
            "inspection_type": insp_type,
            "inspector": random.choice(inspectors),
            "inspection_date": insp_date.strftime("%Y-%m-%d"),
            "next_due_date": (insp_date + timedelta(days=random.choice([90, 180, 365]))).strftime("%Y-%m-%d"),
            "status": random.choices(["completed", "overdue"], weights=[80, 20])[0],
            "findings": findings_map[severity],
            "severity": severity,
            "corrective_actions": f"{'Corrective action plan submitted. Target completion: 30 days.' if severity in ['major', 'critical'] else 'No action required.' if severity == 'none' else 'Housekeeping improvement scheduled.'}",
            "regulatory_ref": reg_ref,
        }
        inspections.append(insp)
    
    return inspections


# ============================================================
# INCIDENTS & NEAR-MISSES
# ============================================================

def generate_incidents():
    """Generate 12 incident/near-miss records."""
    incidents = [
        {
            "incident_id": "INC-2023-001", "incident_type": "near_miss", "severity": "medium",
            "date_occurred": "2023-03-15", "area": "CDU-1", "equipment_tag": "P-101-A",
            "description": "During routine pump start-up, coupling guard was found unsecured. Rotating coupling was exposed while technician was in proximity. Pump was stopped immediately.",
            "root_cause": "Coupling guard bolt not tightened after previous maintenance. Lock-out/Tag-out procedure not fully followed during re-commissioning.",
            "corrective_actions": "1. Retrained all maintenance crew on LOTO procedure. 2. Added coupling guard check to PM checklist. 3. Installed tamper-evident fasteners on all coupling guards.",
            "lessons_learned": "All rotating equipment guards must be physically verified before startup. A dedicated 'guard verification' step has been added to the start-up checklist.",
            "reported_by": "Amit Singh", "status": "closed"
        },
        {
            "incident_id": "INC-2023-002", "incident_type": "incident", "severity": "high",
            "date_occurred": "2023-06-22", "area": "CDU-1", "equipment_tag": "HX-101",
            "description": "Hydrocarbon leak detected at tube-to-tubesheet joint of crude preheat exchanger HX-101. Approximately 50 liters of naphtha leaked before isolation. No fire. Area evacuated per emergency procedure.",
            "root_cause": "Stress corrosion cracking at rolled tube joint due to chloride stress from cooling water side. Chloride levels had exceeded 50 ppm limit for 3 weeks prior to incident.",
            "corrective_actions": "1. Exchanger isolated and depressurized. 2. Leaking tubes plugged. 3. Cooling water chloride monitoring frequency increased from weekly to daily. 4. Chloride limit alarm added to DCS.",
            "lessons_learned": "Cooling water quality must be continuously monitored, not just sampled weekly. Early warning indicators (chloride trending) could have prevented this incident if monitored in real-time.",
            "reported_by": "Rajesh Kumar", "status": "closed"
        },
        {
            "incident_id": "INC-2023-003", "incident_type": "near_miss", "severity": "low",
            "date_occurred": "2023-08-10", "area": "UTILITY", "equipment_tag": "P-301-A",
            "description": "Cooling water pump P-301-A auto-tripped on high vibration during normal operation. Standby pump P-301-B auto-started within 5 seconds. No process impact.",
            "root_cause": "Bearing wear due to extended run beyond recommended service interval. PM was overdue by 2 weeks.",
            "corrective_actions": "Bearing replaced. PM scheduling system updated to send escalation alerts for overdue PMs.",
            "lessons_learned": "Overdue preventive maintenance on critical rotating equipment directly increases risk of unplanned trips. PM compliance must be tracked as a KPI.",
            "reported_by": "Suresh Patel", "status": "closed"
        },
        {
            "incident_id": "INC-2024-001", "incident_type": "incident", "severity": "critical",
            "date_occurred": "2024-01-18", "area": "GAS-PLANT", "equipment_tag": "C-101",
            "description": "Gas compressor C-101 experienced catastrophic valve failure on cylinder 3. Metal fragments found in discharge piping. Compressor automatically shut down on high vibration. Gas release contained by isolation valves.",
            "root_cause": "Fatigue failure of suction valve plate. Metallurgical analysis revealed material defect in valve plate batch (supplier NCR raised). Operating beyond OEM recommended continuous run hours.",
            "corrective_actions": "1. Replaced all valve plates from affected batch. 2. Issued supplier non-conformance report. 3. Reduced continuous run limit from 8000 to 6000 hours. 4. Added valve plate inspection to 3000-hour PM.",
            "lessons_learned": "Material traceability is essential for critical rotating equipment components. Running beyond OEM limits without additional inspection creates unacceptable risk. Supplier quality audits must be more frequent.",
            "reported_by": "Vikram Joshi", "status": "closed"
        },
        {
            "incident_id": "INC-2024-002", "incident_type": "near_miss", "severity": "high",
            "date_occurred": "2024-04-05", "area": "STORAGE", "equipment_tag": "V-301",
            "description": "During routine PESO inspection, LPG sphere V-301 relief valve PSV-301 found with set pressure drifted to 19.5 bar (design: 18 bar). If overpressure event had occurred, relief valve may not have opened at correct pressure.",
            "root_cause": "Spring relaxation due to extended service interval. Last recertification was 18 months overdue.",
            "corrective_actions": "1. PSV-301 immediately replaced with recertified spare. 2. PSV tracking database updated with automated alerts. 3. All PESO-regulated PSVs audited — 2 more found overdue.",
            "lessons_learned": "Safety-critical device testing must never be deferred. Automated tracking and escalation for PSV recertification must be implemented plant-wide.",
            "reported_by": "Dr. K. Raghavan", "status": "closed"
        },
        {
            "incident_id": "INC-2024-003", "incident_type": "unsafe_condition", "severity": "medium",
            "date_occurred": "2024-05-20", "area": "CDU-1", "equipment_tag": "H-101",
            "description": "IR thermography survey of furnace H-101 revealed hot spot (220°C) on casing at Row-3. Normal casing temperature should be below 80°C. Indicates refractory degradation.",
            "root_cause": "Refractory lining crack propagation from thermal shock during emergency shutdown 3 months prior. Rate of cooldown exceeded 50°C/hr limit.",
            "corrective_actions": "1. Installed temporary external cooling fan on hot spot area. 2. Scheduled refractory repair during next maintenance window. 3. Revised ESD cooldown procedure to enforce 30°C/hr maximum rate.",
            "lessons_learned": "Post-ESD inspections should include systematic IR survey of all fired equipment within 48 hours. Thermal shock damage may not be immediately apparent.",
            "reported_by": "Anita Reddy", "status": "closed"
        },
        {
            "incident_id": "INC-2024-004", "incident_type": "incident", "severity": "medium",
            "date_occurred": "2024-07-12", "area": "NHT-1", "equipment_tag": "P-201-A",
            "description": "Naphtha transfer pump P-201-A mechanical seal failure resulted in small naphtha release (~5 liters). Contained within pump sump. Fire watch activated. No ignition.",
            "root_cause": "Seal flush piping (Plan 11) partially blocked by scale deposits, reducing flush flow to seal faces. Resulted in dry running and seal face damage.",
            "corrective_actions": "1. Seal replaced. 2. Flush piping cleaned and flushed. 3. Added flow indicator on seal flush line. 4. Quarterly flush line inspection added to PM plan.",
            "lessons_learned": "Seal support systems (flush, cooling, barrier fluid) must be monitored as actively as the main equipment. A blocked flush line turns a minor issue into a seal failure.",
            "reported_by": "Mohammed Ali", "status": "closed"
        },
        {
            "incident_id": "INC-2024-005", "incident_type": "near_miss", "severity": "low",
            "date_occurred": "2024-09-03", "area": "CDU-1", "equipment_tag": "TI-1001",
            "description": "Temperature indication TI-1001 showing 15°C lower than actual column top temperature. Discovered during cross-check with redundant instrument.",
            "root_cause": "Thermocouple junction degradation. EMF drift causing systematic low reading.",
            "corrective_actions": "Thermocouple replaced. Calibration check performed on all critical temperature instruments in CDU-1.",
            "lessons_learned": "Critical process temperature measurements should always have redundant instruments. Regular cross-checks between redundant instruments should be formalized.",
            "reported_by": "Deepak Verma", "status": "closed"
        },
        {
            "incident_id": "INC-2025-001", "incident_type": "near_miss", "severity": "medium",
            "date_occurred": "2025-01-22", "area": "CDU-1", "equipment_tag": "V-102",
            "description": "High liquid level alarm activated on atmospheric column V-102 reflux drum. Level reached 90% (trip at 95%). Operator responded within 2 minutes to increase reflux draw-off.",
            "root_cause": "Level control valve CV-201 in downstream naphtha line was sluggish (stroking time increased from 15 sec to 45 sec). Control valve positioner was malfunctioning.",
            "corrective_actions": "Control valve positioner recalibrated. Stroking test passed. Added control valve stroking test to quarterly PM checklist.",
            "lessons_learned": "Control valve performance degradation is often gradual and invisible until it causes a process upset. Regular stroking tests must be part of the PM program.",
            "reported_by": "Priya Sharma", "status": "closed"
        },
        {
            "incident_id": "INC-2025-002", "incident_type": "unsafe_condition", "severity": "high",
            "date_occurred": "2025-03-15", "area": "STORAGE", "equipment_tag": "V-301",
            "description": "Annual tank inspection revealed external corrosion on LPG sphere V-301 leg supports. Wall thickness reduction of 15% measured at ground level contact points. Structural integrity assessment required.",
            "root_cause": "Inadequate coating maintenance at sphere leg base plates. Water pooling during monsoon season accelerated corrosion at soil-to-air interface.",
            "corrective_actions": "1. Temporary bracing installed. 2. Surface preparation and re-coating of all 8 leg supports. 3. Drainage improvement around sphere foundations. 4. Added leg support inspection to monsoon pre-season checklist.",
            "lessons_learned": "Below-deck and foundation-level corrosion is easy to overlook but can have catastrophic structural consequences. Monsoon preparedness must include drainage and coating verification.",
            "reported_by": "Sunil Yadav", "status": "investigating"
        },
    ]
    return incidents


# ============================================================
# COMPLIANCE REQUIREMENTS — Indian regulatory framework
# ============================================================

def generate_compliance_requirements():
    """Generate compliance requirements mapping for Indian industrial regulations."""
    requirements = [
        # Factory Act, 1948
        {"req_id": "FA-001", "regulation": "Factories Act 1948", "clause": "Section 7A",
         "requirement_text": "Safety Policy: Every factory must have a written safety policy signed by the occupier, displayed prominently, and communicated to all workers.",
         "category": "general_safety", "applicable_equipment": ["all"],
         "current_status": "compliant", "last_audit_date": "2025-01-15", "next_audit_date": "2026-01-15"},
        {"req_id": "FA-002", "regulation": "Factories Act 1948", "clause": "Section 36",
         "requirement_text": "Precautions against dangerous fumes: No person shall enter any chamber, tank, or confined space until it has been certified safe by a competent person.",
         "category": "confined_space", "applicable_equipment": ["vessel"],
         "current_status": "compliant", "last_audit_date": "2025-02-10", "next_audit_date": "2025-08-10"},
        {"req_id": "FA-003", "regulation": "Factories Act 1948", "clause": "Section 38",
         "requirement_text": "Precautions in case of fire: Every factory must maintain adequate fire-fighting equipment, marked fire exits, and conduct fire drills every 6 months.",
         "category": "fire_protection", "applicable_equipment": ["all"],
         "current_status": "partial", "gap_description": "Fire drill conducted only once in last 12 months. Second drill overdue by 2 months.",
         "last_audit_date": "2025-01-15", "next_audit_date": "2025-07-15"},
        {"req_id": "FA-004", "regulation": "Factories Act 1948", "clause": "Section 40B",
         "requirement_text": "Safety Officer appointment mandatory for factories with 1000+ workers or hazardous processes. Safety officer must have prescribed qualifications.",
         "category": "personnel", "applicable_equipment": ["all"],
         "current_status": "compliant", "last_audit_date": "2025-01-15", "next_audit_date": "2026-01-15"},
        
        # OISD-118: Fire Protection
        {"req_id": "OISD-118-001", "regulation": "OISD-118", "clause": "Clause 4.2",
         "requirement_text": "Firewater system shall be designed for minimum 4 hours continuous operation. Firewater storage capacity shall be minimum 4 hours × design flow rate.",
         "category": "fire_protection", "applicable_equipment": ["all"],
         "current_status": "compliant", "last_audit_date": "2024-11-20", "next_audit_date": "2025-11-20"},
        {"req_id": "OISD-118-002", "regulation": "OISD-118", "clause": "Clause 7.3",
         "requirement_text": "Emergency isolation valves (EIVs) shall be operable within 30 seconds. EIVs shall be tested quarterly for response time.",
         "category": "fire_protection", "applicable_equipment": ["valve"],
         "current_status": "non_compliant", "gap_description": "EIV XV-101 response time measured at 45 seconds during last quarterly test. Exceeds 30-second requirement. Actuator maintenance overdue.",
         "last_audit_date": "2025-03-10", "next_audit_date": "2025-06-10"},
        {"req_id": "OISD-118-003", "regulation": "OISD-118", "clause": "Clause 5.1",
         "requirement_text": "Fixed foam/water spray systems shall be provided for all petroleum storage tanks above 500 m3 capacity. Systems shall be tested annually.",
         "category": "fire_protection", "applicable_equipment": ["vessel"],
         "current_status": "compliant", "last_audit_date": "2025-01-20", "next_audit_date": "2026-01-20"},
        {"req_id": "OISD-118-004", "regulation": "OISD-118", "clause": "Clause 8.2",
         "requirement_text": "Fire detection and alarm system shall provide coverage for all process areas. System shall be tested monthly.",
         "category": "fire_protection", "applicable_equipment": ["all"],
         "current_status": "partial", "gap_description": "Monthly test records missing for March and April 2025. System functional but documentation incomplete.",
         "last_audit_date": "2025-05-01", "next_audit_date": "2025-06-01"},
        
        # OISD-144: Petroleum Storage
        {"req_id": "OISD-144-001", "regulation": "OISD-144", "clause": "Clause 3.4",
         "requirement_text": "All petroleum storage tanks shall have dyke walls capable of containing 110% of the largest tank volume within the dyke.",
         "category": "storage_safety", "applicable_equipment": ["vessel"],
         "current_status": "compliant", "last_audit_date": "2024-12-15", "next_audit_date": "2025-12-15"},
        {"req_id": "OISD-144-002", "regulation": "OISD-144", "clause": "Clause 5.2",
         "requirement_text": "Tank shell thickness survey shall be conducted every 5 years or as recommended by API-653 assessment, whichever is earlier.",
         "category": "structural_integrity", "applicable_equipment": ["vessel"],
         "current_status": "partial", "gap_description": "V-301 LPG sphere leg support corrosion found during recent inspection. Structural assessment pending.",
         "last_audit_date": "2025-03-15", "next_audit_date": "2025-09-15"},
        
        # OISD-150: LPG Safety
        {"req_id": "OISD-150-001", "regulation": "OISD-150", "clause": "Clause 6.1",
         "requirement_text": "LPG storage spheres shall have water spray system, gas detection system, and emergency isolation capable of remote operation from safe location.",
         "category": "lpg_safety", "applicable_equipment": ["vessel"],
         "current_status": "compliant", "last_audit_date": "2025-02-01", "next_audit_date": "2025-08-01"},
        {"req_id": "OISD-150-002", "regulation": "OISD-150", "clause": "Clause 7.3",
         "requirement_text": "All pressure safety valves on LPG service shall be tested and recertified annually. Records shall be maintained for PESO inspection.",
         "category": "pressure_safety", "applicable_equipment": ["safety_valve"],
         "current_status": "non_compliant", "gap_description": "PSV-301 recertification was 18 months overdue when discovered during PESO inspection. Two additional PSVs found overdue.",
         "last_audit_date": "2025-04-05", "next_audit_date": "2025-10-05"},
        
        # PESO
        {"req_id": "PESO-001", "regulation": "PESO", "clause": "Petroleum Rules, Rule 129",
         "requirement_text": "License for storage of petroleum Class A/B: License must be renewed before expiry. Storage installation must comply with all conditions of the license.",
         "category": "licensing", "applicable_equipment": ["vessel"],
         "current_status": "compliant", "last_audit_date": "2024-08-15", "next_audit_date": "2025-08-15"},
        {"req_id": "PESO-002", "regulation": "PESO", "clause": "Petroleum Rules, Rule 144",
         "requirement_text": "Petroleum storage tanks and pressure vessels shall be inspected by PESO-authorized competent person at prescribed intervals.",
         "category": "inspection", "applicable_equipment": ["vessel", "safety_valve"],
         "current_status": "partial", "gap_description": "PESO inspection of 2 out of 5 pressure vessels pending. Scheduled for next quarter.",
         "last_audit_date": "2025-01-10", "next_audit_date": "2025-07-10"},
        
        # Environmental
        {"req_id": "ENV-001", "regulation": "Environment Protection Act", "clause": "Schedule VI",
         "requirement_text": "Stack emissions (SO2, NOx, PM) shall not exceed prescribed limits. Continuous Emission Monitoring System (CEMS) mandatory for units above 50 MW thermal input.",
         "category": "environment", "applicable_equipment": ["furnace"],
         "current_status": "compliant", "last_audit_date": "2025-03-01", "next_audit_date": "2025-09-01"},
    ]
    return requirements


# ============================================================
# STANDARD OPERATING PROCEDURES (SOPs)
# ============================================================

def generate_sops():
    """Generate SOP document metadata and content."""
    sops = [
        {
            "doc_id": "SOP-CDU-001", "title": "CDU-1 Normal Start-Up Procedure",
            "doc_type": "sop", "content_text": """
STANDARD OPERATING PROCEDURE: CDU-1 NORMAL START-UP

Document No: SOP-CDU-001 | Rev: 04 | Date: 2024-06-15
Unit: Crude Distillation Unit 1 (CDU-1)
Approved by: Plant Manager — R. Krishnamurthy

1. PRE-START CHECKS
1.1 Verify all maintenance work orders are closed and PTW (Permit to Work) cleared
1.2 Confirm equipment lineup per P&ID-CDU-001-Rev3
1.3 Verify instrument air supply at 7 bar minimum
1.4 Confirm firewater system pressurized and tested
1.5 Verify all PSVs (PSV-101, PSV-102) are in service
1.6 Confirm DCS and ESD system functional — run partial stroke test on all ESD valves

2. UTILITY ESTABLISHMENT
2.1 Start cooling water pump P-301-A (standby P-301-B on auto)
2.2 Establish steam supply to CDU-1 — verify header pressure at 10.5 bar
2.3 Start instrument air compressor if not running
2.4 Establish nitrogen supply for blanketing

3. COLUMN PREPARATION
3.1 Pressure test atmospheric column V-102 with nitrogen to 2 bar
3.2 Hold for 4 hours — verify no pressure drop (leak test)
3.3 Purge column with nitrogen until O2 < 1% (verify with portable gas detector)
3.4 Establish reflux drum V-102-D level at 50%

4. FURNACE LIGHT-UP (H-101)
4.1 Verify furnace purge completed — 5 volume changes minimum
4.2 Light pilot burners per OEM procedure (Thermax TH-FH-50MW manual Section 6.2)
4.3 Gradually increase firing rate — do not exceed 30°C/hr heating rate
4.4 Monitor all tube skin temperatures — maximum 550°C

5. CRUDE CHARGE
5.1 Line up crude feed from storage through preheat train (HX-101, HX-102)
5.2 Start crude charge pump P-101-A at minimum speed
5.3 Gradually increase charge rate to design (350 m³/hr) over 8 hours
5.4 Monitor column temperatures and pressures continuously

6. PRODUCT ROUTING
6.1 Once column temperatures stabilize, begin product withdrawal
6.2 Route naphtha to Naphtha Hydrotreater (NHT-1) via P-201-A
6.3 Route kerosene and diesel to respective storage tanks
6.4 Route atmospheric residue to Vacuum Distillation Unit (VDU-1)

EMERGENCY: In case of any abnormality, refer to SOP-CDU-ESD-001 (Emergency Shutdown Procedure)
""",
        },
        {
            "doc_id": "SOP-CDU-ESD-001", "title": "CDU-1 Emergency Shutdown Procedure",
            "doc_type": "sop", "content_text": """
STANDARD OPERATING PROCEDURE: CDU-1 EMERGENCY SHUTDOWN

Document No: SOP-CDU-ESD-001 | Rev: 03 | Date: 2024-06-15
Unit: Crude Distillation Unit 1 (CDU-1)
Classification: SAFETY CRITICAL

TRIGGERS FOR EMERGENCY SHUTDOWN:
- Hydrocarbon release/leak not contained within 5 minutes
- Fire in process area
- Loss of all cooling water
- Multiple instrument failures affecting safe operation
- Earthquake above intensity 5 on Richter scale
- Gas detection alarm at 60% LEL sustained for 2 minutes

IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. Press ESD pushbutton (located at Panel CP-01 and field station FS-03)
2. ESD system will automatically:
   a. Close crude feed valve XV-101
   b. Trip all pumps (P-101-A/B, P-201-A)
   c. Trip furnace H-101 (fuel gas shut-off)
   d. Open depressuring valve to flare
3. Sound emergency alarm — activate PA system
4. Evacuate non-essential personnel to assembly point AP-2
5. Notify: Shift Supervisor → Safety Officer → Plant Manager

CONTROLLED COOLDOWN:
- Maximum cooldown rate: 30°C/hr (CRITICAL — exceeding this causes refractory damage)
- Monitor furnace tube skin temperatures until below 200°C
- Maintain nitrogen blanket on column during cooldown
"""
        },
        {
            "doc_id": "SOP-PUMP-PM-001", "title": "Centrifugal Pump Preventive Maintenance Procedure",
            "doc_type": "sop", "content_text": """
STANDARD OPERATING PROCEDURE: CENTRIFUGAL PUMP PM

Document No: SOP-PUMP-PM-001 | Rev: 02 | Date: 2024-03-10
Applicable Equipment: P-101-A/B, P-201-A, P-301-A, P-401-A

FREQUENCY: Every 6 months or 4000 running hours (whichever comes first)

PRE-MAINTENANCE:
1. Isolate pump per LOTO procedure (SOP-LOTO-001)
2. Depressurize and drain pump casing
3. Verify zero energy state — signed off by authorized person

INSPECTION CHECKLIST:
□ Bearing condition — check for play, discoloration, scoring
□ Bearing housing oil level and quality — change oil if discolored/contaminated
□ Mechanical seal condition — check for leakage, carbon face wear
□ Coupling alignment — verify within 0.05mm tolerance (laser alignment)
□ Impeller condition — check for erosion, cavitation damage
□ Shaft runout — maximum 0.025mm TIR
□ Suction strainer — clean and inspect mesh
□ Foundation bolts — torque check to specification

VIBRATION BASELINE:
Record vibration readings at DE and NDE bearings:
- Acceptable: <4.5 mm/s RMS (ISO 10816)
- Alert: 4.5–7.1 mm/s
- Danger: >7.1 mm/s — do not return to service

POST-MAINTENANCE:
1. Reassemble per OEM torque specifications
2. Remove LOTO — verify all locks removed
3. Prime pump and verify rotation direction
4. Start pump on minimum flow — monitor for 30 minutes
5. Record baseline vibration and temperature readings
"""
        },
    ]
    return sops


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_all_seed_data():
    """Generate all synthetic data and return as a dictionary."""
    return {
        "equipment": EQUIPMENT,
        "work_orders": generate_work_orders(),
        "inspections": generate_inspections(),
        "incidents": generate_incidents(),
        "compliance_requirements": generate_compliance_requirements(),
        "sops": generate_sops(),
    }


if __name__ == "__main__":
    data = generate_all_seed_data()
    print(f"Generated:")
    print(f"  Equipment: {len(data['equipment'])} items")
    print(f"  Work Orders: {len(data['work_orders'])} records")
    print(f"  Inspections: {len(data['inspections'])} records")
    print(f"  Incidents: {len(data['incidents'])} records")
    print(f"  Compliance: {len(data['compliance_requirements'])} requirements")
    print(f"  SOPs: {len(data['sops'])} documents")
    
    # Save to seed directory
    import os
    seed_dir = os.path.join(os.path.dirname(__file__), "data", "seed")
    os.makedirs(seed_dir, exist_ok=True)
    
    for key, value in data.items():
        filepath = os.path.join(seed_dir, f"{key}.json")
        with open(filepath, "w") as f:
            json.dump(value, f, indent=2, default=str)
        print(f"  Saved: {filepath}")
