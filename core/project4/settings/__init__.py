from pathlib import Path

from environ import Env
from split_settings.tools import include

env = Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


include(
    "base.py",
    "local.py",
    "project.py",
)
