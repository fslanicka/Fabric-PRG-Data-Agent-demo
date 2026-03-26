# Example Queries for Ontology Data Source (Fabric IQ)

> **These example queries demonstrate the types of graph traversal questions the ontology can answer. Use them as guidance for the Data Agent.**

---

## Single-Hop Relationships

### Question: Which airline operates the most flights?
**Traversal:** Airline →[operates]→ Flight
**Expected:** Count of flights grouped by airline, showing the operates relationship

### Question: What gates are assigned to Ryanair flights?
**Traversal:** Airline[airline_code='FR'] →[operates]→ Flight →[assignedTo]→ GateAssignment
**Expected:** List of gates used by Ryanair flights

---

## Multi-Hop Traversals

### Question: Which crew members flew on delayed flights during storms?
**Traversal:** WeatherObservation[condition='storm'] →[observedOn]→ Flight[status='delayed'] →[crewedBy]→ CrewMember
**Expected:** List of crew members with their roles, flight details, and weather conditions

### Question: Find maintenance events for aircraft that had the most cancellations
**Traversal:** Flight[status='cancelled'] → aircraft_type → MaintenanceEvent
**Expected:** Maintenance history for frequently cancelled aircraft types

### Question: Which captains were on flights affected by unscheduled maintenance?
**Traversal:** MaintenanceEvent[event_type='unscheduled'] →[affectedFlight]→ Flight →[crewedBy]→ CrewMember[role='captain']
**Expected:** List of captains with the maintenance event details

---

## Cross-Domain Reasoning

### Question: For flights delayed due to maintenance, show the crew and weather conditions
**Traversal:** MaintenanceEvent →[affectedFlight]→ Flight[status='delayed'] →[crewedBy]→ CrewMember + Flight →[observedOn⁻¹]→ WeatherObservation
**Expected:** Combined view of maintenance details, crew on affected flights, and weather on those days

### Question: Which airports have the most crew members based there?
**Traversal:** CrewMember →[basedAt]→ Airport
**Expected:** Count of crew members by base airport

### Question: Show all entities connected to London Heathrow within 2 hops
**Traversal:** Airport[airport_code='LHR'] → all relationships → connected entities → their relationships
**Expected:** Flights to/from LHR, crews on those flights, gate assignments, weather, maintenance

---

## Impact Analysis

### Question: What is the blast radius of an AOG event on a B737-800?
**Traversal:** MaintenanceEvent[event_type='aog', aircraft_type='B737-800'] →[affectedFlight]→ Flight →[crewedBy/assignedTo/operates⁻¹/observedOn⁻¹]→ all connected entities
**Expected:** Affected flights, crews grounded, gates freed up, airline impact

### Question: If Prague has a storm, what is affected?
**Traversal:** WeatherObservation[condition='storm'] →[observedOn]→ Flight → all downstream relationships
**Expected:** Flights delayed/cancelled, crews affected, gates reassigned, airlines impacted, maintenance triggered

---

## Comparison with SQL/KQL

### Question: How many flights does Czech Airlines operate? (same question, 3 approaches)
- **SQL (Lakehouse):** `SELECT COUNT(*) FROM flights WHERE airline_code = 'OK'`
- **KQL (Eventhouse):** N/A — flight data not in Eventhouse
- **Ontology:** Airline[airline_code='OK'] →[operates]→ Flight → count

### Question: Average turnaround time at gate A5 (same question, 3 approaches)
- **SQL (Lakehouse):** N/A — gate assignment data not in Lakehouse
- **KQL (Eventhouse):** `gate_assignments | where gate == "A5" | summarize avg(turnaround_minutes)`
- **Ontology:** GateAssignment[gate='A5'] → turnaround_minutes → average
