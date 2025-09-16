Write-Output "Fetching all dog breeds..."

try {
    # Use Invoke-RestMethod to fetch data from the Dog CEO API
    Invoke-RestMethod -Uri "https://dog.ceo/api/breeds/list/all" -OutFile "breeds.json"

    Write-Output "Data fetched successfully and saved to breeds.json"
}
catch {
    Write-Error "Error: Failed to fetch data."
}