# Genera archivos WAV con la voz de Windows (System.Speech) a partir de una lista JSON.
# Uso: powershell -NoProfile -File tts.ps1 -Jobs jobs.json -Voice "Microsoft Helena Desktop" -Rate 0
# jobs.json: [{"file": "ruta.wav", "text": "..."}, ...]. Si el WAV ya existe, no se regenera.
param([string]$Jobs, [string]$Voice = "Microsoft Helena Desktop", [int]$Rate = 0)
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SelectVoice($Voice)
$s.Rate = $Rate
$list = Get-Content -Raw -Encoding UTF8 $Jobs | ConvertFrom-Json
foreach ($j in $list) {
    if (-not (Test-Path $j.file)) {
        $s.SetOutputToWaveFile($j.file)
        $s.Speak($j.text)
        $s.SetOutputToNull()
    }
}
