# postprovision.ps1 — Write Bicep outputs to .env after azd provision
# azd automatically stores Bicep outputs as env vars; we extract them here.

$ErrorActionPreference = "Stop"

$envFile = ".env"
Write-Host "Writing deployment outputs to $envFile..."

# The variables that Bicep outputs (and azd captures)
$vars = @(
    "AZURE_AI_PROJECT_ENDPOINT"
    "MODEL_DEPLOYMENT_NAME"
    "AZURE_AI_SEARCH_CONNECTION_NAME"
    "AZURE_AI_SEARCH_INDEX_NAME"
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

$lines = @()
foreach ($var in $vars) {
    try {
        $value = azd env get-value $var 2>$null
    } catch {
        $value = ""
    }
    if ($value) {
        $lines += "${var}=${value}"
    }
}

$lines | Set-Content -Path $envFile -Encoding UTF8
Write-Host "Done — $($lines.Count) variable(s) written to $envFile"
