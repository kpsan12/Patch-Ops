# Define the input and output files
$inputFile = "output.txt"
$outputFile = "vuln.txt"

# Read the content of the file
$content = Get-Content $inputFile

# Initialize flag to start capturing lines after '[-] Missing patches:' and stop before '[I] KB with the most recent release date'
$capturing = $false
$vulnLines = @()

# Loop through each line and capture the relevant lines
foreach ($line in $content) {
    if ($line -match '^\[-\] Missing patches:') {
        $capturing = $true
    }
    elseif ($line -match '^\[I\] KB with the most recent release date') {
        $capturing = $false
    }
    
    if ($capturing) {
        $vulnLines += $line.Trim()
    }
}

# Save the extracted lines to vuln.txt
$vulnLines | Out-File $outputFile

# Confirm the extraction is done
Write-Host "Vulnerabilities extracted and saved to $outputFile"
