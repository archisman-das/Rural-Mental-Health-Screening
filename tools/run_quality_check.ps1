param(
    [string]$Input = (Join-Path $PSScriptRoot "..\data\screening_results.json"),
    [string]$Output = (Join-Path $PSScriptRoot "..\data\assessment_quality_report.json"),
    [double]$MinAccuracy = 0.70,
    [double]$MinMacroF1 = 0.70,
    [double]$MaxBrierScore = 0.25,
    [switch]$Strict,
    [int]$Mismatches = 10
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$qualityArgs = @(
    "tools/run_quality_check.py",
    "--input", $Input,
    "--output", $Output,
    "--mismatches", $Mismatches.ToString(),
    "--min-accuracy", $MinAccuracy.ToString([System.Globalization.CultureInfo]::InvariantCulture),
    "--min-macro-f1", $MinMacroF1.ToString([System.Globalization.CultureInfo]::InvariantCulture),
    "--max-brier-score", $MaxBrierScore.ToString([System.Globalization.CultureInfo]::InvariantCulture)
)

if ($Strict) {
    $qualityArgs += "--strict"
}

& python @qualityArgs
exit $LASTEXITCODE
