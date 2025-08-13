# AI Assistant

Voice controlled assistant integrating Scrypted cameras, Ollama LLM/VLM and
Coqui/Piper TTS.

## Setup

1. Create and activate a conda environment named `ai-assistant`.
2. `pip install -r requirements.txt`
3. Install a compatible NVIDIA GPU driver.
4. Install [Ollama](https://ollama.ai) and run `scripts/install_ollama_models.ps1`
   to pull the required models (`llama3.1` and `llava`).
5. Copy `.env.example` to `.env` and fill in your `SCRYPTED_URL` and
   `SCRYPTED_TOKEN`.

## Development

Run the assistant in development mode:

```powershell
./scripts/run_dev.ps1
```

## Testing

Run unit tests with:

```bash
pytest
```

## Troubleshooting

- Ensure CUDA is correctly installed and accessible.
- Check audio device permissions if recording or playback fails.
- Verify Scrypted URL/token and network connectivity.
