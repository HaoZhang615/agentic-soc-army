# 🛡️ Agentic SOC Army

A hands-on notebook series for building a **multi-agent Security Operations Center (SOC) workflow** using **Microsoft Foundry Agent Service** and the **Azure AI Agents SDK**.

Each notebook is self-contained with a `MOCK_MODE` — cells marked 🔵 run without Azure credentials, cells marked 🔴 require a connected Foundry project.

---

## 📓 Notebooks

| # | Notebook | Topic | Key SDK |
|---|----------|-------|---------|
| 01 | [Multi-Agent SOC Architecture](notebooks/01_multi_agent_soc_architecture.ipynb) | Router-Worker pattern, Python-orchestrated multi-agent delegation | `AIProjectClient`, `responses.create()`, `PromptAgentDefinition` |
| 02 | [Advanced Tooling & MCP](notebooks/02_advanced_tooling_mcp.ipynb) | `FunctionTool`, `MCPTool`, `OpenApiTool` deep dive | `FunctionTool`, `MCPTool`, `OpenApiTool` |
| 03 | [State & Memory Management](notebooks/03_state_memory_management.ipynb) | Conversation persistence, shift handoff, long-term memory store | Conversation IDs, context injection |
| 04 | [Knowledge Bases & RAG](notebooks/04_knowledge_bases_rag.ipynb) | Vector stores, `FileSearchTool`, `AzureAISearchTool` | `FileSearchTool`, `AzureAISearchTool` |
| 05 | [Evaluation & Guardrails](notebooks/05_evaluation_guardrails.ipynb) | `azure-ai-evaluation`, red team, content filters, telemetry | `GroundednessEvaluator`, `AIProjectInstrumentor` |

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────┐
                        │       SOC Orchestrator          │
                        │  (ConnectedAgentTool router)    │
                        └───────┬──────────┬──────────────┘
                                │          │
               ┌────────────────┘          └────────────────┐
               ▼                                            ▼
  ┌────────────────────────┐              ┌────────────────────────────┐
  │  Threat Intel Agent    │              │  Alert Enrichment Agent    │
  │  FunctionTool:         │              │  FunctionTool:             │
  │  - lookup_ioc          │              │  - query_siem              │
  │  - map_to_mitre        │              │  - get_playbook            │
  └────────────────────────┘              └────────────────────────────┘
               │                                            │
               └──────────► RAG Knowledge Base ◄───────────┘
                            (Playbooks, TI Docs)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — fast Python package manager
- An [Azure AI Foundry](https://ai.azure.com) project with a deployed GPT-4o model
- (Optional) Azure AI Search index for enterprise RAG

### 1. Clone & Install

```bash
git clone <this-repo>
cd agentic-soc-army
uv sync                        # installs all dependencies from uv.lock
```

### 2. Configure `.env`

```bash
cp .env.example .env
# Edit .env with your Azure project details
```

Required:
```
AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 3. Run Notebooks

Open in VS Code or Jupyter:
```bash
uv run jupyter notebook notebooks/
```

Start with `01_multi_agent_soc_architecture.ipynb` — it works in MOCK_MODE without credentials.

---

## 📁 Project Structure

```
agentic-soc-army/
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
└── .github/
    └── agents/
        └── notebook-builder.agent.md  ← Custom VS Code Copilot agent
```

---

## 🔑 Key Concepts

| Concept | Description |
|---------|-------------|
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
