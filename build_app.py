"""提供unity自动出包功能"""
import os
import sys
from pathlib import Path
import configparser
import argparse
from datetime import datetime
from logger import logger
import build_tool


def _resolve_path(value):
    """解析路径，如果路径不存在则返回原始值。"""
    try:
        return str(Path(value).resolve())
    except FileNotFoundError:
        logger.warning(f"Path {value} does not exist, using original value.")
        return str(Path(value))


def _read_app_cfg_and_set_env(file_path):
    logger.info(f"Read build cofnig:{file_path}")
    cfg = configparser.ConfigParser()
    cfg.read(file_path)

    for section in cfg.sections():
        for key, value in cfg.items(section):
            env_key = key.upper()
            v = value
            if value is not None and value.strip() != '':
                # 处理Proj路径
                if env_key == 'PROJ_DIR':
                    v = _resolve_path(value)
                os.environ[env_key] = str(v)
                logger.info("Build set env %s:%s", env_key, v)


def _build_app_and_run_unity_command():
    # 确保所有使用的环境变量都已定义
    required_env_vars = ['BUILD_TARGET', 'PROJ_DIR',
                         'UNITY_EXECUTABLE', 'BUILD_NAME']
    if build_tool.check_environ(required_env_vars) is not True:
        sys.exit(1)

    BUILD_TARGET = os.environ['BUILD_TARGET']
    PROJ_DIR = Path(os.environ['PROJ_DIR'])
    UNITY_EXECUTABLE = os.environ.get(
        'UNITY_EXECUTABLE', 'xvfb-run --auto-servernum --server-args="-screen 0 640x480x24" unity-editor')
    BUILD_NAME = os.environ['BUILD_NAME']

    logger.info(f"Building for {BUILD_TARGET}")

    BUILD_PATH = Path(os.environ['BUILD_OUTPUT_ROOT']) / 'Builds' / BUILD_TARGET
    BUILD_PATH.mkdir(parents=True, exist_ok=True)

    current_date = datetime.now().strftime('%m-%d-%H-%M')

    build_name = f'{BUILD_NAME}_{current_date}'

    # 构建 Unity 命令
    unity_cmd = [
        *UNITY_EXECUTABLE.split(),  # 解析可能包含空格的命令
        '-projectPath', str(PROJ_DIR),
        '-quit',
        '-batchmode',
        '-nographics',
        '-buildTarget', BUILD_TARGET,
        '-customBuildTarget', BUILD_TARGET,
        '-customBuildName', build_name,
        '-customBuildPath', str(BUILD_PATH),
        '-executeMethod', 'BuildCommand.PerformBuild',
        # '-logFile', str(BUILD_LOG_PATH.absolute())
        # '-logFile -'
    ]

    cmd_str = ' '.join(unity_cmd)
    logger.info(f"Running Unity with command: {cmd_str}")
    build_tool.run_unity_command(cmd_str)
    # 列出构建路径中的文件
    logger.info("Contents of build path:")
    if BUILD_PATH.exists():
        for item in BUILD_PATH.iterdir():
            logger.info(item)
    else:
        logger.warning(f"Build path {BUILD_PATH} does not exist.")

    # 检查构建文件夹是否为空
    if not any(BUILD_PATH.iterdir()):
        logger.error("Build folder is empty, failing job.")
        sys.exit(1)


def build_app(file_path):
    """读取配置文件，构建Unity应用

    Args:
        file_path (string): 配置文件路径
    """
    _read_app_cfg_and_set_env(file_path)
    _build_app_and_run_unity_command()


def _main():
    logger.info(build_tool.HEADER)
    parser = argparse.ArgumentParser(description="Unity build tool")
    parser.add_argument('cfg_path', type=str, help='build config ini file')
    args = parser.parse_args()
    if not os.path.isfile(args.cfg_path):
        logger.info(f"Error: The file {args.cfg_path} does not exist.")
        return
    build_app(args.cfg_path)


if __name__ == "__main__":
    logger.add("logs/app/build_app_{time}.log",
               backtrace=True, diagnose=True, enqueue=True)
    _main()
