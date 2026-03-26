# Step 1b: Create Eventhouse & Generate Operational Data

## Prerequisites

- Completed Step 1 (Lakehouse with flight data)
- Microsoft Fabric workspace with **F2 or higher** capacity
- **Contributor** or higher role in the workspace

## 1b.1 Create an Eventhouse

1. Open your **Microsoft Fabric workspace**
2. Click **+ New item**
3. Select **Eventhouse** (under Real-Time Intelligence section)
4. Name it: `PRGOperations`
5. Click **Create**

> A KQL database with the same name (`PRGOperations`) is created automatically inside the Eventhouse.

## 1b.2 Note the Query URI

1. Open the `PRGOperations` KQL database
2. In the **Database details** card, click **Copy URI** next to **Query URI**
3. Save this URI — you'll need it for the notebook configuration

   Example: `https://trd-xxxxxxxx.z0.kusto.fabric.microsoft.com`

## 1b.3 Grant Database Permissions for Notebook Ingestion

The Kusto Spark connector **does not** automatically inherit the notebook session identity. The notebook must explicitly acquire and pass an access token (already configured in CELL 2 of the notebook via `mssparkutils.credentials.getToken("kusto")`).

### Who already has access?

If you are a **workspace Admin, Member, or Contributor**, you automatically inherit the `AllDatabasesAdmin` role on all KQL databases in the workspace — **no extra permission steps are needed**. Just ensure the notebook has the `accessToken` line (already included) and proceed to step 1b.4.

### If you need to grant access to another user

Use one of these approaches:

#### Option A — Share the KQL database item (recommended)

1. In your **workspace item list**, find the `PRGOperations` KQL database
2. Hover over it and click the **⋯** (ellipsis) menu → **Manage permissions**
   - Or click **Share** to send a sharing link
3. Add the user and select **Read and write** (this grants Database Admin, which includes ingestion rights)
4. Click **Grant** / **Share**

> **Note:** Sharing can also be done at the **Eventhouse** level (hover over `PRGOperations` Eventhouse → **Manage permissions**), which propagates to all KQL databases inside it.

#### Option B — Grant via KQL management command

Open the **Explore your data** query editor in the KQL database and run:

```kql
.add database PRGOperations admins ('aaduser=<user-email>;<tenant-domain>') 'Notebook user'
```

Replace:
- `<user-email>` with the user's full UPN (e.g., `john.doe@contoso.com`)
- `<tenant-domain>` with your Entra ID tenant domain (e.g., `contoso.com`) or tenant GUID

> **Important:** You must include the tenant after `;` — without it, Fabric throws `PrincipalIllFormedException`. If the command still fails, use Option A (item sharing).

### Verification

Run the following in the KQL query editor:

```kql
.show database PRGOperations principals
```

You should see the identity listed with an **Admins** role.

> **Why is the access token needed?** Even with proper permissions, the Kusto Spark connector doesn't pick up the Fabric notebook session identity on its own. The notebook calls `mssparkutils.credentials.getToken("kusto")` and passes the token explicitly via `.option("accessToken", ...)`. Without this, writes are rejected regardless of permissions.

## 1b.4 Create Tables in KQL Database (Optional)

> **Note:** The notebook can create tables automatically using `tableCreateOptions: CreateIfNotExist`. If you prefer to create tables manually with explicit schemas, run these KQL commands in the database query editor:

```kql
.create table gate_assignments (
    gate_assignment_id: int,
    flight_id: int,
    gate: string,
    terminal: string,
    scheduled_start: datetime,
    scheduled_end: datetime,
    actual_start: datetime,
    actual_end: datetime,
    turnaround_minutes: int,
    status: string
)

.create table crew_rosters (
    roster_id: int,
    flight_id: int,
    crew_member_id: string,
    crew_name: string,
    role: string,
    license_number: string,
    nationality: string,
    base_airport: string,
    roster_datetime: datetime
)

.create table maintenance_events (
    maintenance_id: int,
    aircraft_type: string,
    aircraft_registration: string,
    event_type: string,
    category: string,
    description: string,
    start_datetime: datetime,
    end_datetime: datetime,
    duration_hours: real,
    related_flight_id: int,
    resolved: bool
)
```

## 1b.5 Import the Operational Data Notebook

1. In your workspace, click **+ New item** → **Notebook**
2. Name it: `Generate Operational Data`
3. Open the file `notebooks/02_generate_operational_data.py` from this project
4. The file contains 9 cells marked with `# CELL 1` through `# CELL 9`
5. For each cell:
   - Create a new code cell in the Fabric Notebook
   - Copy the code between the cell markers
   - For CELL 1, create a **Markdown cell** instead

## 1b.6 Configure the Notebook

1. **Attach the Lakehouse**: Click **Lakehouses** → **Add** → select `PRGFlightData`
2. **Update Eventhouse connection** in CELL 2:
   - Set `KUSTO_URI` to your Eventhouse Query URI (from step 1b.2)
   - Set `KUSTO_DATABASE` to `"PRGOperations"`

## 1b.7 Run the Notebook

1. Click **Run all** in the toolbar
2. The notebook will:
   - Read existing flight data from the Lakehouse (~50K flights)
   - Generate gate assignments (~5,000 rows) — ~10 seconds
   - Generate crew rosters (~3,000 rows) — ~10 seconds
   - Generate maintenance events (~2,000 rows) — ~15 seconds
   - Write all data to the Eventhouse KQL database — ~1-2 minutes
   - Write relationship bridge tables to the Lakehouse (for ontology) — ~30 seconds
3. The final cell prints a summary with row counts and statistics

## 1b.8 Verify in Eventhouse

1. Go back to the `PRGOperations` KQL database
2. Run the following verification queries:

```kql
// Check table row counts
gate_assignments | count
crew_rosters | count
maintenance_events | count

// Verify gate assignments
gate_assignments
| summarize count() by status
| order by count_ desc

// Verify crew rosters
crew_rosters
| summarize count() by role
| order by count_ desc

// Verify maintenance events
maintenance_events
| summarize count() by event_type
| order by count_ desc
```

3. Expected results:
   - gate_assignments: ~5,000 rows
   - crew_rosters: ~3,000 rows
   - maintenance_events: ~2,000 rows

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Kusto write fails with auth/permissions error | Ensure you completed step 1b.3 — grant **Admin** (or Ingestor) role on the KQL database via Fabric UI. Run `.show database PRGOperations principals` to verify. |
| `PrincipalIllFormedException` on `.add database` | Fabric Eventhouse requires explicit tenant in the KQL command: `'aaduser=user@domain.com;domain.com'`. If it still fails, use the Fabric UI (Option A in step 1b.3). |
| "Table not found" | Tables are auto-created; if manual creation was used, verify column names and types match |
| Low row counts | Check that the Lakehouse flights table has data (run Notebook 01 first) |
| Connection timeout | Verify the KUSTO_URI is correct and the Eventhouse is running |
| `accessToken` is empty / None | Ensure you're running the notebook in a Fabric workspace (not locally). `mssparkutils.credentials.getToken("kusto")` only works in Fabric runtime. |

## Next Step

→ Proceed to [02-configure-agent.md](02-configure-agent.md) (updated with Eventhouse + Ontology steps)
