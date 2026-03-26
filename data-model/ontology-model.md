# Ontology Model — Prague Airport Operations (Fabric IQ)

## Overview

This ontology defines the semantic model for Prague Airport operations within Microsoft Fabric IQ. It creates a unified business vocabulary across two data stores (Lakehouse + Eventhouse), enabling graph-based reasoning, multi-hop traversals, and cross-domain analytics through a single semantic layer.

## Architecture

```
Ontology (Fabric IQ)
├── Binds to Lakehouse (SQL Endpoint)
│   ├── flights      → Flight entity type
│   ├── airlines     → Airline entity type
│   ├── airports     → Airport entity type
│   └── weather      → WeatherObservation entity type
│
└── Binds to Eventhouse (KQL Database)
    ├── gate_assignments    → GateAssignment entity type
    ├── crew_rosters        → CrewMember entity type
    └── maintenance_events  → MaintenanceEvent entity type
```

## Entity Types

### 1. Flight

The central entity representing an individual flight event (arrival or departure).

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| flight_id | Integer | ✅ PK | Lakehouse → flights.flight_id |
| flight_number | String | | flights.flight_number |
| airline_code | String | | flights.airline_code |
| flight_type | String | | flights.flight_type |
| origin_airport_code | String | | flights.origin_airport_code |
| destination_airport_code | String | | flights.destination_airport_code |
| scheduled_datetime | DateTime | | flights.scheduled_datetime |
| actual_datetime | DateTime | | flights.actual_datetime |
| status | String | | flights.status |
| delay_minutes | Integer | | flights.delay_minutes |
| delay_reason | String | | flights.delay_reason |
| terminal | String | | flights.terminal |
| gate | String | | flights.gate |
| aircraft_type | String | | flights.aircraft_type |
| passenger_count | Integer | | flights.passenger_count |

**Data Source:** Lakehouse → `flights` table

### 2. Airline

Reference entity for airline carriers.

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| airline_code | String | ✅ PK | Lakehouse → airlines.airline_code |
| airline_name | String | | airlines.airline_name |
| country | String | | airlines.country |
| alliance | String | | airlines.alliance |

**Data Source:** Lakehouse → `airlines` table

### 3. Airport

Reference entity for airports connected to Prague.

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| airport_code | String | ✅ PK | Lakehouse → airports.airport_code |
| airport_name | String | | airports.airport_name |
| city | String | | airports.city |
| country | String | | airports.country |
| region | String | | airports.region |
| latitude | Double | | airports.latitude |
| longitude | Double | | airports.longitude |

**Data Source:** Lakehouse → `airports` table

### 4. WeatherObservation

Daily weather conditions at Prague Airport.

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| weather_id | String | ✅ PK | Lakehouse → weather.weather_id |
| date | Date | | Lakehouse → weather.date |
| temperature_celsius | Double | | weather.temperature_celsius |
| wind_speed_kmh | Double | | weather.wind_speed_kmh |
| visibility_km | Double | | weather.visibility_km |
| precipitation_mm | Double | | weather.precipitation_mm |
| condition | String | | weather.condition |

**Data Source:** Lakehouse → `weather` table

### 5. GateAssignment

Operational entity tracking gate allocation for flights.

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| gate_assignment_id | Integer | ✅ PK | Eventhouse → gate_assignments.gate_assignment_id |
| flight_id | Integer | | gate_assignments.flight_id |
| gate | String | | gate_assignments.gate |
| terminal | String | | gate_assignments.terminal |
| scheduled_start | DateTime | | gate_assignments.scheduled_start |
| scheduled_end | DateTime | | gate_assignments.scheduled_end |
| actual_start | DateTime | | gate_assignments.actual_start |
| actual_end | DateTime | | gate_assignments.actual_end |
| turnaround_minutes | Integer | | gate_assignments.turnaround_minutes |
| status | String | | gate_assignments.status |

**Data Source:** Eventhouse → `gate_assignments` table

### 6. CrewMember

Operational entity representing crew members assigned to flights.

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| roster_id | Integer | ✅ PK | Eventhouse → crew_rosters.roster_id |
| flight_id | Integer | | crew_rosters.flight_id |
| crew_member_id | String | | crew_rosters.crew_member_id |
| crew_name | String | | crew_rosters.crew_name |
| role | String | | crew_rosters.role |
| license_number | String | | crew_rosters.license_number |
| nationality | String | | crew_rosters.nationality |
| base_airport | String | | crew_rosters.base_airport |
| roster_datetime | DateTime | | crew_rosters.roster_datetime (timeseries timestamp) |

**Data Source:** Eventhouse → `crew_rosters` table

### 7. MaintenanceEvent

Operational entity for aircraft maintenance activities.

| Property | Type | Key | Bound To |
|----------|------|-----|----------|
| maintenance_id | Integer | ✅ PK | Eventhouse → maintenance_events.maintenance_id |
| aircraft_type | String | | maintenance_events.aircraft_type |
| aircraft_registration | String | | maintenance_events.aircraft_registration |
| event_type | String | | maintenance_events.event_type |
| category | String | | maintenance_events.category |
| description | String | | maintenance_events.description |
| start_datetime | DateTime | | maintenance_events.start_datetime |
| end_datetime | DateTime | | maintenance_events.end_datetime |
| duration_hours | Double | | maintenance_events.duration_hours |
| related_flight_id | Integer | | maintenance_events.related_flight_id |
| resolved | Boolean | | maintenance_events.resolved |

**Data Source:** Eventhouse → `maintenance_events` table

## Relationship Types

> **Note:** Relationship bindings in Fabric IQ Ontology only support **Lakehouse tables** (preview limitation). Relationships 4-8 use lightweight bridge tables (`rel_weather_flight`, `rel_flight_gate`, `rel_flight_crew`, `rel_flight_maintenance`, `rel_crew_airport`) written to the Lakehouse by Notebook 02.

| # | Name | Source Entity | Target Entity | Source Data Table (Lakehouse) | Source → Source Key | Source → Target Key | Cardinality | Description |
|---|------|--------------|---------------|-------------------------------|---------------------|---------------------|-------------|-------------|
| 1 | operates | Airline | Flight | flights | airline_code | flight_id | 1:N | An airline operates many flights |
| 2 | originOf | Airport | Flight | flights | airport_code | flight_id | 1:N | An airport is the origin of many departures |
| 3 | destinationOf | Airport | Flight | flights | airport_code | flight_id | 1:N | An airport is the destination of many arrivals |
| 4 | observedOn | WeatherObservation | Flight | rel_weather_flight | weather_id | flight_id | 1:N | Weather observed on the day a flight operates |
| 5 | assignedTo | Flight | GateAssignment | rel_flight_gate | flight_id | gate_assignment_id | 1:1 | A flight is assigned to one gate slot |
| 6 | crewedBy | Flight | CrewMember | rel_flight_crew | flight_id | roster_id | 1:N | A flight has multiple crew members |
| 7 | affectedFlight | MaintenanceEvent | Flight | rel_flight_maintenance | related_flight_id | maintenance_id | N:1 | A maintenance event may affect a specific flight |
| 8 | basedAt | CrewMember | Airport | rel_crew_airport | base_airport | roster_id | N:1 | A crew member is based at an airport |

### Relationship Binding Details

**1. operates** (Airline → Flight)
- Source data table: `flights` (Lakehouse)
- Source entity (Airline) column: `airline_code` → matches `airlines.airline_code`
- Target entity (Flight) column: `flight_id` → matches `flights.flight_id`

**2. originOf** (Airport → Flight)
- Source data table: `flights` (Lakehouse)
- Source entity (Airport) column: `origin_airport_code` → matches `airports.airport_code`
- Target entity (Flight) column: `flight_id`
- Filter: Only applies to flights where the airport is the origin

**3. destinationOf** (Airport → Flight)
- Source data table: `flights` (Lakehouse)
- Source entity (Airport) column: `destination_airport_code` → matches `airports.airport_code`
- Target entity (Flight) column: `flight_id`
- Filter: Only applies to flights where the airport is the destination

**4. observedOn** (WeatherObservation → Flight)
- Source data table: `rel_weather_flight` (Lakehouse bridge table)
- Source entity (WeatherObservation) column: `weather_id` → matches `weather.weather_id`
- Target entity (Flight) column: `flight_id`

**5. assignedTo** (Flight → GateAssignment)
- Source data table: `rel_flight_gate` (Lakehouse bridge table)
- Source entity (Flight) column: `flight_id`
- Target entity (GateAssignment) column: `gate_assignment_id`

**6. crewedBy** (Flight → CrewMember)
- Source data table: `rel_flight_crew` (Lakehouse bridge table)
- Source entity (Flight) column: `flight_id`
- Target entity (CrewMember) column: `roster_id`

**7. affectedFlight** (MaintenanceEvent → Flight)
- Source data table: `rel_flight_maintenance` (Lakehouse bridge table)
- Source entity (MaintenanceEvent) column: `related_flight_id`
- Target entity (Flight) column: `maintenance_id`
- Note: Only applies where `related_flight_id IS NOT NULL`

**8. basedAt** (CrewMember → Airport)
- Source data table: `rel_crew_airport` (Lakehouse bridge table)
- Source entity (CrewMember) column: `base_airport` → matches `airports.airport_code`
- Target entity (Airport) column: `roster_id`

## Graph Visualization

When the ontology is published, the graph view displays:

```
                        ┌──────────┐
                        │ Airline  │
                        └────┬─────┘
                             │ operates
                             ▼
┌──────────┐  originOf  ┌──────────┐  assignedTo  ┌────────────────┐
│ Airport  │───────────→│  Flight  │─────────────→│ GateAssignment │
│          │←───────────│          │              └────────────────┘
│          │destinationOf│         │  crewedBy    ┌────────────────┐
└──────────┘            │          │─────────────→│  CrewMember    │──basedAt──→ Airport
     ▲                  └────┬─────┘              └────────────────┘
     │                       │
     │                       │ affectedFlight
     │                  ┌────┴──────────────┐
     │                  │ MaintenanceEvent  │
     │                  └───────────────────┘
     │
┌────┴─────────────────┐
│ WeatherObservation   │──observedOn──→ Flight
└──────────────────────┘
```

## Example Graph Traversals

### 1. Multi-hop: Storm → Flight → Crew
*"Which crew members were on flights delayed during storms?"*
```
WeatherObservation[condition='storm'] 
  → observedOn → Flight[status='delayed'] 
    → crewedBy → CrewMember
```

### 2. Root Cause: Maintenance → Flight → Delay
*"Were delayed flights caused by unscheduled maintenance?"*
```
MaintenanceEvent[event_type='unscheduled'] 
  → affectedFlight → Flight[status='delayed']
```

### 3. Operational Chain: Airline → Flight → Gate → Turnaround
*"What is the average turnaround time for Ryanair flights?"*
```
Airline[airline_code='FR'] 
  → operates → Flight 
    → assignedTo → GateAssignment[turnaround_minutes]
```

### 4. Cross-domain: Crew → Flight → Weather + Maintenance
*"For captain Jan Novák, show flights with bad weather or maintenance issues"*
```
CrewMember[crew_name='Jan Novák', role='captain'] 
  ← crewedBy ← Flight
    → observedOn⁻¹ → WeatherObservation[condition IN ('storm','fog','snow')]
    ← affectedFlight ← MaintenanceEvent
```

### 5. Impact Analysis: Airport → Flights → Gate + Crew + Weather
*"Show all entities connected to London Heathrow within 2 hops"*
```
Airport[airport_code='LHR'] 
  → originOf/destinationOf → Flight 
    → assignedTo → GateAssignment
    → crewedBy → CrewMember
    → observedOn⁻¹ → WeatherObservation
```
