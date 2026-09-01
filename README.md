# AutoPilot CLI

Lightweight Python automation utilities for backups, file organization, and system health checks.

## Install

```bash
pip install -r requirements.txt
```

## Commands

```bash
# Create a ZIP backup
python -m src.cli backup /home/user/projects /mnt/backup

# Organize files by extension
python -m src.cli organize ~/Downloads --move

# Find duplicates
python -m src.cli duplicates ~/Downloads

# System health report
python -m src.cli health

# Disk usage
python -m src.cli usage /home/user
```

## License

MIT
