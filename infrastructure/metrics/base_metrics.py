"""Base metrics collector."""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .metrics_config import METRICS_CONFIG, metrics_state

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Base metrics collector with common functionality."""
    
    def __init__(self):
        self.config = METRICS_CONFIG
        self.state = metrics_state
        
    def record_message(self, user_id: Optional[int] = None):
        """Record message metric."""
        if not self.config['track_messages']:
            return
            
        self.state.message_count += 1
        if user_id:
            self.state.user_sessions.add(user_id)
            
        if self.config['log_metrics']:
            logger.debug(f"📨 Message recorded: total={self.state.message_count}")
    
    def record_callback(self, user_id: Optional[int] = None):
        """Record callback metric."""
        if not self.config['track_callbacks']:
            return
            
        self.state.callback_count += 1
        if user_id:
            self.state.user_sessions.add(user_id)
            
        if self.config['log_metrics']:
            logger.debug(f"🖱️ Callback recorded: total={self.state.callback_count}")
    
    def record_error(self, error_type: str, user_id: Optional[int] = None):
        """Record error metric."""
        if not self.config['track_errors']:
            return
            
        self.state.error_count += 1
        self.state.error_types[error_type] = self.state.error_types.get(error_type, 0) + 1
        
        if self.config['log_metrics']:
            logger.debug(f"❌ Error recorded: {error_type}, total={self.state.error_count}")
    
    def record_handler_time(self, handler_name: str, execution_time: float):
        """Record handler execution time."""
        if not self.config['track_performance']:
            return
            
        if handler_name not in self.state.handler_times:
            self.state.handler_times[handler_name] = []
        
        self.state.handler_times[handler_name].append(execution_time)
        
        # Check performance thresholds
        thresholds = self.config['performance_thresholds']
        if execution_time > thresholds['very_slow_handler']:
            logger.warning(f"🐌 Very slow handler: {handler_name} took {execution_time:.3f}s")
        elif execution_time > thresholds['slow_handler']:
            logger.info(f"🐢 Slow handler: {handler_name} took {execution_time:.3f}s")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        uptime = time.time() - self.state.start_time
        total_actions = self.state.message_count + self.state.callback_count
        error_rate = self.state.error_count / max(total_actions, 1)
        
        # Calculate average handler times
        avg_times = {}
        for handler, times in self.state.handler_times.items():
            if times:
                avg_times[handler] = sum(times) / len(times)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'messages_total': self.state.message_count,
            'callbacks_total': self.state.callback_count,
            'errors_total': self.state.error_count,
            'unique_users': len(self.state.user_sessions),
            'error_rate': error_rate,
            'average_handler_times': avg_times,
            'error_breakdown': dict(self.state.error_types)
        }
    
    def log_metrics_summary(self):
        """Log metrics summary."""
        if not self.config['log_metrics']:
            return
            
        summary = self.get_metrics_summary()
        
        logger.info("📊 METRICS SUMMARY:")
        logger.info(f"   Uptime: {summary['uptime_seconds']:.0f}s")
        logger.info(f"   Messages: {summary['messages_total']}")
        logger.info(f"   Callbacks: {summary['callbacks_total']}")
        logger.info(f"   Unique users: {summary['unique_users']}")
        logger.info(f"   Errors: {summary['errors_total']} (rate: {summary['error_rate']:.1%})")
        
        if summary['error_breakdown']:
            logger.info("   Error breakdown:")
            for error_type, count in summary['error_breakdown'].items():
                logger.info(f"     - {error_type}: {count}")
        
        if summary['average_handler_times']:
            logger.info("   Handler performance:")
            for handler, avg_time in summary['average_handler_times'].items():
                logger.info(f"     - {handler}: {avg_time:.3f}s")
