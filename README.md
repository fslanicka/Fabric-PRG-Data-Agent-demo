# Prague Airport Flight Data — Microsoft Fabric Data Agent Demo

## Overview

A complete demo package for Microsoft Fabric Data Agent featuring realistic flight operations data from Prague Václav Havel Airport (PRG) covering 2024–2025. Includes ~50,000 flights, 40 airlines, 100 connected airports, and daily weather data.

## What's Inside

| Folder | Contents |
|--------|----------|
| `data-model/` | Table schemas, relationships, and sample values |
| `notebooks/` | Fabric Notebook (PySpark) to generate sample data in Lakehouse |
| `agent-config/` | Agent instructions, data source instructions, example queries |
| `setup-guide/` | Step-by-step setup instructions (Lakehouse → Agent → Sharing) |
| `demo-script/` | 20+ demo questions in Czech & English with expected answers |

## Quick Start

### Prerequisites

- Microsoft Fabric workspace with **F2 or higher capacity**
- Fabric admin must enable **Copilot** and **Data Agent** tenant settings
- Contributor or higher role in the workspace

### Steps

1. **Create a Lakehouse** — Follow `setup-guide/01-create-lakehouse.md`
2. **Generate sample data** — Import and run `notebooks/01_generate_flight_data.py`
3. **Configure the Data Agent** — Follow `setup-guide/02-configure-agent.md`
4. **Run the demo** — Use questions from `demo-script/demo-questions.md`

## Data Model Overview

4 tables designed for rich cross-table queries:

```
┌──────────────┐     ┌──────────────┐
│   airlines   │────→│   flights    │←────┌──────────────┐
│  (~40 rows)  │     │ (~50K rows)  │     │   airports   │
└──────────────┘     └──────┬───────┘     │ (~100 rows)  │
                            │             └──────────────┘
                     ┌──────┴───────┐
                     │   weather    │
                     │ (~730 rows)  │
                     └──────────────┘
```

- **flights** — Individual flight records (arrivals & departures) with status, delays, gate, passengers
- **airlines** — Airline reference data with alliance membership
- **airports** — Airport reference data with coordinates and regions
- **weather** — Daily weather at PRG for delay correlation analysis

## Demo Highlights

The demo showcases these Data Agent capabilities:

- **Natural language → SQL**: "Kolik letů bylo v červenci 2024?" / "How many flights were there in July 2024?"
- **Aggregations**: Average delay by airline, monthly flight volumes
- **Cross-table joins**: Delay analysis correlated with weather conditions
- **Time intelligence**: Peak hours, seasonal trends, year-over-year comparisons
- **Business insights**: Worst performing routes, cancellation patterns

## Technologies Used

- Microsoft Fabric Lakehouse (Delta tables)
- PySpark (data generation)
- Microsoft Fabric Data Agent (preview)
- T-SQL compatible queries

## Language

- Agent instructions: English (better agent comprehension)
- Demo questions: Czech + English

## License

This is a demo/sample project. Data is synthetic and does not represent real flight operations.
