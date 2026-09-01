"""
AutoPilot CLI — lightweight automation utilities.
"""

import os
import shutil
import tarfile
import zipfile
import logging
import hashlib
import platform
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("AutoPilot")


class BackupManager:
    def __init__(self, source_dirs: List[str], destination: str):
        self.source_dirs = source_dirs
        self.destination = Path(destination)
        self.destination.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, compress: str = "zip") -> Optional[Path]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = platform.node()
        archive_name = f"backup_{hostname}_{timestamp}"
        
        if compress == "zip":
            archive_path = self.destination / f"{archive_name}.zip"
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for src in self.source_dirs:
                    src_path = Path(src)
                    if not src_path.exists():
                        continue
                    for file in src_path.rglob("*"):
                        if file.is_file():
                            zf.write(file, file.relative_to(src_path.parent))
            logger.info(f"Backup created: {archive_path}")
            return archive_path
        
        elif compress == "tar.gz":
            archive_path = self.destination / f"{archive_name}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tf:
                for src in self.source_dirs:
                    tf.add(src, arcname=os.path.basename(src))
            logger.info(f"Backup created: {archive_path}")
            return archive_path
        
        return None
    
    def prune(self, keep: int = 5):
        backups = sorted(self.destination.glob("backup_*"), key=os.path.getmtime, reverse=True)
        for old in backups[keep:]:
            old.unlink()
            logger.info(f"Pruned old backup: {old}")


class FileOrganizer:
    @staticmethod
    def organize_by_extension(directory: str, move: bool = False):
        path = Path(directory)
        for item in path.iterdir():
            if item.is_file():
                ext = item.suffix.lower() or "no_extension"
                target_dir = path / ext.lstrip(".")
                target_dir.mkdir(exist_ok=True)
                if move:
                    shutil.move(str(item), str(target_dir / item.name))
                else:
                    shutil.copy2(str(item), str(target_dir / item.name))
    
    @staticmethod
    def find_duplicates(directory: str) -> List[List[str]]:
        hashes = {}
        for file in Path(directory).rglob("*"):
            if file.is_file():
                h = hashlib.md5(file.read_bytes()).hexdigest()
                hashes.setdefault(h, []).append(str(file))
        return [files for files in hashes.values() if len(files) > 1]
    
    @staticmethod
    def disk_usage(directory: str) -> dict:
        total = 0
        count = 0
        for f in Path(directory).rglob("*"):
            if f.is_file():
                total += f.stat().st_size
                count += 1
        return {"files": count, "bytes": total, "human": f"{total / (1024**2):.1f} MB"}


class HealthCheck:
    @staticmethod
    def check_disk(path: str = "/") -> dict:
        usage = shutil.disk_usage(path)
        return {
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent_used": round(usage.used / usage.total * 100, 1),
        }
    
    @staticmethod
    def check_memory() -> dict:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        mem = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                mem[k.strip()] = int(v.strip().split()[0])
        total = mem.get("MemTotal", 0)
        available = mem.get("MemAvailable", 0)
        return {
            "total_mb": round(total / 1024, 1),
            "available_mb": round(available / 1024, 1),
            "used_percent": round((total - available) / total * 100, 1) if total else 0,
        }
    
    @staticmethod
    def check_uptime() -> dict:
        with open("/proc/uptime") as f:
            uptime_seconds = float(f.read().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return {
            "uptime_seconds": uptime_seconds,
            "human": f"{days}d {hours}h {minutes}m",
        }
    
    @classmethod
    def system_report(cls) -> dict:
        return {
            "hostname": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "disk": cls.check_disk(),
            "memory": cls.check_memory(),
            "uptime": cls.check_uptime(),
            "timestamp": datetime.now().isoformat(),
        }
