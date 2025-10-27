# scripts\set-openAI.sample.ps1
# Copy this to scripts\set-openAI.ps1 and replace YOUR_KEY without committing.
$env:OPENAI_API_KEY = "YOUR_KEY"
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $env:OPENAI_API_KEY, "User")
Write-Host "OPENAI_API_KEY set for this session and user scope."
