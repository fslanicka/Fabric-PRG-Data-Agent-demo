# Demo Script — Fabric IQ: Multi-Source Data Agent

> This script contains ~20 demo questions showcasing the extended Data Agent with three data sources:
> Lakehouse (SQL), Eventhouse (KQL), and Ontology (Graph/GQL).
> All questions are in English.
> Use these alongside the original `demo-questions.md` for a comprehensive presentation.

---

## 🎯 How to Use This Script

1. Complete the basic demo from `demo-questions.md` first (Lakehouse only)
2. Then transition to this script: "Now let's add operational intelligence..."
3. Questions progress from single-source to cross-source reasoning
4. The script demonstrates why multiple data sources and ontology matter

---

## Category A: Eventhouse / KQL Queries (Operational Data)

> These questions target the Eventhouse KQL database. The agent translates natural language to KQL.

### Q-A1 — Gate Utilization
> **Demonstrates**: KQL aggregation on Eventhouse data

*"Which gates at the airport have the most assignments? Show top 10 by terminal."*

**Expected**: Table with gate, terminal, assignment count. Gates A1-A15 (T1) and D1-D15 (T2) distributed across flights.

---

### Q-A2 — Average Turnaround Time
> **Demonstrates**: KQL summarize with avg()

*"What is the average turnaround time by terminal?"*

**Expected**: T1 and T2 averages, typically 60-90 minutes. T2 (long-haul) may show longer turnarounds.

---

### Q-A3 — Gate Reassignments
> **Demonstrates**: KQL filtering on status

*"How many gate assignments were delayed or reassigned? What percentage does each status represent?"*

**Expected**: ~75% on_time, ~20% delayed, ~5% reassigned

---

### Q-A4 — Top Captains by Flights
> **Demonstrates**: KQL distinct count with role filter

*"Which captains flew the most flights? Show top 10 with flight count."*

**Expected**: List of captain names with their total flights, showing crew utilization patterns.

---

### Q-A5 — Crew Nationality Distribution
> **Demonstrates**: KQL aggregation on categorical data

*"What is the nationality distribution of crew members?"*

**Expected**: Czech dominates (~60%+), followed by German, British, French, etc.

---

### Q-A6 — Maintenance by Aircraft Type
> **Demonstrates**: KQL multi-column summarize

*"Which aircraft types have the most unscheduled maintenance events? Show event count and average duration."*

**Expected**: Common types (A320, B737-800) have more events. Average duration varies by type.

---

### Q-A7 — AOG Events
> **Demonstrates**: KQL filtering critical events

*"How many Aircraft on Ground (AOG) events occurred? Show by aircraft type with total downtime hours."*

**Expected**: ~5% of maintenance events, concentrated on specific aircraft types. AOG has longest duration.

---

### Q-A8 — Seasonal Maintenance Patterns
> **Demonstrates**: KQL time-series with startofmonth()

*"Show the monthly trend of maintenance events. Are there seasonal patterns?"*

**Expected**: More unscheduled events in winter months (Dec-Feb), more scheduled in summer (higher utilization).

---

## Category B: Ontology / Graph Traversals

> These questions use the Ontology data source for graph-based reasoning across entity types.

### Q-B1 — Entity Overview
> **Demonstrates**: Ontology awareness

*"What entity types exist in the ontology and how are they connected?"*

**Expected**: List of 7 entity types (Flight, Airline, Airport, WeatherObservation, GateAssignment, CrewMember, MaintenanceEvent) with relationship descriptions.

---

### Q-B2 — Single-Hop: Airline → Flights
> **Demonstrates**: Basic relationship traversal

*"Show all relationships for Czech Airlines (OK). How many flights do they operate?"*

**Expected**: Airline entity with operates relationship to Flight entities. Count of OK flights.

---

### Q-B3 — Multi-Hop: Weather → Flight → Crew
> **Demonstrates**: 2-hop graph traversal across Lakehouse + Eventhouse

*"Which crew members were on flights that operated during storm conditions?"*

**Expected**: List of crew members (with roles) connected through: WeatherObservation[storm] → Flight → CrewMember

---

### Q-B4 — Multi-Hop: Maintenance → Flight → Airline
> **Demonstrates**: Cross-domain reasoning

*"Find airlines whose flights were affected by unscheduled maintenance. Which airline had the most affected flights?"*

**Expected**: MaintenanceEvent[unscheduled] → Flight → Airline aggregation

---

### Q-B5 — Impact Analysis: Airport Connections
> **Demonstrates**: Graph exploration, connected entities

*"Show all entities connected to London Heathrow (LHR) within 2 hops."*

**Expected**: Flights to/from LHR, airlines operating those flights, crews assigned, gate assignments, weather on flight days.

---

### Q-B6 — Path Finding: Maintenance → Crew
> **Demonstrates**: Multi-hop path through Flight entity

*"Which captains were on flights that had Aircraft on Ground (AOG) maintenance events?"*

**Expected**: MaintenanceEvent[aog] → Flight → CrewMember[captain] with names and flight details.

---

## Category C: Cross-Source Reasoning

> These questions require the agent to combine data from multiple sources or demonstrate the ontology's unifying power.

### Q-C1 — Combined Analysis: Maintenance + Weather + Delay
> **Demonstrates**: 3-way cross-source reasoning

*"For flights that were delayed and had a related maintenance event, what were the weather conditions on those days?"*

**Expected**: Combined view showing flight details (Lakehouse), maintenance info (Eventhouse), and weather (Lakehouse) — connected through the ontology.

---

### Q-C2 — Operational Readiness
> **Demonstrates**: Multi-table operational query

*"Give me an operational summary: How many flights, gate assignments, crew assignments, and maintenance events are in the system? Break down by key status categories."*

**Expected**: Summary combining data from all three sources — flight status distribution, gate assignment status, crew role counts, maintenance event types.

---

### Q-C3 — Crew and Gate for Delayed Flights
> **Demonstrates**: Eventhouse-to-Lakehouse cross-reference

*"For the flights with the longest delays, show their gate assignment details and crew information."*

**Expected**: Top delayed flights (from Lakehouse) with gate turnaround and crew details (from Eventhouse).

---

## Category D: Source Comparison

> Ask the same question through different sources to show query approach differences.

### Q-D1 — Same Question, Different Source
> **Demonstrates**: SQL vs KQL vs Graph approaches

Ask this question **three times**, specifying the source each time:

1. *"Using the Lakehouse: How many flights does Ryanair (FR) operate?"*
2. *"Using the Eventhouse: What is the average turnaround for Ryanair flights?"*
   (Note: This requires knowing FR's flight_ids, which the agent may need to look up)
3. *"Using the Ontology: Show everything connected to Ryanair — flights, crews, gates, maintenance."*

**Expected**: Three different query types (SQL, KQL, Graph traversal) showing complementary capabilities.

---

### Q-D2 — Why Ontology Matters
> **Demonstrates**: The value of unified semantic layer

*"Can you trace the full chain: Which airline had the most cancelled flights, what maintenance events affected those flights, and which crew members were assigned?"*

**Expected**: This requires connecting Lakehouse (flights, airlines) + Eventhouse (maintenance, crew) — only possible through the ontology graph or multi-step reasoning.

---

## 🎬 Recommended Demo Flow

### Full Demo (~30 minutes, includes original questions)
1. **Lakehouse basics** (Q1-Q5 from original demo) — establish SQL capability
2. **Eventhouse introduction** (Q-A1, Q-A4, Q-A6) — show KQL on operational data
3. **Ontology traversals** (Q-B1, Q-B3, Q-B5) — demonstrate graph power
4. **Cross-source finale** (Q-C1, Q-D2) — show unified intelligence

### Fabric IQ Focus (~15 minutes, this script only)
1. **Operational data** (Q-A2, Q-A6) — Eventhouse/KQL
2. **Graph reasoning** (Q-B3, Q-B4) — Ontology traversals
3. **Cross-source** (Q-C1) — combined intelligence
4. **Comparison** (Q-D1) — why multi-source matters
5. **Grand finale** (Q-D2) — full chain traversal

### Quick Demo (~5 minutes)
Q-A4 → Q-B3 → Q-C1 → Q-D2

---

## 💡 Tips for Presenters

- **Start by showing the ontology graph visualization** in Fabric IQ before querying — this gives the audience a mental model
- **Highlight the data source indicator** in the agent's response — it shows which source (SQL/KQL/Graph) was used
- **When a cross-source question fails**, explain that this is exactly why the ontology matters — it bridges the gap
- **Show the same question via Lakehouse, Eventhouse, and Ontology** to demonstrate complementary strengths
- **If graph queries are slow**, explain that ontology is in preview and performance is improving
