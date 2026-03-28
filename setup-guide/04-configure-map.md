# Step 4: Configure Fabric Maps

## Overview

This step adds a **Fabric Maps** visualization to the demo, displaying Prague Airport's flight network, crew distribution, and maintenance data on an interactive map. Fabric Maps uses data from the Eventhouse KQL database to render geographic layers.

## Prerequisites

- Completed Step 1b (Eventhouse with operational data **including airports table** from Notebook 02, CELL 10)
- Microsoft Fabric workspace with **F2 or higher** capacity
- Fabric admin must enable these tenant settings:
  - **Map** — Admin Portal → Tenant settings → search "Map"
  - **Azure Maps services** — If your Fabric capacity is outside EU/US, enable the "Data sent to Azure Maps can be processed outside your capacity's geography region" setting

> **Note**: The airports reference table must exist in the Eventhouse before creating map functions. Verify by running `airports | count` in the KQL query editor — it should return ~100 rows. If it's missing, re-run Notebook 02 (CELL 10 writes the airports table).

## 4.1 Create KQL Stored Functions

KQL stored functions provide map-ready data to Fabric Maps. Each function returns rows with `latitude` and `longitude` columns.

> **Important**: Use stored functions (not KQL querysets). KQL querysets are deprecated and will stop working after June 2026.

1. Open the `PRGOperations` KQL database
2. Click **Explore your data** (or open the KQL query editor)
3. Run each function definition from `agent-config/kql-map-functions.kql`:

### Function 1: fn_destination_map

Shows all airports connected to Prague as map markers.

```kql
.create-or-alter function with (folder="FabricMaps", docstring="All airports connected to Prague — marker layer for Fabric Maps") fn_destination_map() {
    airports
    | where airport_code != "PRG"
    | project
        airport_code,
        airport_name,
        city,
        country,
        region,
        latitude,
        longitude
}
```

**Verify**: Run `fn_destination_map() | count` — should return ~99 rows.

### Function 2: fn_crew_base_distribution

Shows crew member distribution across base airports.

```kql
.create-or-alter function with (folder="FabricMaps", docstring="Crew member distribution by base airport for map visualization") fn_crew_base_distribution() {
    crew_rosters
    | summarize
        crew_count = dcount(crew_member_id),
        captain_count = dcountif(crew_member_id, role == "captain"),
        first_officer_count = dcountif(crew_member_id, role == "first_officer"),
        purser_count = dcountif(crew_member_id, role == "purser"),
        cabin_crew_count = dcountif(crew_member_id, role == "cabin_crew"),
        flights_covered = dcount(flight_id)
        by base_airport
    | join kind=inner (airports) on $left.base_airport == $right.airport_code
    | project
        base_airport,
        airport_name,
        city,
        country,
        region,
        latitude,
        longitude,
        crew_count,
        captain_count,
        first_officer_count,
        purser_count,
        cabin_crew_count,
        flights_covered
    | order by crew_count desc
}
```

**Verify**: Run `fn_crew_base_distribution() | count` — should return ~30-50 rows.

### Function 3: fn_maintenance_at_prg

Shows maintenance event summary at Prague Airport.

```kql
.create-or-alter function with (folder="FabricMaps", docstring="Maintenance events summary at Prague Airport for map visualization") fn_maintenance_at_prg() {
    let prg_lat = real(50.1008);
    let prg_lon = real(14.2600);
    maintenance_events
    | summarize
        total_events = count(),
        scheduled_count = countif(event_type == "scheduled"),
        unscheduled_count = countif(event_type == "unscheduled"),
        aog_count = countif(event_type == "aog"),
        avg_duration_hours = round(avg(duration_hours), 1),
        unresolved_count = countif(resolved == false),
        categories = make_set(category)
        by aircraft_type
    | extend
        latitude = prg_lat,
        longitude = prg_lon,
        airport = "PRG",
        airport_name = "Prague Václav Havel Airport"
}
```

**Verify**: Run `fn_maintenance_at_prg() | count` — should return ~10-15 rows (one per aircraft type).

4. After running all three, verify functions are listed: `.show functions | where Folder == "FabricMaps"`

## 4.2 Create a Map Item

1. In your Fabric workspace, click **+ New item**
2. Search for **Map** and select it
3. Name it: `PRG Airport Operations Map`
4. Click **Create**
5. An empty map canvas opens

## 4.3 Add Map Layers

### Layer 1: Destination Airports (Bubble Markers)

1. In the map editor, click **+ Add layer** (or the **Add data** button)
2. Select **Eventhouse** as the data source type
3. Navigate to **PRGOperations** KQL database
4. Under **Functions**, select `fn_destination_map`
5. In the layer configuration wizard:
   - **Preview**: Verify the data shows airport rows with lat/lon
   - **Latitude column**: `latitude`
   - **Longitude column**: `longitude`
   - **Refresh interval**: Set to manual (static data) or a suitable interval
6. Click **Add** to create the layer
7. Configure the layer:
   - **Layer name**: `Destination Airports`
   - **Layer type**: Marker (bubble)
   - **Style** → **Color**: Use data-driven styling by `region` (different color per region)
   - **Labels**: Enable and set to `airport_code` or `city`
   - **Clustering**: Enable for a cleaner view at lower zoom levels

### Layer 2: Crew Base Distribution (Bubble Markers)

1. Click **+ Add layer** again
2. Select **Eventhouse** → **PRGOperations** → **Functions** → `fn_crew_base_distribution`
3. Configure:
   - **Latitude column**: `latitude`
   - **Longitude column**: `longitude`
4. Click **Add**
5. Configure the layer:
   - **Layer name**: `Crew Bases`
   - **Style** → **Size**: Data-driven by `crew_count` (larger bubbles = more crew)
   - **Style** → **Color**: Use a distinct color (e.g., orange) to differentiate from destinations
   - **Labels**: Enable and set to `base_airport`

### Layer 3: Maintenance at Prague (Single Marker)

1. Click **+ Add layer**
2. Select **Eventhouse** → **PRGOperations** → **Functions** → `fn_maintenance_at_prg`
3. Configure:
   - **Latitude column**: `latitude`
   - **Longitude column**: `longitude`
4. Click **Add**
5. Configure the layer:
   - **Layer name**: `Maintenance Events`
   - **Style**: Use a custom icon or a distinct marker shape
   - **Clustering**: Disable (all points are at PRG)
   - **Popup**: Configure to show `aircraft_type`, `total_events`, `aog_count`, `avg_duration_hours`

## 4.4 Configure Map Settings

1. **Basemap**: Select a style (e.g., **Road** for clear labels, or **Satellite Hybrid** for visual impact)
2. **Default view**: Zoom to Europe level so all airports are visible
   - Center approximately on Prague: Lat `50.10`, Lon `14.26`
   - Zoom level: ~4-5 (shows all of Europe + Middle East)
3. **Layer order**: Place "Destination Airports" at the bottom, "Crew Bases" above, "Maintenance" on top
4. **Layer visibility**: Toggle layers on/off to focus on different stories during the demo

## 4.5 Verify the Map

1. Zoom out to see all destination airports (Europe, Middle East, Asia, Americas, Africa)
2. Toggle the **Crew Bases** layer — verify crew base markers appear at various airports
3. Click on individual markers to see popup details (airport name, city, crew count, etc.)
4. Toggle **Maintenance** layer — verify PRG has maintenance markers with aircraft type breakdown
5. Try using filters to focus on specific regions or high-crew airports

## 4.6 Optional Enhancements

### Add Flight Route Summary Layer

For richer map data (flight counts, delay stats per destination), you can create an additional denormalized table:

1. In a Fabric Notebook (with Lakehouse attached), run the route aggregation query from `agent-config/kql-map-functions.kql` (see the "OPTIONAL: Flight Routes Summary Table" section)
2. Write the result to the Eventhouse
3. Create the `fn_flight_routes_detailed` function
4. Add it as a new map layer with size based on `total_flights`

### Set Up Auto-Refresh

If you plan to regenerate data or add streaming:

1. Select a layer → configure **Refresh interval** (e.g., every 30 seconds)
2. This enables near real-time map updates — useful for demonstrating RTI scenarios

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Map item not available | Enable **Map** in Admin Portal → Tenant settings |
| "Azure Maps service" error | Enable the Azure Maps cross-region processing setting in tenant settings |
| No data in layer | Verify the KQL function returns data: run `fn_destination_map()` in the KQL editor |
| Missing airports table | Re-run Notebook 02 (CELL 10 writes airports to Eventhouse) |
| Function not found | Ensure you ran the `.create-or-alter function` commands in the correct KQL database |
| Layer shows no points | Check that latitude/longitude columns are correctly mapped in the layer config |
| Map is blank | Check that the basemap style is selected and the map is zoomed to a valid area |

## Next Step

→ Return to [03-share-and-publish.md](03-share-and-publish.md) to share the workspace
