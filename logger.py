""" 日志模块

Returns:
    loguru.logger: 返回一个logger实例
"""
import loguru

def setup_logger():
    """创建logger

    Returns:
        logger 
    """
    _logger = loguru.logger
    return _logger


# 初始化全局 logger
logger = setup_logger()
