"""
Module for project-level configuration.
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
S3_BUCKET = "cs4120-final-project-data"
HUGGINGFACE_MODEL = "https://s3.amazonaws.com/models.huggingface.co/transfer-learning-chatbot/gpt_personachat_cache.tar.gz"
WRITE_TEMP_PROGRESS = True
