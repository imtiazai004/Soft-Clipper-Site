# Builds the hero video for the website: the original 16:9 on the left, the
# finished 9:16 clip on the right, side by side, looping and silent.
#
# You supply two files — the source video and a clip Soft Clipper made from it.
# This puts them together, compresses the result to something a web page can
# afford, and pulls a poster frame for the page to show while it loads.
#
#   .\tools\make-hero.ps1 -Source "C:\path\source.mp4" -Clip "C:\path\clip.mp4"
#
# Output lands in public/: hero.mp4, hero.webm, hero.jpg

param(
	[Parameter(Mandatory = $true)][string]$Source,
	[Parameter(Mandatory = $true)][string]$Clip,
	# Keep it short. A hero video is a glance, not a film, and every second
	# costs page weight on the most important page of the site.
	[int]$Seconds = 12,
	[string]$OutDir = "public"
)

$ErrorActionPreference = "Stop"

foreach ($f in @($Source, $Clip)) {
	if (-not (Test-Path $f)) { throw "File not found: $f" }
}
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
	throw "ffmpeg is not on PATH. Install it, or run this from a shell where Soft Clipper's ffmpeg is available."
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$mp4 = Join-Path $OutDir "hero.mp4"
$webm = Join-Path $OutDir "hero.webm"
$poster = Join-Path $OutDir "hero.jpg"

# 1280x720 canvas: the source scaled into the left two-thirds, the vertical clip
# standing full height on the right. Audio is dropped entirely (-an) because the
# video autoplays muted anyway and the track would only add weight.
$filter = @"
[0:v]scale=832:468:force_original_aspect_ratio=decrease,pad=832:720:(ow-iw)/2:(oh-ih)/2:color=0x0c0c18,setsar=1[left];
[1:v]scale=405:720:force_original_aspect_ratio=decrease,pad=448:720:(ow-iw)/2:(oh-ih)/2:color=0x0c0c18,setsar=1[right];
[left][right]hstack=inputs=2[out]
"@ -replace "`r`n", ""

Write-Host "==> Building $mp4"
ffmpeg -y -t $Seconds -i $Source -t $Seconds -i $Clip `
	-filter_complex $filter -map "[out]" -an `
	-c:v libx264 -profile:v high -pix_fmt yuv420p -crf 30 -preset slow `
	-movflags +faststart $mp4

# WebM is typically 30-40% smaller than the MP4 at the same quality. Browsers
# pick whichever they support, so shipping both is a free saving for most.
Write-Host "==> Building $webm"
ffmpeg -y -i $mp4 -c:v libvpx-vp9 -crf 40 -b:v 0 -an $webm

# The poster is what people see before the video plays — and on a slow
# connection it may be all they ever see, so take it from a frame with the
# subject in it rather than the first frame, which is often black.
Write-Host "==> Building $poster"
ffmpeg -y -ss 2 -i $mp4 -frames:v 1 -q:v 3 $poster

Write-Host ""
Write-Host "Done. Sizes:"
Get-ChildItem $mp4, $webm, $poster | ForEach-Object {
	"{0,-12} {1,8:N0} KB" -f $_.Name, ($_.Length / 1KB)
}
Write-Host ""
Write-Host "Aim for hero.mp4 under 2000 KB. If it is bigger, re-run with a lower"
Write-Host "-Seconds value, or raise -crf 30 to 32-34 in this script."
