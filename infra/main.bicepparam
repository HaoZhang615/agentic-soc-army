using './main.bicep'

param resourceBaseName = 'agentic-soc'
param location = readEnvironmentVariable('AZURE_LOCATION', 'eastus2')
param projectName = 'agentic-soc'

// Model
param modelName = 'gpt-4.1'
param modelVersion = '2025-04-14'
param modelSkuName = 'GlobalStandard'
param modelCapacity = 30

// Optional: Azure AI Search (Notebook 04)
param deploySearch = false
param searchSku = 'basic'

// Optional: Application Insights (Notebook 05)
param deployMonitoring = false

// Optional: grant your user Azure AI Developer role
// Find your object ID: az ad signed-in-user show --query id -o tsv
param userPrincipalId = ''
param userPrincipalType = 'User'
