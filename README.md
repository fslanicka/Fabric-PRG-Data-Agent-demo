# Prague Airport Operations — Microsoft Fabric IQ & Data Agent Demo

## Overview

A complete demo package for **Microsoft Fabric Data Agent** with **Fabric IQ** (Ontology) featuring realistic flight and operational data from Prague Václav Havel Airport (PRG) covering 2024–2025. Demonstrates a **triple-source Data Agent** with Lakehouse (SQL), Eventhouse (KQL), and Ontology (Graph/GQL) — showcasing multi-source intelligence, graph-based reasoning, and cross-domain analytics.

Includes ~105,000 flights, 40 airlines, 100 airports, daily weather, ~5,000 gate assignments, ~3,000 crew roster entries, and ~2,000 maintenance events.

## What's Inside

| Folder | Contents |
|--------|----------|
| `data-model/` | Table schemas (Lakehouse + Eventhouse), ontology model, relationships |
| `notebooks/` | Fabric Notebooks — flight data (Lakehouse) + operational data (Eventhouse) |
| `agent-config/` | Agent instructions, 3× data source configs (Lakehouse, Eventhouse, Ontology), example queries |
| `setup-guide/` | Step-by-step setup (Lakehouse → Eventhouse → Ontology → Agent → Sharing) |
| `demo-script/` | 40+ demo questions: Lakehouse (CZ+EN), Fabric IQ (EN) with expected answers |

## Quick Start

### Prerequisites

- Microsoft Fabric workspace with **F2 or higher capacity**
- Fabric admin must enable these tenant settings:
  - **Copilot** and **Data Agent**
  - **Fabric IQ** (for Ontology)
  - **Graph** (for ontology graph visualization)
  - **Real-Time Intelligence** (for Eventhouse)
- Contributor or higher role in the workspace

### Steps

1. **Create a Lakehouse** — Follow `setup-guide/01-create-lakehouse.md`
2. **Generate flight data** — Import and run `notebooks/01_generate_flight_data.py`
3. **Create an Eventhouse** — Follow `setup-guide/01b-create-eventhouse.md`
4. **Generate operational data** — Import and run `notebooks/02_generate_operational_data.py`
5. **Configure Fabric IQ Ontology** — Follow `setup-guide/02b-configure-ontology.md`
6. **Configure the Data Agent** — Follow `setup-guide/02-configure-agent.md` (3 data sources)
7. **Run the demo** — Start with `demo-script/demo-questions.md`, then `demo-script/demo-questions-fabric-iq.md`

## Data Model Overview

7 tables across 2 data stores, unified by a Fabric IQ Ontology:

```
 Lakehouse (SQL)                              Eventhouse (KQL)
┌──────────────┐     ┌──────────────┐        ┌───────────────────┐
│   airlines   │────→│   flights    │←──────→│ gate_assignments  │
│  (~40 rows)  │     │ (~50K rows)  │        │   (~5K rows)      │
└──────────────┘     └──────┬───────┘←──────→├───────────────────┤
                            │        ←──────→│  crew_rosters     │
┌──────────────┐     ┌──────┴───────┐        │   (~3K rows)      │
│   airports   │────→│   flights    │        ├───────────────────┤
│ (~100 rows)  │     └──────┬───────┘←──────→│maintenance_events │
└──────────────┘            │                │   (~2K rows)      │
                     ┌──────┴───────┐        └───────────────────┘
                     │   weather    │
                     │ (~730 rows)  │                  ▲
                     └──────────────┘                  │
                            ▲                          │
                            │    ┌─────────────────┐   │
                            └────│   Ontology      │───┘
                                 │  (Fabric IQ)    │
                                 │ 7 entity types  │
                                 │ 8 relationships │
                                 └─────────────────┘
```

### Lakehouse Tables (SQL)
- **flights** — Individual flight records (arrivals & departures) with status, delays, gate, passengers
- **airlines** — Airline reference data with alliance membership
- **airports** — Airport reference data with coordinates and regions
- **weather** — Daily weather at PRG for delay correlation analysis

### Eventhouse Tables (KQL)
- **gate_assignments** — Gate allocation with turnaround times and status tracking
- **crew_rosters** — Crew member assignments to flights with roles and nationalities
- **maintenance_events** — Aircraft maintenance records (scheduled, unscheduled, AOG)

### Ontology (Fabric IQ)
- 7 entity types: Flight, Airline, Airport, WeatherObservation, GateAssignment, CrewMember, MaintenanceEvent
- 8 relationships enabling graph traversals across both data stores

## Demo Highlights

The demo showcases these Data Agent and Fabric IQ capabilities:

### Lakehouse (NL → SQL)
- **Natural language → SQL**: "Kolik letů bylo v červenci 2024?" / "How many flights were there in July 2024?"
- **Aggregations**: Average delay by airline, monthly flight volumes
- **Cross-table joins**: Delay analysis correlated with weather conditions
- **Time intelligence**: Peak hours, seasonal trends, year-over-year comparisons

### Eventhouse (NL → KQL)
- **Natural language → KQL**: "What is the average turnaround time by terminal?"
- **Operational analytics**: Gate utilization, crew scheduling, maintenance patterns
- **Real-time patterns**: AOG events, unscheduled maintenance, gate reassignments

### Ontology (NL → Graph/GQL)
- **Graph traversals**: "Which crew members flew on delayed flights during storms?"
- **Multi-hop reasoning**: Airline → Flight → Maintenance → Resolution chain
- **Cross-domain analysis**: Connecting Lakehouse + Eventhouse data through entity relationships
- **Impact analysis**: "Show all entities connected to London Heathrow within 2 hops"

## Technologies Used

- Microsoft Fabric Lakehouse (Delta tables) — flight analytics data
- Microsoft Fabric Eventhouse / KQL Database — operational data
- Microsoft Fabric IQ — Ontology (preview) — unified semantic layer
- Microsoft Fabric Graph (preview) — entity relationship graph
- Microsoft Fabric Data Agent (preview) — conversational AI
- PySpark + NumPy (data generation)
- T-SQL, KQL, GQL — three query languages

## Language

- Agent instructions: English (better agent comprehension)
- Demo questions (Lakehouse): Czech + English
- Demo questions (Fabric IQ): English only

## License

This is a demo/sample project. Data is synthetic and does not represent real flight operations.
