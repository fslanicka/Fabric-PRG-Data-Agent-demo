# Step 2: Configure the Fabric Data Agent

## 2.1 Create a New Data Agent

1. In your Fabric workspace, click **+ New item**
2. Select **Agent** (under Data Science section, or search for "Agent")
3. Name it: `Prague Airport Flight Agent`
4. Click **Create**

> **Note**: If you don't see the Agent option, your Fabric admin needs to enable the Data Agent preview in tenant settings.

## 2.2 Add the Data Source

1. In the Agent configuration page, find **Data Sources**
2. Click **+ Add data source**
3. Select **Lakehouse**
4. Choose your `PRGFlightData` Lakehouse
5. Select the following tables:
   - ✅ `flights`
   - ✅ `airlines`
   - ✅ `airports`
   - ✅ `weather`
6. Click **Confirm**

## 2.2b Add Eventhouse Data Source

1. In the Agent configuration page, find **Data Sources**
2. Click **+ Add data source**
3. Select **KQL Database**
4. Choose your `PRGOperations` KQL database (from the Eventhouse)
5. Select the following tables:
   - ✅ `gate_assignments`
   - ✅ `crew_rosters`
   - ✅ `maintenance_events`
6. Click **Confirm**

## 2.2c Add Ontology Data Source

1. In the Agent configuration page, find **Data Sources**
2. Click **+ Add data source**
3. Search for **PRGAirportOntology** (the ontology created in Step 2b)
4. Select it and click **Add**
5. The ontology and its entity types are now visible in the Explorer

> **Note**: The ontology must be created and configured first (see `setup-guide/02b-configure-ontology.md`).

## 2.3 Add Data Source Descriptions

### Lakehouse Description
1. Click on the **Lakehouse** data source
2. Find the **Description** field
3. Copy and paste the content from `agent-config/datasource-description.md`
   - Copy only the text between the `---` markers

### Eventhouse Description
1. Click on the **KQL Database** data source
2. Find the **Description** field
3. Copy and paste the content from `agent-config/eventhouse-datasource-description.md`
   - Copy only the text between the `---` markers

### Ontology Description

> ⚠️ **Known limitation (preview):** The Fabric Data Agent UI does not currently display Description or Instructions fields for ontology data sources. Only Lakehouse and KQL Database data sources show these fields. As a workaround, include the ontology description and instructions content in the **Agent Instructions** (section 2.6). The provided `agent-config/agent-instructions.md` already contains ontology guidance — see "Ontology / Fabric IQ" and "Cross-Domain Questions" sections. For additional detail, append content from `agent-config/ontology-datasource-description.md` and `agent-config/ontology-datasource-instructions.md` to your agent instructions.

~~1. Click on the **Ontology** data source~~
~~2. Find the **Description** field~~
~~3. Copy and paste the content from `agent-config/ontology-datasource-description.md`~~

> The descriptions help the agent understand what each data source contains and when to use it.

## 2.4 Add Data Source Instructions

### Lakehouse Instructions
1. Click on the **Lakehouse** data source
2. Find the **Instructions** field
3. Copy and paste the content from `agent-config/datasource-instructions.md`
   - Copy only the text between the `---` markers
4. This includes: table descriptions, SQL query logic, joins, filtering patterns

### Eventhouse Instructions
1. Click on the **KQL Database** data source
2. Find the **Instructions** field
3. Copy and paste the content from `agent-config/eventhouse-datasource-instructions.md`
   - Copy only the text between the `---` markers
4. This includes: KQL table descriptions, query patterns, value formats

### Ontology Instructions

> ⚠️ **Known limitation (preview):** Same as above — the ontology data source does not expose an Instructions field in the UI. Include this content in the **Agent Instructions** instead.

~~1. Click on the **Ontology** data source~~
~~2. Find the **Instructions** field~~
~~3. Copy and paste the content from `agent-config/ontology-datasource-instructions.md`~~
~~4. This includes: entity types, relationships, GQL patterns, source routing logic~~

> These instructions guide the agent in generating accurate SQL, KQL, and graph queries.

## 2.5 Add Example Queries

### Lakehouse Example Queries (SQL)
1. Click on the **Lakehouse** data source → find **Example queries**
2. For each query in `agent-config/example-queries.sql`:
   - Click **+ Add example**
   - Enter the **Question** (the comment line starting with `-- Question:`)
   - Enter the **SQL Query** (the SQL code below the question)
3. Add at least the first 8-10 examples for best results

### Eventhouse Example Queries (KQL)
1. Click on the **KQL Database** data source → find **Example queries**
2. For each query in `agent-config/example-queries-eventhouse.kql`:
   - Click **+ Add example**
   - Enter the **Question** (the comment line starting with `// Question:`)
   - Enter the **KQL Query** (the code below the question)
3. Add at least 8-10 examples

> Example queries act as few-shot learning samples. The agent retrieves the top 3 most relevant examples for each user question, per data source.

## 2.6 Add Agent Instructions

1. Go back to the main Agent configuration page
2. Find **Agent Instructions** (at the agent level, not data source level)
3. Copy and paste the content from `agent-config/agent-instructions.md`
   - Copy only the text between the `---` markers
4. **Important:** Since the ontology data source does not support Description/Instructions fields in the UI (see sections 2.3 and 2.4), also append the content from:
   - `agent-config/ontology-datasource-description.md` (between the `---` markers)
   - `agent-config/ontology-datasource-instructions.md` (between the `---` markers)
5. This includes:
   - Objective
   - Data source descriptions
   - Key terminology
   - Response guidelines
   - Handling common topics

## 2.7 Test the Agent

1. Click **Chat** or open the agent's chat interface
2. Test each data source:

**Lakehouse (SQL):**
   - "How many flights are in the database?" → expects ~100,000
   - "Which airline has the most flights?"

**Eventhouse (KQL):**
   - "What is the average turnaround time by terminal?" → expects 60-90 min
   - "Which captains flew the most flights?"

**Ontology (Graph):**
   - "What entity types exist in the ontology?"
   - "Which crew members were on flights to London during fog?"

3. If any data source doesn't respond correctly, check the description and instructions for that source

## 2.8 Fine-tune (Optional)

If the agent doesn't answer correctly:
- **Wrong data source**: Adjust the data source description to be more specific
- **Wrong columns**: Add more detail to data source instructions
- **Wrong query logic**: Add more example queries covering the failing scenario
- **Wrong formatting**: Adjust response guidelines in agent instructions

## Next Step

→ Proceed to [03-share-and-publish.md](03-share-and-publish.md)
