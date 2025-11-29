"""Metrics configuration."""
import os
import time
from typing import Dict, Any

METRICS_CONFIG = {
    'enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
    'prometheus_enabled': os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true',
    'log_metrics': os.getenv('LOG_METRICS', 'true').lower() == 'true',
    'metrics_interval': int(os.getenv('METRICS_INTERVAL', '60')),  # seconds
    'track_performance': True,
    'track_errors': True,
    'track_user_actions': True,
    'track_messages': True,
    'track_callbacks': True,
    'performance_thresholds': {
        'slow_handler': 1.0,  # seconds
        'very_slow_handler': 3.0,  # seconds
        'high_error_rate': 0.1  # 10%
    }
}

class MetricsState:
    """Global metrics state."""
    
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.callback_count = 0
        self.error_count = 0
        self.user_sessions = set()
        self.handler_times = {}
        self.error_types = {}
        
    def reset(self):
        """Reset metrics (for testing)."""
        self.message_count = 0
        self.callback_count = 0
        self.error_count = 0
        self.user_sessions.clear()
        self.handler_times.clear()
        self.error_types.clear()

# Global metrics state
metrics_state = MetricsState()
