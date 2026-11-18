# Pushes a branch of THIS project's own repository to origin as the GitHub account AbeneilMagpantay.
#
# This machine holds two GitHub logins. The token for AbeneilMagpantay is fetched for this
# process only and is never printed. Do NOT use `gh auth switch`: other projects on this
# machine rely on the other login staying active.
#
# Usage:  & '.\tools\git_push.ps1'            (pushes main)
#         & '.\tools\git_push.ps1' -Branch x
param([string]$Branch = 'main')

$proj = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $proj

$top = (git rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0 -or $top -ne ($proj -replace '\\', '/')) {
    Write-Output "ABORT: not at this project's own repository root (toplevel '$top')"
    exit 3
}

$tok = (gh auth token --user AbeneilMagpantay)
if ($LASTEXITCODE -ne 0 -or -not $tok) {
    Write-Output 'ABORT: no gh token for AbeneilMagpantay'
    exit 4
}
$env:GH_TOKEN = $tok
$tok = $null

$login = (gh api user --jq .login)
if ($login -ne 'AbeneilMagpantay') {
    $env:GH_TOKEN = $null
    Write-Output "ABORT: the token belongs to '$login'"
    exit 5
}

git -c credential.helper= -c "credential.helper=!gh auth git-credential" push -u origin $Branch
$pushCode = $LASTEXITCODE
$remote = (git -c credential.helper= -c "credential.helper=!gh auth git-credential" ls-remote origin "refs/heads/$Branch")
$env:GH_TOKEN = $null

if ($pushCode -ne 0) {
    Write-Output "PUSH FAILED (exit $pushCode)"
    exit 6
}

$local = (git rev-parse $Branch)
$remoteSha = ''
if ($remote) { $remoteSha = ($remote -split '\s+')[0] }
if ($remoteSha -eq $local) {
    Write-Output "PUSHED $Branch $local (origin matches)"
    exit 0
}
Write-Output "MISMATCH: local $local, origin '$remoteSha'"
exit 7
