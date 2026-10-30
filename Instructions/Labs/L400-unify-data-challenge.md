---
lab:
    title: 'Solve Caldova launch-readiness challenges with grounded agents'
    module: 'Unify your data and AI platform'
    description: 'Deliver three customer solutions: mirrored business data in Teams, real-time operational intelligence in Foundry, and ontology-grounded Litware integration.'
    duration: 360
    level: 400
    islab: true
    status: 'in-development'
    targetDate: '2026-11-30'
    primarytopics:
        - Microsoft Fabric
        - Microsoft Foundry
        - Microsoft Copilot Studio
        - Microsoft Teams
        - Fabric IQ
---

# Solve Caldova launch-readiness challenges with grounded agents

## Scenario

Caldova Pharmaceuticals prepares a next-generation therapy for launch while integrating Litware's manufacturing operations. The supplied plan for launch `LP001` has an 18,900-unit, 7% capacity gap and a binding constraint at plant `PL003`. Different teams need different ways to use the company's data.

You are the solution engineer. Implement these customer requests:

- **Business answers in Teams:** Commercial users need launch and customer information. Keep feedback in its transactional database and make it available without building a separate extract, transform, and load (ETL) pipeline.
- **Real-time operational answers in Foundry:** Operations needs a separate agent that combines the plan with production and supplier exceptions arriving through a stream.
- **Governed Litware integration:** Extend the business solution with acquired-company identifiers, qualification constraints, and interpreted customer feedback. Use shared business relationships to explain what Litware can realistically contribute.

Build distinct agents for the customer requests while reusing one Fabric workspace and its planning tables. The operational agent uses planning and streaming data, not customer feedback. The Litware solution extends the business agent, but doesn't require the operational agent's streaming sources.

## Objectives

After you complete this challenge, you're able to:

- Deliver a Teams agent grounded in planning data and mirrored transactional records.
- Apply real-time ingestion when the customer needs operational exception evidence.
- Connect a directly grounded Fabric data agent to a Foundry agent.
- Generate and persist sentiment with a Foundry model, then add issue enrichment.
- Resolve acquired-company identifiers and model qualified capacity through an ontology.
- Verify each solution's answers against its source data and preserve evidence limitations.

## Duration

**Estimated time:** 360 minutes for a self-paced learner.

| Solution | Minutes |
|---|---:|
| Business answers in Teams | 100 |
| Real-time operational answers in Foundry | 110 |
| Governed Litware integration | 135 |
| Clean up | 15 |
| **Total** | **360** |

Each solution includes the setup it needs. Keep the business solution available for the Litware extension. Complete cleanup after all three solutions.

> **Note**: Fabric data-agent, Fabric IQ, and ontology capabilities are in preview or active development. Portal labels can change. Use the linked documentation when your interface differs.

## Before you begin

Use your prepared Windows environment and assigned work or school account. You need familiarity with SQL, basic KQL, Fabric notebooks, Python execution in PowerShell, and agent configuration. No previous exercise is required.

Confirm that you can open Fabric, Foundry, Copilot Studio, and Teams with your assigned account. Have your Fabric capacity, Azure subscription and region, Copilot Studio environment, and resource ownership boundaries available. If an assigned value or access is missing, contact your environment provider.

The supplied notebooks populate the Lakehouse tables; you don't need to enter the planning data manually. The solutions reuse procedures and assets from the [L300 exercise](./L300-unify-data.md). When a linked reference shows an L300 package path, use the corresponding file in `Downloads\L400-unify-data`.

Use one workspace, `caldova-challenge-<initials>`, and one `caldova_lakehouse` throughout the challenge. Populate the planning tables once, then add only the sources each solution needs. Give each data agent its own source selection and instructions.

If you need to recover from an error, rerun notebooks only in your own workspace: they overwrite their named output tables. The customer-database script drops and recreates its two tables; use it again only for an intentional reset. Don't force-replay the event simulator merely because ingestion is delayed.

## Task 01: Deliver business answers in Teams

### Introduction

Commercial users want a Teams assistant that connects the launch plan with submitted customer feedback. The feedback remains in a transactional SQL database. The customer doesn't want another pipeline that exports and reloads that data for every update.

### Description

Build a business solution using notebook-populated planning tables, a Fabric SQL database, its automatically mirrored data, and a Lakehouse shortcut. Ground a Copilot Studio agent through a published Fabric data agent and make it available in Teams. This request doesn't need streaming, model-generated sentiment, or an ontology. **Estimated time:** 100 minutes.

### Success criteria

- The planning notebook validates 318 records across six tables.
- Fabric SQL contains 25 products and 16 submitted feedback records, including six for `P101`.
- A source update becomes visible through the Lakehouse shortcut without rerunning an ingestion notebook or exporting a file.
- The published agent returns the source-backed launch gap, binding plant, leading eligible supplier, and `P101` feedback count.
- A conversation with the installed Teams agent invokes the Fabric tool and returns accurate answers.

### Learning resource

- [L300 Lakehouse setup](./L300-unify-data.md#configure-the-environment).
- [L300 customer-database creation](./L300-unify-data.md#create-and-load-the-customer-database).
- [Automatic mirroring for Fabric SQL](https://learn.microsoft.com/fabric/database/sql/mirroring-overview).
- [Create a OneLake shortcut](https://learn.microsoft.com/fabric/onelake/shortcuts/create-onelake-shortcut).
- [Fabric data agents as Copilot Studio tools](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio-tool).
- [Teams and Microsoft Copilot channels](https://learn.microsoft.com/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams).

### Key tasks

#### Key task 01: Make transactional feedback available without an ETL pipeline

Populate the planning data quickly, then connect the transactional source. Verify that a change in the database propagates to the data the agent will query.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. Download [L400-unify-data.zip](https://raw.githubusercontent.com/MicrosoftLearning/mslearn-unify-data/main/Allfiles/L400-unify-data/L400-unify-data.zip){:target="_blank"} from `https://raw.githubusercontent.com/MicrosoftLearning/mslearn-unify-data/main/Allfiles/L400-unify-data/L400-unify-data.zip`. Extract it to `Downloads\L400-unify-data`. Confirm that `code`, `data`, `notebooks`, and `event-simulator` appear directly inside that folder.
1. Open [Fabric](https://app.fabric.microsoft.com/), select **Workspaces** > **+ New workspace**, and create `caldova-challenge-<initials>`. Under **Advanced**, select **Fabric** and your assigned capacity.
1. Select **Import** > **Notebook** > **From this computer**, and import `notebooks\curate_caldova_tables.ipynb`. In the notebook, select **Add data items** > **New lakehouse**, create `caldova_lakehouse` with schemas enabled, and attach it as default.
1. Select **Run all**. The notebook downloads the six supplied Caldova files and writes managed `dbo` tables. Confirm `Validation passed: 318 rows across six tables; all tested relationships are valid.`
1. In the same workspace, create a **SQL database** named `caldova_customer_db`. In **New query**, paste the SQL in `code\01-create-customer-database.txt`, starting at `SET NOCOUNT ON`, and run it. Confirm 25 products and 16 feedback records: six for `P101`, five for `P104`, and five for `P113`. Leave `Sentiment` empty.
1. In `caldova_lakehouse` **Explorer**, open the menu for **Tables** > **dbo**, select **New table shortcut**, and choose **Microsoft OneLake** under **Internal sources**. Select `caldova_customer_db` in this workspace, retain **Pass-through** authentication, and select its `dbo.customer_feedback` table. Name the shortcut `customer_feedback` and select **Create**. Wait for automatic mirroring and endpoint synchronization, then confirm 16 rows in `dbo.customer_feedback`.
1. In the writable SQL database query editor, run the following source update. It changes a submission channel, not the feedback population:

    ```sql
    UPDATE dbo.customer_feedback
    SET Channel = 'Email'
    WHERE FeedbackID = 4;

    SELECT FeedbackID, ProductID, Channel
    FROM dbo.customer_feedback
    WHERE FeedbackID = 4;
    ```

1. Open the Lakehouse **SQL analytics endpoint** and run the following query until the shortcut reflects `Email`:

    ```sql
    SELECT FeedbackID, ProductID, Channel
    FROM dbo.customer_feedback
    WHERE FeedbackID = 4;
    ```

    Refresh and wait if it still shows `Portal`. Don't rerun the planning notebook or copy the table to make the value appear.

1. Restore the original channel in the writable SQL database, then repeat the endpoint query and confirm that `Portal` returns:

    ```sql
    UPDATE dbo.customer_feedback
    SET Channel = 'Portal'
    WHERE FeedbackID = 4;
    ```

**Expected result:** Planning tables are populated, and a source update propagates to the shortcut without a learner-maintained ETL pipeline. The SQL database remains writable; the OneLake analytical copy and shortcut are read-only.

A shortcut is like a reference to the operational record, not another independently maintained customer list. It avoids an extra export pipeline, but you still account for synchronization delay before checking a recent change.

</details>

#### Key task 02: Publish the business data agent

Give the agent the joins and eligibility rules it needs to answer the commercial request. Use submitted feedback as evidence without inventing sentiment scores.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. Create a **Data agent** named `caldova_business_data_agent`. Add `caldova_lakehouse`, selecting `launch_program`, `product`, `plant`, `capacity_plan`, `batch`, `supplier`, and the `customer_feedback` shortcut.
1. Add these agent instructions:

    ```prompt
    You support Caldova business users. Use only the selected Lakehouse sources.
    Give source-backed launch, plant, supplier, and submitted-feedback facts.
    customer_feedback joins to product on ProductID and has one row per FeedbackID.
    If Sentiment is null, don't infer a stored score or treat it as neutral.
    Don't make clinical conclusions. Separate source facts from recommendations and never
    present supplier ranking as procurement approval.
    ```

1. Open `code\06-fabric-data-agent-snippets.txt`. Add its **Lakehouse source instructions** and two SQL examples to the Lakehouse source. Don't add its Eventhouse configuration; this solution has no streaming source.
1. Append this source instruction:

    ```prompt
    Use customer_feedback for submitted comments and counts, joining to product on
    ProductID. The shortcut reads mirrored transactional records. A null Sentiment
    means unscored, not neutral. Don't count feedback again by joining it to every
    supplier, batch, or capacity row.
    ```

1. Run the supplied launch and supplier example queries in the Lakehouse **SQL analytics endpoint**. Confirm the 18,900-unit, 7% gap, binding plant `PL003`, and Meridian Biologics as the leading eligible supplier. Eligibility requires a currently valid GMP certificate, zero open critical findings, fast-track eligibility, and capacity of at least 18,900 units.
1. Add this feedback-count example and run it directly:

    ```sql
    SELECT ProductID, COUNT(*) AS FeedbackCount
    FROM dbo.customer_feedback
    WHERE ProductID = 'P101'
    GROUP BY ProductID;
    ```

    The result must be `P101` with six records.

1. Ask the following question and inspect the completed SQL steps:

    ```input
    For LP001, summarize the capacity gap, binding plant, leading eligible supplier,
    and number of submitted feedback records for its product. Use source facts
    and distinguish any recommendation from an approved action.
    ```

1. Correct source instructions or example queries if an answer differs from the direct SQL results. Select **Publish** after the answer is accurate.

**Expected result:** The published data agent returns the launch facts, supplier result, and six-record `P101` feedback count. It doesn't invent sentiment, operational exceptions, or an ontology.

</details>

#### Key task 03: Deliver the business agent in Teams

Connect the published data agent to a business-facing experience and verify the installed channel.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. Open [Copilot Studio](https://copilotstudio.microsoft.com/) in your assigned environment. Select **Agents**, open the arrow next to **New agent**, and select **Agent** under **Optimize your business processes**. This agent type supports the Fabric IQ Data MCP tool. Name it `Caldova business readiness` and use the description `Answers launch-readiness and submitted customer-feedback questions using governed Caldova sources.`
1. Add these instructions:

    ```prompt
    Use the Caldova Fabric data tool for every Caldova data question. Pass the
    complete question and use only returned evidence. Give a brief business summary
    followed by supporting counts and limitations. Don't invent unavailable
    sentiment scores or treat supplier ranking as approval.
    ```

1. Open **Build** > **Tools** > **+**, search for **Fabric**, and select **Fabric IQ Data MCP**. Create or select your user connection when prompted. In **OneLake catalog**, select published `caldova_business_data_agent`.
1. Set the tool description to `Queries Caldova launch, product, plant, capacity, batch, supplier, and submitted customer-feedback data.` Select **User** authentication so the call uses your own Fabric access.
1. Ask the business question from the preceding key task in the test pane. Confirm that the Fabric tool is invoked and that its answers match the launch, supplier, and feedback SQL results.
1. Select **Publish**. Open **Channels** > **Teams and Microsoft Copilot**, select **Make agent available in Microsoft Copilot**, and select **Add channel**.
1. Select **See agent in Teams** > **Add**. In Teams, start a new conversation and ask the same business question. Complete any sign-in prompt and verify the source-backed results. In Microsoft 365 Copilot, select or @mention the installed agent and verify one product-feedback question.

**Expected result:** The agent works in Teams and Microsoft 365 Copilot through the published Fabric data agent. If installation or sign-in is blocked, contact your environment provider. Keep this workspace, database, shortcut, and agent for Task 03.

</details>

## Task 02: Deliver real-time operational answers in Foundry

### Introduction

Operations needs a different solution: production and supplier exceptions must inform a launch-readiness assistant in Foundry. A transactional feedback database doesn't satisfy this requirement because it doesn't contain the arriving operational events.

### Description

Reuse the populated planning tables and add Eventstream ingestion, an Eventhouse for querying exceptions, and a Lakehouse destination for retained history. Create a separate operational data agent and connect it to Foundry. This agent doesn't query customer feedback or use the Copilot Studio agent. **Estimated time:** 110 minutes.

### Success criteria

- The operational agent queries the existing six planning tables without reloading them.
- The Eventstream routes simulated events to Eventhouse and Lakehouse history.
- Eventhouse returns four simulated `LP001` threshold breaches.
- Lakehouse history contains 11 simulator rows after one priming event and one full replay, with four breaches.
- The Foundry agent invokes the operational data agent and returns accurate planning, supplier, and simulated exception evidence.

### Learning resource

- [L300 streaming configuration](./L300-unify-data.md#configure-streaming-data-and-detect-exceptions).
- [Eventhouse destination configuration](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database).
- [Lakehouse destination configuration](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-lakehouse).
- [L300 operational data-agent configuration](./L300-unify-data.md#build-tune-test-and-publish-a-fabric-data-agent).
- [L300 Foundry setup](./L300-unify-data.md#build-a-microsoft-foundry-agent).
- [Connect Foundry agents to Fabric IQ](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric-iq).
- [Portal steps for adding a published data agent](https://learn.microsoft.com/fabric/data-science/data-agent-foundry-fabric-iq).

### Key tasks

#### Key task 01: Supply the operational assistant with arriving events

Add the destinations required by the real-time use case to the existing workspace. Retain the planning and customer tables already present.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. Use the supplied simulator and code files at `Downloads\L400-unify-data`.
1. Open `caldova-challenge-<initials>` and confirm that `caldova_lakehouse` contains `launch_program`, `product`, `plant`, `capacity_plan`, `batch`, and `supplier`. Reuse these tables; don't rerun the planning notebook or create another workspace or Lakehouse.
1. Create an **Eventhouse** named `caldova_events`. In its default KQL database, create a **KQL Queryset** named `caldova_exception_queries`.
1. Open `code\05-operational-events.txt`. Run its table-creation command and JSON-mapping command separately, without the descriptive file heading.
1. Create an **Eventstream** named `caldova_operational_stream`. Add a **Custom endpoint** named `caldova-simulator`.
1. Add an **Eventhouse** destination with **Direct ingestion**, selecting this workspace's Eventhouse and KQL database. Connect the default stream to it.
1. Add a **Lakehouse** destination, select this workspace's `caldova_lakehouse` and its **dbo** schema, and create the table `operational_event_history`. Select **JSON**. Under **Advanced**, set **Minimum rows = 1** and **Maximum duration = 1 minute** (60 seconds). Connect the default stream to it and select **Publish**.
1. Select the custom endpoint's **Details** > **Event Hub** > **SAS Key Authentication**. Obtain **Connection string-primary key** and **Event hub name**. In PowerShell, run these commands to set process-local credentials and send a priming event:

    ```powershell
    Set-Location "$HOME\Downloads\L400-unify-data\event-simulator"
    $env:EVENTSTREAM_CONNECTION_STRING = (
        [System.Net.NetworkCredential]::new(
            '',
            (Read-Host 'Paste the complete Event Hub connection string-primary key' -AsSecureString)
        ).Password
    ).Trim()
    $env:EVENTSTREAM_ENTITY_NAME = (Read-Host 'Paste Event hub name').Trim()
    python .\replay_events.py --prime --delay-seconds 0
    ```

1. Confirm `Replay complete: 1 event sent.` In Eventstream **Live view**, configure the Eventhouse destination. Select the existing `operational_events` table, select **JSON**, enable **Use existing mapping**, select `operational_events_json`, and finish the wizard.
1. Run the full replay once, then remove the credential variables:

    ```powershell
    python .\replay_events.py
    Remove-Item Env:\EVENTSTREAM_CONNECTION_STRING
    Remove-Item Env:\EVENTSTREAM_ENTITY_NAME
    ```

    Expect `Replay complete: 10 events sent.` Keep the simulator state files. They prevent accidental replay; don't use `--force` to compensate for delayed ingestion.

1. Run the final threshold query from `05-operational-events.txt`. Confirm two `PL003` utilization breaches, one `PL003` quality-deviation breach, and one `CMO006` projected lead-time breach.
1. Open this Lakehouse's **SQL analytics endpoint** and run the following history query after the batching and synchronization delays:

    ```sql
    SELECT COUNT(*) AS SimulatorRows,
           SUM(CASE WHEN LaunchProgramID = 'LP001' AND MetricValue > Threshold
                    THEN 1 ELSE 0 END) AS ThresholdBreaches
    FROM dbo.operational_event_history
    WHERE SourceSystem = 'CaldovaLabSimulator';
    ```

    Expect 11 rows and four breaches. Wait and refresh if necessary; don't resend events. If counts are larger, inspect duplicate `EventID` values before continuing.

**Expected result:** Eventhouse supplies queryable operational exceptions, and Lakehouse retains the same stream's history. Don't count the two destinations as independent populations of events.

</details>

#### Key task 02: Connect the operational data agent to Foundry

Ground operational answers in both planning tables and event queries, without introducing an ontology for this focused requirement.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. In `caldova-challenge-<initials>`, create `caldova_ops_data_agent`. Select only the six Lakehouse planning tables and the Eventhouse `operational_events` table. Leave the business data agent unchanged; don't add its feedback shortcut or the duplicate Lakehouse event history to the operational agent.
1. Open `code\06-fabric-data-agent-snippets.txt`. Add its agent instructions, Lakehouse source instructions and SQL examples, and Eventhouse source instructions and KQL example to the corresponding configuration areas.
1. Ask the following question and inspect its completed SQL and KQL steps:

    ```input
    For LP001, summarize the capacity gap, binding plant, leading eligible supplier,
    and simulated threshold breaches. Separate facts from recommended actions.
    ```

    Verify the 18,900-unit, 7% gap, `PL003`, Meridian Biologics, and four simulated breaches against direct queries. Correct the affected source instructions or examples if the agent differs, then select **Publish**.

1. Open the [Foundry portal](https://ai.azure.com/) with **New Foundry** enabled. Create `caldova-operations-<initials>` in a new resource group named `caldova-operations-<initials>-rg`, using your assigned subscription and region.
1. Open **Build** > **Models**, select **Deploy** > **Deploy a base model**, and deploy `gpt-5-mini` or an environment-provider-approved comparable small reasoning model that supports Foundry Agent Service and Fabric IQ tool calling. Open **Build** > **Agents**, open the arrow next to **New agent**, and select **Build an agent**. Create `caldova_foundry_ops` and select your deployment in **Model** on its **Playground** tab.
1. Add these instructions:

    ```prompt
    You support Caldova operations. Use caldova_ops_data_agent for every
    Caldova data question. State source-backed capacity, plant, supplier, and event
    evidence. Label events as simulated. Distinguish facts from recommendations.
    Supplier ranking is not procurement approval. Don't invent clinical claims.
    ```

1. Select **Tools** > **Add** > **Browse all tools** > **Fabric IQ (OneLake Catalog)** > **Add tool**. Sign in with your assigned account, filter to **Data agent**, select published `caldova_ops_data_agent` from `caldova-challenge-<initials>`, and select **Add**.
1. Select **Save**, then ask the operational question in a new Foundry conversation. Confirm that the Fabric IQ call targets the operational data agent and returns the source-backed results.
1. Open workspace **Lineage view** and inspect the Eventstream's two destinations. In **OneLake catalog**, confirm that your planning, event, and data-agent items are discoverable with the expected access.

**Expected result:** The Foundry assistant answers operational questions using SQL and KQL evidence. Direct grounding is like giving the assistant indexed source binders: explicit keys and rules are sufficient for this focused request, while each added source creates instructions to maintain.

This solution is complete without the transactional feedback database or the Teams agent. If a data agent isn't listed in Foundry, confirm its published state, selected workspace, and signed-in account; contact your environment provider if it remains unavailable.

If a Fabric tool call times out, deploy your environment provider's approved background-mode-capable model in the operational Foundry project, using the model-deployment steps above. In **Playground**, select that deployment under **Model**, open the parameters icon, turn on **Background mode**, and save before retesting. The linked documentation lists supported models, including `gpt-5.4` and `gpt-5.5`. Don't replay the events to resolve an agent timeout.

</details>

## Task 03: Govern Litware integration through shared business context

### Introduction

Caldova's commercial and leadership teams now ask whether Litware can help the launch and which customer concerns need attention. Local product identifiers differ, nominal capacity can be unqualified or too late, and submitted comments don't yet have consistent analytical labels.

### Description

Extend the **business solution from Task 01**. Generate sentiment through Foundry and persist it in its Fabric SQL database. Add issue enrichment and Litware capacity evidence, model the relationships in an ontology, and update the business Teams agent to use an ontology-grounded data agent. This solution doesn't require Task 02's Foundry agent, Eventstream, or Eventhouse. **Estimated time:** 135 minutes.

The Litware files contain 31 fictional business records:

| CSV file | Rows | Grain and key |
|---|---:|---|
| `data\litware\litware_plant.csv` | 3 | One site; `LitwarePlantID`. |
| `data\litware\litware_product_mapping.csv` | 4 | One local product; `LitwareProductID`. |
| `data\litware\litware_capacity_plan.csv` | 18 | One site-product planning window; `LitwareCapacityPlanID`. |
| `data\litware\litware_product_qualification.csv` | 6 | One qualification snapshot; `LitwarePlantID` and `LitwareProductID`. |

Approved product mappings connect local identifiers to Caldova `P101`, `P104`, and `P113`. Some products have no approved mapping. Join capacity and qualification through both site and local product. Dates use ISO format; an empty mapped product represents null.

Use the fixed planning snapshot **November 1, 2026**, and `LP001` launch deadline **November 26, 2026**, not today's date. Qualification intervals and capacity-window endpoints are inclusive. Count a complete window only when:

- The product mapping and qualification are approved.
- The site is compliant and there are no open critical findings.
- Qualification covers the full window, and readiness starts no later than its first day.
- The window starts on or after the snapshot and ends on or before the launch deadline.

Don't prorate partially eligible windows. Capacity allocations are disjoint, product-specific reservations. `FinishedProductUnits` means finished-product-equivalent counts at the site's manufacturing stage. Fill Finish capacity isn't interchangeable with Packaging capacity.

### Success criteria

- All 16 feedback records have valid persisted sentiment, and the shortcut reflects those results.
- Issue enrichment retains all 16 records and their product keys, with valid categories and no classification errors.
- Litware's 31 source records produce 18 assessed windows with traceable qualification keys and exclusion reasons.
- The ontology contains 11 entity types and 13 bound relationship types, using only the Lakehouse planning, customer, and Litware sources.
- The ontology-grounded data agent and updated Teams agent return accurate customer counts and distinguish 54,000 nominal `P101` units from 12,000 eligible planned Packaging units.
- Answers preserve the original launch facts and don't invent a Caldova mapping for the unmapped product.

### Learning resource

- [Fabric SQL connections](https://learn.microsoft.com/fabric/database/sql/connect).
- [Foundry OpenAI endpoints and Microsoft Entra authentication](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/switching-endpoints).
- [L300 issue enrichment](./L300-unify-data.md#add-customer-feedback-enrichment-to-the-fabric-data-agent).
- [PySpark AI-function runtime compatibility](https://learn.microsoft.com/fabric/data-science/ai-functions/runtime-2-0-workarounds#configure-pyspark-ai-functions).
- [Bind ontology data](https://learn.microsoft.com/fabric/iq/ontology/how-to-bind-data).
- [Create and bind relationship types](https://learn.microsoft.com/fabric/iq/ontology/how-to-create-relationship-types).
- [Use ontology as Fabric data-agent context](https://learn.microsoft.com/fabric/data-science/data-agent-ontology-sources).

### Key tasks

#### Key task 01: Add interpreted customer evidence to the business solution

Use Foundry to generate sentiment only now that the customer needs interpreted feedback. Retain the database as the operational source rather than replacing it with a scored export.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. Open `caldova-challenge-<initials>`. Confirm that `caldova_customer_db` and the Lakehouse feedback shortcut each contain 16 records. Don't rerun the database-creation script.
1. In Foundry, create `caldova-enrichment-<initials>` in a new resource group named `caldova-enrichment-<initials>-rg`, using your assigned subscription and region. Deploy `gpt-5-mini` or an environment-provider-approved comparable small reasoning model that supports the OpenAI Responses API and the supplied client's `minimal` reasoning effort. This project and deployment are separate from Task 02's operational agent.
1. Record the deployment name and resource **OpenAI v1 endpoint**, such as `https://<resource>.openai.azure.com/openai/v1/`. Don't use a project `/api/projects/...` endpoint.
1. Open `caldova_customer_db` **Settings** > **Connection strings**. Record its writable **SQL database** server and database values, not the read-only **SQL analytics endpoint**.
1. Open PowerShell and prepare the supplied sentiment client:

    ```powershell
    Set-Location "$HOME\Downloads\L400-unify-data\code"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r .\requirements.txt
    az login
    ```

    Sign in with your assigned account. The script uses `DefaultAzureCredential` for Microsoft Entra tokens. If environment activation is blocked, contact your environment provider.

1. Enter the non-secret resource values at the prompts, then run the client:

    ```powershell
    $env:FABRIC_SQL_SERVER = (Read-Host 'Business SQL database server').Trim()
    $env:FABRIC_SQL_DATABASE = (Read-Host 'Business SQL database name').Trim()
    $env:FOUNDRY_OPENAI_BASE_URL = (Read-Host 'Foundry resource OpenAI v1 endpoint').Trim()
    $env:SENTIMENT_MODEL_DEPLOYMENT = (Read-Host 'Enrichment project sentiment deployment name').Trim()
    python .\score_feedback_foundry.py
    ```

    The client reads feedback, invokes the Foundry model with minimal reasoning effort, checks that the response completed, validates each returned label, and commits it to SQL. It retains successful scores when rerun and stops with an exception on failure.

1. Confirm `Validation passed: 16 feedback records scored through Foundry deployment ...`. Run this query in the writable SQL database to obtain the authoritative sentiment distribution:

    ```sql
    SELECT ProductID, Sentiment, COUNT(*) AS FeedbackCount
    FROM dbo.customer_feedback
    WHERE AIError IS NULL
    GROUP BY ProductID, Sentiment
    ORDER BY ProductID, Sentiment;
    ```

    Supported labels are `positive`, `negative`, `neutral`, and `mixed`. Counts total 16, including six for `P101`. Model-generated distributions can vary; use actual results, not predetermined positive or negative counts. Wait until the shortcut reflects all stored labels with null `AIError`.

1. Remove the process-local configuration and deactivate the environment:

    ```powershell
    Remove-Item Env:\FABRIC_SQL_SERVER, Env:\FABRIC_SQL_DATABASE,
        Env:\FOUNDRY_OPENAI_BASE_URL, Env:\SENTIMENT_MODEL_DEPLOYMENT
    deactivate
    ```

1. Import `notebooks\05-enrich-caldova-feedback.ipynb` into `caldova-challenge-<initials>`, attach `caldova_lakehouse` as default, and select **Run all**. This notebook includes the documented PySpark AI-function model settings for Runtime 2.0 compatibility, classifies issues through Fabric's built-in AI endpoint, and derives review priority from sentiment. It doesn't call your separate Foundry sentiment deployment.
1. Confirm `Validation passed: 16 feedback records enriched and written to customer_feedback_enriched.` Valid categories are `delivery`, `packaging`, `instructions`, `support`, `scheduling`, and `other`. Negative sentiment receives `high` priority, mixed receives `medium`, and positive or neutral receives `standard`.
1. Run this query in the Lakehouse SQL analytics endpoint to verify the issue counts:

    ```sql
    SELECT ProductID, IssueCategory, ReviewPriority, COUNT(*) AS FeedbackCount
    FROM dbo.customer_feedback_enriched
    WHERE ProductID = 'P101' AND CategoryAIError IS NULL
    GROUP BY ProductID, IssueCategory, ReviewPriority
    ORDER BY IssueCategory, ReviewPriority;
    ```

    The groups total six. If you also filter to high priority, no rows is a valid result when this run has no negative `P101` sentiment.

**Expected result:** Foundry sentiment is persisted in the existing SQL source, mirrored into OneLake, and enriched into 16 issue records. AI-generated interpretations don't change the source launch gap.

If rate-limited, wait and rerun the client; it retains completed rows. An invalid label is stored with null sentiment and an error. Resolve the model configuration and rerun rather than resetting the database. If you later change feedback or scores, rerun enrichment so its derived table isn't stale.

</details>

#### Key task 02: Integrate qualified Litware capacity

Keep local identifiers and exclusion evidence. An approved site alone doesn't establish that a specific product can be manufactured there in time.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. In the Lakehouse **Files**, create `litware` and upload the four CSV files from `data\litware` directly into that folder.
1. Import `notebooks\07-integrate-litware.ipynb` into `caldova-challenge-<initials>`, attach `caldova_lakehouse` as default, and select **Run all**.
1. Confirm that input validation completes before table writes. The notebook checks keys, references, mappings, dates, nonoverlapping windows, arithmetic, and expected synthetic outcomes. It creates a stable `QualificationID` from site and local product, separated by `|`.
1. Confirm five outputs: `litware_plant` (3), `litware_product_mapping` (4), `litware_capacity_plan` (18), `litware_product_qualification` (6), and `litware_capacity_assessment` (18). The assessment is a derived table over the same allocations, not an additional capacity population.
1. Run this query in the Lakehouse SQL analytics endpoint:

    ```sql
    SELECT CaldovaProductID, LitwarePlantID, PlantType, ExclusionReason,
           SUM(AvailableCapacityUnits) AS AvailableUnits,
           SUM(EligibleCapacityUnits) AS EligibleUnits
    FROM dbo.litware_capacity_assessment
    GROUP BY CaldovaProductID, LitwarePlantID, PlantType, ExclusionReason
    ORDER BY CaldovaProductID, LitwarePlantID;
    ```

1. Verify all six groups:

    | Site and local product | Nominal units | Interpretation |
    |---|---:|---|
    | `LPL001` / `LPR001` -> `P101` | 12,000 | Eligible planned Packaging capacity. |
    | `LPL002` / `LPR001` -> `P101` | 24,000 | Qualification Pending; also Fill Finish, not Packaging. |
    | `LPL003` / `LPR001` -> `P101` | 18,000 | Earliest readiness November 28, after its windows and launch. |
    | `LPL001` / `LPR002` -> `P104` | 9,000 | One open critical finding. |
    | `LPL002` / `LPR003` -> `P113` | 6,000 | Qualification expired October 31. |
    | `LPL003` / `LPR004` -> null | 3,000 | No approved Caldova mapping. |

**Expected result:** Of 54,000 nominal `P101` units across different manufacturing stages, 12,000 pass the supplied qualification and timing rules, all at Packaging. Those units are a potential mitigation, not verified end-to-end output. Materials, transfer timing, upstream throughput, and execution approval aren't provided.

</details>

#### Key task 03: Model the business relationships

Give agents shared definitions for the acquired-company joins, customer interpretations, and qualified-capacity rules. Include only sources needed for this business question.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. In `caldova-challenge-<initials>`, create an **Ontology** named `caldova_launch_ontology`.
1. Create and bind the following entity types. For each, select **Bind data**, choose the specified Lakehouse `dbo` table, set its entity key, retain properties required by relationships and answers, and review the source data preview.

    | Entity | Lakehouse table | Entity key |
    |---|---|---|
    | `LaunchProgram` | `launch_program` | `LaunchProgramID` |
    | `Product` | `product` | `ProductID` |
    | `Plant` | `plant` | `PlantID` |
    | `CapacityPlan` | `capacity_plan` | `CapacityPlanID` |
    | `Batch` | `batch` | `BatchID` |
    | `Supplier` | `supplier` | `CMOID` |
    | `CustomerFeedback` | `customer_feedback_enriched` | `FeedbackID` |
    | `LitwarePlant` | `litware_plant` | `LitwarePlantID` |
    | `LitwareProduct` | `litware_product_mapping` | `LitwareProductID` |
    | `LitwareQualification` | `litware_product_qualification` | `QualificationID` |
    | `LitwareCapacityPlan` | `litware_capacity_assessment` | `LitwareCapacityPlanID` |

    Retain the Caldova gap, plant, supplier-eligibility, and product properties. Retain customer sentiment, issue category, priority, and classification error. For Litware, retain the supplied columns, `QualificationID`, `EligibleCapacityUnits`, and `ExclusionReason`. Bind assessed capacity, not a second entity over the raw allocations.

1. Describe sentiment and issue categories as AI-generated, submitted comments as synthetic feedback, and Litware eligibility as a derived planning result. Define `EligibleCapacityUnits` with this task's fixed snapshot, full-window rules, and manufacturing-stage limitation.
1. Create and bind each relationship below. Select the origin and target entities and choose each entity's key property from the preceding table. Enable **Use mapping table?**, select the specified binding table, and map its origin and target columns to those properties. For `mapsToCaldovaProduct`, the binding column `CaldovaProductID` maps to the Product entity's `ProductID` property. Select **Save** for each relationship.

    | Relationship | Origin -> target | Binding table: origin key -> target key |
    |---|---|---|
    | `launches` | `LaunchProgram` -> `Product` | `launch_program`: `LaunchProgramID` -> `ProductID` |
    | `hasCapacityPlan` | `LaunchProgram` -> `CapacityPlan` | `capacity_plan`: `LaunchProgramID` -> `CapacityPlanID` |
    | `plannedAt` | `CapacityPlan` -> `Plant` | `capacity_plan`: `CapacityPlanID` -> `PlantID` |
    | `hasBatch` | `LaunchProgram` -> `Batch` | `batch`: `LaunchProgramID` -> `BatchID` |
    | `runsAt` | `Batch` -> `Plant` | `batch`: `BatchID` -> `PlantID` |
    | `evaluatesSupplier` | `LaunchProgram` -> `Supplier` | `supplier`: `LaunchProgramID` -> `CMOID` |
    | `receivesFeedback` | `Product` -> `CustomerFeedback` | `customer_feedback_enriched`: `ProductID` -> `FeedbackID` |
    | `mapsToCaldovaProduct` | `LitwareProduct` -> `Product` | `litware_product_mapping`: `LitwareProductID` -> `CaldovaProductID` |
    | `allocatedAtLitwarePlant` | `LitwareCapacityPlan` -> `LitwarePlant` | `litware_capacity_assessment`: `LitwareCapacityPlanID` -> `LitwarePlantID` |
    | `allocatesLitwareProduct` | `LitwareCapacityPlan` -> `LitwareProduct` | `litware_capacity_assessment`: `LitwareCapacityPlanID` -> `LitwareProductID` |
    | `governedByQualification` | `LitwareCapacityPlan` -> `LitwareQualification` | `litware_capacity_assessment`: `LitwareCapacityPlanID` -> `QualificationID` |
    | `qualifiesAtLitwarePlant` | `LitwareQualification` -> `LitwarePlant` | `litware_product_qualification`: `QualificationID` -> `LitwarePlantID` |
    | `qualifiesLitwareProduct` | `LitwareQualification` -> `LitwareProduct` | `litware_product_qualification`: `QualificationID` -> `LitwareProductID` |

1. Review the bound records and relationship columns: `LP001` resolves to `P101` and related Caldova evidence; `LPR001` maps to `P101`; allocations resolve to their own sites and qualifications. `LPR004` remains without a Caldova product relationship.
1. Confirm 11 entity types and 13 bound relationship types, with each binding saved. The next key task validates this context in a data agent; a materialized ontology graph isn't required.

**Expected result:** The ontology supplies shared vocabulary and relationships without a streaming dependency. It is like a manufacturing route map: connecting stations explains how they relate, but doesn't certify every route or make different stages' capacities interchangeable.

The ontology adds modeling and maintenance work. Its value here is reusable meaning across acquired identifiers and product-site qualifications; it doesn't replace the source calculation or permissions.

</details>

#### Key task 04: Deliver the ontology-grounded business answer

Use the shared business context to explain Litware's contribution and customer concerns in the business agent.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. In `caldova-challenge-<initials>`, create `caldova_ontology_data_agent`. In **Sources** > **Add sources** > **Add an ontology**, select `caldova_launch_ontology`. Review its 11 entities and underlying Lakehouse source. Use the preview runtime when available, as recommended by the ontology-context documentation.
1. Confirm that the bound Lakehouse tables are available for queries. Mount the underlying Lakehouse source to add source instructions and SQL examples. Select only the 11 ontology-bound tables, not streaming history or the raw feedback shortcut. Reuse the planning source instructions and two SQL examples from `code\06-fabric-data-agent-snippets.txt`, then add the customer and Litware guidance below.
1. Add these agent instructions:

    ```prompt
    Use the ontology context and its underlying Lakehouse for Caldova
    launch-readiness questions. The launch record is authoritative for the original
    gap and binding plant. Use litware_capacity_assessment for derived eligibility
    and join qualifications by QualificationID. Different manufacturing stages
    aren't interchangeable, and nominal capacity isn't eligible output. Don't
    invent a mapping for LPR004. Customer sentiment and issue categories are
    AI-generated, not verified intent. State supporting records and relationships.
    ```

1. Add the source guidance for customer counts:

    ```prompt
    customer_feedback_enriched has one row per FeedbackID and joins to product on
    ProductID. Its Sentiment comes from the scored SQL records through the shortcut;
    IssueCategory is AI-generated and ReviewPriority is derived. Use this table
    for customer summaries without joining to every supplier or capacity row.
    Exclude CategoryAIError failures from issue summaries and state excluded counts.
    Don't change launch facts based on customer tone.
    ```

1. Add this sentiment example over the ontology-bound feedback table. Its counts must match the persisted SQL distribution from the first key task:

    ```sql
    SELECT ProductID, Sentiment, COUNT(*) AS FeedbackCount
    FROM dbo.customer_feedback_enriched
    WHERE ProductID = 'P101'
    GROUP BY ProductID, Sentiment
    ORDER BY Sentiment;
    ```

1. Add the issue-count query from this task and the following capacity example:

    ```sql
    SELECT CaldovaProductID, LitwarePlantID, PlantType,
           SUM(AvailableCapacityUnits) AS NominalUnits,
           SUM(EligibleCapacityUnits) AS EligiblePlannedUnits
    FROM dbo.litware_capacity_assessment
    WHERE CaldovaProductID = 'P101'
    GROUP BY CaldovaProductID, LitwarePlantID, PlantType;
    ```

    Confirm nominal values of 12,000, 24,000, and 18,000 for the three sites. Only `LPL001` has eligible planned units: 12,000 at Packaging.

1. Ask the following question, inspect the queries and relationship context, and publish the data agent after it returns the source-backed result:

    ```input
    For LP001, explain whether Litware can eliminate the launch gap and which
    customer concerns need attention. Include product mapping, qualification,
    readiness, manufacturing stage, and feedback counts. Preserve original
    launch facts and distinguish evidence from recommendations.
    ```

    Expect the original 18,900-unit, 7% gap and `PL003`, the limited 12,000-unit planned Packaging contribution, and customer groups totaling six for `P101`. A 6,900-unit arithmetic remainder is conditional, not a verified revised launch gap.

1. In Copilot Studio, edit `Caldova business readiness`. Replace its direct business data-agent tool with published `caldova_ontology_data_agent`, retain **User** authentication, and describe the tool's acquired-product, qualification, capacity, and customer capabilities. Remove the old overlapping tool.
1. Update the Copilot Studio agent description and instructions to include acquired-company evidence, identify sentiment and categories as AI-generated, and distinguish planned capacity from approved outcomes. Continue using the Fabric tool for all Caldova questions.
1. Ask the integrated question in the test pane. Publish the change, then start a new conversation in Teams and verify the source-backed facts and counts. Check one integrated question in Microsoft 365 Copilot as well.
1. Ask `Which Caldova product does LPR004 represent?` in the ontology data agent. Confirm that it identifies the missing mapping rather than inventing a product.

**Expected result:** The ontology-grounded data agent and updated business agent explain the acquired-company contribution and customer concerns accurately, without depending on the operational solution. The original direct data agent remains a separate published item, but the Teams agent now calls the ontology-grounded item.

If context appears stale, refresh it in the data agent and inspect **Download ontology context** to confirm the bindings. Republish the data agent and downstream agent, then start a fresh conversation.

</details>

## Task 04: Clean up your solution resources

### Introduction

Remove the challenge agents and their resources without affecting shared services.

### Description

Delete the agents, deployments, dedicated resource groups, and Fabric workspace you created. **Estimated time:** 15 minutes.

### Success criteria

- Your Teams app and Copilot Studio agent are removed.
- Both learner-created Foundry projects and their deployments are removed.
- Your challenge Fabric workspace is removed.
- Shared capacities, environments, accounts, and connections remain unchanged.

### Key tasks

#### Key task 01: Remove only your challenge resources

Use the ownership boundaries supplied for your environment.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

1. In Teams, remove your installed `Caldova business readiness` app. Remove it from your Microsoft 365 Copilot agent list if it remains there.
1. In Copilot Studio, delete `Caldova business readiness`. Delete only connections you created exclusively for this challenge; retain shared connections and the assigned environment.
1. In Foundry, delete the model deployments you created in your operational and enrichment projects, including any approved substitute or timeout-recovery deployment. Delete `caldova_foundry_ops` if it isn't removed with its project.
1. In the [Azure portal](https://portal.azure.com/), delete your dedicated `caldova-operations-<initials>-rg` and `caldova-enrichment-<initials>-rg` resource groups. Don't delete any shared resource group.
1. In Fabric, remove `caldova-challenge-<initials>` through **Workspace settings** > **General** > **Remove this workspace**. Confirm its name before deletion.
1. Confirm the challenge workspace no longer appears in **Workspaces** and both dedicated resource groups are deleted or completing deletion. Verify that no challenge-owned model deployments remain outside them. Retain the shared Fabric capacity and Copilot Studio environment.
1. Close the PowerShell windows used for simulator credentials and scoring configuration. Remove the extracted package and virtual environment when you no longer need them.

**Expected result:** Your solution resources are removed, and shared services remain available.

</details>

## Summary

You delivered a business assistant using mirrored transactional data, a separate operational assistant using streamed exceptions, and an ontology-grounded extension for acquired-company context. Each solution uses the infrastructure needed for its customer request.

You have successfully completed this exercise. You verified each implemented experience against source evidence and removed your challenge resources.
