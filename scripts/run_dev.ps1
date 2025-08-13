# Activate conda environment and run the assistant in development mode
param([string]$Args="")
conda activate ai-assistant
python -m assistant.main $Args
