---
lab:
    title: 'Prepare your environment'
    description: 'Confirm the tools, licenses, permissions, and cloud services required for the Caldova data agent labs.'
    islab: false
    status: 'in-development'
---

# Prepare your environment

Use this checklist before you start the labs in your own environment. The supported path uses a Windows computer, browser-based cloud services, and PowerShell for the event simulator.

For hosted delivery, the lab provider prepares the same tools, access, and settings before learners start. This page describes the required starting state, not the resources built during the exercises. Use it for environment preparation; licensing, software installation, and administrator approvals aren't part of the L400 challenge's six-hour duration.

## Prepare your computer

Use a Windows 11 computer with the following software and access:

| Requirement | Expected configuration |
|---|---|
| Web browser | Current Microsoft Edge with permission to sign in to the lab services, download files, and upload notebooks. |
| PowerShell | PowerShell 7, available from the Windows Start menu. |
| Python | Python 3.13, with `python` and its `pip` module available in PowerShell. |
| Local files | Write access to your `Downloads` folder, ZIP extraction through File Explorer, and a text editor for the supplied code files. |
| Package installation | Permission to install the event simulator's Python dependency in the interpreter used for the lab. |
| Network access | Access to Microsoft sign-in, Fabric, Microsoft Foundry, Copilot Studio, the Azure portal, GitHub raw downloads, and the Python package index over HTTPS. Permit outbound AMQP over TLS on TCP port 5671 to the Fabric eventstream custom endpoint. |

Install [PowerShell 7](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-windows) and [Python 3.13](https://www.python.org/downloads/windows/) before you start. Include `pip` and add Python to `PATH` during Python installation.

1. Open PowerShell and confirm the installed versions:

    ```powershell
    $PSVersionTable.PSVersion
    python --version
    python -m pip --version
    ```

1. Install the event simulator dependency from this repository's `main` branch:

    ```powershell
    python -m pip install --requirement https://raw.githubusercontent.com/MicrosoftLearning/mslearn-unify-data/main/Allfiles/L300-unify-data/event-simulator/requirements.txt
    ```

1. Confirm that the dependency is available:

    ```powershell
    python -m pip show azure-eventhub
    ```

The Fabric notebooks run in Fabric, not on your computer. You don't need a local Spark installation, SQL Server, Git, Visual Studio Code, or Azure CLI for the L300 exercise.

## Confirm licenses and permissions

Use a work or school Microsoft Entra account for the lab services. Use the same account and tenant for Fabric and Copilot Studio.

| Service | Required starting state |
|---|---|
| Microsoft Fabric | Access to an active, paid **F2 or higher Fabric capacity** in a region that supports the lab features. Your account can create a workspace and assign it to that capacity. Fabric Trial isn't the supported capacity for this lab's data-agent path. |
| Fabric workspace | Permission to create, edit, run, publish, and delete the lab's Lakehouse, notebooks, Eventhouse, KQL queries, Eventstream, SQL database, shortcuts, data agents, and ontology. Your account can read the underlying data and obtain the custom endpoint's connection details. |
| Fabric tenant settings | An administrator has enabled Fabric item creation, data-agent and Copilot features, and the AI functions and ontology features used by the exercise for your account and capacity. Required regional processing and storage settings are approved and enabled before delivery. |
| Microsoft Foundry and Azure | An active Azure subscription with permission to create and delete the lab resource group, Foundry resource and project, connections, and model deployment. The selected region supports the Fabric integration and `gpt-5-mini`, with available deployment quota. |
| Microsoft Copilot Studio | A licensed authoring account, access to a prepared environment with agent usage capacity, and permission to create, edit, connect tools to, test, publish, and delete agents. Include the Microsoft 365 Copilot license required by the documented Fabric data-agent integration. |
| Cross-service connections | Permission to create and use the Fabric connections in Foundry and Copilot Studio, with access to the Fabric data agent and its underlying sources. Organizational policies permit these connections and the associated data processing. |

The exercise creates the workspace, data, agents, and Foundry deployment. You don't need to create those items in advance.

Review the administrator requirements in [Fabric data agent tenant settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings). Complete these approvals before the lab rather than changing tenant policies during it.

## Prepare the L300 customer-feedback extensions

To complete the sentiment and enrichment tasks as well as the core path, prepare:

- An Azure OpenAI resource with a deployed chat-completion model that supports the lab's sentiment request, plus its resource name and deployment name.
- Access from Fabric SQL to the Azure OpenAI endpoint. The administrator responsible for role assignments can grant **Cognitive Services OpenAI User** on that resource to the Fabric SQL managed identity used by the database when you create it.
- Permission to create database-scoped credentials, tables, and stored procedures in the lab SQL database.
- A Fabric notebook runtime with the supplied `synapse.ml.spark.aifunc` module and permission to use its AI functions.
- Access to SQL database mirroring, OneLake shortcuts, and ontology creation in the selected Fabric region and capacity.

Azure OpenAI and AI-function usage must have approved billing and available quota. Use synthetic lab data only.

## Record your environment values

Keep the following non-secret values available for the exercise. In your own environment, record the resources and settings you prepared. In hosted delivery, the provider supplies these values.

| Value | What to record |
|---|---|
| Lab account | The work or school account and tenant used for the services. |
| Fabric capacity | The paid capacity name and region to select when you create the workspace. |
| Azure subscription | The subscription and supported region for the Foundry project and deployment. |
| Copilot Studio environment | The environment in which you create the agent. |
| Sentiment model (L300) | The prepared Azure OpenAI resource name and model deployment name for the L300 customer-feedback tasks. The L400 challenge creates its own Foundry sentiment deployment. |
| Cleanup boundary | The resources you own and can delete, and any shared resources that must remain. |

Don't record passwords, access tokens, or connection strings in this table. You obtain the eventstream connection details during the exercise and use them only in the current PowerShell session.

## Confirm readiness

- [ ] PowerShell 7, Python 3.13, `pip`, and the event simulator dependency are available.
- [ ] Browser sign-in and the required network connections are allowed.
- [ ] Your account has the required licenses, paid Fabric capacity access, and workspace-creation permissions.
- [ ] Required tenant settings, cross-service access, regional availability, and model quota are prepared.
- [ ] The customer-feedback prerequisites are prepared for the full exercise.
- [ ] Your environment values and resource ownership boundaries are recorded.

## Prepare for the L400 challenge

Prepare the common computer, Fabric, Foundry, and Copilot Studio requirements above and the additions below. The L400 challenge doesn't use the L300 extension's prepared Azure OpenAI resource, SQL managed-identity credential, or sentiment stored procedure. It uses a Foundry model called by a supplied Python client.

The solutions use distinct agents and source selections in one Fabric workspace. Planning tables are populated once and reused. Prepare access for all three solutions, but leave resource creation to the learner:

| Solution | Starting capability to prepare | Resources the learner builds |
|---|---|---|
| Business answers in Teams | Fabric SQL and OneLake shortcut access; Copilot Studio and Teams publication. | Challenge workspace, notebook-populated Lakehouse, transactional SQL database, shortcut, direct data agent, and Copilot Studio agent. |
| Real-time operational answers in Foundry | Eventstream connectivity; Eventhouse access; Foundry agent permissions and quota for `gpt-5-mini` or an approved compatible model. | Eventhouse, Eventstream, operational data agent, and Foundry project and agent, reusing the existing Lakehouse planning tables. |
| Governed Litware integration | Notebook AI functions; ontology access; local SQL client authentication; inference quota for `gpt-5-mini` or an approved compatible model. | Persisted sentiment, issue enrichment, Litware tables, ontology and data agent in the same workspace; a separate Foundry project and deployment for sentiment. |

| Requirement | Expected starting state |
|---|---|
| Local SQL client | Microsoft [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server) installed for the Python architecture. No local SQL Server installation is needed. |
| Developer authentication | [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed. The assigned identity can use `az login` and obtain Microsoft Entra tokens for Fabric SQL and model inference. PowerShell configuration permits virtual-environment activation. |
| SQL network and data access | Outbound TCP 1433 to the Fabric SQL database connection endpoint. The identity can create and populate its database, then read and update `dbo.customer_feedback` from Python through the writable SQL endpoint. |
| Fabric settings and capacity | Paid F2 or higher capacity with required item, data-agent, ontology, and AI-function settings enabled. Each data agent and its underlying source items use capacities in the same supported region. |
| Notebook runtime | Fabric Runtime 1.3 or later with `synapse.ml.spark.aifunc` available, and approved AI-function usage and billing for issue enrichment. The enrichment notebook includes the documented Runtime 2.0 model settings. |
| Foundry models and permissions | Supported region and quota for operational orchestration and sentiment inference deployments, using `gpt-5-mini` as the example or approved compatible replacements. The learner can create and delete two dedicated resource groups and projects, deploy models, and invoke the sentiment model through its resource OpenAI v1 endpoint. Prepare **Foundry User** for building and testing agents and **Foundry Project Manager** for creating the Fabric IQ connection. Include the runtime identity and any delegated user identities where required. Prepare model-inference access, such as **Cognitive Services OpenAI User**, including for resources the learner creates. |
| Long-running Foundry calls | Approve a background-mode-capable model and quota, such as `gpt-5.4` or `gpt-5.5`, for use if the Fabric data-agent call exceeds the synchronous timeout. Supply the approved model or deployment name and permit deployment in the learner's operational project. This is a timeout recovery path, not another required solution. |
| Cross-service identity | Same tenant across Fabric, Foundry, Copilot Studio, Teams, and Microsoft 365 Copilot. User-authenticated Fabric IQ calls have read access to the data agent and its underlying sources. Don't substitute a more privileged maker identity. |
| Teams and Microsoft 365 | Required authoring, usage, and Microsoft 365 Copilot licenses; access to both Teams and Microsoft 365 Copilot; permission to add the **Teams and Microsoft Copilot** channel and install the agent personally. Confirm the Copilot Studio **Agent** option under **Optimize your business processes** and its **Fabric IQ Data MCP** tool are available. Required Power Platform app policies and organizational approvals are completed beforehand. |
| Resource ownership | The learner can create one dedicated Fabric workspace and remove it at the end. Shared capacities, environments, and connections are identified and protected. |

Fabric SQL automatically mirrors supported tables into OneLake. Don't require Azure SQL Database or separate mirroring configuration. The business solution validates propagation of a source update through a shortcut; the ontology solution later adds sentiment in the same database.

Before delivery, verify sign-in, simulator dependency installation, local SQL authentication, model invocation, notebook AI functions, and personal Teams installation with an equivalent identity. Use disposable provider resources for checks requiring a database or model; don't prebuild the learner's solution. Supply the assigned account, capacity, subscription, region, Copilot Studio environment, cleanup boundary, and support contact through the environment's resource information panel.

Release the source assets and L400 ZIP to the repository's `main` branch before delivery. The setup dependency command, learner download, and curation notebook all use `MicrosoftLearning/mslearn-unify-data/main`. Confirm that those URLs return the released files; local files alone don't make these download paths available.

Check the [model retirement schedule](https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirement-schedule) before delivery. Treat `gpt-5-mini` as an example, not a permanent model requirement. Supply approved model choices and available quota for the assigned region. An operational replacement must support Foundry Agent Service and Fabric IQ tool calling. A sentiment replacement must support the OpenAI Responses API, the supplied client's `minimal` reasoning effort, and its output-token parameter. Verify a completed response with a valid sentiment label and an operational Fabric IQ call before approving a replacement. If the replacement requires different client parameters, update and retest the supplied client and package before delivery rather than asking learners to troubleshoot model compatibility. Don't use deprecated models unavailable to new customers, such as `gpt-4.1-mini`, as a new-subscription dependency.

The 360-minute allocation is an author estimate, not a pilot-verified duration. Reuse infrastructure without merging the agents' source scopes: the operational agent uses planning and streaming evidence, while the business and ontology agents use their relevant transactional and curated data. The ontology solution extends the business solution and doesn't require streaming sources. Validate all required service paths, reset procedures, cleanup, and self-paced timing before release.

Continue to either [Build an end-to-end Caldova data agent solution](./L300-unify-data.md) or [Solve Caldova launch-readiness challenges with grounded agents](./L400-unify-data-challenge.md). Download the corresponding learner package and create the lab resources as instructed there.
