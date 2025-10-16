from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

@dataclass
class AppConfig(object):
    """Base configuration class."""

    logo_path: Path = Path(__file__).parent.parent / "assets" / "logo-2.png"
    icon_path: Path = Path(__file__).parent.parent / "assets" / "logo.png"
    favicon_path: Path = Path(__file__).parent.parent / "assets" / "favicon.ico"
    app_name: str = str(os.getenv("APP_NAME", "Cell"))
    page_title: str = str(os.getenv("PAGE_TITLE", "Cell - GenAI Chat UI"))
    log_max_size: int = int(os.getenv("LOG_MAX_SIZE", 10000000))  # in bytes
    log_max_backups: int = int(os.getenv("LOG_MAX_BACKUPS", 5))  # number of backup files