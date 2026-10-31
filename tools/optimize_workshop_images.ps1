# Deterministic export/compression only. No generated content or artwork edits.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$modRoot = Split-Path -Parent $PSScriptRoot
$originalCover = Join-Path $modRoot 'thumbnail-original.png'
$activeCover = Join-Path $modRoot 'thumbnail.png'
$expectedOriginal = 'B52FE002FC92D7344B187AB93A904D234D9EAF15A5080977394028730A630CBA'
if (-not (Test-Path -LiteralPath $originalCover)) {
    if ((Get-FileHash -LiteralPath $activeCover -Algorithm SHA256).Hash -ne $expectedOriginal) {
        throw 'Original cover differs; preserve and review before optimizing.'
    }
    Copy-Item -LiteralPath $activeCover -Destination $originalCover
}
if ((Get-FileHash -LiteralPath $originalCover -Algorithm SHA256).Hash -ne $expectedOriginal) {
    throw 'Original cover hash changed.'
}
$jpegEncoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
$records = [System.Collections.Generic.List[object]]::new()
function Export-UploadImage {
    param([string]$Source, [string]$Destination, [int]$MaxWidth, [bool]$Png)
    $inputImage = [System.Drawing.Image]::FromFile($Source)
    $bitmap = $null
    $canvas = $null
    $encoderOptions = $null
    try {
        $width = [Math]::Min($MaxWidth, $inputImage.Width)
        $height = [int][Math]::Round($inputImage.Height * $width / $inputImage.Width)
        $bitmap = [System.Drawing.Bitmap]::new($width, $height, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
        $canvas = [System.Drawing.Graphics]::FromImage($bitmap)
        $canvas.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        $canvas.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $canvas.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $canvas.DrawImage($inputImage, [System.Drawing.Rectangle]::new(0, 0, $width, $height))
        if ($Png) {
            $bitmap.Save($Destination, [System.Drawing.Imaging.ImageFormat]::Png)
        } else {
            $encoderOptions = [System.Drawing.Imaging.EncoderParameters]::new(1)
            $encoderOptions.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new([System.Drawing.Imaging.Encoder]::Quality, [long]90)
            $bitmap.Save($Destination, $jpegEncoder, $encoderOptions)
        }
        $bytes = (Get-Item -LiteralPath $Destination).Length
        if ($bytes -ge 1000000) { throw "Upload asset exceeds conservative 1 MB limit: $Destination" }
        $records.Add([ordered]@{
            file = $Destination.Substring($modRoot.Length + 1).Replace('\', '/')
            source = $Source.Substring($modRoot.Length + 1).Replace('\', '/')
            width = $width; height = $height; bytes = $bytes
            source_bytes = (Get-Item -LiteralPath $Source).Length
            sha256 = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
        })
    } finally {
        if ($encoderOptions) { $encoderOptions.Dispose() }
        if ($canvas) { $canvas.Dispose() }
        if ($bitmap) { $bitmap.Dispose() }
        $inputImage.Dispose()
    }
}
Export-UploadImage -Source $originalCover -Destination $activeCover -MaxWidth 512 -Png $true
foreach ($name in @('workshop-banner', 'divider-current-features', 'divider-planned-features', 'divider-alpha-feedback')) {
    Export-UploadImage -Source (Join-Path $modRoot "workshop/assets/$name.png") -Destination (Join-Path $modRoot "workshop/assets/$name.jpg") -MaxWidth 1280 -Png $false
}
$report = [ordered]@{
    date = '2026-10-30'; method = 'Windows System.Drawing resize and PNG/JPEG encoding'
    original_cover_preserved = $true; steam_upload_verified = $false; assets = $records
}
$json = $report | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText((Join-Path $modRoot 'workshop/optimized-assets-manifest.json'), $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
$records | ForEach-Object { [pscustomobject]$_ } | Select-Object file, width, height, bytes | Format-Table -AutoSize
