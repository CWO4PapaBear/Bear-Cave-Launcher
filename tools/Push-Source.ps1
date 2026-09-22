param()
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$command = Get-Command git -ErrorAction SilentlyContinue
$gitExe = if ($command) { $command.Source } else { Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' }
if (-not (Test-Path -LiteralPath $gitExe)) { throw 'Install Git for Windows, then reopen PowerShell.' }
$remote = & $gitExe -C $root remote get-url origin
if ($LASTEXITCODE -ne 0 -or $remote -ne 'https://github.com/CWO4PapaBear/Bear-Cave-Launcher.git') { throw 'Unexpected repository remote.' }
$dirty = & $gitExe -C $root status --porcelain
if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'Review and commit pending source changes before pushing.' }
& $gitExe --no-pager -c http.sslBackend=openssl -C $root push -u origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed. Complete GitHub authentication and retry. No force push was attempted.' }
$localHead = & $gitExe -C $root rev-parse HEAD
$remoteHead = & $gitExe -c http.sslBackend=openssl -C $root ls-remote origin refs/heads/main
if ($LASTEXITCODE -ne 0 -or -not $remoteHead -or $remoteHead.Split()[0] -ne $localHead) { throw 'Push returned, but remote verification failed.' }
Write-Host "SOURCE PUSH VERIFIED: $localHead"
Write-Host 'Client release assets and PTR promotion are separate. No client update was published by this command.'
