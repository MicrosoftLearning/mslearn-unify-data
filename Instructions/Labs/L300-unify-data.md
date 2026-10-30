---
lab:
    title: 'Build an end-to-end Caldova data agent solution'
    description: 'Build, govern, extend, and validate a cross-service Caldova data agent solution with Microsoft Fabric, Microsoft Foundry, and Microsoft Copilot Studio.'
    duration: 225
    level: 300
    islab: true
    status: 'in-development'
    targetDate: '2026-11-30'
---

# Build an end-to-end Caldova data agent solution

Caldova Pharmaceuticals must decide where to focus before launch program `LP001` moves forward. The core path combines planning and supplier data with simulated operational evidence, then validates the same grounded facts across Fabric, Microsoft Foundry, and Microsoft Copilot Studio.

In this exercise, you first build the complete core launch-readiness path. Optional sentiment and enrichment tasks then add customer evidence, and a final ontology models the cross-source relationships explicitly.

This exercise should take approximately **225** minutes to complete when you perform every task.

## Learning objectives

By the end of this exercise, you can:

1. Build a Fabric foundation that combines planning, supplier, batch, and operational data.

1. Route simulated events to Eventhouse and Lakehouse destinations.

1. Build, tune, test, and publish a multi-source Fabric data agent.

1. Inspect discovery, security, governance, and lineage in OneLake catalog.

1. Ground Microsoft Foundry and Microsoft Copilot Studio agents through a published Fabric data agent.

1. Compare planning, supplier, and operational evidence across three agent experiences.

1. Optionally apply Azure OpenAI sentiment analysis and issue-category enrichment, then model cross-source business context with a Fabric ontology.

## Before you start

Complete the checklist in [Prepare your environment](./00-environment-setup.md) before you start. It applies to both your own environment and a hosted lab computer.

> **Note**: This exercise requires a paid F2 or higher Fabric capacity. Have your prepared Azure subscription, supported region, Microsoft Copilot Studio environment, and Azure OpenAI resource and deployment names available. In a hosted lab, the provider supplies these values.

> **Important**: Fabric Trial can support the Lakehouse and streaming foundation, but it doesn't meet the data-agent capacity prerequisite. Confirm that your lab identity can create a workspace on the prepared paid capacity. Capacity and tenant settings are configured before the exercise.

> **Note**: Fabric data agent, Fabric IQ, and ontology features used in this exercise are in preview. Labels in the user interface can change.

## Configure the environment

Caldova needs a shared, governed foundation before teams can assess `LP001`. In this task, you create the workspace, Lakehouse, and curated launch-readiness tables.

**Estimated time:** 25 minutes.

### Download the necessary files

Download and extract the learner package so every required dataset, notebook, code file, and event-simulation asset is available for the remaining tasks.

1. Open a browser on your lab computer, and download the learner package:

    [Download L300-unify-data.zip](https://raw.githubusercontent.com/MicrosoftLearning/mslearn-unify-data/main/Allfiles/L300-unify-data/L300-unify-data.zip){:target="_blank"} from `https://raw.githubusercontent.com/MicrosoftLearning/mslearn-unify-data/main/Allfiles/L300-unify-data/L300-unify-data.zip`.

1. Open the **Downloads** folder in File Explorer.

1. Extract the `L300-unify-data.zip` to the default location `Downloads\L300-unify-data`.

1. Open the extracted `L300-unify-data` folder, and verify that it contains:

    - `code`
    - `data`
    - `notebooks`
    - `event-simulator`

### Create the workspace and lakehouse

Create a capacity-backed Fabric workspace and Lakehouse that provide the governed storage foundation for the Caldova solution and its agents.

1. Open the [Microsoft Fabric home page](https://app.fabric.microsoft.com/home?experience=fabric){:target="_blank"} at `https://app.fabric.microsoft.com/home?experience=fabric`, and sign in with the account you prepared for the exercise.

1. Select **Workspaces** > **+ New workspace** and name it `caldova-agent`.

1. Expand **Advanced**, select the **Fabric** license mode and the paid capacity you prepared for the exercise, and create the workspace.

1. Open the workspace, and select **Import** > **Notebook** > **From this computer**.

1. Import the notebook from `Downloads\L300-unify-data\notebooks\curate_caldova_tables.ipynb`.

1. In the notebook **Explorer** pane, select **Add data items** > **New lakehouse**.

1. Enter `caldova_lakehouse`, select your workspace, enable **Lakehouse schemas** (which might be labeled **Public Preview**), and select **Create**. The notebook writes its tables to the `dbo` schema.

1. Return to `curate_caldova_tables`, and select **Run all**.

1. Confirm these outcomes:

    - The final output reports:

        ```output
        Validation passed: 318 rows across six tables; all tested relationships are valid.
        ```

    - The Lakehouse contains `dbo.launch_program`, `dbo.product`, `dbo.plant`, `dbo.capacity_plan`, `dbo.batch`, and `dbo.supplier`.

    - The notebook result grids show an 18,900-unit gap and a 7% gap for `LP001`. The launch result displays the binding plant name. To verify the plant ID, open `dbo.launch_program` in the Lakehouse, find `LP001`, and confirm that `BindingConstraintPlantID` is `PL003`.

    - Meridian Biologics ranks first among eligible suppliers.

## Configure streaming data and detect exceptions

The static `LP001` plan doesn't show new production or supplier exceptions. In this task, you stream operational events and detect threshold breaches that can increase launch risk.

**Estimated time:** 25 minutes.

### Create the eventhouse table and mapping

Prepare Eventhouse to receive consistently typed events. This setup creates an empty destination; you analyze the events after the replay.

1. Select **+ New item** in the Caldova workspace, search for **Eventhouse**, and create `caldova_events`.

1. Open `caldova_events`, and verify that its default KQL database appears. Dismiss any first-time welcome or guided-tour panels.

1. In the default KQL database, select **KQL Queryset** on the toolbar, and name it `caldova_exception_queries`. The **New** menu is for table-related objects.

1. Open `Downloads\L300-unify-data\code\05-operational-events.txt`. The file contains the table command, JSON ingestion mapping, and LP001 threshold-breach query.

1. Copy and run the `.create table operational_events` command. This creates the empty destination table and defines the data type for each event field.

1. Copy and run the `.create-or-alter table operational_events ingestion json mapping` command. This maps each incoming JSON field to its Eventhouse column.

1. Confirm that `operational_events` appears in the KQL database. The table remains empty until you configure the Eventstream destination and replay the events.

You use the final query in `05-operational-events.txt` after the replay to analyze which observations exceed their thresholds.

### Create and publish the eventstream

Create and publish an eventstream that routes each simulated event to Eventhouse for low-latency analysis and to the Lakehouse for durable history.

1. Return to the workspace, select **+ New item**, search for **Eventstream**, and create `caldova_operational_stream`.

1. Select **Add source** > **Custom endpoint** in **Edit** mode, and name the source `caldova-simulator`.

1. Select **Add destination**, find **Eventhouse** in the destination catalog, select **Configure**, and enter:

    | Setting | Value |
    |---|---|
    | **Ingestion mode** | **Direct ingestion** |
    | **Destination name** | `eventhouse-operational-events` |
    | **Workspace** | Your Caldova workspace |
    | **Eventhouse** | `caldova_events` |
    | **KQL database** | `caldova_events` |

1. Connect the default stream's output port to the Eventhouse destination's input port. Adding a destination doesn't automatically connect it.

1. Select **Add destination**, find **Lakehouse** in the destination catalog, select **Configure**, and enter:

    | Setting | Value |
    |---|---|
    | **Destination name** | `lakehouse-operational-history` |
    | **Workspace** | Your Caldova workspace |
    | **Lakehouse** | `caldova_lakehouse` |
    | **Delta table** | Create `dbo.operational_event_history` |
    | **Input data format** | `JSON` |
    | **Minimum rows** (under **Advanced settings**) | `1` |
    | **Seconds per file** (under **Advanced settings**) | `60` |

1. Connect the default stream to the Lakehouse destination.

1. Select **Publish**, and wait until the custom source and Lakehouse destination show **Active**. The Eventhouse destination remains **Unconfigured** until you send the priming event and complete its **Get data** wizard.

### Prepare the simulator and prime the stream

Publish the simulated event set, validate four LP001 threshold breaches, and confirm that both streaming destinations receive the expected operational evidence.

1. Select the `caldova-simulator` source in the eventstream, open **Details**, and select **Event Hub** > **SAS Key Authentication**. Locate **Connection string-primary key** and **Event hub name**. Use the complete connection string, not the standalone **Primary key** or credentials from the AMQP or Kafka tabs.

1. Open PowerShell, and change to the event simulator folder:

    ```powershell
    Set-Location "$HOME\Downloads\L300-unify-data\event-simulator"
    ```

1. Set temporary process-level environment variables. Run these commands, then paste each value from Fabric at its prompt:

    ```powershell
    $env:EVENTSTREAM_CONNECTION_STRING = (
        [System.Net.NetworkCredential]::new(
            '',
            (Read-Host 'Paste the complete Event Hub connection string-primary key' -AsSecureString)
        ).Password
    ).Trim()
    $env:EVENTSTREAM_ENTITY_NAME = (Read-Host 'Paste Event hub name').Trim()
    ```

    `EVENTSTREAM_ENTITY_NAME` must match **Event hub name**, which is also the connection string's `EntityPath` value. It isn't the source display name `caldova-simulator`. The connection-string prompt hides your input and keeps it out of the command text in PowerShell history. Don't share credentials in chat, screenshots, or saved files.

1. Send one nonexception priming event, and confirm that PowerShell reports `Replay complete: 1 event sent.`:

    ```powershell
    python .\replay_events.py --prime --delay-seconds 0
    ```

    The event supplies a representative JSON schema without adding a threshold breach. A local guard prevents accidental repeat priming. Priming is tracked separately and doesn't block the full replay.

1. Keep this PowerShell window open for the full replay. The credential variables are available only in this session.

### Connect the Eventhouse destination

1. Return to the eventstream **Live view**, and select **Configure** on the Eventhouse destination.

1. Select the existing `operational_events` table in the `caldova_events` KQL database, retain the generated **Data connection name**, and select **Next**.

1. On **Inspect the data**, select **JSON** as the format.

1. Open the mapping dropdown above the preview grid, turn on **Use existing mapping**, and select `operational_events_json`.

1. Confirm that the preview displays the event in the expected columns, then select **Finish** to complete the **Get data** flow.

1. Verify that the Eventhouse destination reports a successful connection.

### Replay and verify the simulated events

1. Return to PowerShell, send the ten deterministic simulated events, and confirm that PowerShell reports `Replay complete: 10 events sent.`:

    ```powershell
    python .\replay_events.py
    ```

    > **Note**: The simulator records the attempt in a local state file beside the script. After a successful run, another full replay stops with **Replay already completed. No events sent.** If an attempt fails or is interrupted, the guard also blocks a retry because some events might already have arrived. If results haven't appeared yet, refresh the destination or rerun the query, not the simulator.

    With instructor approval, append `--force` to intentionally repeat a full replay, or add it to the priming command to repeat priming. This can duplicate events and change the expected counts. Never use `--force` while another replay is running. The guard applies only to this extracted simulator folder, not another copy or machine. Keep the state files in place.

1. Clear the temporary credentials:

    ```powershell
    Remove-Item Env:\EVENTSTREAM_CONNECTION_STRING
    Remove-Item Env:\EVENTSTREAM_ENTITY_NAME
    ```

    Removing the variables keeps the endpoint secrets out of later commands in the current process.

1. Reopen `Downloads\L300-unify-data\code\05-operational-events.txt`, and locate the final query.

    _The query begins with `operational_events`, filters `LaunchProgramID` to `LP001`, and compares `MetricValue` with `Threshold`._

1. Copy only the final query that begins with `operational_events`, paste it into `caldova_exception_queries`, and run it.

1. Review the four returned rows. For each row, compare `MetricValue` with `Threshold` and use `AmountOverThreshold` to determine the size of the exception.

1. Confirm these findings:

    - `PL003` has two utilization exceptions above 110% and one quality-deviation exception.
    - `CMO006` has one projected supplier lead-time exception.
    - The results contain four simulated threshold breaches in total.

### Verify Lakehouse history

1. Open `caldova_lakehouse`, refresh its table list, and expand **Tables** > **dbo**. Select `operational_event_history` to preview the persisted events.

1. Switch to the Lakehouse's **SQL analytics endpoint**, open a new SQL query, and run:

    ```sql
    SELECT
        COUNT(*) AS SimulatorRows,
        SUM(CASE
            WHEN LaunchProgramID = 'LP001' AND MetricValue > Threshold
            THEN 1 ELSE 0
        END) AS ThresholdBreaches
    FROM dbo.operational_event_history
    WHERE SourceSystem = 'CaldovaLabSimulator';
    ```

1. For a fresh table with one successful priming event and one full replay, confirm `SimulatorRows` is `11` and `ThresholdBreaches` is `4`. Allow at least the configured 60-second batching interval, plus ingestion and SQL endpoint synchronization time. If the table or rows aren't available immediately, wait, refresh, and rerun the query. Don't resend the events.

These simulated exceptions add current operational evidence to Caldova's existing `LP001` capacity and supplier risks.

## Build, tune, test, and publish a Fabric data agent

Decision makers need one way to evaluate planning, suppliers, and current exceptions. In this task, you publish the initial Fabric data agent over the governed core sources.

**Estimated time:** 20 minutes.

### Create the data agent

Create a Fabric data agent that reasons across curated planning and supplier records with simulated Eventhouse telemetry.

1. Return to the workspace, select **+ New item**, search for **Data agent**, and create `caldova_data_agent`.

1. Select **Add a data source**, and add `caldova_lakehouse`.

1. Select these Lakehouse tables:

    - `launch_program`
    - `product`
    - `plant`
    - `capacity_plan`
    - `batch`
    - `supplier`

1. Select **Add a data source**, add the `caldova_events` KQL database, and select `operational_events`.

> **Tip**: For easier copying, open `Downloads\L300-unify-data\code\06-fabric-data-agent-snippets.txt`.

```prompt
You are Caldova's launch-readiness data assistant. Use only the selected Lakehouse and Eventhouse sources. Join records with their documented business keys. Treat operational events as simulated exercise evidence. For launch recommendations, report the capacity gap, binding plant, eligible supplier evidence, operational threshold breaches, and supporting record counts. Separate source facts from recommendations. Never present a supplier ranking as procurement approval, and don't make medical, clinical, safety, or efficacy claims.
```

1. Open **Agent instructions** in the data agent, copy the preceding instructions, and save them.

### Add Lakehouse source instructions and SQL examples

Guide the agent to join Lakehouse records correctly and answer capacity and supplier questions with governed SQL evidence.

```prompt
launch_program has one row per launch and joins to product on ProductID. product has one row per product. plant has one row per plant. capacity_plan and batch join to launch_program on LaunchProgramID and to plant on PlantID. supplier joins to launch_program on LaunchProgramID and to product on ProductID. For eligible supplier comparisons, require a currently valid GMP certificate, zero open critical findings, fast-track eligibility, and enough qualified available capacity to cover the launch gap.
```

1. Open the `caldova_lakehouse` **Data source instructions**, copy the preceding instructions, and save them.

Add the first example question and SQL query:

```input
What is the capacity gap and binding plant for LP001?
```

```sql
SELECT LaunchProgramID, TargetLaunchVolume, QualifiedCapacity,
       CapacityGapUnits, CapacityGapPercent, BindingConstraintPlantID
FROM dbo.launch_program
WHERE LaunchProgramID = 'LP001';
```

1. Add the preceding question and SQL query to the Lakehouse source.

Add the second example question and SQL query:

```input
Which eligible supplier leads for LP001?
```

```sql
SELECT CMOName, QualifiedAvailableCapacityUnits, LeadTimeWeeks,
       GMPCertStatus, OpenCriticalFindings, FastTrackEligible, WeightedScore
FROM dbo.supplier
WHERE LaunchProgramID = 'LP001'
  AND GMPCertStatus = 'Currently valid'
  AND OpenCriticalFindings = 0
  AND FastTrackEligible = 'Yes'
  AND QualifiedAvailableCapacityUnits >= 18900
ORDER BY WeightedScore DESC;
```

1. Add the preceding question and SQL query to the Lakehouse source.

### Add Eventhouse source instructions and a KQL example

Guide the agent to interpret simulated operational telemetry correctly and identify threshold breaches with qualified KQL evidence for `LP001` launch analysis.

```prompt
operational_events contains simulated telemetry. EventID is the event key. LaunchProgramID, ProductID, PlantID, BatchID, and CMOID connect events to curated business records. A threshold breach requires MetricValue greater than Threshold, not equal to Threshold. State that event evidence is simulated and don't describe it as historical production telemetry.
```

1. Open the `caldova_events` **Data source instructions**, copy the preceding instructions, and save them.

Add the example question and KQL query:

```input
Which simulated LP001 events breached their thresholds?
```

```kusto
operational_events
| where LaunchProgramID == "LP001" and MetricValue > Threshold
| summarize BreachCount=count() by EventType, PlantID, CMOID, MetricName
```

1. Add the preceding question and KQL query to the Eventhouse source.

### Test and publish the Fabric data agent

Validate that the agent invokes both source types, preserves fixed facts and evidence qualifiers, and publishes a shareable grounded experience.

1. Ask this question in the agent test pane:

    ```input
    For LP001, summarize the capacity gap, binding plant, leading eligible supplier, and simulated threshold breaches. Separate source facts, simulated evidence, and recommendations.
    ```

1. Review the completed steps and response:

    - The agent uses both SQL and KQL.
    - An 18,900-unit, 7% gap
    - `PL003` as the binding plant
    - Meridian Biologics as the leading eligible supplier
    - Four simulated threshold breaches

1. Select **Publish**, review the selected sources, and publish `caldova_data_agent`.

1. Confirm that the agent shows a published state and that you have permission to share it with the assigned Foundry and Copilot Studio environments.

## Tour OneLake catalog

Caldova must make the estate findable, controlled, and traceable before agents are shared. In this task, you inspect discovery, access, governance metadata, and lineage.

**Estimated time:** 15 minutes.

### Discover items and review details

Find the Caldova items you created and inspect the metadata that identifies each item's purpose, owner, type, and location.

1. Select **OneLake catalog** in the Fabric navigation pane.

1. Filter **Workspace** to your Caldova workspace in the **Explore** section.

1. Search for `caldova`, and verify that these items from your workspace are discoverable:

    - `caldova_lakehouse`
    - `caldova_events`
    - `caldova_operational_stream`
    - `caldova_data_agent`

1. Find the imported `curate_caldova_tables` notebook in the same workspace.

1. Select `caldova_lakehouse`, and review **Details**, owner, item type, location, and last refresh information.

1. See that the description is empty. Add the following details:

    ```text
    Curated Caldova launch, capacity, supplier, batch, plant, product, and operational-event history for the L300 agent journey.
    ```

1. Set the `caldova_lakehouse` endorsement to **Promoted**.

### Inspect security and governance

Inspect access and governance information for the Caldova workspace and the items you created.

1. Navigate to the **Secure** section.

1. Filter to your Caldova workspace, and review the workspace and item access shown for your identity.

1. Confirm that your identity can read `caldova_lakehouse` and `caldova_events`.

1. Navigate to the **Govern** section.

1. Review the description and endorsement coverage for the Caldova items you created, and inspect any recommended actions associated with those items.

### Trace workspace lineage

Trace how notebooks, eventstreams, storage items, and the data agent connect so each answer remains linked to visible or documented source relationships.

1. Return to the Caldova workspace, and open **Lineage view**.

1. Confirm these lineage outcomes:

    - `caldova_operational_stream` feeds `caldova_events` and `caldova_lakehouse`.
    - The curated notebook connects to `caldova_lakehouse`.
    - `caldova_data_agent` shows its visible source dependencies.
    - Any relationship not displayed in lineage can still be traced through the source instructions and business keys you configured.

## Build a Microsoft Foundry agent

Solution teams need the core Caldova assessment in broader AI prototypes. In this task, you connect Foundry to the initial published Fabric data agent.

**Estimated time:** 25 minutes.

### Create the Foundry project and deploy a model

Create an isolated Foundry project and deploy the model that runs the learner-created Foundry agent.

1. Open the [Microsoft Foundry portal](https://ai.azure.com/){:target="_blank"} at `https://ai.azure.com/`.

1. Open the project selector, and select **Create new project**.

1. Enter `caldova-foundry-` followed by your initials as the project name.

1. Expand **Advanced options**.

1. Create a resource group named `caldova-foundry-` followed by your initials and `-rg`, and select the supported region supplied for the exercise.

1. Select **Create project**, and wait for the project overview page to open.

1. Select **Build** > **Models**.

1. Select **Deploy** > **Deploy a base model**, and search for `gpt-5-mini`.

1. Select `gpt-5-mini`, and then select **Deploy** > **Default settings**.

1. Confirm that the deployment is available in the project, and note its deployment name.

For project and model setup details, see [Set up Microsoft Foundry resources](https://learn.microsoft.com/azure/foundry/tutorials/quickstart-create-foundry-resources).

### Create and ground the Foundry agent

Create a Foundry agent that invokes the published Fabric data agent while preserving its governed query, permission, and evidence boundaries.

1. Open the agent creation experience in your `caldova-foundry-<initials>` project, and create an agent named `caldova_foundry_agent`.

1. Select the `gpt-5-mini` deployment you created.

1. Enter these agent instructions:

    ```prompt
    You are Caldova's launch-readiness assistant. Use the connected Fabric IQ data agent for every question about Caldova launch programs, capacity, plants, batches, suppliers, or operational events. Preserve the simulated-event qualifier from the tool, separate facts from recommendations, and never treat a supplier result as procurement approval.
    ```

1. Select **Tools** > **Add** > **Browse all tools**.

1. Select **Fabric IQ (OneLake Catalog)**.

1. Sign in or create the connection with the learner identity if prompted.

1. Filter the catalog item type to **Data agent**.

1. Select the published `caldova_data_agent`.

1. Add the selected data agent as a tool.

### Test the Foundry grounding

Confirm that the Foundry agent invokes the Fabric tool and returns the planning, supplier, and operational evidence.

1. Ask:

    ```input
    For LP001, summarize the capacity gap, binding plant, leading eligible supplier, and simulated threshold breaches. Separate source facts, simulated evidence, and recommendations.
    ```

1. Review the completed steps and response:

    - The published `caldova_data_agent` tool is invoked.
    - The response includes the **18,900-unit**, **7%** gap, `PL003`, Meridian Biologics, and four simulated threshold breaches.

1. Save the agent configuration.

## Build a Microsoft Copilot Studio agent

Business users need the same core launch-readiness answer through a low-code experience. In this task, you connect Copilot Studio to the initial published Fabric data agent.

**Estimated time:** 15 minutes.

### Add the Fabric IQ Data MCP tool

Create a Copilot Studio agent that delegates Caldova data questions to the published Fabric data agent through Fabric IQ Data MCP.

1. Open [Microsoft Copilot Studio](https://copilotstudio.microsoft.com/){:target="_blank"} at `https://copilotstudio.microsoft.com/`, and select the provided environment.

1. Create an agent named `Caldova launch readiness`.

1. Set its description to:

    ```text
    Answers governed Caldova launch-readiness questions through the published Fabric data agent.
    ```

1. Add these agent instructions:

    ```prompt
    Use the Caldova Fabric IQ data tool for every question about launch programs, capacity, plants, batches, suppliers, or operational events. Use only returned data. Preserve simulated-event qualifiers, separate facts from recommendations, and don't represent a supplier result as procurement approval.
    ```

1. Open the **Build** tab, and select **Tools** > **+** > **Fabric IQ Data MCP** > **OneLake catalog**.

1. Sign in with the learner identity if prompted.

1. Select the published `caldova_data_agent`.

1. Configure the tool description:

    ```text
    Queries governed Caldova launch, capacity, plant, batch, supplier, and simulated operational-event data.
    ```

1. Configure the tool instructions:

    ```prompt
    Call this tool for all Caldova data questions. Pass the user's complete question. Return the grounded answer and preserve source names, counts, and simulated-event qualifiers.
    ```

1. Save the tool.

### Test and publish the Copilot Studio agent

Validate the complete grounded launch-readiness answer, then publish the agent for continued testing.

1. Ask this question in the test pane:

    ```input
    For LP001, summarize the capacity gap, binding plant, leading eligible supplier, and simulated threshold breaches. Separate source facts, simulated evidence, and recommendations.
    ```

1. Review the completed steps and response:

    - The Fabric IQ Data MCP tool invokes the published `caldova_data_agent`.
    - The response includes the same planning, supplier, and operational evidence returned in Fabric and Foundry.
    - The response identifies operational events as simulated.

1. Select **Publish**, and publish the Copilot Studio agent.

1. Switch back to the test pane, and confirm that the published agent still returns the complete grounded launch-readiness result.

## Validate the same facts across three agent experiences

In this task, you confirm that Fabric, Foundry, and Copilot Studio return the same planning, supplier, and operational evidence from one published Fabric data agent.

**Estimated time:** 15 minutes.

### Run the shared prompt set

Run the same launch-readiness question through all three agents.

1. Open the published Fabric data agent, the Foundry agent test pane, and the Copilot Studio test pane.

1. Submit this prompt unchanged in all three experiences:

    ```input
    For LP001, summarize the capacity gap, binding plant, leading eligible supplier, and simulated threshold breaches. Separate source facts, simulated evidence, and recommendations.
    ```

### Compare the results

Confirm that all three agents return the same core Caldova facts.

1. Check the responses for these expected results:

    - The `LP001` capacity gap is **18,900 units**, or **7%**.
    - The binding plant is `PL003`.
    - The leading eligible supplier is Meridian Biologics.
    - The simulated data contains four threshold breaches.
    - The responses identify operational events as simulated.

> **Core solution complete**: Fabric, Microsoft Foundry, and Microsoft Copilot Studio return the same planning, supplier, and operational evidence. Continue with the optional extensions and ontology tasks.

## Analyze customer sentiment

This optional extension adds customer evidence to the already working launch-readiness agent without changing the core planning, supplier, and operational path.

**Estimated time:** 25 minutes.

### Create and load the customer database

Create the operational product and feedback tables so customer evidence uses the same Caldova product keys as the launch data.

1. Select **+ New item** in the Caldova workspace, search for **SQL database**, and create `caldova_customer_db`.

1. Open `caldova_customer_db`, and select **New query**.

1. Open `Downloads\L300-unify-data\code\01-create-customer-database.txt`.

    _The file starts with `SET NOCOUNT ON`, creates `dbo.product` and `dbo.customer_feedback`, loads the records, and ends with three validation queries._

1. Copy the code into the query editor, and select **Run**.

1. Confirm the run completed successfully:

    - The first result reports **25** products, matching `products.csv`.
    - The second result reports **16** feedback records.
    - The final result contains only `P101` with **6** records, `P104` with **5** records, and `P113` with **5** records.
    - After you refresh the database explorer, `dbo.product` and `dbo.customer_feedback` appear under **Tables**.

### Create the feedback shortcut

Make the submitted comments available to the Lakehouse as a read-only shortcut for sentiment analysis.

1. Return to `caldova_lakehouse`, and select **Get data** > **New shortcut**.

1. Select **Microsoft OneLake** > **SQL database**.

1. Select the current workspace and `caldova_customer_db`.

1. Select `customer_feedback`, retain the table name, and select **Create**.

1. Refresh **Tables**, open `customer_feedback`, and confirm:

    - The table has a shortcut icon.
    - It contains **16** rows mapped to `P101`, `P104`, and `P113`.
    - The `Sentiment` values can remain empty before scoring.

Fabric SQL automatically maintains the read-only OneLake analytical copy. Later scoring updates flow to the shortcut through mirroring.

### Configure Azure OpenAI credential

Create the managed identity credential that allows Fabric SQL to call the provided Azure OpenAI endpoint without storing an API key.

1. Open a new query in `caldova_customer_db`.

1. Open `Downloads\L300-unify-data\code\02-create-azure-openai-credential.txt`. The file creates the `Managed Identity` database-scoped credential used to call Azure OpenAI.

1. Replace each `<azure-openai-resource>` placeholder with the provided Azure OpenAI resource name.

1. Paste the updated code into the query editor, and select **Run**.

1. Expand **Security** > **Database scoped credentials**, and verify that the Azure OpenAI endpoint credential appears.

### Run sentiment scoring

Create and run the sentiment procedure so each mapped feedback record receives a validated sentiment label for later agent analysis.

1. Open `Downloads\L300-unify-data\code\03-create-sentiment-procedure.txt`. The file creates `dbo.score_feedback_sentiment`, calls `sp_invoke_external_rest_endpoint`, validates the returned label, and updates `dbo.customer_feedback`.

1. Replace `<azure-openai-resource>` with the provided Azure OpenAI resource name and `<deployment-name>` with the provided model deployment name.

1. Paste the updated code into a new query, and select **Run**.

1. Verify that `dbo.score_feedback_sentiment` appears under **Programmability** > **Stored procedures**.

1. Open `Downloads\L300-unify-data\code\04-score-customer-feedback.txt`. The file processes unscored records, checks for errors, and returns the sentiment counts. Copy the code into a new query, and select **Run**.

1. Confirm that the sentiment counts total **16**, every row has a valid `positive`, `negative`, `neutral`, or `mixed` value, and record the distribution for later comparisons.

### Add sentiment to the Fabric data agent

Add the feedback shortcut to the working agent, teach it how to use model-generated sentiment, validate the six `P101` labels, and republish.

1. Return to `caldova_lakehouse`. Wait for Fabric SQL mirroring to update the OneLake analytical copy, refresh **Tables**, and reopen the `customer_feedback` shortcut.

1. Confirm that all 16 rows contain `Sentiment` values and no rows contain an `AIError`.

1. Open `caldova_data_agent`, and select **Edit** to work on its draft configuration.

1. Edit the `caldova_lakehouse` source, and add `customer_feedback`.

> **Tip**: For easier copying, open `Downloads\L300-unify-data\code\07-add-sentiment-to-fabric-agent.txt`.

Copy **UPDATED LAKEHOUSE SOURCE INSTRUCTIONS**:

```prompt
launch_program has one row per launch and joins to product on ProductID. capacity_plan and batch join to launch_program on LaunchProgramID and to plant on PlantID. supplier joins to launch_program on LaunchProgramID and to product on ProductID. customer_feedback joins to product on ProductID and contains submitted comments. Sentiment is model-generated. Ignore customer_feedback rows where AIError is not null when analyzing sentiment. For eligible supplier comparisons, require a currently valid GMP certificate, zero open critical findings, fast-track eligibility, and enough qualified available capacity to cover the launch gap.
```

1. Replace the `caldova_lakehouse` **Data source instructions** with the preceding instructions, and save them.

Copy **SENTIMENT EXAMPLE**:

```input
What is the sentiment distribution for P101?
```

```sql
SELECT ProductID, Sentiment, COUNT(*) AS FeedbackCount
FROM dbo.customer_feedback
WHERE ProductID = 'P101'
  AND AIError IS NULL
GROUP BY ProductID, Sentiment
ORDER BY Sentiment;
```

1. Add the preceding question and SQL query to the Lakehouse source.

1. Save the draft, and ask:

    ```input
    What is the sentiment count and distribution for P101?
    ```

1. Expand the completed steps, and confirm that the response:

    - Uses `dbo.customer_feedback`.
    - Reports sentiment as model-generated.
    - Returns only valid sentiment labels whose counts total **6** for `P101`.
    - Matches the distribution recorded in `caldova_customer_db`.

1. Select **Publish**, publish the updated `caldova_data_agent`, and confirm that the published version returns the six-record `P101` sentiment distribution.

## Add customer-feedback enrichment to the Fabric data agent

Sentiment supplies the broad tone of customer feedback. In this task, enrichment adds an issue category and priority so the agent can identify specific `P101` concerns that could affect `LP001`.

**Estimated time:** 15 minutes.

### Run the enrichment notebook

Create an enriched feedback table that classifies each comment by issue and converts sentiment into a follow-up priority linked to the affected Caldova product.

1. Return to the Fabric workspace, and select **Import** > **Notebook** > **From this computer**.

1. Import `Downloads\L300-unify-data\notebooks\05-enrich-caldova-feedback.ipynb`.

1. Open the imported notebook, select **Add lakehouse**, select **Existing lakehouse**, and attach `caldova_lakehouse` as the default.

1. Select **Run all**.

1. Confirm these enrichment outcomes:

    - The final output reports:

        ```output
        Validation passed: 16 feedback records enriched and written to customer_feedback_enriched.
        ```

    - After you refresh **Tables** and open `customer_feedback_enriched`, the table contains 16 rows with `IssueCategory`, `ReviewPriority`, and `CategoryAIError`.
    - `IssueCategory` uses `delivery`, `packaging`, `instructions`, `support`, `scheduling`, or `other`.
    - Negative sentiment receives `high` priority, mixed sentiment receives `medium` priority, and positive or neutral sentiment receives `standard` priority.
    - The notebook retains the mapped `P101`, `P104`, and `P113` `ProductID` values.


### Add the enriched source and republish

Extend the Fabric data agent so it can identify which products have high-priority feedback, the issue categories involved, and the supporting record counts.

1. Open `caldova_data_agent`, and select **Edit** to work on its draft configuration.

1. Edit the `caldova_lakehouse` source, and add `customer_feedback_enriched`.

1. Add this source instruction:

    ```prompt
    customer_feedback_enriched has one row per feedback record and joins to product on ProductID. IssueCategory is AI-generated. ReviewPriority is derived from analytical fields. Ignore category results where CategoryAIError is not null, report the number of records behind summaries, and identify these fields as analytical enrichment rather than verified customer intent.
    ```

1. Add this example question and SQL query:

    ```input
    Which issue categories contain high-priority feedback for P101?
    ```

    ```sql
    SELECT ProductID, IssueCategory, COUNT(*) AS FeedbackCount
    FROM dbo.customer_feedback_enriched
    WHERE ProductID = 'P101'
      AND ReviewPriority = 'high'
      AND CategoryAIError IS NULL
    GROUP BY ProductID, IssueCategory
    ORDER BY FeedbackCount DESC, ProductID, IssueCategory;
    ```

    The query excludes failed classifications and retains the product key for explainable joins.

1. Save the draft, and ask:

    ```input
    For P101, which high-priority customer issue categories could affect LP001 readiness, and how many records support each category?
    ```

1. Expand the completed steps, and confirm that the agent:

    - Uses `customer_feedback_enriched`.
    - Joins product context through `ProductID`.
    - Returns `P101`, the issue category, and the record count for high-priority feedback.

1. Select **Publish**, publish the updated `caldova_data_agent`, and confirm that the published version includes the enriched table.

The enrichment doesn't change the capacity gap, binding plant, supplier evidence, or operational exceptions. It adds customer concern themes that the ontology relates to the existing launch evidence in the next task.

## Build an ontology and ontology-grounded Fabric data agent

As Caldova combines planning, feedback, supplier, and event data, implicit joins become harder to govern. In this task, you model those relationships in a Fabric ontology.

**Estimated time:** 30 minutes.

### Create and bind the eight entities

Bind eight ontology entities to governed Lakehouse and Eventhouse sources so reusable business concepts retain their keys, properties, and evidence classifications.

1. Return to the workspace, select **+ New item**, search for **Ontology**, and create `caldova_launch_ontology`.

1. Create the entity types and bind them as shown:

    | Entity type | Source item | Source table | Key property |
    |---|---|---|---|
    | `LaunchProgram` | `caldova_lakehouse` | `launch_program` | `LaunchProgramID` |
    | `Product` | `caldova_lakehouse` | `product` | `ProductID` |
    | `Plant` | `caldova_lakehouse` | `plant` | `PlantID` |
    | `CapacityPlan` | `caldova_lakehouse` | `capacity_plan` | `CapacityPlanID` |
    | `Batch` | `caldova_lakehouse` | `batch` | `BatchID` |
    | `Supplier` | `caldova_lakehouse` | `supplier` | `CMOID` |
    | `CustomerFeedback` | `caldova_lakehouse` | `customer_feedback_enriched` | `FeedbackID` |
    | `OperationalEvent` | `caldova_events` | `operational_events` | `EventID` |

1. Repeat these steps for each entity:

    1. Select **Add entity type** and enter the entity type name.

    1. Select **Bind data**.

    1. Select the source item and table from the binding table.

    1. Select the key property.

    1. Retain the identifier and descriptive properties needed for relationships and agent answers.

    1. Save the binding and inspect at least one instance.

1. Include these properties at minimum:

    | Entity type | Required properties |
    |---|---|
    | `LaunchProgram` | `LaunchProgramID`, `ProductID`, `TargetLaunchVolume`, `QualifiedCapacity`, `CapacityGapUnits`, `CapacityGapPercent`, `BindingConstraintPlantID`, `Status` |
    | `Product` | `ProductID`, `ProductName`, `TherapyArea`, `LifecycleStage` |
    | `Plant` | `PlantID`, `PlantName`, `Country`, `GMPStatus` |
    | `CapacityPlan` | `CapacityPlanID`, `LaunchProgramID`, `PlantID`, `AvailableCapacity`, `UtilizationPercent` |
    | `Batch` | `BatchID`, `LaunchProgramID`, `PlantID`, `ProductID`, `BatchStatus`, `ProductionVolume` |
    | `Supplier` | `CMOID`, `CMOName`, `LaunchProgramID`, `ProductID`, `GMPCertStatus`, `OpenCriticalFindings`, `QualifiedAvailableCapacityUnits`, `LeadTimeWeeks`, `FastTrackEligible`, `WeightedScore` |
    | `CustomerFeedback` | `FeedbackID`, `ProductID`, `FeedbackText`, `Sentiment`, `IssueCategory`, `ReviewPriority`, `CategoryAIError` |
    | `OperationalEvent` | `EventID`, `LaunchProgramID`, `ProductID`, `PlantID`, `CMOID`, `EventType`, `MetricName`, `MetricValue`, `Threshold`, `Severity`, `SourceSystem` |

1. Add concise descriptions that distinguish source facts from analytical or simulated values. For example:

    ```text
    CustomerFeedback represents a submitted synthetic exercise comment. Sentiment, IssueCategory, and ReviewPriority are analytical enrichment and can be wrong.
    ```

    ```text
    OperationalEvent represents simulated telemetry. Compare MetricValue with Threshold and don't describe an event as historical production evidence.
    ```

1. Confirm that the ontology contains exactly eight entity types and that each entity opens at least one instance.

For binding guidance, see [Data binding in ontology](https://learn.microsoft.com/fabric/iq/ontology/how-to-bind-data).

### Create the ontology relationships

Connect the eight entities with nine directed relationships so launch, product, plant, supplier, feedback, and operational evidence can be traversed explicitly.

| Relationship | From entity and property | To entity and property |
|---|---|---|
| `launches` | `LaunchProgram.ProductID` | `Product.ProductID` |
| `hasCapacityPlan` | `LaunchProgram.LaunchProgramID` | `CapacityPlan.LaunchProgramID` |
| `plannedAt` | `CapacityPlan.PlantID` | `Plant.PlantID` |
| `hasBatch` | `LaunchProgram.LaunchProgramID` | `Batch.LaunchProgramID` |
| `runsAt` | `Batch.PlantID` | `Plant.PlantID` |
| `evaluatesSupplier` | `LaunchProgram.LaunchProgramID` | `Supplier.LaunchProgramID` |
| `receivesFeedback` | `Product.ProductID` | `CustomerFeedback.ProductID` |
| `hasOperationalEvent` | `LaunchProgram.LaunchProgramID` | `OperationalEvent.LaunchProgramID` |
| `eventAtPlant` | `OperationalEvent.PlantID` | `Plant.PlantID` |

1. Select **Add relationship type**.

1. Enter the relationship name exactly as shown.

1. Select the source and target entities.

1. Map the source and target properties from the table.

1. Save the relationship.

1. Repeat until all nine relationships appear in the ontology graph.

1. Confirm these relationship outcomes:

    - An `LP001` instance resolves related instances through `launches`, `hasCapacityPlan`, `hasBatch`, `evaluatesSupplier`, and `hasOperationalEvent`.
    - The `hasCapacityPlan` > `plannedAt` path resolves the related plant instance.
    - The `receivesFeedback` relationship from product `P101` resolves related feedback instances.

1. Save and publish `caldova_launch_ontology`.

### Create and publish the ontology-grounded agent

Create and publish an ontology-grounded agent that answers cross-source launch-readiness questions through named relationships.

1. Return to the workspace, select **+ New item**, search for **Data agent**, and create `caldova_ontology_agent`.

1. Select **Add a data source**, add `caldova_launch_ontology`, and confirm that all eight entities and nine relationships appear.

1. Open **Agent instructions**, and enter:

    ```prompt
    You are Caldova's ontology-grounded launch-readiness assistant. Use the ontology entities and relationships to answer cross-source questions. For LP001, traverse launches, hasCapacityPlan, plannedAt, hasBatch, runsAt, evaluatesSupplier, receivesFeedback, hasOperationalEvent, and eventAtPlant as needed. Treat sentiment and issue classification as analytical enrichment and operational events as simulated evidence. State record counts, name the relationships used, separate facts from recommendations, and never treat a supplier result as procurement approval.
    ```

1. Save the instructions.

1. Ask:

    ```input
    For LP001, explain the capacity gap, binding plant, leading eligible supplier, related customer-feedback themes, and simulated operational breaches. Name the ontology relationships used.
    ```

1. Expand the completed steps, and confirm that the agent traverses multiple entities.

1. Select **Publish**, publish `caldova_ontology_agent`, and confirm its published state.

## Validate the ontology-grounded agent

Caldova needs proof that semantic relationships improve traceability without changing source facts. In this task, you compare direct and ontology-grounded answers for the same decisions.

**Estimated time:** 10 minutes.

### Run cross-source prompts

Compare direct and ontology-grounded answers to confirm that semantic traversal improves traceability without changing governed facts or required evidence qualifiers.

1. Open `caldova_data_agent` and `caldova_ontology_agent`.

1. Ask both agents:

    ```input
    For LP001, trace the launch to its product, binding plant, leading eligible supplier, customer-feedback issue categories, and simulated threshold breaches. State counts and identify the relationships or keys used.
    ```

1. Ask both agents:

    ```input
    Does the customer and operational evidence change the capacity-gap fact or the supplier eligibility result? Separate source facts, analytical enrichment, simulated evidence, and recommendation.
    ```

1. Record the results:

    | Criterion | Direct `caldova_data_agent` | `caldova_ontology_agent` |
    |---|---|---|
    | Capacity gap remains 18,900 units and 7% | Record result | Record result |
    | Binding plant remains `PL003` | Record result | Record result |
    | Leading eligible supplier remains Meridian Biologics | Record result | Record result |
    | Four simulated threshold breaches | Record result | Record result |
    | Sentiment and categories match current tables | Record result | Record result |
    | Product-to-feedback connection is traceable | Record keys used | Record relationship used |
    | Launch-to-event-to-plant path is traceable | Record keys used | Record relationships used |
    | Evidence types remain qualified | Record result | Record result |

1. Review the ontology agent's completed steps and comparison table:

    - The cross-source answer uses `receivesFeedback`, `hasOperationalEvent`, and `eventAtPlant`.
    - Both agents preserve the same governed facts even when their reasoning paths differ.

> **Ontology solution complete**: You now have direct and ontology-grounded agents that preserve the same governed facts through different reasoning paths.

## Summary

In this exercise, you:

- Built the Fabric planning foundation and streamed simulated operational events to Lakehouse and Eventhouse destinations.
- Built and published the initial Fabric data agent over planning, supplier, batch, plant, and operational evidence.
- Reviewed discovery, security, governance, and lineage in OneLake catalog.
- Grounded Foundry and Copilot Studio agents through the initial Fabric data agent and validated the same core evidence.
- Created the customer database and shortcut, scored sentiment, and extended the Fabric data agent with customer evidence.
- Added customer-feedback issue-category enrichment to the Fabric data agent.
- Built and validated an eight-entity, nine-relationship ontology and ontology-grounded agent.

You have successfully completed this exercise.

## Clean up

Now that you've finished the exercise, delete the cloud resources you created to avoid unnecessary resource usage. Preserve shared resources managed by the training environment.

**Estimated time:** 5 minutes.

1. Delete `Caldova launch readiness` in Microsoft Copilot Studio.

1. Open the [Azure portal](https://portal.azure.com/){:target="_blank"} at `https://portal.azure.com/`.

1. Delete the `caldova-foundry-<initials>-rg` resource group you created for the Foundry project.

1. Open the Caldova workspace in Fabric.

1. Select **Workspace settings** > **General** > **Remove this workspace**.

1. Enter the workspace name, confirm deletion, and verify that it no longer appears under **Workspaces**.

1. Don't delete the shared Fabric capacity, sentiment Azure OpenAI resource and deployment, Copilot Studio environment, or shared connections.
