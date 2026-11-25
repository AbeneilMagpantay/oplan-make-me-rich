# Commit-and-push gate for this project's own repository. The coordinator runs it; workers never do.
#
#   & '.\tools\git_gate.ps1' -MessageFile <text file holding the commit message>
#
# It refuses to commit when:
#   - the kernel lock or the ledger chain does not verify (unless -SkipVerify, for mid-build snapshots);
#   - anything under data\ other than manifest.json, validation.json, symbols.json and the pinned
#     raw\exchange_info_*.json response is staged;
#   - a staged file is larger than 5 MB (25 MB for calibration artifacts);
#   - the private-detail scan (tools\scan_private.py) finds anything.
# After a successful commit it pushes the CURRENT branch with tools\git_push.ps1 (unless -NoPush).
# An unapproved kernel change is committed on its own branch; main carries only approved, verifying states.
param(
    [Parameter(Mandatory = $true)][string]$MessageFile,
    [switch]$SkipVerify,
    [switch]$NoPush
)

$proj = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $proj
$py = Join-Path $proj '.venv\Scripts\python.exe'

$top = (git rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0 -or $top -ne ($proj -replace '\\', '/')) {
    Write-Output "ABORT: not at this project's own repository root (toplevel '$top')"
    exit 3
}
if (-not (Test-Path -LiteralPath $MessageFile)) { Write-Output 'ABORT: message file not found'; exit 4 }

$lock = (& $py -m omr.kernel_lock verify)
$lockCode = $LASTEXITCODE
Write-Output ("lock:   " + ($lock -join ' | '))
$ledger = (& $py -m omr.ledger verify)
$ledgerCode = $LASTEXITCODE
Write-Output ("ledger: " + ($ledger -join ' | '))
if (-not $SkipVerify) {
    if ($lockCode -ne 0) { Write-Output 'ABORT: the kernel lock does not verify'; exit 5 }
    if ($ledgerCode -ne 0) { Write-Output 'ABORT: the ledger does not verify'; exit 6 }
}

git add -A
if ($LASTEXITCODE -ne 0) { Write-Output "ABORT: git add exit $LASTEXITCODE"; exit 7 }

$staged = @(git diff --cached --name-status)
if ($staged.Count -eq 0) { Write-Output 'nothing to commit'; exit 0 }
Write-Output '--- staged ---'
$staged | ForEach-Object { $_ }

$paths = @(git diff --cached --name-only --diff-filter=AM)
$keep = @('data/manifest.json', 'data/validation.json', 'data/symbols.json')
$bad = @($paths | Where-Object {
        $_ -match '^data/' -and $_ -notin $keep -and $_ -notmatch '^data/raw/exchange_info_[0-9TZ]+\.json$'
    })
if ($bad.Count -gt 0) { Write-Output 'ABORT: data files are staged:'; $bad; exit 8 }
# Calibration artifacts hold one record per simulated pair and may reach a few MB; everything else stays small.
$big = @($paths | Where-Object {
        $len = (Get-Item -LiteralPath (Join-Path $proj ($_ -replace '/', '\'))).Length
        if ($_ -match '^ledger/u?calibration_[0-9a-f]+.*\.json$') { $len -gt 25MB } else { $len -gt 5MB }
    })
if ($big.Count -gt 0) { Write-Output 'ABORT: a staged file is larger than its limit (5 MB; 25 MB for calibration artifacts):'; $big; exit 9 }

if ($paths.Count -gt 0) {
    $scan = (& $py -I (Join-Path $proj 'tools\scan_private.py') @paths)
    $scanCode = $LASTEXITCODE
    $scan | ForEach-Object { $_ }
    if ($scanCode -ne 0) { Write-Output 'ABORT: the private-detail scan found something; nothing was committed'; exit 10 }
}

git commit -q -F $MessageFile
if ($LASTEXITCODE -ne 0) { Write-Output "ABORT: commit exit $LASTEXITCODE"; exit 11 }
Write-Output ("committed: " + (git rev-parse HEAD))

if ($NoPush) { exit 0 }
$branch = (git rev-parse --abbrev-ref HEAD)
if ($LASTEXITCODE -ne 0 -or -not $branch -or $branch -eq 'HEAD') { Write-Output 'ABORT: no current branch to push'; exit 12 }
& (Join-Path $proj 'tools\git_push.ps1') -Branch $branch
exit $LASTEXITCODE
