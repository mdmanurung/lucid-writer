param(
    [ValidateSet("codex", "claude", "both")]
    [string]$Target = "both",
    [switch]$SkillOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$SkillSource = Join-Path $Root "skills\lucid-writer"

function Install-Skill([string]$Destination) {
    $Parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    if (Test-Path $Destination) {
        $Item = Get-Item -Force $Destination
        # A junction or symlink: delete the link only. Windows PowerShell 5.1's
        # Remove-Item -Recurse would follow it and empty the target directory.
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { $Item.Delete() }
        else { Remove-Item -Recurse -Force $Destination }
    }
    Copy-Item -Recurse -Force $SkillSource $Destination
    Write-Host "Installed skill -> $Destination"
}

function Install-AgentFiles([string]$SourceDirectory, [string]$DestinationDirectory, [string]$Filter) {
    New-Item -ItemType Directory -Force -Path $DestinationDirectory | Out-Null
    $Files = @(Get-ChildItem -Path $SourceDirectory -Filter $Filter -File)
    if ($Files.Count -eq 0) { throw "No subagent files found in $SourceDirectory" }
    foreach ($File in $Files) {
        $Destination = Join-Path $DestinationDirectory $File.Name
        Copy-Item -Force $File.FullName $Destination
        Write-Host "Installed subagent -> $Destination"
    }
}

function Install-Codex {
    Install-Skill (Join-Path $HOME ".agents\skills\lucid-writer")
    if (-not $SkillOnly) {
        Install-AgentFiles (Join-Path $Root ".codex\agents") (Join-Path $HOME ".codex\agents") "*.toml"
    }
}

function Install-Claude {
    Install-Skill (Join-Path $HOME ".claude\skills\lucid-writer")
    if (-not $SkillOnly) {
        Install-AgentFiles (Join-Path $Root "agents") (Join-Path $HOME ".claude\agents") "*.md"
    }
}

if ($Target -eq "codex") { Install-Codex }
elseif ($Target -eq "claude") { Install-Claude }
else { Install-Codex; Install-Claude }
