$ErrorActionPreference = 'Stop'
$source = Join-Path (Split-Path $PSScriptRoot -Parent) 'L300-unify-data'
$destination = Join-Path $PSScriptRoot 'L400-unify-data.zip'
$temporary = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())

try {
    New-Item -ItemType Directory -Path $temporary | Out-Null
    foreach ($directory in @('code', 'data', 'notebooks', 'event-simulator')) {
        Copy-Item -LiteralPath (Join-Path $source $directory) -Destination $temporary -Recurse
    }
    foreach ($directory in @('code', 'notebooks')) {
        Copy-Item -Path (Join-Path $PSScriptRoot "$directory\*") -Destination (Join-Path $temporary $directory) -Recurse -Force
    }
    Get-ChildItem -LiteralPath $temporary -Directory -Recurse |
        Where-Object { $_.Name -in @('__pycache__', 'tests', '.venv') } |
        Sort-Object { $_.FullName.Length } -Descending |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
    Get-ChildItem -LiteralPath (Join-Path $temporary 'event-simulator') -File -Force |
        Where-Object { $_.Name -in @('.replay-prime.state', '.replay-full.state') } |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
    $readme = Join-Path $temporary 'data\litware\readme.md'
    if (Test-Path -LiteralPath $readme) {
        Remove-Item -LiteralPath $readme
    }
    Compress-Archive -Path (Join-Path $temporary '*') -DestinationPath $destination -Force
    Write-Output "Created $destination"
}
finally {
    if (Test-Path -LiteralPath $temporary) {
        Remove-Item -LiteralPath $temporary -Recurse -Force
    }
}
