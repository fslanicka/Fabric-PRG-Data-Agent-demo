# Step 1: Create Lakehouse & Generate Sample Data

## Prerequisites

- Microsoft Fabric workspace with **F2 or higher** capacity
- **Contributor** or higher role in the workspace
- Fabric admin has enabled **Copilot** and **Data Agent** in tenant settings
  - Admin Portal → Tenant settings → Copilot and Azure OpenAI Service → Enable

## 1.1 Create a New Lakehouse

1. Open your **Microsoft Fabric workspace**
2. Click **+ New item**
3. Select **Lakehouse**
4. Name it: `PRGFlightData` (or any name you prefer)
5. Click **Create**

## 1.2 Import the Data Generation Notebook

1. In your workspace, click **+ New item** → **Notebook**
2. Name it: `Generate Flight Data`
3. Open the file `notebooks/01_generate_flight_data.py` from this project
4. The file contains 8 cells marked with `# CELL 1` through `# CELL 8`
5. For each cell:
   - Create a new code cell in the Fabric Notebook
   - Copy the code between the cell markers
   - For CELL 1, create a **Markdown cell** instead with the title text

> **Tip**: You can also upload the .py file directly via **Import** in the notebook toolbar, but you'll need to split it into cells manually.

## 1.3 Attach the Lakehouse

1. In the notebook, click **Lakehouses** in the left panel
2. Click **Add** → **Existing Lakehouse**
3. Select `PRGFlightData`
4. The Lakehouse is now the default for `saveAsTable()` calls

## 1.4 Run the Notebook

1. Click **Run all** in the toolbar
2. The notebook will generate:
   - `airlines` table (~40 rows) — ~5 seconds
   - `airports` table (~100 rows) — ~5 seconds
   - `weather` table (~730 rows) — ~10 seconds
   - `flights` table (~105,000 rows) — ~1-2 minutes
3. The final cell prints a summary with row counts and statistics
4. Verify the output matches approximately:
   - airlines: 40
   - airports: ~100
   - weather: 731
   - flights: ~105,000

## 1.5 Verify in Lakehouse

1. Go back to the `PRGFlightData` Lakehouse
2. Expand **Tables** in the explorer
3. You should see 4 tables: `airlines`, `airports`, `flights`, `weather`
4. Click on each table to preview the data
5. Verify the `flights` table has the expected columns and ~50K rows

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Notebook fails with "Lakehouse not found" | Make sure the Lakehouse is attached (step 1.3) |
| `saveAsTable` fails | Ensure you have Contributor role or higher |
| Low row counts | Check that `START_DATE` and `END_DATE` in CELL 2 are set correctly |
| Out of memory | Run cells individually instead of "Run all" |

## Next Step

→ Proceed to [02-configure-agent.md](02-configure-agent.md)
