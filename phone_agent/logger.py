"""Logging utilities for PhoneAgent - 日志工具模块

这个模块的作用：
1. 让程序输出同时显示在控制台和保存到文件
2. 支持 emoji 和中文字符
3. 自动在日志文件中添加时间戳
4. 支持保存截图到日志目录

使用方法：
    # 在 main.py 中初始化（指定输出文件）
    from phone_agent.logger import setup_logger, get_logger
    logger = setup_logger(output_file="./output/result.log")
    
    # 在其他模块中直接使用
    from phone_agent.logger import get_logger
    logger = get_logger()
    logger.info("这条消息会同时输出到控制台和文件")
    
    # 保存截图
    from phone_agent.logger import save_screenshot
    screenshot_path = save_screenshot(base64_data, step_num=1)
"""

import base64
import logging
import sys
from datetime import datetime
from pathlib import Path


class AgentFormatter(logging.Formatter):
    """自定义格式器，支持 emoji 和原样输出消息"""

    def format(self, record):
        return record.getMessage()


# 全局 logger 实例
_agent_logger = None
# 全局日志目录
_log_dir = None


def setup_logger(output_file: str | None = None, verbose: bool = True) -> logging.Logger:
    """
    设置并配置 agent 日志器。

    Args:
        output_file: 可选的日志文件路径。如果为 None，只输出到控制台。
        verbose: 是否显示详细输出。

    Returns:
        配置好的 logger 实例。
    """
    global _agent_logger, _log_dir

    logger = logging.getLogger("phone_agent")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # 清除已有的 handlers
    logger.handlers.clear()

    # 控制台 handler - 始终添加
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(AgentFormatter())
    logger.addHandler(console_handler)

    # 文件 handler - 如果指定了 output_file 则添加
    if output_file:
        # 确保目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存日志目录路径（用于保存截图）
        _log_dir = output_path.parent

        file_handler = logging.FileHandler(output_file, encoding="utf-8", mode="w")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(AgentFormatter())
        logger.addHandler(file_handler)

        # 写入带时间戳的文件头
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("=" * 50)
        logger.info(f"📝 Phone Agent 日志 - {timestamp}")
        logger.info("=" * 50)
        logger.info("")

    _agent_logger = logger
    return logger


def get_logger() -> logging.Logger:
    """
    获取 agent logger 实例。

    Returns:
        Logger 实例。如果未初始化则创建默认 logger。
    """
    global _agent_logger
    if _agent_logger is None:
        _agent_logger = setup_logger()
    return _agent_logger


def get_log_dir() -> Path | None:
    """
    获取日志目录路径。

    Returns:
        日志目录的 Path 对象，如果未设置则返回 None。
    """
    return _log_dir


def save_screenshot(base64_data: str, step_num: int, prefix: str = "step") -> str | None:
    """
    保存截图到日志目录。

    Args:
        base64_data: 截图的 base64 编码数据。
        step_num: 当前步骤编号。
        prefix: 文件名前缀，默认为 "step"。

    Returns:
        保存的截图文件路径，如果保存失败则返回 None。
    """
    global _log_dir
    
    if _log_dir is None:
        return None
    
    try:
        # 创建 screenshots 子目录
        screenshots_dir = _log_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"{prefix}_{step_num:03d}_{timestamp}.png"
        filepath = screenshots_dir / filename
        
        # 解码并保存图片
        image_data = base64.b64decode(base64_data)
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        # 返回相对路径（相对于日志目录）
        return f"screenshots/{filename}"
    
    except Exception as e:
        logger = get_logger()
        logger.info(f"⚠️ 保存截图失败: {e}")
        return None
