The following example illustrates how a SAS ODS RTF report is converted to TOON using the Python converter and then reconstructed as an RTF report. `Word Compare` can be used to verify that no differences are detected between the original and reconstructed reports.


```
$base = 'C:\dev\rtf_toon\RTF_benchmark\R_pharmaverse'
$run = Get-Date -Format 'yyyyMMdd-HHmmss'
$toon = "$base\toon\$run"
$rtf = "$base\new_rtf\$run"

New-Item -ItemType Directory -Path $toon,$rtf -Force | Out-Null

py 'C:\dev\rtf_toon\rtf_to_toon.py' "$base\original_rtf" $toon --version v9

Get-ChildItem -LiteralPath $toon -Filter '*.toon' -File | ForEach-Object {
    py 'C:\dev\rtf_toon\toon_to_rtf.py' $_.FullName (Join-Path $rtf ($_.BaseName + '_v9.rtf'))
}
```
