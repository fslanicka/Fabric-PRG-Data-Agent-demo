# Step 3: Share and Publish the Agent

## 3.1 Test Before Sharing

Before sharing the agent, verify it handles the key scenarios from the demo script:

1. Open the agent's chat interface
2. Run through at least 5 questions from `demo-script/demo-questions.md`
3. Verify the answers are accurate and well-formatted
4. Adjust instructions if needed (see Step 2.8)

## 3.2 Share the Agent

### Option A: Share within Fabric Workspace

1. Users with **Viewer** or higher role in the workspace can access the agent
2. They can find it under the workspace items list
3. No additional sharing steps needed

### Option B: Share with Specific Users

1. In the agent configuration, click **Share** (or **Manage permissions**)
2. Enter the email addresses of users you want to share with
3. Select the permission level:
   - **Viewer**: Can chat with the agent
   - **Contributor**: Can modify agent configuration
4. Click **Grant access**

### Option C: Embed in Power BI (Coming Soon)

Data Agents can be accessed through Power BI Copilot when configured in the same workspace as a Power BI report. Users can ask questions about the data through the Copilot side panel.

## 3.3 Share via Teams (Optional)

1. In the agent settings, look for **Teams integration** options
2. Follow the prompts to create a Teams bot connector
3. Users can then interact with the agent directly in Microsoft Teams

## 3.4 Demo Day Checklist

Before presenting the demo:

- [ ] Lakehouse is running and tables are populated
- [ ] Agent responds correctly to test questions
- [ ] Agent instructions are properly configured
- [ ] You have the demo questions ready (`demo-script/demo-questions.md`)
- [ ] All demo participants have Viewer access to the workspace
- [ ] (Optional) Prepare a backup — screenshot expected answers in case of live demo issues

## 3.5 Maintenance

- **Data refresh**: Re-run the notebook to regenerate data (overwrites existing tables)
- **Add more data**: Modify `START_DATE`/`END_DATE` in the notebook to extend the date range
- **Update instructions**: Edit agent/data source instructions as needed — changes take effect immediately
- **Monitor usage**: Check the agent's usage metrics in the Fabric workspace

## Resources

- [Microsoft Fabric Data Agent Documentation](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations)
- [Data Agent Best Practices](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)
- [Fabric Data Agent End-to-End Tutorial](https://github.com/MicrosoftDocs/fabric-docs/blob/main/docs/data-science/data-agent-end-to-end-tutorial.md)
