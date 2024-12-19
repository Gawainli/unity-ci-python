import sys
import loguru

# from pathlib import Path

def setup_logger():
    """创建logger

    Returns:
        logger 
    """
    _logger = loguru.logger
    return _logger

# 初始化全局 logger
logger = setup_logger()
