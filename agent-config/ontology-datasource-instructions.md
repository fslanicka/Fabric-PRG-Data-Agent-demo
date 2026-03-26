# Ontology Data Source Instructions (Fabric IQ)

> **Copy the content below (between the --- markers) into the "Instructions" field for your Ontology data source in the Fabric Data Agent configuration.**

---

## General Knowledge

This ontology is built in Microsoft Fabric IQ and represents a unified semantic layer for Prague Airport operations. It defines business entities and their relationships across two underlying data stores:
- **Lakehouse** (SQL): flights, airlines, airports, weather
- **Eventhouse** (KQL): gate_assignments, crew_rosters, maintenance_events

The ontology enables graph-based traversals and cross-domain queries that are impossible with a single data source.

## Entity Types

### Flight
Central entity. Represents an individual flight (arrival or departure) at PRG.
- Key: `flight_id`
- Source: Lakehouse → flights table
- Key properties: flight_number, airline_code, flight_type, status, delay_minutes, aircraft_type, passenger_count, scheduled_datetime

### Airline
Reference entity for airline carriers.
- Key: `airline_code`
- Source: Lakehouse → airlines table
- Key properties: airline_name, country, alliance

### Airport
Reference entity for airports connected to Prague.
- Key: `airport_code`
- Source: Lakehouse → airports table
- Key properties: airport_name, city, country, region

### WeatherObservation
Daily weather conditions at Prague Airport.
- Key: `date`
- Source: Lakehouse → weather table
- Key properties: temperature_celsius, condition, visibility_km, precipitation_mm

### GateAssignment
Operational entity for gate allocation and turnaround tracking.
- Key: `gate_assignment_id`
- Source: Eventhouse → gate_assignments table
- Key properties: gate, terminal, turnaround_minutes, status

### CrewMember
Operational entity for crew assignments to flights.
- Key: `roster_id`
- Source: Eventhouse → crew_rosters table
- Key properties: crew_name, role, nationality, base_airport

### MaintenanceEvent
Operational entity for aircraft maintenance records.
- Key: `maintenance_id`
- Source: Eventhouse → maintenance_events table
- Key properties: aircraft_type, event_type, category, duration_hours, resolved

## Relationships

| Relationship | From | To | Description |
|-------------|------|-----|-------------|
| operates | Airline | Flight | An airline operates flights |
| originOf | Airport | Flight | An airport is the origin of departures |
| destinationOf | Airport | Flight | An airport is the destination of arrivals |
| observedOn | WeatherObservation | Flight | Weather on the day a flight operates |
| assignedTo | Flight | GateAssignment | A flight has a gate assignment |
| crewedBy | Flight | CrewMember | A flight has assigned crew members |
| affectedFlight | MaintenanceEvent | Flight | Maintenance affects or was triggered by a flight |
| basedAt | CrewMember | Airport | A crew member's home base airport |

## Query Guidance

### When to use the Ontology (vs. Lakehouse or Eventhouse)
- **Use Ontology** for: relationship traversals, multi-hop queries, cross-domain reasoning (connecting Lakehouse + Eventhouse data), impact analysis, "find all entities connected to X"
- **Use Lakehouse** for: aggregations over flights, airlines, airports, weather; time-series analysis; SQL-style analytics
- **Use Eventhouse** for: operational queries on gate assignments, crew rosters, maintenance events; real-time patterns

### Graph Traversal Patterns
- **Single hop**: "Which airline operates flight OK 456?" → Airline →[operates]→ Flight
- **Multi-hop**: "Which crew flew on delayed flights during storms?" → WeatherObservation[condition='storm'] →[observedOn]→ Flight[status='delayed'] →[crewedBy]→ CrewMember
- **Cross-domain**: "For flights with maintenance issues, what was the gate turnaround?" → MaintenanceEvent →[affectedFlight]→ Flight →[assignedTo]→ GateAssignment
- **Impact analysis**: "Show everything connected to airport LHR within 2 hops" → Airport[LHR] →[originOf/destinationOf]→ Flight →[crewedBy/assignedTo/...]→ related entities

### Aggregation in GQL
When the user asks for counts, averages, or other aggregations through the ontology, add `Support group by in GQL` to the agent instructions to enable this capability.

---
