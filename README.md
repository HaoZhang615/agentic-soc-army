# 🛡️ Agentic SOC Army

A hands-on notebook series for building a **multi-agent Security Operations Center (SOC) workflow** using the **Microsoft Agent Framework**, **Azure AI Foundry Agent Service**, and the **Azure AI Agents SDK**.

Each notebook requires a deployed Azure AI Foundry project. Run `azd up` to provision infrastructure before running notebooks.

---

## 📓 Notebooks

| # | Notebook | Topic | Key SDK |
|---|----------|-------|---------|
| 01 | [Multi-Agent SOC Architecture](notebooks/01_multi_agent_soc_architecture.ipynb) | True Router-Worker pattern via Agent Framework `GroupChatBuilder` | `GroupChatBuilder`, `AzureOpenAIResponsesClient`, `@tool` |
| 02 | [Advanced Tooling & MCP](notebooks/02_advanced_tooling_mcp.ipynb) | `FunctionTool`, `MCPTool`, `OpenApiTool` deep dive | `FunctionTool`, `MCPTool`, `OpenApiTool` |
| 03 | [State & Memory Management](notebooks/03_state_memory_management.ipynb) | Conversation persistence, shift handoff, long-term memory store | Conversation IDs, context injection |
| 04 | [Knowledge Bases & RAG](notebooks/04_knowledge_bases_rag.ipynb) | Vector stores, `FileSearchTool`, `AzureAISearchTool` | `FileSearchTool`, `AzureAISearchTool` |
| 05 | [Evaluation & Guardrails](notebooks/05_evaluation_guardrails.ipynb) | `azure-ai-evaluation`, red team, content filters, telemetry | `GroundednessEvaluator`, `AIProjectInstrumentor` |

---

## 🏗️ Architecture

```
                  ┌──────────────────────────────────────┐
                  │     SOC Router (selection_func)     │
                  │  (Deterministic routing via         │
                  │   GroupChatBuilder)                 │
                  └──────┬──────────┬──────────┬────────┘
                         │          │          │
            ┌────────────┘          │          └──────────────┐
            ▼                       ▼                         ▼
  ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐
  │ Threat Intel      │  │ Alert Enrichment   │  │ SOC Reporter     │
  │ Worker            │  │ Worker             │  │                  │
  │ @tool:            │  │ @tool:             │  │ Synthesises      │
  │ - lookup_ioc      │  │ - query_siem       │  │ findings into    │
  │ - siem_query      │  │ - mitre_map        │  │ final triage     │
  └──────────────────┘  │ - get_playbook      │  │ report           │
                        └────────────────────┘  └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — fast Python package manager
- [Azure Developer CLI (`azd`)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) — for one-command infrastructure provisioning
- An Azure subscription with permission to create resources
- (Optional) Azure AI Search index for enterprise RAG

### 1. Clone & Install

```bash
git clone <this-repo>
cd agentic-soc-army
uv sync                        # installs all dependencies from uv.lock
```

### 2. Provision Azure Infrastructure

The repo uses [Azure Developer CLI (`azd`)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) for one-command provisioning.

```bash
azd auth login
azd up            # provisions Foundry account + project + GPT-4.1 model
```

`azd up` will prompt for a subscription and location, deploy the Bicep infrastructure, and auto-populate your `.env` file via a postprovision hook.

**Optional resources** — edit `infra/main.bicepparam` before deploying:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `deploySearch` | `false` | Set `true` to provision Azure AI Search + Foundry connection (Notebook 04) |
| `deployMonitoring` | `false` | Set `true` to provision Application Insights + Log Analytics (Notebook 05) |
| `userPrincipalId` | `''` | Your AAD object ID — grants Azure AI Developer role (`az ad signed-in-user show --query id -o tsv`) |

### 3. Configure `.env`

If you used `azd up`, the `.env` file is auto-populated by the postprovision hook — **no manual step needed.**

To configure manually instead:
```bash
cp .env.example .env
# Fill in values from the Azure portal or azd env get-values
```

### 4. Run Notebooks

Open in VS Code or Jupyter:
```bash
uv run jupyter notebook notebooks/
```

Start with `01_multi_agent_soc_architecture.ipynb` — requires a deployed Azure AI Foundry project (`azd up`).

---

## 📁 Project Structure

```
agentic-soc-army/
├── azure.yaml                  ← azd manifest (infra-only, postprovision hooks)
├── infra/
│   ├── main.bicep              ← Azure infrastructure (Foundry, Search, AppInsights)
│   ├── main.bicepparam         ← Deployment parameters
│   ├── postprovision.sh        ← Auto-populates .env on Linux/macOS
│   └── postprovision.ps1       ← Auto-populates .env on Windows
├── notebooks/
│   ├── 01_multi_agent_soc_architecture.ipynb
│   ├── 02_advanced_tooling_mcp.ipynb
│   ├── 03_state_memory_management.ipynb
│   ├── 04_knowledge_bases_rag.ipynb
│   ├── 05_evaluation_guardrails.ipynb
│   └── data/
│       ├── sample_alerts.json          ← 5 realistic SOC alerts
│       ├── ir_playbook_credential_attack.md  ← IR runbook for RAG
│       └── threat_intel_reference.md   ← TI reference for RAG
├── .env.example
├── pyproject.toml              ← Dependencies (uv sync)
└── .github/
    └── agents/
        └── notebook-builder.agent.md  ← Custom VS Code Copilot agent
```

---

## 🔑 Key Concepts

| Concept | Description |
|---------|-------------|
| **GroupChatBuilder** | Agent Framework orchestration — deterministic `selection_func` routes worker agents based on alert severity and IOC presence |
| **AzureOpenAIResponsesClient** | Stateless Azure OpenAI Responses API client — supports runtime tool injection and structured output, used by `GroupChatBuilder` for dynamic speaker selection |
| **@tool decorator** | Agent Framework decorator that infers JSON Schema from `Annotated` function signatures |
| **Conversation** | Persistent multi-turn context — `conversation.id` survives across Python sessions |
| **Responses API** | `openai_client.responses.create()` — single call replaces threads + runs |
| **FunctionTool** | Python functions exposed as agent tools — explicit JSON Schema, manual `FunctionCallOutput` loop |
| **FileSearchTool** | Built-in vector store RAG — upload docs, auto-indexed, citations returned |
| **AzureAISearchTool** | Enterprise-scale search over existing Azure AI Search indices |
| **MCPTool** | Connect to MCP servers for external tool access (requires approval flow) |
| **Groundedness** | Key eval metric for SOC agents — hallucinated containment steps = dangerous |

---

## 🔒 Security Notes

- All tool functions are read-only by design — no destructive SIEM operations
- `DefaultAzureCredential` — no hardcoded secrets, managed identity in production
- Content filters configured for **Strict** jailbreak + prompt injection detection
- Red team evaluation included in Notebook 05 before any production deployment
