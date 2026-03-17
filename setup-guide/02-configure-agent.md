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

## 2.3 Add Data Source Description

1. Click on the Lakehouse data source you just added
2. Find the **Description** field
3. Copy and paste the content from `agent-config/datasource-description.md`
   - Copy only the text between the `---` markers

> The description helps the agent understand what the data source contains and when to use it.

## 2.4 Add Data Source Instructions

1. In the same data source configuration, find the **Instructions** field
2. Copy and paste the content from `agent-config/datasource-instructions.md`
   - Copy only the text between the `---` markers
3. This includes:
   - General knowledge about the dataset
   - Table descriptions with column details
   - Query logic (joins, filtering, common patterns)
   - Value format reference

> These instructions guide the agent in generating accurate SQL queries.

## 2.5 Add Example Queries

1. In the data source configuration, find **Example queries**
2. For each query in `agent-config/example-queries.sql`:
   - Click **+ Add example**
   - Enter the **Question** (the comment line starting with `-- Question:`)
   - Enter the **SQL Query** (the SQL code below the question)
3. Add at least the first 8-10 examples for best results

> Example queries act as few-shot learning samples. The agent retrieves the top 3 most relevant examples for each user question.

## 2.6 Add Agent Instructions

1. Go back to the main Agent configuration page
2. Find **Agent Instructions** (at the agent level, not data source level)
3. Copy and paste the content from `agent-config/agent-instructions.md`
   - Copy only the text between the `---` markers
4. This includes:
   - Objective
   - Data source descriptions
   - Key terminology
   - Response guidelines
   - Handling common topics

## 2.7 Test the Agent

1. Click **Chat** or open the agent's chat interface
2. Try a simple question: "How many flights are in the database?"
3. The agent should query the flights table and return a count of ~100,000
4. Try a few more test questions:
   - "Which airline has the most flights?"
   - "What is the average delay in minutes?"
   - "Show me the busiest month"

## 2.8 Fine-tune (Optional)

If the agent doesn't answer correctly:
- **Wrong data source**: Adjust the data source description to be more specific
- **Wrong columns**: Add more detail to data source instructions
- **Wrong query logic**: Add more example queries covering the failing scenario
- **Wrong formatting**: Adjust response guidelines in agent instructions

## Next Step

→ Proceed to [03-share-and-publish.md](03-share-and-publish.md)
