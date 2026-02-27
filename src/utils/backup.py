import shutil
import os
from pathlib import Path
from datetime import datetime

def perform_backup(source_path):
    backup_dir_str = os.environ.get("BOOKMARK_BACKUP_DIR")
    if not backup_dir_str:
        print("Backup directory not set. Add $BOOKMARK_BACKUP_DIR to your environment variable.")
        return

    backup_dir = Path(backup_dir_str)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Using underscores instead of colons for better shell compatibility
    timestring = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"urls_{timestring}.db"

    try:
        shutil.copy2(source_path, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Backup failed: {e}")
