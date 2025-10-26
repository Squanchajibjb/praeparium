# scripts/run-water.ps1
# One-click regeneration for the Water pillar (Hub + Review + Guide)

# 1. Activate your virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Choose model
$env:PRAEPARIUM_MODEL = "gpt-4o"

# 3. Create output folder
mkdir .\out\brightline -Force | Out-Null

# 4. Generate all water articles
praeparium bundle-generate data\sourcepacks\water_ladder_hub.json --out out\brightline\
praeparium bundle-generate data\sourcepacks\water_containers.json --out out\brightline\
praeparium bundle-generate data\sourcepacks\sanitize_containers.json --out out\brightline\

# 5. Run QA
praeparium qa-report --path out\brightline\

Write-Host "`n✅ Water pillar build complete`n"
