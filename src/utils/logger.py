import logging
import os
from datetime import datetime
from pathlib import Path

class HedgeLabLogger:
    """Centralized logging system for HedgeLab"""
    
    def __init__(self, name: str = "hedgelab"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for all logs
        all_logs_file = logs_dir / f"hedgelab_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(all_logs_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # File handler for errors only
        error_logs_file = logs_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_logs_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # File handler for API calls
        api_logs_file = logs_dir / f"api_calls_{datetime.now().strftime('%Y%m%d')}.log"
        api_handler = logging.FileHandler(api_logs_file)
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(simple_formatter)
        
        # Console handler (only warnings and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(api_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def api_call(self, endpoint: str, status: str, response_time: float = None, error: str = None):
        """Log API call details"""
        message = f"API_CALL - {endpoint} - {status}"
        if response_time:
            message += f" - {response_time:.2f}s"
        if error:
            message += f" - ERROR: {error}"
        self.logger.info(message)
    
    def rate_limit(self, endpoint: str, retry_after: int = None):
        """Log rate limiting events"""
        message = f"RATE_LIMIT - {endpoint}"
        if retry_after:
            message += f" - Retry after {retry_after}s"
        self.logger.warning(message)
    
    def data_fallback(self, source: str, reason: str):
        """Log when falling back to mock data"""
        self.logger.info(f"DATA_FALLBACK - {source} - {reason}")
    
    def user_action(self, action: str, details: str = None):
        """Log user actions"""
        message = f"USER_ACTION - {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def performance(self, operation: str, duration: float):
        """Log performance metrics"""
        self.logger.info(f"PERFORMANCE - {operation} - {duration:.2f}s")

# Global logger instance
logger = HedgeLabLogger() 