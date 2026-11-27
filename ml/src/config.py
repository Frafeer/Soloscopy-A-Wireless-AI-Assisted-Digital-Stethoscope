from pathlib import Path

# Resolves to .../Soloscopy-A-Wireless-AI-Assisted-Digital-Stethoscope/ml
ML_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ML_DIR / "data"