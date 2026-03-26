# Step 2b: Configure Fabric IQ Ontology

## Prerequisites

- Completed Step 1 (Lakehouse with flight data)
- Completed Step 1b (Eventhouse with operational data)
- Fabric admin has enabled **Fabric IQ** and **Graph** in tenant settings:
  - Admin Portal → Tenant settings → Ontology → Enable
  - Admin Portal → Tenant settings → Graph → Enable

## 2b.1 Create an Ontology Item

1. In your Fabric workspace, click **+ New item**
2. Search for and select **Ontology (preview)**
3. Name it: `PRGAirportOntology`
4. Click **Create**

> **Tip**: Ontology names can include numbers, letters, and underscores. Don't use spaces or dashes.

## 2b.2 Create Entity Types — Lakehouse Bindings

Create the following entity types with data bindings to the **PRGFlightData Lakehouse**:

### Flight Entity Type

1. Select **Add entity type** from the ribbon
2. Name: `Flight`
3. Switch to the **Bindings** tab → **Add data to entity type**
4. Select **PRGFlightData** Lakehouse → `flights` table → **Connect**
5. All columns bind automatically. Select **Save**
6. **Add entity type key**: Select `flight_id`

### Airline Entity Type

1. **Add entity type** → Name: `Airline`
2. Bind to **PRGFlightData** → `airlines` table
3. **Entity type key**: `airline_code`

### Airport Entity Type

1. **Add entity type** → Name: `Airport`
2. Bind to **PRGFlightData** → `airports` table
3. **Entity type key**: `airport_code`

### WeatherObservation Entity Type

1. **Add entity type** → Name: `WeatherObservation`
2. Bind to **PRGFlightData** → `weather` table
3. **Entity type key**: `weather_id`

### ⟳ Refresh the Graph

After creating all 4 Lakehouse entity types, refresh the graph so the data is ingested before continuing:

1. Go to your **Fabric workspace** item list
2. Find the **Graph** item (child of `PRGAirportOntology`) → click **⋯** → **Schedule** → **Refresh now**
3. Wait for the refresh to complete

## 2b.3 Create Entity Types — Eventhouse Bindings

Eventhouse entities require **two bindings** in the ontology:
1. **Static binding from Lakehouse** (required first) — provides the entity key and static properties. Without this, the entity type overview shows "missing static binding" and the Graph cannot ingest the entity.
2. **Timeseries binding from Eventhouse** (optional, adds real-time properties) — Fabric forces Timeseries mode for Eventhouse sources.

Notebook 02 writes full copies of the operational data to the Lakehouse (`lkh_gate_assignments`, `lkh_crew_rosters`, `lkh_maintenance_events`) specifically for this purpose.

### GateAssignment Entity Type

1. **Add entity type** → Name: `GateAssignment`

**Step A — Static binding (Lakehouse):**

2. Switch to **Bindings** tab → **Add data to entity type**
3. Select **PRGFlightData** Lakehouse → `lkh_gate_assignments` table → **Connect**
4. **Binding type**: Static
5. Bind these properties:

   | Source column | Property name |
   |---------------|---------------|
   | gate_assignment_id | gate_assignment_id |
   | flight_id | flight_id |
   | gate | gate |
   | terminal | terminal |
   | turnaround_minutes | turnaround_minutes |
   | status | status |

6. Click **Save**
7. **Entity type key**: `gate_assignment_id`

**Step B — Timeseries binding (Eventhouse, optional):**

8. In the **Bindings** tab → **Add data to entity type** again
9. Select **PRGOperations** KQL database → `gate_assignments` table → **Connect**
10. **Binding type**: Timeseries (forced)
11. **Source data timestamp column**: `scheduled_start`
12. In the **Static** section, bind `gate_assignment_id` to the existing key property
13. **Add Timeseries properties**:

   | Source column | Property name |
   |---------------|---------------|
   | scheduled_start | scheduled_start |
   | scheduled_end | scheduled_end |
   | actual_start | actual_start |
   | actual_end | actual_end |

14. Click **Save**

### CrewMember Entity Type

1. **Add entity type** → Name: `CrewMember`

**Step A — Static binding (Lakehouse):**

2. **Bindings** → **Add data to entity type** → **PRGFlightData** → `lkh_crew_rosters`
3. **Binding type**: Static
4. Bind these properties:

   | Source column | Property name |
   |---------------|---------------|
   | roster_id | roster_id |
   | flight_id | flight_id |
   | crew_member_id | crew_member_id |
   | crew_name | crew_name |
   | role | role |
   | license_number | license_number |
   | nationality | nationality |
   | base_airport | base_airport |

5. Click **Save**
6. **Entity type key**: `roster_id`

**Step B — Timeseries binding (Eventhouse, optional):**

7. **Bindings** → **Add data to entity type** → **PRGOperations** → `crew_rosters`
8. **Binding type**: Timeseries
9. **Source data timestamp column**: `roster_datetime`
10. In the **Static** section, bind `roster_id` to the existing key property
11. **Add Timeseries properties**:

   | Source column | Property name |
   |---------------|---------------|
   | roster_datetime | roster_datetime |

12. Click **Save**

### MaintenanceEvent Entity Type

1. **Add entity type** → Name: `MaintenanceEvent`

**Step A — Static binding (Lakehouse):**

2. **Bindings** → **Add data to entity type** → **PRGFlightData** → `lkh_maintenance_events`
3. **Binding type**: Static
4. Bind these properties:

   | Source column | Property name |
   |---------------|---------------|
   | maintenance_id | maintenance_id |
   | aircraft_type | aircraft_type |
   | aircraft_registration | aircraft_registration |
   | event_type | event_type |
   | category | category |
   | description | description |
   | duration_hours | duration_hours |
   | related_flight_id | related_flight_id |
   | resolved | resolved |

5. Click **Save**
6. **Entity type key**: `maintenance_id`

**Step B — Timeseries binding (Eventhouse, optional):**

7. **Bindings** → **Add data to entity type** → **PRGOperations** → `maintenance_events`
8. **Binding type**: Timeseries
9. **Source data timestamp column**: `start_datetime`
10. In the **Static** section, bind `maintenance_id` to the existing key property
11. **Add Timeseries properties**:

   | Source column | Property name |
   |---------------|---------------|
   | start_datetime | start_datetime |
   | end_datetime | end_datetime |

12. Click **Save**

### ⟳ Refresh the Graph

After creating all 3 Eventhouse entity types, refresh the graph again:

1. Workspace → **Graph** item → **⋯** → **Schedule** → **Refresh now**
2. Wait for the refresh to complete

> **Tip:** The graph does a full re-ingestion each time. It's more efficient to batch all entity type changes before refreshing, as we do here — once after Lakehouse entities and once after Eventhouse entities.

## 2b.4 Create Relationship Types

> **Important:** Relationship bindings in Fabric IQ Ontology only support **Lakehouse tables** as the source data (preview limitation). Eventhouse tables cannot be used. Notebook 02 creates Lakehouse copies of Eventhouse data (`lkh_gate_assignments`, `lkh_crew_rosters`, `lkh_maintenance_events`) and a bridge table (`rel_weather_flight`) specifically for this purpose.

Add the following relationships. For each:
1. Select **Add relationship** from the ribbon
2. Enter the details from the table below
3. Configure the source data table (always from **Lakehouse**) and key columns

| # | Name | Source Entity | Target Entity | Source Data Table (Lakehouse) | Source Key → Source Entity | Source Key → Target Entity |
|---|------|--------------|---------------|-------------------------------|---------------------------|---------------------------|
| 1 | operates | Airline | Flight | `flights` | airline_code | flight_id |
| 2 | originOf | Airport | Flight | `flights` | origin_airport_code | flight_id |
| 3 | destinationOf | Airport | Flight | `flights` | destination_airport_code | flight_id |
| 4 | observedOn | WeatherObservation | Flight | `rel_weather_flight` | weather_id | flight_id |
| 5 | assignedTo | Flight | GateAssignment | `lkh_gate_assignments` | flight_id | gate_assignment_id |
| 6 | crewedBy | Flight | CrewMember | `lkh_crew_rosters` | flight_id | roster_id |
| 7 | affectedFlight | MaintenanceEvent | Flight | `lkh_maintenance_events` | related_flight_id | maintenance_id |
| 8 | basedAt | CrewMember | Airport | `lkh_crew_rosters` | base_airport | roster_id |

### Example: Creating the "operates" relationship

1. Click **Add relationship** from the ribbon
2. Enter:
   - **Relationship type name**: `operates`
   - **Source entity type**: `Airline`
   - **Target entity type**: `Flight`
3. In the **Relationship configuration** pane:
   - **Source data**: Select PRGFlightData Lakehouse → `flights` table
   - **Source entity type (Airline) → Source column**: `airline_code`
   - **Target entity type (Flight) → Source column**: `flight_id`
4. Click **Create**

### Example: Creating the "assignedTo" relationship (bridge table)

1. Click **Add relationship** from the ribbon
2. Enter:
   - **Relationship type name**: `assignedTo`
   - **Source entity type**: `Flight`
   - **Target entity type**: `GateAssignment`
3. In the **Relationship configuration** pane:
   - **Source data**: Select PRGFlightData Lakehouse → `lkh_gate_assignments` table
   - **Source entity type (Flight) → Source column**: `flight_id`
   - **Target entity type (GateAssignment) → Source column**: `gate_assignment_id`
4. Click **Create**

Repeat for all relationships in the table above.

### ⟳ Refresh the Graph

After creating all 8 relationships, do a final graph refresh so that relationship edges are visible:

1. Workspace → **Graph** item → **⋯** → **Schedule** → **Refresh now**
2. Wait for the refresh to complete
3. This is the most important refresh — it makes relationships visible in the graph view

## 2b.5 Verify the Ontology (after final refresh)

### View entity type overview

1. Open the `PRGAirportOntology` ontology item
2. In the **Entity Types** pane on the left, select an entity type (e.g., `Flight`)
3. Click **Entity type overview** in the ribbon
4. The preview experience opens showing:
   - **Entity instances** table with bound data
   - Any auto-generated tiles (timeseries charts, static property charts)

5. Verify entity instance counts:
   - Flight: ~105,000+ instances
   - Airline: ~40 instances
   - Airport: ~100 instances
   - WeatherObservation: ~730 instances
   - GateAssignment: ~5,000 instances
   - CrewMember: ~3,000 instances (roster entries)
   - MaintenanceEvent: ~2,000 instances

### Explore the graph view

1. In the entity type overview, find a **Graph tile** (or add one via **+ Add Tile** → **Fabric graph**)
2. Click **Expand** on the graph tile to open the full graph view
3. You should see nodes for entity types and edges for relationships
4. Use the **Query builder** ribbon to run queries:
   - The default query shows the current entity and all relationships one hop away
   - Click **Run query** to see matching instances
   - Use **Add filters** to filter by property values
   - Switch between **Diagram**, **Card**, and **Table** views for results

### Explore a specific entity instance

1. In the entity type overview, click a row in the **Entity instances** table
2. The instance view shows properties and relationship details for that specific entity
3. Click **Expand** on the graph tile to see this instance's neighborhood in the graph

### Open in Fabric Graph (advanced)

For more complex exploration, click **Open in Fabric Graph** in the graph view to use the full Graph in Microsoft Fabric interface.

## 2b.6 Set Up Recurring Refresh (Optional)

If you plan to re-run the data generation notebooks or add new data, set up automatic graph refresh:

1. Workspace → **Graph** item → **⋯** → **Schedule**
2. Toggle **Scheduled refresh** to **On**
3. Configure the refresh frequency (e.g., daily, hourly) based on how often your source data changes
4. Click **Apply**

> **Why?** The ontology graph does **not** automatically detect changes in upstream data sources. Without a refresh (manual or scheduled), the graph displays stale data. Schema changes within the ontology editor (adding/editing entity types, properties, relationships) do trigger an automatic refresh, but data changes in Lakehouse or Eventhouse tables do not.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ontology item not available | Enable Fabric IQ in Admin Portal → Tenant settings |
| Graph not showing | Enable Graph in Admin Portal → Tenant settings. The Graph item appears in your workspace as a child of the ontology — look there, not inside the ontology editor |
| No entity instances | Refresh the Graph item: workspace → Graph item → **⋯** → **Schedule** → **Refresh now**. Then verify data bindings in the ontology |
| Missing relationships | Check that source data tables and key columns are correct |
| Eventhouse bindings fail | Ensure Eventhouse is in the same workspace or has proper permissions |
| Eventhouse binding type is only "Timeseries" | This is expected — Eventhouse sources always use Timeseries binding. But each entity type also needs a **static binding from a Lakehouse table first**. See section 2b.3 — bind the `lkh_*` Lakehouse tables (Step A) before adding the Eventhouse timeseries binding (Step B). |
| "Missing static binding" in Entity type overview | The entity type has only a Timeseries binding (Eventhouse) but no Static binding (Lakehouse). Add a static binding from the corresponding `lkh_*` table first. |
| `crew_rosters` timestamp column | Use `roster_datetime` — it contains the flight's scheduled datetime, added specifically for the Timeseries binding |
| Entity type key not available for DATE columns | Ontology only offers STRING-type columns as entity keys. Use a string ID column (e.g., `weather_id`) instead of DATE/datetime columns |

## Next Step

→ Proceed to [02-configure-agent.md](02-configure-agent.md) (updated with Ontology data source step)
