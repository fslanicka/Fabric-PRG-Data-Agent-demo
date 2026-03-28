"""
Prague Airport Operational Data Generator for Microsoft Fabric
==============================================================

Usage in Fabric:
    Copy this script into a Fabric Notebook, splitting at each '# CELL N' marker.
    Each CELL comment denotes where to create a new notebook cell.
    CELL 1 should be a Markdown cell; all others are Code cells.

    Prerequisites:
    - Lakehouse with flight data (from 01_generate_flight_data.py) must be attached
    - Eventhouse with KQL database 'PRGOperations' must exist
    - Update KUSTO_URI and KUSTO_DATABASE in CELL 2 before running

Generates operational data linked to existing flights:
    - gate_assignments  (~5,000 rows) → gate allocation and turnaround tracking
    - crew_rosters      (~3,000 rows) → crew member assignments per flight
    - maintenance_events (~2,000 rows) → aircraft maintenance records
"""

# ============================================================================
# CELL 1 — Markdown Cell
# ============================================================================
# Create a **Markdown** cell in Fabric with the following content:
#
#   # Prague Airport Operational Data Generator
#   Generates operational data (gate assignments, crew rosters, maintenance events)
#   and writes to the Eventhouse KQL database `PRGOperations`.
#   **Requires:** Lakehouse with flight data from Notebook 01.
#

# ============================================================================
# CELL 2 — Imports and Configuration
# ============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as F
import builtins
import random
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np

# Restore Python builtins shadowed by PySpark
round = builtins.round
max = builtins.max
min = builtins.min

spark = SparkSession.builder.getOrCreate()

# Configuration
SEED = 42
random.seed(SEED)
rng = np.random.default_rng(SEED)

# ── Eventhouse connection ──
# Update these values with your Eventhouse Query URI and database name.
# Find the Query URI in your KQL database dashboard → "Database details" card → Copy URI.
KUSTO_URI = "<YOUR_EVENTHOUSE_QUERY_URI>"       # e.g., "https://xyz.z0.kusto.fabric.microsoft.com"
KUSTO_DATABASE = "PRGOperations"                 # KQL database name

# Acquire access token for Eventhouse authentication.
# The Kusto Spark connector does NOT inherit the notebook session identity automatically —
# an explicit token must be passed, otherwise writes fail with a permissions error.
accessToken = mssparkutils.credentials.getToken("kusto")

print(f"Configuration: SEED={SEED}, Database={KUSTO_DATABASE}")
print(f"Kusto URI: {KUSTO_URI}")
print(f"Access token acquired: {'Yes' if accessToken else 'No'}")

# ============================================================================
# CELL 3 — Load Existing Flight Data from Lakehouse
# ============================================================================
# Read flights table to link operational data via flight_id

df_flights = spark.sql("""
    SELECT flight_id, flight_number, airline_code, flight_type,
           origin_airport_code, destination_airport_code,
           scheduled_datetime, status, delay_minutes, delay_reason,
           terminal, gate, aircraft_type, passenger_count
    FROM flights
    ORDER BY flight_id
""")

pdf_flights = df_flights.toPandas()
print(f"Loaded {len(pdf_flights):,} flights from Lakehouse")

# Also load airports for crew base assignments
df_airports = spark.sql("SELECT airport_code, city, country FROM airports")
airports_list = [row["airport_code"] for row in df_airports.collect()]
print(f"Loaded {len(airports_list)} airports")

# ============================================================================
# CELL 4 — Generate Gate Assignments (~5,000 rows)
# ============================================================================
# Select a subset of flights for gate assignment tracking.
# In practice, not every flight has detailed gate assignment data.

TARGET_GATE_ASSIGNMENTS = 5000

# Sample flights for gate assignments (prefer departures, spread across dates)
flight_ids = pdf_flights["flight_id"].values
sample_idx = rng.choice(len(pdf_flights), size=min(TARGET_GATE_ASSIGNMENTS, len(pdf_flights)), replace=False)
sample_flights = pdf_flights.iloc[sample_idx].copy().reset_index(drop=True)

n_ga = len(sample_flights)

# Scheduled start: 60-120 minutes before flight scheduled_datetime
lead_minutes = rng.integers(60, 121, size=n_ga)
ga_sched_start = pd.to_datetime(sample_flights["scheduled_datetime"]) - pd.to_timedelta(lead_minutes, unit="m")

# Scheduled end: 15-30 minutes after flight scheduled_datetime
trail_minutes = rng.integers(15, 31, size=n_ga)
ga_sched_end = pd.to_datetime(sample_flights["scheduled_datetime"]) + pd.to_timedelta(trail_minutes, unit="m")

# Turnaround minutes: time between previous flight leaving and this one boarding
turnaround = rng.integers(30, 121, size=n_ga)

# Status: ~75% on_time, ~20% delayed, ~5% reassigned
status_rolls = rng.random(n_ga)
ga_status = np.where(status_rolls < 0.75, "on_time",
            np.where(status_rolls < 0.95, "delayed", "reassigned"))

# Actual start/end: based on status
actual_start_offset = np.zeros(n_ga)
actual_end_offset = np.zeros(n_ga)

delayed_mask = ga_status == "delayed"
actual_start_offset[delayed_mask] = rng.integers(5, 46, size=delayed_mask.sum())
actual_end_offset[delayed_mask] = actual_start_offset[delayed_mask] + rng.integers(0, 16, size=delayed_mask.sum())

reassigned_mask = ga_status == "reassigned"
actual_start_offset[reassigned_mask] = rng.integers(10, 61, size=reassigned_mask.sum())
actual_end_offset[reassigned_mask] = actual_start_offset[reassigned_mask] + rng.integers(5, 31, size=reassigned_mask.sum())

ga_actual_start = ga_sched_start + pd.to_timedelta(actual_start_offset, unit="m")
ga_actual_end = ga_sched_end + pd.to_timedelta(actual_end_offset, unit="m")

# For cancelled flights, set actual times to NaT
cancelled_mask = sample_flights["status"].values == "cancelled"
ga_actual_start[cancelled_mask] = pd.NaT
ga_actual_end[cancelled_mask] = pd.NaT

pdf_gate_assignments = pd.DataFrame({
    "gate_assignment_id": range(1, n_ga + 1),
    "flight_id": sample_flights["flight_id"].values,
    "gate": sample_flights["gate"].values,
    "terminal": sample_flights["terminal"].values,
    "scheduled_start": ga_sched_start,
    "scheduled_end": ga_sched_end,
    "actual_start": ga_actual_start,
    "actual_end": ga_actual_end,
    "turnaround_minutes": turnaround,
    "status": ga_status,
})

print(f"Generated {len(pdf_gate_assignments):,} gate assignments")
print(f"  Status: {pd.Series(ga_status).value_counts().to_dict()}")

# ============================================================================
# CELL 5 — Generate Crew Rosters (~3,000 rows)
# ============================================================================
# Create a pool of ~200 crew members and assign them to flights.

NUM_CREW_MEMBERS = 200

# Generate crew member pool
first_names_male = ["Jan", "Petr", "Martin", "Tomáš", "Jiří", "David", "Lukáš",
                    "Michael", "Thomas", "James", "Robert", "Hans", "Pierre",
                    "Marco", "Stefan", "Andreas", "Erik", "Lars", "Piotr", "Miroslav"]
first_names_female = ["Jana", "Eva", "Marie", "Lucie", "Petra", "Anna", "Tereza",
                      "Sarah", "Emma", "Sophie", "Laura", "Maria", "Claudia",
                      "Katarina", "Ingrid", "Elena", "Monika", "Agnieszka", "Hana", "Kristýna"]
last_names = ["Novák", "Svoboda", "Novotný", "Dvořák", "Černý", "Procházka", "Kučera",
              "Veselý", "Horák", "Němec", "Pokorný", "Marek", "Mueller", "Schmidt",
              "Fischer", "Weber", "Smith", "Johnson", "Williams", "Brown",
              "Dupont", "Bernard", "Rossi", "Bianchi", "Eriksson", "Andersson",
              "Kowalski", "Nowak", "Horváth", "Tóth"]
nationalities = ["Czech", "Czech", "Czech", "Czech", "German", "German", "British",
                 "French", "Italian", "Swedish", "Polish", "Slovak", "Austrian", "Dutch"]

crew_pool = []
for i in range(NUM_CREW_MEMBERS):
    is_female = rng.random() < 0.45
    first = rng.choice(first_names_female if is_female else first_names_male)
    last = rng.choice(last_names)
    nat = rng.choice(nationalities)
    base = rng.choice(["PRG"] * 12 + ["FRA", "LHR", "CDG", "AMS", "VIE", "MUC", "WAW", "BUD"])
    crew_pool.append({
        "crew_member_id": f"CRW-{i+1:04d}",
        "crew_name": f"{first} {last}",
        "nationality": nat,
        "base_airport": base,
    })

# Role distribution for crew
# Captains (IDs 1-40), First Officers (41-80), Pursers (81-120), Cabin Crew (121-200)
captain_ids = list(range(40))
fo_ids = list(range(40, 80))
purser_ids = list(range(80, 120))
cabin_ids = list(range(120, NUM_CREW_MEMBERS))

# Select a subset of flights for crew assignment
TARGET_FLIGHTS_WITH_CREW = 600
crew_flight_idx = rng.choice(len(pdf_flights), size=min(TARGET_FLIGHTS_WITH_CREW, len(pdf_flights)), replace=False)
crew_flights = pdf_flights.iloc[crew_flight_idx]

roster_rows = []
roster_id = 1

for _, flight in crew_flights.iterrows():
    fid = flight["flight_id"]
    pax = flight["passenger_count"]
    flight_dt = flight["scheduled_datetime"]

    # Assign 1 captain
    cap = crew_pool[rng.choice(captain_ids)]
    license_num = f"ATPL-{cap['nationality'][:2].upper()}-{rng.integers(2010, 2024)}-{rng.integers(1000, 9999)}"
    roster_rows.append({
        "roster_id": roster_id, "flight_id": fid,
        "crew_member_id": cap["crew_member_id"], "crew_name": cap["crew_name"],
        "role": "captain", "license_number": license_num,
        "nationality": cap["nationality"], "base_airport": cap["base_airport"],
        "roster_datetime": flight_dt,
    })
    roster_id += 1

    # Assign 1 first officer
    fo = crew_pool[rng.choice(fo_ids)]
    license_num = f"ATPL-{fo['nationality'][:2].upper()}-{rng.integers(2012, 2025)}-{rng.integers(1000, 9999)}"
    roster_rows.append({
        "roster_id": roster_id, "flight_id": fid,
        "crew_member_id": fo["crew_member_id"], "crew_name": fo["crew_name"],
        "role": "first_officer", "license_number": license_num,
        "nationality": fo["nationality"], "base_airport": fo["base_airport"],
        "roster_datetime": flight_dt,
    })
    roster_id += 1

    # Assign 1 purser
    pr = crew_pool[rng.choice(purser_ids)]
    roster_rows.append({
        "roster_id": roster_id, "flight_id": fid,
        "crew_member_id": pr["crew_member_id"], "crew_name": pr["crew_name"],
        "role": "purser", "license_number": None,
        "nationality": pr["nationality"], "base_airport": pr["base_airport"],
        "roster_datetime": flight_dt,
    })
    roster_id += 1

    # Assign 2-6 cabin crew (based on passenger count)
    n_cabin = 2 if pax < 100 else (3 if pax < 150 else (4 if pax < 200 else (5 if pax < 280 else 6)))
    cabin_selection = rng.choice(cabin_ids, size=n_cabin, replace=False)
    for ci in cabin_selection:
        cc = crew_pool[ci]
        roster_rows.append({
            "roster_id": roster_id, "flight_id": fid,
            "crew_member_id": cc["crew_member_id"], "crew_name": cc["crew_name"],
            "role": "cabin_crew", "license_number": None,
            "nationality": cc["nationality"], "base_airport": cc["base_airport"],
            "roster_datetime": flight_dt,
        })
        roster_id += 1

pdf_crew_rosters = pd.DataFrame(roster_rows)
print(f"Generated {len(pdf_crew_rosters):,} crew roster entries")
print(f"  Unique crew members: {pdf_crew_rosters['crew_member_id'].nunique()}")
print(f"  Role distribution: {pdf_crew_rosters['role'].value_counts().to_dict()}")

# ============================================================================
# CELL 6 — Generate Maintenance Events (~2,000 rows)
# ============================================================================

TARGET_MAINTENANCE = 2000

# Aircraft registration pool (based on aircraft types in flights)
aircraft_types = pdf_flights["aircraft_type"].unique()
registrations = {}
reg_prefixes = {"A320": "OK-TV", "A319": "OK-NE", "A321": "OK-TS", "A321neo": "OK-TS",
                "A220-300": "OK-JF", "A330": "OK-YB", "A350-900": "B-LR",
                "B737-800": "OK-SW", "B737 MAX 8": "OK-SX", "B777-300ER": "A6-EG",
                "B787-8": "ET-A", "B787-9": "A6-BL", "ATR 72": "OK-KF",
                "E190": "OK-GJ", "E195": "OK-GK", "E175": "SP-LI",
                "CRJ 900": "D-ACN", "A320neo": "HA-LV"}
for at in aircraft_types:
    prefix = reg_prefixes.get(at, "OK-XX")
    n_aircraft = rng.integers(2, 8)
    registrations[at] = [f"{prefix}{chr(65 + i)}" for i in range(n_aircraft)]

# Event types and categories
event_types = np.array(["scheduled", "unscheduled", "aog"])
event_type_probs = np.array([0.60, 0.35, 0.05])
categories = np.array(["engine", "avionics", "hydraulic", "structural", "cabin", "landing_gear"])
category_probs = np.array([0.15, 0.20, 0.15, 0.10, 0.25, 0.15])

# Descriptions by category
descriptions = {
    "engine": ["Routine engine inspection", "Fan blade replacement", "Oil filter change",
               "Compressor wash", "Engine vibration analysis", "Fuel nozzle inspection"],
    "avionics": ["Flight computer software update", "Nav system calibration", "Weather radar check",
                 "Transponder replacement", "Autopilot servo test", "Display unit replacement"],
    "hydraulic": ["Hydraulic pump replacement", "Brake line inspection", "Hydraulic fluid top-up",
                  "Actuator seal replacement", "Pressure test", "Reservoir inspection"],
    "structural": ["Fuselage crack inspection", "Wing spar check", "Corrosion treatment",
                   "Landing gear bay inspection", "Tail section NDT", "Window seal replacement"],
    "cabin": ["Seat repair", "Lavatory maintenance", "Galley equipment check",
              "Emergency equipment inspection", "Carpet replacement", "IFE system update"],
    "landing_gear": ["Tire replacement", "Brake pad change", "Shock strut servicing",
                     "Wheel bearing inspection", "Steering system check", "Gear retraction test"],
}

maint_rows = []
# Generate dates across the 2024-2025 range
start_date = date(2024, 1, 1)
end_date = date(2025, 12, 31)
total_days = (end_date - start_date).days

for i in range(TARGET_MAINTENANCE):
    # Pick a random date with seasonal weighting (more events in winter)
    day_offset = rng.integers(0, total_days + 1)
    event_date = start_date + timedelta(days=int(day_offset))
    month = event_date.month

    # Seasonal adjustment for event type
    if month in (12, 1, 2):  # Winter: more unscheduled
        et_probs = np.array([0.45, 0.47, 0.08])
    elif month in (6, 7, 8):  # Summer: more scheduled (high utilization)
        et_probs = np.array([0.70, 0.25, 0.05])  # FIXED: probability array sums to 1.0
    else:
        et_probs = event_type_probs.copy()

    # Ensure the sum of probabilities is exactly 1.0 to avoid ValueError
    et_probs = et_probs / et_probs.sum()

    event_type = rng.choice(event_types, p=et_probs)
    category = rng.choice(categories, p=category_probs)

    # Aircraft selection
    acft_type = rng.choice(aircraft_types)
    regs = registrations.get(acft_type, [f"OK-XX{i}"])
    reg = rng.choice(regs)

    # Duration depends on event type
    if event_type == "scheduled":
        duration = round(rng.uniform(2.0, 48.0), 1)
    elif event_type == "unscheduled":
        duration = round(rng.uniform(1.0, 24.0), 1)
    else:  # aog
        duration = round(rng.uniform(4.0, 96.0), 1)

    # Start time (maintenance usually at night for scheduled)
    if event_type == "scheduled":
        hour = rng.choice([22, 23, 0, 1, 2])
    else:
        hour = int(rng.integers(0, 24))
    minute = int(rng.integers(0, 60))
    start_dt = datetime(event_date.year, event_date.month, event_date.day, hour, minute)
    end_dt = start_dt + timedelta(hours=duration)

    # Description
    desc = rng.choice(descriptions[category])

    # Link to a flight (for unscheduled/aog, ~40% chance)
    related_fid = None
    if event_type in ("unscheduled", "aog") and rng.random() < 0.40:
        # Find flights near this date with matching aircraft type
        date_str = event_date.isoformat()
        candidates = pdf_flights[
            (pdf_flights["aircraft_type"] == acft_type) &
            (pdf_flights["scheduled_datetime"].dt.date.astype(str) == date_str)
        ]
        if len(candidates) > 0:
            related_fid = int(rng.choice(candidates["flight_id"].values))

    # Resolved: scheduled always resolved, unscheduled 95%, aog 85%
    if event_type == "scheduled":
        resolved = True
    elif event_type == "unscheduled":
        resolved = bool(rng.random() < 0.95)
    else:
        resolved = bool(rng.random() < 0.85)

    maint_rows.append({
        "maintenance_id": i + 1,
        "aircraft_type": acft_type,
        "aircraft_registration": reg,
        "event_type": event_type,
        "category": category,
        "description": desc,
        "start_datetime": start_dt,
        "end_datetime": end_dt,
        "duration_hours": duration,
        "related_flight_id": related_fid,
        "resolved": resolved,
    })

pdf_maintenance = pd.DataFrame(maint_rows)

# Convert related_flight_id to nullable int
pdf_maintenance["related_flight_id"] = pdf_maintenance["related_flight_id"].astype("Int64")

print(f"Generated {len(pdf_maintenance):,} maintenance events")
print(f"  Event types: {pdf_maintenance['event_type'].value_counts().to_dict()}")
print(f"  Categories: {pdf_maintenance['category'].value_counts().to_dict()}")
print(f"  With related flight: {pdf_maintenance['related_flight_id'].notna().sum()}")


# ============================================================================
# CELL 7 — Write to Eventhouse KQL Database
# ============================================================================
# Uses the Kusto Spark connector to write DataFrames to KQL tables.
# The tables must be created in the KQL database first (see setup guide).

def write_to_eventhouse(pdf, table_name, schema):
    """Write a Pandas DataFrame to an Eventhouse KQL table via Spark."""
    df = spark.createDataFrame(pdf, schema=schema)
    df.write \
        .format("com.microsoft.kusto.spark.synapse.datasource") \
        .option("kustoCluster", KUSTO_URI) \
        .option("kustoDatabase", KUSTO_DATABASE) \
        .option("kustoTable", table_name) \
        .option("accessToken", accessToken) \
        .option("tableCreateOptions", "CreateIfNotExist") \
        .mode("Append") \
        .save()
    print(f"  ✅ {table_name}: {len(pdf):,} rows written to Eventhouse")

# --- Gate Assignments ---
print("Writing gate_assignments...")
ga_schema = StructType([
    StructField("gate_assignment_id", IntegerType(), False),
    StructField("flight_id", IntegerType(), False),
    StructField("gate", StringType(), False),
    StructField("terminal", StringType(), False),
    StructField("scheduled_start", TimestampType(), False),
    StructField("scheduled_end", TimestampType(), False),
    StructField("actual_start", TimestampType(), True),
    StructField("actual_end", TimestampType(), True),
    StructField("turnaround_minutes", IntegerType(), False),
    StructField("status", StringType(), False),
])
write_to_eventhouse(pdf_gate_assignments, "gate_assignments", ga_schema)

# --- Crew Rosters ---
print("Writing crew_rosters...")
cr_schema = StructType([
    StructField("roster_id", IntegerType(), False),
    StructField("flight_id", IntegerType(), False),
    StructField("crew_member_id", StringType(), False),
    StructField("crew_name", StringType(), False),
    StructField("role", StringType(), False),
    StructField("license_number", StringType(), True),
    StructField("nationality", StringType(), False),
    StructField("base_airport", StringType(), False),
    StructField("roster_datetime", TimestampType(), False),
])
write_to_eventhouse(pdf_crew_rosters, "crew_rosters", cr_schema)

# --- Maintenance Events ---
print("Writing maintenance_events...")
me_schema = StructType([
    StructField("maintenance_id", IntegerType(), False),
    StructField("aircraft_type", StringType(), False),
    StructField("aircraft_registration", StringType(), False),
    StructField("event_type", StringType(), False),
    StructField("category", StringType(), False),
    StructField("description", StringType(), False),
    StructField("start_datetime", TimestampType(), False),
    StructField("end_datetime", TimestampType(), False),
    StructField("duration_hours", DoubleType(), False),
    StructField("related_flight_id", IntegerType(), True),
    StructField("resolved", BooleanType(), False),
])
write_to_eventhouse(pdf_maintenance, "maintenance_events", me_schema)

print("\nAll operational data written to Eventhouse!")

# ============================================================================
# CELL 8 — Write Relationship Bridge Tables to Lakehouse
# ============================================================================
# Fabric IQ Ontology only supports Lakehouse tables as relationship binding
# sources (preview limitation). These lightweight bridge tables contain just
# the FK pairs needed to define ontology relationships between entity types.

print("Writing Lakehouse tables for ontology (static bindings + relationship bridges)...")
print("(Ontology requires a static Lakehouse binding per entity type before timeseries can work)")

# lkh_gate_assignments: Full static copy for GateAssignment entity + relationship bridge
pdf_lkh_ga = pdf_gate_assignments.copy()
df_lkh_ga = spark.createDataFrame(pdf_lkh_ga, schema=StructType([
    StructField("gate_assignment_id", IntegerType(), False),
    StructField("flight_id", IntegerType(), False),
    StructField("gate", StringType(), False),
    StructField("terminal", StringType(), False),
    StructField("scheduled_start", TimestampType(), False),
    StructField("scheduled_end", TimestampType(), False),
    StructField("actual_start", TimestampType(), True),
    StructField("actual_end", TimestampType(), True),
    StructField("turnaround_minutes", IntegerType(), False),
    StructField("status", StringType(), False),
]))
df_lkh_ga.write.mode("overwrite").format("delta").saveAsTable("lkh_gate_assignments")
print(f"  ✅ lkh_gate_assignments: {len(pdf_lkh_ga):,} rows → Lakehouse")

# lkh_crew_rosters: Full static copy for CrewMember entity + relationship bridge
pdf_lkh_cr = pdf_crew_rosters.copy()
df_lkh_cr = spark.createDataFrame(pdf_lkh_cr, schema=StructType([
    StructField("roster_id", IntegerType(), False),
    StructField("flight_id", IntegerType(), False),
    StructField("crew_member_id", StringType(), False),
    StructField("crew_name", StringType(), False),
    StructField("role", StringType(), False),
    StructField("license_number", StringType(), True),
    StructField("nationality", StringType(), False),
    StructField("base_airport", StringType(), False),
    StructField("roster_datetime", TimestampType(), False),
]))
df_lkh_cr.write.mode("overwrite").format("delta").saveAsTable("lkh_crew_rosters")
print(f"  ✅ lkh_crew_rosters: {len(pdf_lkh_cr):,} rows → Lakehouse")

# lkh_maintenance_events: Full static copy for MaintenanceEvent entity + relationship bridge
pdf_lkh_me = pdf_maintenance.copy()
pdf_lkh_me["related_flight_id"] = pdf_lkh_me["related_flight_id"].astype("Int64")
df_lkh_me = spark.createDataFrame(pdf_lkh_me, schema=StructType([
    StructField("maintenance_id", IntegerType(), False),
    StructField("aircraft_type", StringType(), False),
    StructField("aircraft_registration", StringType(), False),
    StructField("event_type", StringType(), False),
    StructField("category", StringType(), False),
    StructField("description", StringType(), False),
    StructField("start_datetime", TimestampType(), False),
    StructField("end_datetime", TimestampType(), False),
    StructField("duration_hours", DoubleType(), False),
    StructField("related_flight_id", IntegerType(), True),
    StructField("resolved", BooleanType(), False),
]))
df_lkh_me.write.mode("overwrite").format("delta").saveAsTable("lkh_maintenance_events")
print(f"  ✅ lkh_maintenance_events: {len(pdf_lkh_me):,} rows → Lakehouse")

# rel_weather_flight: WeatherObservation ↔ Flight (date-level join)
df_rel_weather = spark.sql("""
    SELECT DISTINCT
        CONCAT('WX-', CAST(scheduled_datetime AS DATE)) AS weather_id,
        flight_id
    FROM flights
""")
df_rel_weather.write.mode("overwrite").format("delta").saveAsTable("rel_weather_flight")
rel_weather_count = df_rel_weather.count()
print(f"  ✅ rel_weather_flight: {rel_weather_count:,} rows → Lakehouse")

print("\nAll Lakehouse tables for ontology written!")

# ============================================================================
# CELL 9 — Verification & Summary
# ============================================================================

print("=" * 60)
print("OPERATIONAL DATA GENERATION COMPLETE")
print("=" * 60)
print(f"\nTarget Eventhouse: {KUSTO_DATABASE}")
print(f"Kusto URI: {KUSTO_URI}")
print(f"\nTables written:")
print(f"  gate_assignments:   {len(pdf_gate_assignments):,} rows")
print(f"  crew_rosters:       {len(pdf_crew_rosters):,} rows")
print(f"  maintenance_events: {len(pdf_maintenance):,} rows")

print("\n--- Gate Assignment Statistics ---")
print(f"  Status distribution: {pdf_gate_assignments['status'].value_counts().to_dict()}")
print(f"  Avg turnaround: {pdf_gate_assignments['turnaround_minutes'].mean():.0f} min")

print("\n--- Crew Roster Statistics ---")
print(f"  Unique crew members: {pdf_crew_rosters['crew_member_id'].nunique()}")
print(f"  Flights with crew: {pdf_crew_rosters['flight_id'].nunique()}")
print(f"  Role distribution: {pdf_crew_rosters['role'].value_counts().to_dict()}")

print("\n--- Maintenance Statistics ---")
print(f"  Event types: {pdf_maintenance['event_type'].value_counts().to_dict()}")
print(f"  Categories: {pdf_maintenance['category'].value_counts().to_dict()}")
print(f"  Linked to flights: {pdf_maintenance['related_flight_id'].notna().sum()}")
print(f"  Avg duration: {pdf_maintenance['duration_hours'].mean():.1f} hours")

print("\nAll tables are ready in your Eventhouse!")
print("Proceed to setup-guide/02b-configure-ontology.md to create the ontology.")

# ============================================================================
# CELL 10 — Write Airports Reference Table to Eventhouse (for Fabric Maps)
# ============================================================================
# Fabric Maps requires geographic data (latitude/longitude) in the KQL database.
# This cell copies the airports reference table from the Lakehouse to the Eventhouse,
# enabling KQL stored functions that join operational data with airport coordinates.

print("\nWriting airports reference table to Eventhouse for Fabric Maps...")

df_airports = spark.sql("SELECT * FROM airports")

airports_kql_schema = StructType([
    StructField("airport_code", StringType(), False),
    StructField("airport_name", StringType(), False),
    StructField("city", StringType(), False),
    StructField("country", StringType(), False),
    StructField("region", StringType(), False),
    StructField("latitude", DoubleType(), False),
    StructField("longitude", DoubleType(), False),
])

df_airports.write \
    .format("com.microsoft.kusto.spark.synapse.datasource") \
    .option("kustoCluster", KUSTO_URI) \
    .option("kustoDatabase", KUSTO_DATABASE) \
    .option("kustoTable", "airports") \
    .option("accessToken", accessToken) \
    .option("tableCreateOptions", "CreateIfNotExist") \
    .mode("Append") \
    .save()

airports_count = df_airports.count()
print(f"  ✅ airports: {airports_count:,} rows written to Eventhouse")
print("\nAirports reference data is now available for Fabric Maps KQL functions.")
print("See setup-guide/04-configure-map.md for creating the map.")
