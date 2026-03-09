// ──────────────────────────────────────────────────────────────────────────────
// Agentic SOC Army — Infrastructure
//
// Provisions the Azure resources required by the notebook series:
//   • AI Foundry account + project + GPT-4.1 deployment  (always)
//   • Azure AI Search + Foundry connection               (optional)
//   • Log Analytics + Application Insights                (optional)
//   • Role assignments for the deploying user             (optional)
//
// Deploy:
//   az deployment group create \
//     --resource-group <rg> \
//     --template-file infra/main.bicep \
//     --parameters infra/main.bicepparam
// ──────────────────────────────────────────────────────────────────────────────

targetScope = 'resourceGroup'

// ── Parameters ───────────────────────────────────────────────────────────────

@description('Base name used to derive all resource names (lowercase, no spaces).')
param resourceBaseName string

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Name of the AI Foundry project.')
param projectName string = 'agentic-soc'

@description('OpenAI model to deploy.')
param modelName string = 'gpt-4.1'

@description('Model version (region-dependent; check availability).')
param modelVersion string = '2025-04-14'

@description('Deployment SKU name.')
param modelSkuName string = 'GlobalStandard'

@description('Deployment capacity in thousands of tokens per minute.')
param modelCapacity int = 30

@description('Deploy Azure AI Search and create a Foundry connection (for Notebook 02).')
param deploySearch bool = false

@description('Azure AI Search SKU.')
@allowed(['free', 'basic', 'standard', 'standard2', 'standard3'])
param searchSku string = 'basic'

@description('Deploy Log Analytics + Application Insights (enables tracing for all notebooks).')
param deployMonitoring bool = false

@description('Object ID of the user or service principal to grant Azure AI Developer role. Leave empty to skip.')
param userPrincipalId string = ''

@description('Principal type for the role assignment.')
@allowed(['User', 'ServicePrincipal', 'Group'])
param userPrincipalType string = 'User'

// ── Variables ────────────────────────────────────────────────────────────────

var uniqueSuffix = uniqueString(resourceGroup().id, resourceBaseName)
var accountName = '${resourceBaseName}-${uniqueSuffix}'
var searchName = '${resourceBaseName}-search-${uniqueSuffix}'
var searchConnectionName = '${searchName}-connection'
var logAnalyticsName = '${resourceBaseName}-logs-${uniqueSuffix}'
var appInsightsName = '${resourceBaseName}-appins-${uniqueSuffix}'
var appInsightsConnectionName = 'appins-${uniqueSuffix}'
var deploymentName = modelName // match MODEL_DEPLOYMENT_NAME expected by notebooks

// Built-in role definition IDs
var azureAiDeveloperRoleId = '64702f94-c441-49e6-a78b-ef80e0188fee'
var searchIndexDataReaderRoleId = '1407120a-92aa-4202-b7e9-c0e197c71c8f'

// ── AI Foundry Account ───────────────────────────────────────────────────────

resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: accountName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: accountName
    allowProjectManagement: true
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

// ── AI Foundry Project ───────────────────────────────────────────────────────

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: account
  name: projectName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'Agentic SOC Army'
    description: 'Multi-agent SOC workflow notebooks'
  }
}

// ── GPT-4.1 Deployment ────────────────────────────────────────────────────────

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: deploymentName
  sku: {
    name: modelSkuName
    capacity: modelCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    raiPolicyName: 'Microsoft.Default'
  }
}

// ── Azure AI Search (optional) ───────────────────────────────────────────────

resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' = if (deploySearch) {
  name: searchName
  location: location
  sku: {
    name: searchSku
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
  }
}

// Foundry → AI Search connection (AAD-based)
resource searchConnection 'Microsoft.CognitiveServices/accounts/connections@2025-06-01' = if (deploySearch) {
  parent: account
  name: searchConnectionName
  properties: {
    category: 'CognitiveSearch'
    target: deploySearch ? 'https://${searchService.name}.search.windows.net' : ''
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: deploySearch ? searchService.id : ''
      location: location
    }
  }
}

// Grant Foundry MI → Search Index Data Reader
resource searchRoleFoundry 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deploySearch) {
  name: guid(searchService.id, account.id, searchIndexDataReaderRoleId)
  scope: searchService
  properties: {
    principalId: account.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexDataReaderRoleId)
    principalType: 'ServicePrincipal'
  }
}

// ── Monitoring (optional) ────────────────────────────────────────────────────

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = if (deployMonitoring) {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = if (deployMonitoring) {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: deployMonitoring ? logAnalytics.id : ''
  }
}

// Foundry Project → Application Insights connection (enables agent tracing)
resource appInsightsConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = if (deployMonitoring) {
  parent: project
  name: appInsightsConnectionName
  properties: {
    category: 'AppInsights'
    target: deployMonitoring ? appInsights.id : ''
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: deployMonitoring ? appInsights!.properties.InstrumentationKey : ''
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: deployMonitoring ? appInsights.id : ''
      location: location
    }
  }
}

// ── Role Assignments (optional) ──────────────────────────────────────────────

// Grant deploying user → Azure AI Developer on the Foundry account
resource userRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(userPrincipalId)) {
  name: guid(account.id, userPrincipalId, azureAiDeveloperRoleId)
  scope: account
  properties: {
    principalId: userPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', azureAiDeveloperRoleId)
    principalType: userPrincipalType
  }
}

// ── Outputs ──────────────────────────────────────────────────────────────────
// These map directly to the .env variables expected by the notebooks.

@description('AZURE_AI_PROJECT_ENDPOINT — used by all notebooks')
output AZURE_AI_PROJECT_ENDPOINT string = 'https://${account.properties.customSubDomainName}.services.ai.azure.com/api/projects/${project.name}'

@description('MODEL_DEPLOYMENT_NAME — used by all notebooks')
output MODEL_DEPLOYMENT_NAME string = modelDeployment.name

@description('AZURE_AI_SEARCH_CONNECTION_NAME — used by Notebook 04 (empty if search not deployed)')
output AZURE_AI_SEARCH_CONNECTION_NAME string = deploySearch ? searchConnection.name : ''

@description('AZURE_AI_SEARCH_INDEX_NAME — the index itself is created at query time; this is a suggested default')
output AZURE_AI_SEARCH_INDEX_NAME string = 'soc-threat-intel'

@description('APPLICATIONINSIGHTS_CONNECTION_STRING — enables agent tracing across all notebooks (empty if monitoring not deployed)')
output APPLICATIONINSIGHTS_CONNECTION_STRING string = deployMonitoring ? appInsights!.properties.ConnectionString : ''
