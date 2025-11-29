"""Log file management and utilities."""
import os
import glob
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LogManager:
    """Manager for log files and log rotation."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure log directory exists."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            logger.info(f"📁 Created log directory: {self.log_dir}")
    
    def get_log_files(self, pattern: str = "*.log") -> List[str]:
        """Get list of log files matching pattern."""
        search_pattern = os.path.join(self.log_dir, pattern)
        return sorted(glob.glob(search_pattern), key=os.path.getmtime, reverse=True)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about log files."""
        log_files = self.get_log_files()
        total_size = 0
        file_stats = []
        
        for log_file in log_files:
            try:
                size = os.path.getsize(log_file)
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                total_size += size
                
                file_stats.append({
                    'filename': os.path.basename(log_file),
                    'size_bytes': size,
                    'size_human': self._human_readable_size(size),
                    'modified': mtime,
                    'age_days': (datetime.now() - mtime).days
                })
            except OSError as e:
                logger.error(f"❌ Error getting stats for {log_file}: {e}")
        
        return {
            'total_files': len(log_files),
            'total_size_bytes': total_size,
            'total_size_human': self._human_readable_size(total_size),
            'files': file_stats
        }
    
    def cleanup_old_logs(self, max_age_days: int = 30):
        """Clean up log files older than specified days."""
        log_files = self.get_log_files()
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        for log_file in log_files:
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                if mtime < cutoff_date:
                    os.remove(log_file)
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted old log file: {os.path.basename(log_file)}")
            except OSError as e:
                logger.error(f"❌ Error deleting {log_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"✅ Cleaned up {deleted_count} old log files")
        else:
            logger.debug("✅ No old log files to clean up")
    
    def get_log_content(self, filename: str, lines: int = 100) -> List[str]:
        """Get last N lines from a log file."""
        filepath = os.path.join(self.log_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Log file not found: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.readlines()[-lines:]
        except Exception as e:
            logger.error(f"❌ Error reading log file {filename}: {e}")
            raise
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def log_system_info(self):
        """Log system information for debugging."""
        import platform
        import sys
        
        system_info = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'working_directory': os.getcwd(),
            'log_directory': self.log_dir
        }
        
        logger.info("🔧 System information:")
        for key, value in system_info.items():
            logger.info(f"   {key}: {value}")

def setup_log_cleanup(max_age_days: int = 30):
    """Setup periodic log cleanup."""
    log_manager = LogManager()
    
    try:
        log_manager.cleanup_old_logs(max_age_days)
    except Exception as e:
        logger.error(f"❌ Log cleanup failed: {e}")
