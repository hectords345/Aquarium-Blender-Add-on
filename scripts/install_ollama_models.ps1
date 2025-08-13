# Ensure the Ollama service is reachable and pull required models
try {
    curl http://localhost:11434/api/version | Out-Null
} catch {
    Write-Host "Ollama service not running" -ForegroundColor Red
    exit 1
}

ollama pull llama3.1
ollama pull llava
