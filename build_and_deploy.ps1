# PowerShell script to deploy the app

# Define variables
$sourceDirectory = Get-Location
$deployUser = "christopher"
$deployHost = "192.168.1.217"
$deployPath = "/home/christopher/gimme/backend"
$deployLocation = "$deployUser@${deployHost}:$deployPath"

# Exclude the script file itself
$scriptName = $MyInvocation.MyCommand.Name

# Get the list of files to copy, excluding the script itself and folders other than 'torrent_plugins'
$filesToCopy = Get-ChildItem -Path $sourceDirectory -Recurse | Where-Object {
    $_.Name -ne $scriptName -and
    ($_.PSIsContainer -eq $false -or $_.FullName -like "*torrent_plugins*")
}

# Deploy the files using SCP
foreach ($file in $filesToCopy) {
    $relativePath = $file.FullName.Substring($sourceDirectory.Length + 1)
    $destinationPath = Join-Path -Path $deployPath -ChildPath $relativePath
    $destinationDirectory = Split-Path -Path $destinationPath -Parent

    # Create the remote directory if it does not exist
    ssh $deployUser@$deployHost "mkdir -p $destinationDirectory"

    # Copy the file
    scp $file.FullName "$deployLocation/"
}

Write-Output "Deployment completed successfully."
