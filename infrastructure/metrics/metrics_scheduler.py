"""Metrics scheduling and periodic collection."""
import asyncio
import logging
from typing import Optional

from .metrics_config import METRICS_CONFIG
from .telegram_metrics import TelegramMetrics
from .prometheus_exporter import PrometheusExporter

logger = logging.getLogger(__name__)

class MetricsScheduler:
    """Scheduler for periodic metrics collection and reporting."""
    
    def __init__(self, metrics_collector: TelegramMetrics):
        self.metrics = metrics_collector
        self.config = METRICS_CONFIG
        self.exporter: Optional[PrometheusExporter] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False
        
        if self.config['prometheus_enabled']:
            self.exporter = PrometheusExporter(metrics_collector)
    
    async def start(self):
        """Start metrics scheduling."""
        if not self.config['enabled']:
            logger.info("⚠️ Metrics disabled, skipping scheduler")
            return
            
        self._running = True
        
        # Start Prometheus server if enabled
        if self.exporter and self.config['prometheus_enabled']:
            self.exporter.start_metrics_server()
        
        # Start periodic metrics collection
        self._task = asyncio.create_task(self._metrics_loop())
        logger.info("✅ Metrics scheduler started")
    
    async def stop(self):
        """Stop metrics scheduling."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Metrics scheduler stopped")
    
    async def _metrics_loop(self):
        """Main metrics collection loop."""
        while self._running:
            try:
                await self._collect_and_report_metrics()
                await asyncio.sleep(self.config['metrics_interval'])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in metrics loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _collect_and_report_metrics(self):
        """Collect and report current metrics."""
        try:
            # Log metrics summary
            self.metrics.log_metrics_summary()
            
            # Export to Prometheus if enabled
            if self.exporter:
                self.exporter.export_metrics()
            
            # Check for performance issues
            self._check_performance_issues()
            
        except Exception as e:
            logger.error(f"❌ Error collecting metrics: {e}")
    
    def _check_performance_issues(self):
        """Check for performance issues and alert."""
        summary = self.metrics.get_metrics_summary()
        thresholds = self.config['performance_thresholds']
        
        # Check error rate
        if summary['error_rate'] > thresholds['high_error_rate']:
            logger.warning(
                f"🚨 High error rate: {summary['error_rate']:.1%} "
                f"({summary['errors_total']} errors)"
            )
        
        # Check slow handlers
        for handler, avg_time in summary['average_handler_times'].items():
            if avg_time > thresholds['slow_handler']:
                logger.warning(
                    f"🐢 Slow handler detected: {handler} "
                    f"(avg: {avg_time:.3f}s)"
                )
    
    def get_metrics_report(self) -> dict:
        """Get current metrics report."""
        return self.metrics.get_detailed_metrics()
