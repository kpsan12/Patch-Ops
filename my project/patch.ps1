# List of KB updates to download and install
$kbUpdates = @(
    "KB5048652",
    "KB5027538",
    "KB5030180",
    "KB5034275",
    "KB5032339",
    "KB5044091",
    "KB5020694",
    "KB5037036",
    "KB5041019"
)

# Function to download the update using kbupdate
function Download-Update {
    param (
        [string]$kbId
    )
    Write-Host "Downloading update $kbId..."
    $downloadCommand = "kbupdate -HotfixId $kbId -ComputerName localhost"
    Invoke-Expression $downloadCommand
}

# Function to install the MSU file using wusa.exe
function Install-Update {
    param (
        [string]$msuPath
    )
    Write-Host "Installing update $msuPath..."
    $installCommand = "wusa.exe `"$msuPath`" /quiet /norestart"
    Invoke-Expression $installCommand
}

# Main script to handle downloading and installation
foreach ($kb in $kbUpdates) {
    # Define the download path for the MSU file
    $msuFile = "C:\Users\Patchops-testing\Downloads\Patchops\my project\$kb.msu"
    
    # Check if the MSU file already exists, otherwise download
    if (-Not (Test-Path $msuFile)) {
        Download-Update -kbId $kb
    }

    # Ask user if they want to continue or stop after this update
    $userInput = Read-Host "Do you want to install $kb? (y/n)"
    
    if ($userInput -eq 'y') {
        Install-Update -msuPath $msuFile
    } else {
        Write-Host "Skipping $kb installation."
    }

    # Ask if user wants to continue with the next update
    $continueInput = Read-Host "Do you want to continue with the next update? (y/n)"
    
    if ($continueInput -ne 'y') {
        Write-Host "Exiting the update process."
        break
    }
}

Write-Host "Update process complete."
