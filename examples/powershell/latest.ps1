param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$DeviceId = "room-sensor-1"
)

Invoke-RestMethod -Uri "$BaseUrl/latest/$DeviceId"
