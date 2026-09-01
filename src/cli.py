"""AutoPilot CLI entry point."""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autopilot import BackupManager, FileOrganizer, HealthCheck

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("AutoPilot")


def cmd_backup(args):
    mgr = BackupManager(args.sources, args.destination)
    archive = mgr.create_backup(compress=args.format)
    if archive:
        print(f"Backup created: {archive}")
        if args.prune:
            mgr.prune(keep=args.keep)
    else:
        print("Backup failed")
        sys.exit(1)


def cmd_organize(args):
    FileOrganizer.organize_by_extension(args.directory, move=args.move)
    print(f"Organized files in {args.directory}")


def cmd_duplicates(args):
    dups = FileOrganizer.find_duplicates(args.directory)
    if dups:
        print(f"Found {len(dups)} duplicate groups:")
        for group in dups:
            for f in group:
                print(f"  {f}")
            print()
    else:
        print("No duplicates found")


def cmd_health(args):
    report = HealthCheck.system_report()
    print(json.dumps(report, indent=2))


def cmd_usage(args):
    usage = FileOrganizer.disk_usage(args.directory)
    print(json.dumps(usage, indent=2))


def main():
    parser = argparse.ArgumentParser(description="AutoPilot CLI — automation utilities")
    sub = parser.add_subparsers(dest="command")

    # backup
    p_backup = sub.add_parser("backup", help="Create compressed backup")
    p_backup.add_argument("sources", nargs="+", help="Source directories")
    p_backup.add_argument("destination", help="Destination directory")
    p_backup.add_argument("--format", choices=["zip", "tar.gz"], default="zip")
    p_backup.add_argument("--prune", action="store_true", help="Remove old backups")
    p_backup.add_argument("--keep", type=int, default=5)

    # organize
    p_organize = sub.add_parser("organize", help="Organize files by extension")
    p_organize.add_argument("directory", help="Target directory")
    p_organize.add_argument("--move", action="store_true", help="Move instead of copy")

    # duplicates
    p_dup = sub.add_parser("duplicates", help="Find duplicate files")
    p_dup.add_argument("directory", help="Target directory")

    # health
    sub.add_parser("health", help="System health report")

    # usage
    p_usage = sub.add_parser("usage", help="Disk usage")
    p_usage.add_argument("directory", help="Target directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "backup": cmd_backup,
        "organize": cmd_organize,
        "duplicates": cmd_duplicates,
        "health": cmd_health,
        "usage": cmd_usage,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
