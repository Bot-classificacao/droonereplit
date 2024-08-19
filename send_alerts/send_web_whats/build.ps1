$exclude = @("venv", "send_web_whats.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "send_web_whats.zip" -Force