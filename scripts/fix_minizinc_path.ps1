$miniZincDir = Join-Path $env:LOCALAPPDATA 'Programs\MiniZinc'
$miniZincExe = Join-Path $miniZincDir 'minizinc.exe'

if (-not (Test-Path $miniZincExe)) {
    Write-Error "No se encontro $miniZincExe. Instala MiniZinc primero."
    exit 1
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $userPath) {
    $userPath = ''
}

$parts = $userPath -split ';' | Where-Object { $_ -and $_.Trim() -ne '' }
if ($parts -notcontains $miniZincDir) {
    $newUserPath = ($parts + $miniZincDir) -join ';'
    [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
    Write-Output "MiniZinc agregado al PATH de usuario: $miniZincDir"
} else {
    Write-Output "MiniZinc ya estaba en PATH de usuario."
}

if ($env:Path -notlike "*$miniZincDir*") {
    $env:Path = $env:Path + ';' + $miniZincDir
}

Write-Output "Validacion inmediata:"
& $miniZincExe --version
