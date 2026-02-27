import os
from pathlib import Path

# Database Paths
DATABASE_FILE = os.path.expanduser("~/.urls.db")

# Backup Configuration
BACKUP_DIR_STR = os.environ.get("BOOKMARK_BACKUP_DIR")
BACKUP_DIR = Path(BACKUP_DIR_STR) if BACKUP_DIR_STR else None
BACKUP_THRESHOLD = 5

# Logging Constants
LOG_FILE = "errors.log"
LOG_FORMAT = "%(asctime)s - %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"
