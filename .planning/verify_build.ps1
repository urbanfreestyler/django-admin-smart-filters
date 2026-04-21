$ErrorActionPreference = "Stop"

$venvPath = Join-Path -Path $PWD -ChildPath ".temp-verify-venv"

Write-Host "Creating virtual environment at $venvPath"
python -m venv $venvPath

try {
    $pythonExe = Join-Path $venvPath "Scripts\python.exe"
    $pipExe = Join-Path $venvPath "Scripts\pip.exe"
    
    $whlFile = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
    if (-not $whlFile) {
        throw "No .whl file found in dist directory"
    }
    
    Write-Host "Installing wheel: $($whlFile.FullName)"
    & $pipExe install --quiet $whlFile.FullName
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed with exit code $LASTEXITCODE"
    }
    
    Write-Host "Verifying import..."
    $result = & $pythonExe -c "import django_admin_smart_filters; print('Success')"
    
    if ($result -eq "Success") {
        Write-Host "Package successfully installed and imported."
    } else {
        throw "Verification failed. Expected 'Success', got '$result'"
    }
} finally {
    Write-Host "Cleaning up virtual environment..."
    Start-Sleep -Seconds 1
    if (Test-Path $venvPath) {
        Remove-Item -Path $venvPath -Recurse -Force
    }
}
