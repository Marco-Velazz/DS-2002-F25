# A variable to store the name of our input file
$DATA_FILE = "breeds.json"

# Check if the data file exists
if (-Not (Test-Path $DATA_FILE)) {
    Write-Error "Error: Data file '$DATA_FILE' not found. Please run fetch_data.ps1 first."
    exit 1
}

Write-Output "Processing data from '$DATA_FILE'..."

# Read the JSON file and convert to a PowerShell object
$json = Get-Content $DATA_FILE | ConvertFrom-Json

# Count the number of top-level keys under 'message'
$NUM_BREEDS = $json.message.PSObject.Properties.Count

# Print result
Write-Output "Total number of unique dog breeds: $NUM_BREEDS"
