"""Prometheus metrics exporter."""
import time
import logging
from typing import Dict, Any

from .metrics_config import METRICS_CONFIG
from .telegram_metrics import TelegramMetrics

logger = logging.getLogger(__name__)

class PrometheusExporter:
    """Prometheus metrics exporter for Telegram bot."""
    
    def __init__(self, metrics_collector: TelegramMetrics):
        self.metrics = metrics_collector
        self.config = METRICS_CONFIG
        
        if self.config['prometheus_enabled']:
            try:
                from prometheus_client import Counter, Histogram, Gauge, start_http_server
                self.prometheus_available = True
                self.setup_prometheus_metrics()
                logger.info("✅ Prometheus exporter initialized")
            except ImportError:
                self.prometheus_available = False
                logger.warning("⚠️ Prometheus client not available")
        else:
            self.prometheus_available = False
    
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        if not self.prometheus_available:
            return
            
        from prometheus_client import Counter, Histogram, Gauge
        
        # Counters
        self.messages_counter = Counter(
            'telegram_bot_messages_total',
            'Total number of messages processed',
            ['type']
        )
        
        self.errors_counter = Counter(
            'telegram_bot_errors_total',
            'Total number of errors',
            ['error_type']
        )
        
        self.user_actions_counter = Counter(
            'telegram_bot_user_actions_total',
            'Total user actions',
            ['action_type', 'status']
        )
        
        # Gauges
        self.active_users_gauge = Gauge(
            'telegram_bot_active_users',
            'Number of active users'
        )
        
        self.uptime_gauge = Gauge(
            'telegram_bot_uptime_seconds',
            'Bot uptime in seconds'
        )
        
        # Histograms
        self.handler_duration_histogram = Histogram(
            'telegram_bot_handler_duration_seconds',
            'Handler execution duration',
            ['handler_name'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
    
    def export_metrics(self):
        """Export current metrics to Prometheus."""
        if not self.prometheus_available:
            return
            
        try:
            detailed_metrics = self.metrics.get_detailed_metrics()
            
            # Update counters
            self.messages_counter.labels(type='text').inc(detailed_metrics['messages_total'])
            self.messages_counter.labels(type='callback').inc(detailed_metrics['callbacks_total'])
            
            # Update error counters
            for error_type, count in detailed_metrics['error_breakdown'].items():
                self.errors_counter.labels(error_type=error_type).inc(count)
            
            # Update gauges
            self.active_users_gauge.set(detailed_metrics['unique_users'])
            self.uptime_gauge.set(detailed_metrics['uptime_seconds'])
            
            # Update handler durations
            for handler_name, stats in detailed_metrics['handler_statistics'].items():
                self.handler_duration_histogram.labels(handler_name=handler_name).observe(
                    stats['avg_time_seconds']
                )
                
            logger.debug("✅ Metrics exported to Prometheus")
            
        except Exception as e:
            logger.error(f"❌ Failed to export metrics to Prometheus: {e}")
    
    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server."""
        if not self.prometheus_available:
            logger.warning("⚠️ Prometheus not enabled, skipping metrics server")
            return
            
        try:
            from prometheus_client import start_http_server
            start_http_server(port)
            logger.info(f"📊 Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"❌ Failed to start Prometheus server: {e}")
