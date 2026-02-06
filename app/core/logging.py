import logging
import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable to store the request_id
request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

class RequestIdFilter(logging.Filter):
    """
    Logging filter that injects the current request_id from contextvars into the log record.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get() or "no-request-id"
        return True

def setup_logging():
    """
    Configures the standard logging library with a professional format and the RequestIdFilter.
    """
    log_format = "%(asctime)s | %(levelname)-8s | [%(request_id)s] | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    
    # Configure the root logger
    logging.basicConfig(level=logging.INFO)
    
    # Get the root logger or specific loggers as needed
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplicates (important for some environments)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    # Add our custom filter
    handler.addFilter(RequestIdFilter())
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Optional: Silence some noisy third-party loggers
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = True
