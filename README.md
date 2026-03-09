# Agentic SOC Army

A comprehensive multi-agent SOC (Security Operations Center) workflow demonstrating advanced AI patterns for security incident investigation. Built with **Microsoft Agent Framework** and **Microsoft Foundry**, this series of notebooks showcases agent orchestration, state management, hierarchical coordination, and production-grade guardrails.

## 🎯 Overview

This project uses **multi-agent architecture** to automate and enhance SOC workflows:
- **Foundation agents** for triage and investigation
- **Functional agents** with Model Context Protocol (MCP) tooling
- **RAG-powered agents** for threat intelligence search
- **Stateful agents** with conversation persistence
- **Router/worker patterns** for workload distribution
- **Hierarchical teams** with task coordination
- **Guardrails & evaluation** for production safety

All notebooks run against **Azure AI Search**, **Application Insights** tracing, and **mock/live threat data**.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.13+ (see [.python-version](.python-version))
- **OS**: Windows, Linux, or macOS
- **Package manager**: `uv` (recommended) or `pip`

### Azure Resources (minimal starting point)
- Azure subscription with billing enabled
- Microsoft Foundry account
- GPT-4.1 model deployment (auto-provisioned via Bicep)

### Local Development
- Git
- VS Code (recommended) with Jupyter notebook support
- Azure CLI (`az` command-line tool) for deployment

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/HaoZhang615/agentic-soc-army.git
cd agentic-soc-army

# Install dependencies
uv sync
```

### 2. Configure Infrastructure (Azure)

#### Option A: Automated (`azd`)
```bash
# Initialize Azure Dev
azd init --template agentic-soc-army

# Provision resources (one-time setup)
azd up

# This will:
# - Create resource group
# - Deploy Bicep template (AI Foundry, GPT-4.1, optional Search & Monitoring)
# - Write outputs to .env
```

#### Option B: Manual Deployment
```bash
# Create resource group
az group create --name my-soc-rg --location eastus2

# Deploy infrastructure
az deployment group create \
  --resource-group my-soc-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

### 3. Configure Environment

Copy the template and fill in Azure credentials:
```bash
cp .env.example .env
```

Populate `.env` with values from deployment outputs:
- `AZURE_AI_PROJECT_ENDPOINT` — from Bicep output
- `MODEL_DEPLOYMENT_NAME` — auto-set to `gpt-4.1`
- `AZURE_AI_SEARCH_CONNECTION_NAME` — optional, for Notebook 02
- `AZURE_AI_SEARCH_INDEX_NAME` — optional, for Notebook 02
- `APPLICATIONINSIGHTS_CONNECTION_STRING` — optional, enables tracing

**Note:** If deploying via `azd up`, these are automatically written to `.env`.

### 4. Launch Notebooks

Open and run notebooks in sequence using Jupyter or VS Code:

```bash
jupyter notebook
```

Or open directly in VS Code (native notebook integration).

## 📚 Notebook Sequence

### **Notebook 00: Foundation Investigation Thread**
**Goal:** Single-agent incident triage and investigation  
**Key Concepts:**
- Basic agent setup with GPT-4.1
- Alert ingestion and entity extraction
- Timeline generation for investigations
- Tracing setup (Application Insights integration)

**Outputs:** `data/investigation_00.json`

---

### **Notebook 01: SOC Tooling & MCP Functions**
**Goal:** Multi-agent coordination with external tools (Model Context Protocol)  
**Key Concepts:**
- MCP server integration (Sentinel KQL mock)
- Multi-agent collaboration patterns
- Tool registration and execution
- Agent-to-agent communication

**Optional Env:**
- `MCP_SERVER_URL` — external MCP server endpoint
- `MCP_SERVER_LABEL` — name of MCP service

**Outputs:** `data/investigation_01.json`

---

### **Notebook 02: RAG & Threat Intel Search**
**Goal:** Retrieve-Augmented Generation (RAG) for threat intelligence  
**Key Concepts:**
- Azure AI Search integration (optional)
- Mock RAG vs. live search modes
- Threat intelligence chunking and retrieval
- Fallback patterns for missing infrastructure

**Optional Env:**
- `AZURE_AI_SEARCH_CONNECTION_NAME` — activates live RAG mode
- `AZURE_AI_SEARCH_INDEX_NAME` — search index name

**Outputs:** `data/investigation_02.json`

---

### **Notebook 03: State Memory & Long-Running Conversations**
**Goal:** Persistent conversation state across resumption  
**Key Concepts:**
- Conversation history and memory management
- Session state persistence (in-memory + external)
- Background task simulation
- Conversation resumption patterns

**Optional Env:**
- `EXISTING_CONVERSATION_ID` — resume a prior conversation thread

**Outputs:** `data/investigation_03.json`

---

### **Notebook 04: Router & Worker Triage**
**Goal:** Scalable agent orchestration with routing  
**Key Concepts:**
- Router agent for workload distribution
- Worker agents specializing in different alert types
- Load balancing and delegation patterns
- Result aggregation and consensus

**Outputs:** `data/investigation_04.json`

---

### **Notebook 05: Hierarchical SOC Team (Microsoft Agent Framework)**
**Goal:** Multi-level agent hierarchy for enterprise SOC  
**Key Concepts:**
- Team-based coordination (manager, specialists)
- Hierarchical task decomposition
- Microsoft Agent Framework (MAF) orchestration
- Real-time tracing and observability
- Application Insights integration

**Requires:**
- `APPLICATIONINSIGHTS_CONNECTION_STRING` highly recommended for full tracing

**Outputs:** `data/investigation_05.json`

---

### **Notebook 06: Evaluation & Guardrails**
**Goal:** Production-grade quality gates and safety  
**Key Concepts:**
- Agent output evaluation (response quality, safety)
- Guardrails and constraint enforcement
- Automated quality scoring
- Test suite patterns for agents

**Outputs:** Test results and evaluation metrics

---

### **Notebook 07: Operationalization & Versioned Agents**
**Goal:** Package agents for production deployment  
**Key Concepts:**
- Agent versioning and registry patterns
- Configuration-driven deployment
- CI/CD-ready agent packaging
- Multi-version rollout strategies

**Outputs:** Deployment artifacts and version metadata

---

## 🏗️ Infrastructure Architecture

### Always Provisioned
```
AI Foundry Account
├── AI Foundry Project
├── GPT-4.1 Deployment (30 TPM)
└── Role assignments (Azure AI Developer)
```

### Optional (Enable in `infra/main.bicepparam`)

#### Azure AI Search (Notebook 02)
```
Azure AI Search Service
├── Connection via Foundry
├── Role assignment (Search Index Data Reader)
└── Suggested index: soc-threat-intel
```

#### Monitoring (All notebooks)
```
Log Analytics Workspace
├── Application Insights
├── Project connection (AppInsights)
└── Auto-discovered by SDK
```

### Deployment Via Bicep

- **Template:** [infra/main.bicep](infra/main.bicep)
- **Parameters:** [infra/main.bicepparam](infra/main.bicepparam)
- **Post-scripts:** [infra/postprovision.ps1](infra/postprovision.ps1) / [infra/postprovision.sh](infra/postprovision.sh)

Outputs are automatically saved to `.env` for notebook consumption.

## 📂 Project Structure

```
agentic-soc-army/
├── notebooks/                      # 8-step learning path
│   ├── 00_foundation_investigation_thread.ipynb
│   ├── 01_soc_tooling_mcp_functions.ipynb
│   ├── 02_rag_threat_intel_search.ipynb
│   ├── 03_state_memory_long_running.ipynb
│   ├── 04_router_worker_triage.ipynb
│   ├── 05_hierarchical_soc_team_maf.ipynb
│   ├── 06_evaluation_guardrails.ipynb
│   └── 07_operationalization_versioned_agents.ipynb
│
├── data/                           # Mock data + generated outputs
│   ├── alerts.json                 # Sample security alerts
│   ├── entity_risk.json            # Entity risk profiles
│   ├── network_events.json         # Mock network telemetry
│   ├── process_events.json         # Mock process telemetry
│   ├── signin_logs.json            # Mock auth events
│   ├── threat_intel_chunks.json    # Threat intel corpus
│   ├── playbook_chunks.json        # SOC playbook chunks
│   └── investigation_*.json        # Generated outputs (gitignored)
│
├── infra/                          # Infrastructure as Code (Bicep)
│   ├── main.bicep                  # Resource definitions
│   ├── main.bicepparam             # Parameter file (deployment config)
│   ├── postprovision.ps1           # Post-deploy script (Windows)
│   └── postprovision.sh            # Post-deploy script (POSIX)
│
├── src/                            # Shared Python utilities
│   └── soc_workshop/
│       ├── __init__.py             # Public API exports
│       ├── settings.py             # Centralized env var loading
│       ├── clients.py              # Azure AI auth & client setup
│       ├── incident_schema.py      # Type definitions
│       └── tools/                  # Mock tools for offline testing
│           ├── kql_mock.py         # KQL query simulator
│           ├── search_mock.py      # AI Search simulator
│           └── sentinel_mock.py    # Sentinel data mock
│
├── .env.example                    # Configuration template
├── .github/                        # CI/CD workflows (optional)
├── pyproject.toml                  # Python dependencies (uv/pip)
├── azure.yaml                      # Azure Dev CLI config
├── .gitignore                      # Git exclusions
└── README.md                       # This file
```

## 🔧 Development

### Install Dev Dependencies
```bash
uv sync  # Includes ipykernel, jupyter for notebook dev
```

### Environment Variables

**Required:**
- `AZURE_AI_PROJECT_ENDPOINT` — from `azd up` or Bicep outputs

**Optional (enable features):**
- `MCP_SERVER_URL` + `MCP_SERVER_LABEL` — MCP integration (Notebook 01)
- `AZURE_AI_SEARCH_CONNECTION_NAME` + `AZURE_AI_SEARCH_INDEX_NAME` — Live RAG (Notebook 02)
- `APPLICATIONINSIGHTS_CONNECTION_STRING` — Tracing (all notebooks)
- `EXISTING_CONVERSATION_ID` — Conversation resumption (Notebook 03)

### Running Offline

The notebooks **gracefully fall back to mock data** if optional resources are unavailable:
- Set `SOC_WORKSHOP_OFFLINE=1` to skip all live Azure calls
- Mock data auto-loads from [data/](data/) folder
- Perfect for local development & demos

### Debugging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Application Insights tracing is automatically captured if `APPLICATIONINSIGHTS_CONNECTION_STRING` is set.

## 🧪 Testing & Evaluation (Notebook 06)

Use `azure-ai-evaluation` framework to assess agent quality:
```python
from azure.ai.evaluation import evaluate

results = evaluate(
    data=test_cases,
    evaluators=[
        response_quality_evaluator,
        safety_evaluator,
        relevance_evaluator,
    ],
)
```

## 📦 Dependencies

### Core
- `agent-framework-azure-ai` — Microsoft Agent Framework for Azure AI
- `azure-ai-agents` — Agentic APIs
- `azure-ai-projects` — Microsoft Foundry SDK
- `azure-ai-evaluation` — Quality scoring
- `azure-identity` — Azure authentication

### Support
- `pandas`, `matplotlib`, `seaborn` — Data exploration & visualization
- `python-dotenv` — Environment configuration
- `azure-monitor-opentelemetry` — Tracing

See [pyproject.toml](pyproject.toml) for full dependency list and versions.

## 🔐 Security & Best Practices

- **Secrets**: Use `.env` (gitignored) for sensitive values
- **Authentication**: Azure Managed Identity or Service Principal (via `DefaultAzureCredential`)
- **RBAC**: Bicep grants minimal required roles per resource
- **Tracing**: All agent activity logged to Application Insights (if enabled)
- **Evaluation**: Validate outputs before production use (Notebook 06)

## 📈 Next Steps

1. **Run Notebook 00** → Understand single-agent patterns
2. **Run Notebooks 01–05** → Explore advanced agent coordination
3. **Run Notebook 06** → Evaluate agent quality
4. **Run Notebook 07** → Package for production
5. **Deploy** → Integrate into your SOC workflow

## 🐛 Troubleshooting

### `AZURE_AI_PROJECT_ENDPOINT` not found
```bash
# Verify .env is populated:
cat .env | grep AZURE_AI_PROJECT_ENDPOINT

# Re-run deployment:
azd up
```

### MCP Server not available
The notebooks gracefully skip MCP integration; mock tooling is used instead.

### Azure AI Search connection fails
Search is optional; notebooks fall back to mock retrieval.

### Application Insights tracing not appearing
Ensure `APPLICATIONINSIGHTS_CONNECTION_STRING` is set and valid. Check Azure Portal for logs.

## 📚 References

- [Microsoft Agent Framework Documentation](https://docs.microsoft.com/en-us/dotnet/api/microsoft.ai.agents)
- [Microsoft Foundry Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📄 License

[Add your license information here]

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a pull request

## 💬 Support & Questions

For issues, questions, or suggestions:
- Open a GitHub issue
- Check existing troubleshooting in notebooks
- Review Azure documentation
