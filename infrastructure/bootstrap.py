"""Bootstrap application."""
import logging
from infrastructure.cache import create_cache

logger = logging.getLogger(__name__)

class Application:
    """Main application class."""
    
    def __init__(self, config: dict):
        self.config = config
        self.bot = None
        self.dispatcher = None
        self.cache = None
        self.metrics = None
        self.metrics_scheduler = None
        
    async def setup_logging(self):
        """Setup application logging."""
        from infrastructure.logging import setup_logging, setup_log_cleanup
        
        # Get logging configuration
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_to_file = log_config.get('file_enabled', True)
        
        # Setup logging
        setup_logging(
            log_level=log_level,
            log_to_file=log_to_file,
            log_dir='logs'
        )
        
        # Cleanup old logs
        setup_log_cleanup(max_age_days=30)
        
        logger.info(f"✅ Logging configured. Level: {log_level}, File: {log_to_file}")

    async def setup_cache(self):
        """Setup cache."""
        try:
            from infrastructure.cache import create_cache
            self.cache = create_cache()
            logger.info("✅ Cache initialized")
        except Exception as e:
            logger.error(f"❌ Cache setup failed: {e}")
            raise
    
    async def setup_error_handling(self):
        """Setup error handling middleware."""
        from infrastructure.error_handling import ErrorHandlingMiddleware
        
        # Add error handling middleware to dispatcher
        error_middleware = ErrorHandlingMiddleware()
        self.dispatcher.update.outer_middleware(error_middleware)
        logger.info("✅ Error handling middleware registered")
    
    async def setup_request_logging(self):
        """Setup request logging middleware."""
        from infrastructure.logging import RequestLoggingMiddleware
        
        # Add request logging middleware
        request_middleware = RequestLoggingMiddleware()
        self.dispatcher.update.outer_middleware(request_middleware)
        logger.info("✅ Request logging middleware registered")

    async def setup_metrics(self):
        """Setup metrics collection."""
        if not self.config.get('metrics', {}).get('enabled', True):
            logger.info("⚠️ Metrics disabled")
            return
            
        from infrastructure.metrics import TelegramMetrics, MetricsScheduler
        
        # Initialize metrics
        self.metrics = TelegramMetrics()
        self.metrics_scheduler = MetricsScheduler(self.metrics)
        
        # Pass metrics to context
        self.dispatcher['metrics'] = self.metrics
        
        # Start metrics collection
        await self.metrics_scheduler.start()
        logger.info("✅ Metrics system initialized")

    async def setup(self):
        """Setup application."""
        # Setup logging first (so we can log everything else)
        await self.setup_logging()
        
        logger.info("🔧 Starting application initialization...")
        
        # Initialize cache
        await self.setup_cache()
        
        # Create bot and dispatcher
        from presentation.telegram.bot import create_bot, create_dispatcher
        from presentation.telegram.handlers import setup_handlers
        
        self.bot = create_bot(self.config['telegram']['bot_token'])
        self.dispatcher = create_dispatcher()
        
        # Pass services to context
        self.dispatcher['cache'] = self.cache
        
        # Setup request logging
        await self.setup_request_logging()
        
        # Setup error handling
        await self.setup_error_handling()
        
        # Setup metrics
        await self.setup_metrics()
        
        # Setup handlers
        setup_handlers(self.dispatcher)
        logger.info("✅ Handlers registered")
        
        logger.info("✅ Initialization completed")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.cache:
            await self.cache.close()
            logger.info("✅ Cache closed")
        
        if hasattr(self, 'metrics_scheduler'):
     await self.metrics_scheduler.stop()
            logger.info("✅ Metrics scheduler stopped")
