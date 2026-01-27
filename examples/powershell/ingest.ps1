param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$PayloadPath = ".\examples\payloads\ingest_full.json"
)

$payload = Get-Content $PayloadPath -Raw | ConvertFrom-Json
$body = $payload | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "$BaseUrl/ingest" -ContentType "application/json" -Body $body
