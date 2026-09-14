from __future__ import annotations
import logging
import sys

def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging with configurable level."""
    logging_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set third-party loggers to a higher level to reduce noise
    logging.getLogger("uvicorn").setLevel(logging_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
