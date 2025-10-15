from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

@dataclass
class AppConfig(object):
    """Base configuration class."""

    logo_path: Path = Path(__file__).parent.parent / "assets" / "logo-2.png"
    favicon_path: Path = Path(__file__).parent.parent / "assets" / "favicon.ico"
    page_title: str = "Cell "