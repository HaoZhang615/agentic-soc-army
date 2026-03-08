#!/bin/bash
# postprovision.sh — Write Bicep outputs to .env after azd provision
# azd automatically stores Bicep outputs as env vars; we extract them here.

set -euo pipefail

ENV_FILE=".env"
echo "Writing deployment outputs to ${ENV_FILE}..."

# The variables that Bicep outputs (and azd captures)
VARS=(
  AZURE_AI_PROJECT_ENDPOINT
  MODEL_DEPLOYMENT_NAME
  AZURE_AI_SEARCH_CONNECTION_NAME
  AZURE_AI_SEARCH_INDEX_NAME
  APPLICATIONINSIGHTS_CONNECTION_STRING
)

: > "${ENV_FILE}"

for var in "${VARS[@]}"; do
  value=$(azd env get-value "$var" 2>/dev/null || echo "")
  if [ -n "$value" ]; then
    echo "${var}=${value}" >> "${ENV_FILE}"
  fi
done

echo "Done — $(wc -l < "${ENV_FILE}") variable(s) written to ${ENV_FILE}"
