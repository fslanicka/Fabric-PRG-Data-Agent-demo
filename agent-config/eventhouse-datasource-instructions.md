# Eventhouse Data Source Instructions

> **Copy the content below (between the --- markers) into the "Instructions" field for your Eventhouse KQL Database data source in the Fabric Data Agent configuration.**

---

## General Knowledge

This Eventhouse KQL database (`PRGOperations`) contains operational data for Prague Václav Havel Airport (PRG) from January 2024 to December 2025. The data is synthetic but follows realistic patterns for airport ground operations, crew management, and aircraft maintenance.

This data complements the Lakehouse data source. The key cross-reference is `flight_id`, which links operational records to individual flights in the Lakehouse.

## Table Descriptions

### gate_assignments (~5,000 rows)
Tracks gate allocation and turnaround operations for flights.
- **gate_assignment_id** (int): Primary key
- **flight_id** (int): Links to flights table in Lakehouse
- **gate** (string): Gate identifier, e.g. "A1", "B12", "D5"
- **terminal** (string): Terminal, "T1" (Schengen) or "T2" (non-Schengen)
- **scheduled_start** (datetime): Planned gate occupancy start
- **scheduled_end** (datetime): Planned gate occupancy end
- **actual_start** (datetime): Actual start, null if not started or cancelled
- **actual_end** (datetime): Actual end, null if still occupied or cancelled
- **turnaround_minutes** (int): Time between previous departure and next boarding (30-120 min)
- **status** (string): 'on_time', 'delayed', or 'reassigned'

### crew_rosters (~3,000 rows)
Maps crew members to specific flights with their roles.
- **roster_id** (int): Primary key
- **flight_id** (int): Links to flights table in Lakehouse
- **crew_member_id** (string): Unique crew ID, e.g. "CRW-0042"
- **crew_name** (string): Full name, e.g. "Jan Novák"
- **role** (string): 'captain', 'first_officer', 'purser', or 'cabin_crew'
- **license_number** (string): ATPL license for pilots, null for cabin crew
- **nationality** (string): e.g. "Czech", "German", "British"
- **base_airport** (string): Home base IATA code, e.g. "PRG", "FRA"

### maintenance_events (~2,000 rows)
Aircraft maintenance records including scheduled checks and unscheduled repairs.
- **maintenance_id** (int): Primary key
- **aircraft_type** (string): Aircraft model, e.g. "A320", "B737-800"
- **aircraft_registration** (string): Unique registration, e.g. "OK-TVX"
- **event_type** (string): 'scheduled', 'unscheduled', or 'aog' (Aircraft on Ground)
- **category** (string): 'engine', 'avionics', 'hydraulic', 'structural', 'cabin', 'landing_gear'
- **description** (string): Brief description of maintenance work
- **start_datetime** (datetime): When maintenance began
- **end_datetime** (datetime): When maintenance completed
- **duration_hours** (real): Duration in hours
- **related_flight_id** (int): Links to affected flight in Lakehouse, null if routine
- **resolved** (bool): Whether the issue was fully resolved

## Query Logic (KQL)

### Common Patterns

- Gate utilization: `gate_assignments | summarize count() by gate, terminal | order by count_ desc`
- Average turnaround: `gate_assignments | summarize avg(turnaround_minutes) by terminal`
- Crew flights: `crew_rosters | where role == "captain" | summarize flights=dcount(flight_id) by crew_name | order by flights desc`
- Maintenance by type: `maintenance_events | summarize count() by event_type, category`
- Unresolved issues: `maintenance_events | where resolved == false | order by start_datetime desc`
- AOG events: `maintenance_events | where event_type == "aog" | summarize count() by aircraft_type`

### Filtering

- For captains only: `| where role == "captain"`
- For unscheduled maintenance: `| where event_type == "unscheduled"`
- For specific terminal: `| where terminal == "T1"`
- For delayed gate assignments: `| where status == "delayed"`
- Monthly grouping: `| extend month = startofmonth(scheduled_start) | summarize ... by month`

### Value Formats

- gate: uppercase letter + number, e.g. "A1", "B12", "D5"
- terminal: "T1" or "T2"
- status (gate): lowercase, one of: 'on_time', 'delayed', 'reassigned'
- role: lowercase, one of: 'captain', 'first_officer', 'purser', 'cabin_crew'
- event_type: lowercase, one of: 'scheduled', 'unscheduled', 'aog'
- category: lowercase, one of: 'engine', 'avionics', 'hydraulic', 'structural', 'cabin', 'landing_gear'
- crew_member_id: format "CRW-NNNN"
- base_airport: 3-letter IATA code

### Cross-Reference Note

The `flight_id` column in all three tables references the `flights` table in the **Lakehouse** data source. Direct joins between Eventhouse and Lakehouse are not possible in a single KQL query. For cross-source analysis, use the Ontology data source or answer in two parts.

---
